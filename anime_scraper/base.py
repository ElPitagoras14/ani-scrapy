from abc import ABC, abstractmethod
import asyncio
from loguru import logger

from anime_scraper.browser_manager import BrowserManager
from anime_scraper.schemas import (
    DownloadLinkInfo,
    EpisodeDownloadInfo,
    PagedSearchAnimeInfo,
    AnimeInfo,
)

levels = [
    "debug",
    "info",
    "success",
    "warning",
    "error",
]


class BaseAnimeScraper(ABC):
    """
    Abstract base class for anime scrapers.
    """

    def __init__(self, verbose: bool = False, level: str = "info"):
        """
        Initialize the scraper.

        Parameters
        ----------
        verbose : bool, optional
            Whether to enable verbose logging. Defaults to False.

        level : str, optional
            The level of the messages to log (info, debug, warning,
            error, critical). Defaults to "info".
        """
        self.verbose = verbose
        self.level = level

    def _log(self, message: str, level: str = "info"):
        """
        Log a message with the specified level.

        Parameters
        ----------
        message : str
            The message to log.
        level : str, optional
            The level of the message (info, debug, warning, error, critical).
            Defaults to "info".
        """
        if not self.verbose and level not in levels:
            return

        curr_idx = levels.index(level)
        base_idx = levels.index(self.level)

        if curr_idx < base_idx:
            return

        log_fn = getattr(logger, level, logger.info)
        log_fn(message)

    # ==========================================================================
    # ASYNC METHODS
    # ==========================================================================

    @abstractmethod
    async def search_anime_async(
        self, query: str, **kwargs
    ) -> PagedSearchAnimeInfo:
        pass

    @abstractmethod
    async def get_anime_info_async(self, anime_id: str, **kwargs) -> AnimeInfo:
        pass

    @abstractmethod
    async def get_table_download_links_async(
        self, anime_id: str, episode_id: int, **kwargs
    ) -> EpisodeDownloadInfo:
        pass

    @abstractmethod
    async def get_iframe_download_links_async(
        self,
        anime_id: str,
        episode_id: int,
        browser: BrowserManager | None = None,
    ) -> EpisodeDownloadInfo:
        pass

    @abstractmethod
    async def get_file_download_links_async(
        self,
        download_info: DownloadLinkInfo,
        browser: BrowserManager | None = None,
    ):
        pass

    # ==========================================================================
    # SYNC METHODS
    # ==========================================================================

    def search_anime(self, query: str, **kwargs) -> PagedSearchAnimeInfo:
        return asyncio.run(self.search_anime_async(query, **kwargs))

    def get_anime_info(self, anime_id: str) -> AnimeInfo:
        return asyncio.run(self.get_anime_info_async(anime_id))

    def get_table_download_links(
        self,
        anime_id: str,
        episode_id: int,
        **kwargs,
    ) -> EpisodeDownloadInfo:
        return asyncio.run(
            self.get_table_download_links_async(anime_id, episode_id, **kwargs)
        )

    def get_iframe_download_links(
        self,
        anime_id: str,
        episode_id: int,
        browser: BrowserManager | None = None,
    ) -> EpisodeDownloadInfo:
        return asyncio.run(
            self.get_iframe_download_links_async(anime_id, episode_id, browser)
        )

    def get_file_download_links(
        self,
        download_info: DownloadLinkInfo,
        browser: BrowserManager | None = None,
    ):
        return asyncio.run(
            self.get_file_download_links_async(download_info, browser)
        )
