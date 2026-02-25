"""AnimeFLV scraper."""

import asyncio
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from loguru import logger

from ani_scrapy.core.base import BaseScraper
from ani_scrapy.core.browser import AsyncBrowser
from ani_scrapy.core.http import AsyncHttpAdapter
from ani_scrapy.animeflv.parser import AnimeFLVParser
from ani_scrapy.animeflv.constants import (
    BASE_URL,
    ANIME_VIDEO_ENDPOINT,
    BASE_EPISODE_IMG_URL,
    SW_DOWNLOAD_URL,
)
from ani_scrapy.core.constants.general import (
    SW_TIMEOUT,
    YOURUPLOAD_TIMEOUT,
    YOURUPLOAD_DOWNLOAD_URL,
)
from ani_scrapy.core.schemas import (
    PagedSearchAnimeInfo,
    AnimeInfo,
    EpisodeInfo,
    EpisodeDownloadInfo,
    DownloadLinkInfo,
)


class AnimeFLVScraper(BaseScraper):
    """AnimeFLV scraper."""

    def __init__(
        self,
        headless: bool = True,
        executable_path: str = "",
    ):
        super().__init__(
            headless=headless,
            executable_path=executable_path,
        )
        self.http = AsyncHttpAdapter(base_url=BASE_URL)
        self.parser = AnimeFLVParser()

        self._tab_link_getters = {
            "SW": self._get_sw_link,
            "YourUpload": self._get_yourupload_link,
        }

        self._file_link_getters = {
            "SW": self._get_sw_file_link,
            "YourUpload": self._get_yourupload_file_link,
        }

    async def search_anime(
        self,
        query: str,
        page: int = 1,
    ) -> PagedSearchAnimeInfo:
        """Search anime."""
        log = logger
        log.info("Searching anime | query={query}", query=query)

        if page < 1:
            raise ValueError("The variable 'page' must be greater than 0")

        html = await self.http.get("browse", params={"q": query, "page": page})
        animes = self.parser.parse_search_results(html)

        log.info("Search completed | count={count}", count=len(animes))

        return PagedSearchAnimeInfo(
            page=page,
            total_pages=1,
            animes=animes,
        )

    async def get_anime_info(
        self,
        anime_id: str,
        include_episodes: bool = True,
    ) -> AnimeInfo:
        """Get anime info."""
        log = logger
        log.info("Getting anime info | anime_id={anime_id}", anime_id=anime_id)

        anime = await self._fetch_and_parse_info(anime_id, include_episodes)

        log.info("Anime info fetched")
        return anime

    async def get_new_episodes(
        self,
        anime_id: str,
        last_episode_number: int,
    ) -> list[EpisodeInfo]:
        """Get new episodes since last_episode_number."""
        log = logger
        log.info(
            "Getting new episodes | anime_id={anime_id} last_episode_number={last_episode_number}",
            anime_id=anime_id,
            last_episode_number=last_episode_number,
        )

        html = await self.http.get(f"anime/{anime_id}")
        info_ids, episodes_data = self.parser.extract_episode_data(html)

        if not info_ids or not episodes_data:
            return []

        anime_thumb_id = info_ids[0]
        episodes = []

        for episode_number, _ in episodes_data:
            number = int(episode_number)
            if number <= last_episode_number:
                break

            image_prev = (
                f"{BASE_EPISODE_IMG_URL}/{anime_thumb_id}/{number}/th_3.jpg"
            )
            episodes.append(
                EpisodeInfo(
                    number=number,
                    anime_id=anime_id,
                    image_preview=image_prev,
                )
            )

        log.info("New episodes fetched | count={count}", count=len(episodes))
        return list(reversed(episodes))

    async def get_table_download_links(
        self,
        anime_id: str,
        episode_number: int,
    ) -> EpisodeDownloadInfo:
        """Get table download links for an episode."""
        log = logger
        log.info(
            "Getting table download links | anime_id={anime_id} episode_number={episode_number}",
            anime_id=anime_id,
            episode_number=episode_number,
        )

        if episode_number < 0:
            raise ValueError(
                "The variable 'episode_number' must be greater than "
                + "or equal to 0"
            )

        url = f"{ANIME_VIDEO_ENDPOINT}/{anime_id}-{episode_number}"
        html = await self.http.get(url)
        download_links_data = self.parser.parse_table_download_links(
            html, episode_number
        )

        rows = [
            DownloadLinkInfo(server=link["server"], url=link["url"])
            for link in download_links_data
        ]

        log.info(
            "Table download links fetched | count={count}", count=len(rows)
        )
        return EpisodeDownloadInfo(
            episode_number=episode_number,
            download_links=rows,
        )

    async def get_iframe_download_links(
        self,
        anime_id: str,
        episode_number: int,
    ) -> EpisodeDownloadInfo:
        """Get iframe download links for an episode."""
        log = logger
        log.info(
            "Getting iframe download links | anime_id={anime_id} episode_number={episode_number}",
            anime_id=anime_id,
            episode_number=episode_number,
        )

        url = f"{ANIME_VIDEO_ENDPOINT}/{anime_id}-{episode_number}"

        executable_path = (
            self.executable_path if self.executable_path else None
        )
        async with AsyncBrowser(
            executable_path=executable_path,
            headless=self.headless,
        ) as browser:
            async with await browser.new_page() as page:
                return await self._get_iframe_download_links_internal(
                    page, url
                )

    async def _fetch_and_parse_info(
        self, anime_id: str, include_episodes: bool
    ) -> AnimeInfo:
        """Internal method for fetching and parsing anime info."""
        url = f"anime/{anime_id}"
        html = await self.http.get(url)
        anime_info = self.parser.parse_anime_info(
            html, anime_id, include_episodes=include_episodes
        )
        return anime_info

    async def _get_iframe_download_links_internal(self, page, url):
        """Internal method for getting iframe download links."""

        log = logger

        async def close_not_allowed_popups(popup) -> None:
            try:
                await popup.wait_for_load_state("domcontentloaded")
                if "www.yourupload.com" not in popup.url:
                    await popup.close()
            except Exception:
                try:
                    await popup.close()
                except Exception:
                    pass

        page.on(
            "popup",
            lambda popup: asyncio.create_task(close_not_allowed_popups(popup)),
        )
        await page.goto(url)

        server_urls = await page.query_selector_all("div.CpCnA ul.CapiTnv li")
        server_names = []

        for server_url in server_urls:
            try:
                title = await server_url.get_attribute("title")
                if title:
                    server_names.append(title)
            except Exception:
                continue

        download_links = []

        for server_name in server_names:
            try:
                if server_name in self._tab_link_getters:
                    link = await self._tab_link_getters[server_name](page)
                    download_links.append(
                        DownloadLinkInfo(
                            server=server_name,
                            url=link,
                        )
                    )
            except Exception as e:
                log.warning(
                    "Failed to get link for server | server={server} error={error}",
                    server=server_name,
                    error=str(e),
                )
                download_links.append(
                    DownloadLinkInfo(
                        server=server_name,
                        url=None,
                    )
                )

        log.info(
            "Iframe download links fetched | count={count}",
            count=len(download_links),
        )
        return EpisodeDownloadInfo(
            episode_number=int(url.split("-")[-1]),
            download_links=download_links,
        )

    async def get_file_download_link(
        self,
        download_info: DownloadLinkInfo,
    ) -> str | None:
        """Get file download link for a download link info object."""
        log = logger

        if not isinstance(download_info, DownloadLinkInfo):
            raise TypeError("download_info must be a DownloadLinkInfo object")

        server = download_info.server
        url = download_info.url

        if url is None:
            return None

        log.info("Getting file download link | server={server}", server=server)

        if server not in self._file_link_getters:
            log.error(
                "Server not supported for file download | server={server}",
                server=server,
            )
            return None

        executable_path = (
            self.executable_path if self.executable_path else None
        )
        async with AsyncBrowser(
            executable_path=executable_path,
            headless=self.headless,
        ) as browser:
            async with await browser.new_page() as page:
                page.on("popup", lambda popup: popup.close())
                return await self._file_link_getters[server](page, url)

    async def _get_sw_link(self, page):
        """Get SW server link."""
        log = logger
        log.debug("Getting SW link")

        video_element = await page.wait_for_selector(
            "div#video_box", timeout=SW_TIMEOUT
        )
        iframe_element = await video_element.query_selector("iframe")
        iframe_src = await iframe_element.get_attribute("src")
        video_id = iframe_src.split("/")[-1].split("?")[0]
        return f"{SW_DOWNLOAD_URL}/{video_id}"

    async def _get_yourupload_link(self, page):
        """Get YourUpload server link."""
        log = logger
        log.debug("Getting YourUpload link")

        video_element = await page.wait_for_selector(
            "div#video_box", timeout=YOURUPLOAD_TIMEOUT
        )
        iframe_element = await video_element.query_selector("iframe")
        iframe_src = await iframe_element.get_attribute("src")
        video_id = iframe_src.split("/")[-1].split("?")[0]
        return f"{YOURUPLOAD_DOWNLOAD_URL}/{video_id}"

    async def _get_sw_file_link(self, page, url: str):
        """Get SW file download link."""
        log = logger
        log.debug("Getting SW file link")

        try:
            await page.goto(url)
            video_id = url.split("/")[-1]
            try_urls = [
                f"{SW_DOWNLOAD_URL}/{video_id}_h",
                f"{SW_DOWNLOAD_URL}/{video_id}_n",
                f"{SW_DOWNLOAD_URL}/{video_id}_l",
            ]

            for try_url in try_urls:
                retries = 3
                for _ in range(retries):
                    try:
                        await page.goto(try_url)

                        download_button = await page.wait_for_selector(
                            "form#F1 button", timeout=3000
                        )
                        await download_button.click()

                        try:
                            error_label = await page.wait_for_selector(
                                "div.text-danger.text-center.mb-5",
                                timeout=SW_TIMEOUT,
                            )
                            text_label = await error_label.inner_text()
                            if text_label.strip() == "Downloads disabled 620":
                                continue
                            else:
                                break
                        except PlaywrightTimeoutError:
                            pass

                        download_link = await page.wait_for_selector(
                            "div.text-center a.btn", timeout=SW_TIMEOUT
                        )
                        return await download_link.get_attribute("href")
                    except Exception:
                        continue
        except Exception:
            pass
        return None

    async def _get_yourupload_file_link(self, page, url: str):
        """Get YourUpload file download link."""
        log = logger
        log.debug("Getting YourUpload file link")

        try:
            await page.goto(url)

            try:
                video_element = await page.wait_for_selector(
                    "div.jw-media video.jw-video", timeout=YOURUPLOAD_TIMEOUT
                )
                video_src = await video_element.get_attribute("src")
                return video_src
            except PlaywrightTimeoutError:
                return None
        except Exception:
            return None

    async def aclose(self) -> None:
        """Cleanup resources."""
        await self.http.close()
