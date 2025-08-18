from abc import abstractmethod

from ani_scrapy.core.base import BaseScraper
from ani_scrapy.core.schemas import (
    AnimeInfo,
    DownloadLinkInfo,
    EpisodeDownloadInfo,
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
    async def get_anime_info(self, anime_id: str, **kwargs) -> AnimeInfo:
        pass

    @abstractmethod
    async def get_table_download_links(
        self, anime_id: str, episode_id: int, **kwargs
    ) -> EpisodeDownloadInfo:
        pass

    @abstractmethod
    async def get_iframe_download_links(
        self,
        anime_id: str,
        episode_id: int,
        browser: AsyncBrowser | None = None,
    ) -> EpisodeDownloadInfo:
        pass

    @abstractmethod
    async def get_file_download_link(
        self,
        download_info: DownloadLinkInfo,
        browser: AsyncBrowser | None = None,
    ):
        pass
