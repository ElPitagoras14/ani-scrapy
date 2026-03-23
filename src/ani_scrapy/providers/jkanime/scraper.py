"""JKAnime scraper."""

import asyncio
import time
from typing import Optional
from urllib.parse import quote
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from ani_scrapy.core.log import logger

from ani_scrapy.core.base import BaseScraper
from ani_scrapy.core.browser import AsyncBrowser
from ani_scrapy.core.http import AsyncHttpAdapter
from ani_scrapy.providers.jkanime.parser import JKAnimeParser
from ani_scrapy.providers.jkanime.constants import (
    BASE_URL,
    SEARCH_ENDPOINT,
    SW_DOWNLOAD_URL,
    SUPPORTED_SERVERS,
)
from ani_scrapy.core.constants.general import (
    SW_TIMEOUT,
    MEDIAFIRE_TIMEOUT,
)
from ani_scrapy.core.exceptions import ScraperTimeoutError
from ani_scrapy.core.schemas import (
    AnimeInfo,
    DownloadLinkInfo,
    EpisodeDownloadInfo,
    EpisodeInfo,
    PagedSearchAnimeInfo,
)


class JKAnimeScraper(BaseScraper):
    """JKAnime scraper."""

    def __init__(
        self,
        headless: bool = True,
        executable_path: str = "",
        external_browser: Optional[AsyncBrowser] = None,
    ):
        super().__init__(
            headless=headless,
            executable_path=executable_path,
            external_browser=external_browser,
        )
        self.http = AsyncHttpAdapter(base_url=BASE_URL)
        self.parser = JKAnimeParser()

        self._file_link_getters = {
            "Streamwish": self._get_streamwish_file_link,
            "Mediafire": self._get_mediafire_file_link,
        }

        self._iframe_link_getters = {
            "Magi": self._get_magi_link,
            "Streamwish": self._get_streamwish_link,
        }

    async def _safe_click(
        self,
        element,
        page,
        reclick: bool = False,
        timeout: int = 10,
        debug_name: str = "",
    ) -> None:
        """Safely click an element handling popups."""
        ctx = page.context

        popup_task = asyncio.create_task(ctx.wait_for_event("page"))

        start = time.perf_counter()
        await element.click(force=True)
        elapsed = time.perf_counter() - start
        logger.debug(
            "[{name}] Clicked | {ms}ms",
            name=debug_name,
            ms=round(elapsed * 1000, 2),
        )

        popup = None
        try:
            popup = await asyncio.wait_for(popup_task, timeout=timeout / 1000)
            await popup.wait_for_load_state("domcontentloaded", timeout=3000)
            await popup.close()
        except (asyncio.TimeoutError, PlaywrightTimeoutError):
            if popup:
                await popup.close()
        finally:
            if reclick:
                await element.click(force=True)

    async def search_anime(self, query: str, page: int = 1) -> PagedSearchAnimeInfo:
        """Search anime."""

        logger.info("Searching anime | query={query}", query=query)

        safe_query = quote(query)
        search_anime_url = f"{SEARCH_ENDPOINT}/{safe_query}"
        logger.debug("Using search URL | url={url}", url=search_anime_url)

        try:
            html_text = await self.http.get(search_anime_url)
        except ConnectionError as e:
            raise ScraperTimeoutError(str(e)) from e

        animes = self.parser.parse_search_results(html_text)

        logger.info("Search completed | count={count}", count=len(animes))

        return PagedSearchAnimeInfo(
            page=1,
            total_pages=1,
            animes=animes,
        )

    async def get_anime_info(
        self,
        anime_id: str,
        include_episodes: bool = True,
    ) -> AnimeInfo:
        """Get anime info."""

        logger.info("Getting anime info | anime_id={anime_id}", anime_id=anime_id)

        if include_episodes:
            url = f"{BASE_URL}/{anime_id}"
            browser = await self._get_browser()
            async with await browser.new_page() as page:
                return await self._get_anime_info_with_episodes(page, url, anime_id)

        try:
            html_text = await self.http.get(anime_id)
        except ConnectionError as e:
            raise ScraperTimeoutError(str(e)) from e

        return self.parser.parse_anime_info(html_text, anime_id)

    async def _get_anime_info_with_episodes(
        self, page, url: str, anime_id: str
    ) -> AnimeInfo:
        """Get anime info with episodes using Playwright."""

        logger.debug("Fetching anime info page with Playwright")

        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_selector("div.col-lg-2.picd")

        html_text = await page.content()
        anime_info = self.parser.parse_anime_info(html_text, anime_id)

        episodes = await self._extract_all_episodes(page, anime_id)
        anime_info.episodes = list(episodes)

        logger.info("Anime info fetched | episodes={count}", count=len(episodes))
        return anime_info

    async def _extract_all_episodes(self, page, anime_id: str) -> list[EpisodeInfo]:
        """Extract all episodes by navigating pages."""

        await page.wait_for_selector("div.nice-select.anime__pagination ul > li")
        select = await page.query_selector("div.nice-select.anime__pagination")

        paged_episodes = await select.query_selector_all("ul.list > li")

        logger.info(
            "Starting episode extraction | total_pages={total}",
            total=len(paged_episodes),
        )

        all_episodes = []
        idx = 0
        retries = max(int(len(paged_episodes) * 1.5), 5)
        is_retry = False

        while idx < len(paged_episodes):
            if retries <= 0:
                logger.warning("Retries exceeded, breaking")
                break

            if is_retry:
                await page.wait_for_selector(
                    "div.nice-select.anime__pagination ul > li"
                )
                select = await page.query_selector("div.nice-select.anime__pagination")
                paged_episodes = await select.query_selector_all("ul.list > li")
                is_retry = False

                if idx >= len(paged_episodes):
                    logger.warning(
                        "Index out of bounds after retry | idx={idx} | pages={pages}",
                        idx=idx,
                        pages=len(paged_episodes),
                    )
                    break

            paged_episode = paged_episodes[idx]

            logger.info(
                "Processing page {idx} of {total}",
                idx=idx + 1,
                total=len(paged_episodes),
            )

            await self._safe_click(
                select,
                page,
                reclick=True,
                timeout=3000,
                debug_name=f"select_reclick_{idx + 1}",
            )

            await self._safe_click(
                paged_episode,
                page,
                timeout=2000,
                debug_name=f"page_click_{idx + 1}",
            )

            html_text = await page.content()
            new_episodes = self.parser.parse_episode_page(html_text, anime_id)

            logger.info(
                "Extracted episodes from page | count={count} | last={last}",
                count=len(new_episodes),
                last=new_episodes[-1].number if new_episodes else None,
            )

            if not new_episodes:
                logger.warning("[ITER_{idx}] EMPTY - Continuing", idx=idx + 1)

                retries -= 1
                is_retry = True
                continue

            if idx > 0 and all_episodes:
                last_extracted = all_episodes[-1].number
                last_page_episode = new_episodes[-1].number
                if last_page_episode == last_extracted:
                    logger.warning(
                        "[ITER_{idx}] SAME episodes detected - Continuing",
                        idx=idx + 1,
                    )

                    retries -= 1
                    is_retry = True
                    continue

            all_episodes.extend(new_episodes)
            idx += 1

        logger.info("All episodes extracted | count={count}", count=len(all_episodes))
        return all_episodes

    async def get_new_episodes(
        self,
        anime_id: str,
        last_episode_number: int,
    ) -> list[EpisodeInfo]:
        """Get new episodes since last_episode_number."""

        logger.info(
            "Getting new episodes | anime_id={anime_id} last_episode_number={last_episode_number}",
            anime_id=anime_id,
            last_episode_number=last_episode_number,
        )

        url = f"{BASE_URL}/{anime_id}"

        browser = await self._get_browser()
        async with await browser.new_page() as page:
            return await self._get_new_episodes_internal(
                page, url, anime_id, last_episode_number
            )

    async def _get_new_episodes_internal(
        self,
        page,
        url: str,
        anime_id: str,
        last_episode_number: int,
    ) -> list[EpisodeInfo]:
        """Internal method for getting new episodes."""

        await page.goto(url)
        await page.wait_for_selector("div.nice-select.anime__pagination ul > li")

        select = await page.query_selector("div.nice-select.anime__pagination")
        paged_episodes = await select.query_selector_all("ul.list > li")

        logger.debug(
            "Found {count} episode pages",
            count=len(paged_episodes),
        )

        all_episodes = []
        idx = len(paged_episodes) - 1
        retries = max(int(len(paged_episodes) * 1.5), 5)
        finished = False
        is_retry = False

        logger.debug(
            "Starting new episode extraction | start_page={page} | last_episode={last}",
            page=idx + 1,
            last=last_episode_number,
        )

        while idx >= 0:
            if retries <= 0:
                logger.warning("Retries exceeded, breaking")
                break

            if is_retry:
                logger.debug("Retrying, fetching fresh select elements")
                await page.wait_for_selector(
                    "div.nice-select.anime__pagination ul > li"
                )
                select = await page.query_selector("div.nice-select.anime__pagination")
                paged_episodes = await select.query_selector_all("ul.list > li")
                is_retry = False

            logger.debug(
                "Processing page {idx} of {total}",
                idx=idx + 1,
                total=len(paged_episodes),
            )

            paged_episode = paged_episodes[idx]
            await self._safe_click(
                select,
                page,
                reclick=True,
                timeout=3000,
            )
            await self._safe_click(
                paged_episode,
                page,
                timeout=2000,
            )

            page_url = page.url
            if page_url != url:
                logger.warning(
                    "Page URL changed, retrying | retries_left={retries}",
                    retries=retries,
                )
                await page.close()
                page = await page.context.new_page()
                await page.goto(url)
                retries -= 1
                is_retry = True
                continue

            html_text = await page.content()
            new_episodes = self.parser.parse_episode_page(html_text, anime_id)

            logger.debug(
                "Extracted episodes from page | count={count} | last_episode={last}",
                count=len(new_episodes),
                last=new_episodes[-1].number if new_episodes else None,
            )

            if not new_episodes:
                logger.warning(
                    "Empty episodes page detected, retrying | retries_left={retries}",
                    retries=retries,
                )
                retries -= 1
                is_retry = True
                continue

            new_episodes_found = 0
            for episode in reversed(new_episodes):
                if episode.number <= last_episode_number:
                    finished = True
                    break
                all_episodes.append(episode)
                new_episodes_found += 1

            logger.debug(
                "New episodes on page | count={count} | last_extracted={last}",
                count=new_episodes_found,
                last=all_episodes[-1].number if all_episodes else None,
            )

            if idx > 0 and all_episodes:
                if new_episodes and new_episodes[-1].number == all_episodes[-1].number:
                    logger.warning(
                        "Same paged_episode detected, retrying | retries_left={retries}",
                        retries=retries,
                    )
                    retries -= 1
                    is_retry = True
                    continue

            idx -= 1

            if finished:
                break

        logger.info("New episodes fetched | count={count}", count=len(all_episodes))
        return all_episodes

    async def get_table_download_links(
        self,
        anime_id: str,
        episode_number: int,
    ) -> EpisodeDownloadInfo:
        """Get table download links for an episode."""

        logger.info(
            "Getting table download links | anime_id={anime_id} episode_number={episode_number}",
            anime_id=anime_id,
            episode_number=episode_number,
        )

        browser = await self._get_browser()
        async with await browser.new_page() as page:
            return await self._get_table_download_links_internal(
                page, anime_id, episode_number
            )

    async def _get_table_download_links_internal(
        self,
        page,
        anime_id: str,
        episode_number: int,
    ) -> EpisodeDownloadInfo:
        """Get table download links using page from Playwright."""

        url = f"{BASE_URL}/{anime_id}/{episode_number}"
        await page.goto(url)

        html = await page.content()
        download_links_data = self.parser.parse_table_download_links(
            html, episode_number
        )
        all_download_links: list[DownloadLinkInfo] = [
            DownloadLinkInfo(
                server=link["server"],
                url=(
                    None
                    if link["url"] and "c1.jkplayers.com" in link["url"]
                    else link["url"]
                ),
            )
            for link in download_links_data
        ]

        logger.info(
            "Table download links fetched | count={count}",
            count=len(all_download_links),
        )
        return EpisodeDownloadInfo(
            episode_number=episode_number,
            download_links=all_download_links,
        )

    async def get_iframe_download_links(
        self,
        anime_id: str,
        episode_number: int,
    ) -> EpisodeDownloadInfo:
        """Get iframe download links for an episode."""

        logger.info(
            "Getting iframe download links | anime_id={anime_id} episode_number={episode_number}",
            anime_id=anime_id,
            episode_number=episode_number,
        )

        browser = await self._get_browser()
        async with await browser.new_page() as page:
            return await self._get_iframe_download_links_internal(
                page, anime_id, episode_number
            )

    async def _get_iframe_download_links_internal(
        self,
        page,
        anime_id: str,
        episode_number: int,
    ) -> EpisodeDownloadInfo:
        """Get iframe download links using page from Playwright."""

        url = f"{BASE_URL}/{anime_id}/{episode_number}"
        await page.goto(url)

        await page.wait_for_selector("#collapseServers")

        download_links: list[DownloadLinkInfo] = []

        for server_name, link_getter in self._iframe_link_getters.items():
            logger.debug("Looking for server | server={server}", server=server_name)
            server_link = await page.query_selector(
                f'#collapseServers a:has-text("{server_name}")'
            )

            if not server_link:
                logger.warning(
                    "Server not found in page | server={server}",
                    server=server_name,
                )
                continue

            await server_link.click()
            await page.wait_for_timeout(3000)

            try:
                download_url = await link_getter(page)
                if download_url is not None:
                    download_links.append(
                        DownloadLinkInfo(server=server_name, url=download_url)
                    )
                    logger.info(
                        "Got iframe URL | server={server} url={url}",
                        server=server_name,
                        url=download_url,
                    )
            except Exception as e:
                logger.warning(
                    "Failed to get link for server | server={server} error={error}",
                    server=server_name,
                    error=str(e),
                )
                download_links.append(DownloadLinkInfo(server=server_name, url=None))

        logger.info(
            "Iframe download links fetched | count={count}",
            count=len(download_links),
        )
        return EpisodeDownloadInfo(
            episode_number=episode_number,
            download_links=download_links,
        )

    async def _get_magi_link(self, page) -> str | None:
        """Get Magi server link."""
        logger.debug("Getting Magi link")

        video_box_iframe = await page.query_selector("#video_box iframe")
        if not video_box_iframe:
            logger.warning("Video box iframe not found")
            return None

        src = await video_box_iframe.get_attribute("src")
        logger.debug("Video box iframe src | src={src}", src=src)

        frame = page.frame(url=lambda u: "jkanime.net/jkplayer" in u)
        if not frame:
            logger.warning("JKPlayer frame not found")
            return None

        logger.debug("Found jkanime frame, waiting for content...")

        try:
            magi_video = await frame.wait_for_selector(
                "video#video_html5_api", timeout=5000
            )
            if magi_video:
                source = await magi_video.query_selector("source")
                if source:
                    download_url = await source.get_attribute("src")
                    logger.debug("Found Magi source | src={src}", src=download_url)
                    return download_url
        except Exception:
            logger.warning("Magi video not found")

        return None

    async def _get_streamwish_link(self, page) -> str | None:
        """Get Streamwish server link."""
        logger.debug("Getting Streamwish link")

        video_box_iframe = await page.query_selector("#video_box iframe")
        if not video_box_iframe:
            logger.warning("Video box iframe not found")
            return None

        src = await video_box_iframe.get_attribute("src")
        logger.debug("Video box iframe src | src={src}", src=src)

        frame = page.frame(url=lambda u: "jkanime.net/jkplayer" in u)
        if not frame:
            logger.warning("JKPlayer frame not found")
            return None

        logger.debug("Found jkanime frame, waiting for content...")

        try:
            streamwish_iframe = await frame.wait_for_selector(
                'iframe[src*="sfastwish.com"]', timeout=5000
            )
            if streamwish_iframe:
                iframe_src = await streamwish_iframe.get_attribute("src")
                video_id = iframe_src.split("/")[-1]
                download_url = f"{SW_DOWNLOAD_URL}/{video_id}"
                logger.debug("Found Streamwish iframe | src={src}", src=iframe_src)
                return download_url
        except Exception:
            logger.warning("Streamwish iframe not found")

        return None

    async def get_file_download_link(
        self,
        download_info: DownloadLinkInfo,
    ) -> str | None:
        """Get file download link for a download link info object."""

        if not isinstance(download_info, DownloadLinkInfo):
            raise TypeError("download_info must be a DownloadLinkInfo object")

        server = download_info.server
        url = download_info.url

        if url is None:
            return None

        logger.info("Getting file download link | server={server}", server=server)

        if server not in SUPPORTED_SERVERS:
            logger.error(
                "Server not supported | server={server} supported={supported}",
                server=server,
                supported=SUPPORTED_SERVERS,
            )
            return None

        browser = await self._get_browser()
        async with await browser.new_page() as page:
            return await self._file_link_getters[server](page, url)

    async def _get_streamwish_file_link(self, page, url: str) -> str | None:
        """Get Streamwish file download link."""

        logger.debug("Getting Streamwish file link")

        await page.goto(url)
        current_url = page.url
        video_id = current_url.split("/")[-1]

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
                    await download_button.click(delay=1000)

                    try:
                        error_label = await page.wait_for_selector(
                            "div.text-danger.text-center.mb-5",
                            timeout=SW_TIMEOUT,
                        )
                        text_label = await error_label.inner_text()
                        if text_label.strip() == "Downloads disabled 620":
                            continue
                    except PlaywrightTimeoutError:
                        pass

                    download_link = await page.wait_for_selector(
                        "div.text-center a.btn", timeout=SW_TIMEOUT
                    )
                    return await download_link.get_attribute("href")
                except Exception:
                    continue

        return None

    async def _get_mediafire_file_link(self, page, url: str) -> str | None:
        """Get Mediafire file download link."""

        logger.debug("Getting Mediafire file link")

        await page.goto(url)

        try:
            download_button = await page.wait_for_selector(
                "a#downloadButton", timeout=MEDIAFIRE_TIMEOUT
            )
        except PlaywrightTimeoutError:
            return None

        async with page.expect_download() as download_info:
            await download_button.click()

        download = await download_info.value
        real_url = download.url
        await download.cancel()
        return real_url

    async def aclose(self) -> None:
        """Close resources."""
        await self.http.close()
        await super().aclose()
