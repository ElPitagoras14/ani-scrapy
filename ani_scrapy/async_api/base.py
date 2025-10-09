from abc import abstractmethod

from ani_scrapy.core.base import BaseScraper
from ani_scrapy.core.schemas import (
    AnimeInfo,
    DownloadLinkInfo,
    EpisodeDownloadInfo,
    EpisodeInfo,
    PagedSearchAnimeInfo,
)
from ani_scrapy.async_api.browser import AsyncBrowser


class AsyncBaseScraper(BaseScraper):
    """
    Abstract base class for async anime scrapers.
    """

    @abstractmethod
    async def search_anime(self, query: str, **kwargs) -> PagedSearchAnimeInfo:
        pass

    @abstractmethod
    async def get_anime_info(
        self,
        anime_id: str,
        include_episodes: bool = True,
        tab_timeout: int = 200,
        **kwargs,
    ) -> AnimeInfo:
        pass

    @abstractmethod
    async def get_new_episodes(
        self,
        anime_id: str,
        last_episode_number: int,
        browser: AsyncBrowser | None = None,
    ) -> list[EpisodeInfo]:
        pass

    @abstractmethod
    async def get_table_download_links(
        self, anime_id: str, episode_number: int, **kwargs
    ) -> EpisodeDownloadInfo:
        pass

    @abstractmethod
    async def get_iframe_download_links(
        self,
        anime_id: str,
        episode_number: int,
        browser: AsyncBrowser | None = None,
    ) -> EpisodeDownloadInfo:
        pass

    @abstractmethod
    async def get_file_download_link(
        self,
        download_info: DownloadLinkInfo,
        browser: AsyncBrowser | None = None,
    ) -> str | None:
        pass
