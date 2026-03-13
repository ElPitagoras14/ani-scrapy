"""AnimeAV1 scraper."""

from datetime import datetime
from typing import Optional

from ani_scrapy.core.log import logger

from ani_scrapy.core.base import BaseScraper
from ani_scrapy.core.browser import AsyncBrowser
from ani_scrapy.core.http import AsyncHttpAdapter
from ani_scrapy.providers.animeav1.parser import AnimeAV1Parser
from ani_scrapy.providers.animeav1.constants import BASE_URL, SEARCH_ENDPOINT
from ani_scrapy.core.schemas import (
    PagedSearchAnimeInfo,
    AnimeInfo,
    EpisodeInfo,
    EpisodeDownloadInfo,
    DownloadLinkInfo,
)


class AnimeAV1Scraper(BaseScraper):
    """AnimeAV1 scraper."""

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
        self.parser = AnimeAV1Parser()
        self._schedule_cache: dict[str, datetime] = {}

    async def search_anime(
        self,
        query: str,
        page: int = 1,
    ) -> PagedSearchAnimeInfo:
        """Search anime."""

        logger.info("Searching anime | query={query}", query=query)

        if page < 1:
            raise ValueError("The variable 'page' must be greater than 0")

        html = await self.http.get(
            SEARCH_ENDPOINT, params={"search": query, "page": page}
        )
        animes = self.parser.parse_search_results(html)
        total_pages = self.parser.parse_total_pages(html)

        logger.info("Search completed | count={count}", count=len(animes))

        return PagedSearchAnimeInfo(
            page=page,
            total_pages=total_pages,
            animes=animes,
        )

    async def get_anime_info(
        self,
        anime_id: str,
        include_episodes: bool = True,
    ) -> AnimeInfo:
        """Get anime info."""

        logger.info("Getting anime info | anime_id={anime_id}", anime_id=anime_id)

        html = await self.http.get(f"media/{anime_id}")
        anime_info = self.parser.parse_anime_info(html, anime_id, include_episodes)

        # If not finished, fetch schedule for next episode date
        if not anime_info.is_finished and not anime_info.next_episode_date:
            schedule = await self._get_schedule()
            if anime_id in schedule:
                anime_info.next_episode_date = schedule[anime_id]

        logger.info("Anime info fetched")
        return anime_info

    async def _get_schedule(self) -> dict[str, datetime]:
        """Get schedule from /horario page."""

        if self._schedule_cache:
            return self._schedule_cache

        try:
            html = await self.http.get("horario")
            schedule = self.parser.parse_schedule(html)
            self._schedule_cache = schedule
            return schedule
        except Exception as e:
            logger.warning("Failed to get schedule | error={error}", error=str(e))
            return {}

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

        html = await self.http.get(f"media/{anime_id}")
        anime_info = self.parser.parse_anime_info(html, anime_id, include_episodes=True)

        new_episodes = [
            ep
            for ep in anime_info.episodes
            if ep is not None and ep.number > last_episode_number
        ]

        logger.info("New episodes fetched | count={count}", count=len(new_episodes))
        return new_episodes

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

        if episode_number < 0:
            raise ValueError(
                "The variable 'episode_number' must be greater than or equal to 0"
            )

        html = await self.http.get(f"media/{anime_id}/{episode_number}")
        download_links = self.parser.parse_episode_page(html, anime_id)

        logger.info(
            "Table download links fetched | count={count}",
            count=len(download_links),
        )
        return EpisodeDownloadInfo(
            episode_number=episode_number,
            download_links=download_links,
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

        if episode_number < 0:
            raise ValueError(
                "The variable 'episode_number' must be greater than or equal to 0"
            )

        html = await self.http.get(f"media/{anime_id}/{episode_number}")
        iframe_links = self.parser.parse_episode_embeds(html)

        logger.info(
            "Iframe download links fetched | count={count}",
            count=len(iframe_links),
        )
        return EpisodeDownloadInfo(
            episode_number=episode_number,
            download_links=iframe_links,
        )

    async def get_file_download_link(
        self,
        download_info: DownloadLinkInfo,
    ) -> str | None:
        """Get file download link from download info."""

        if not isinstance(download_info, DownloadLinkInfo):
            raise TypeError("download_info must be a DownloadLinkInfo object")

        server = download_info.server
        url = download_info.url

        if url is None:
            return None

        logger.info("Getting file download link | server={server}", server=server)

        if server == "PDrain":
            return await self._get_pdrawin_download_link(url)
        elif server == "UPNShare":
            return await self._get_upnshare_download_link(url)
        else:
            logger.warning("Server not supported | server={server}", server=server)
            return None

    async def _get_pdrawin_download_link(self, url: str) -> str | None:
        """Get PDrain download link."""
        file_id = url.split("/")[-1].split("?")[0]
        return f"https://pixeldrain.com/api/file/{file_id}?download"

    async def _get_upnshare_download_link(self, url: str) -> str | None:
        """Get UPNShare download link."""

        dl_url = url + "&dl=1" if "&" not in url else url + "&dl=1"

        try:
            browser = await self._get_browser()
            async with await browser.new_page() as page:
                await page.goto(dl_url)

                await page.wait_for_load_state("networkidle")
                await page.wait_for_timeout(2000)

                await page.evaluate(
                    """() => {
                        const overlay = document.querySelector('div[style*="z-index: 2147483647"]');
                        if (overlay) {
                            overlay.remove();
                        }
                    }"""
                )

                button = await page.wait_for_selector(
                    "button.downloader-button", timeout=10000
                )

                if button:
                    await button.dispatch_event("click")

                    anchor = await page.wait_for_selector(
                        "a.downloader-button[href][download]", timeout=15000
                    )

                    if anchor is not None:
                        download_url = await anchor.get_attribute("href")
                        return download_url

        except Exception as e:
            logger.warning(
                "Failed to get UPNShare download link | error={error}",
                error=str(e),
            )

        return None

    async def aclose(self) -> None:
        """Cleanup resources."""
        await self.http.close()
        await super().aclose()
