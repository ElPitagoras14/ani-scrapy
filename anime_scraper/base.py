from abc import ABC, abstractmethod
from typing import List
import asyncio

from anime_scraper.browser_manager import BrowserManager
from anime_scraper.schemas import (
    BulkDownloadLinkInfo,
    PagedSearchAnimeInfo,
    AnimeInfo,
    DownloadLinkInfo,
)


class BaseAnimeScraper(ABC):
    # ASYNC METHODS
    @abstractmethod
    async def search_anime_async(
        self, query: str = None, **kwargs
    ) -> List[PagedSearchAnimeInfo]:
        pass

    @abstractmethod
    async def get_anime_info_async(self, anime_id: str = None) -> AnimeInfo:
        pass

    @abstractmethod
    async def get_static_download_links_async(
        self, anime_id: str = None, episode_id: int = None
    ) -> List[DownloadLinkInfo]:
        pass

    @abstractmethod
    async def get_dynamic_download_links_async(
        self,
        anime_id: str = None,
        episode_id: int = None,
        link_limit: int = None,
        browser: BrowserManager = None,
    ) -> List[DownloadLinkInfo]:
        pass

    @abstractmethod
    async def get_bulk_dynamic_download_links_async(
        self,
        anime_id: str = None,
        episodes_ids: List[int] = None,
        link_limit: int = None,
        max_concurrent: int = 3,
    ) -> List[BulkDownloadLinkInfo]:
        pass

    # SYNC METHODS

    def search_anime(
        self, query: str = None, **kwargs
    ) -> List[PagedSearchAnimeInfo]:
        return asyncio.run(self.search_anime_async(query, **kwargs))

    def get_anime_info(self, anime_id: str = None) -> AnimeInfo:
        return asyncio.run(self.get_anime_info_async(anime_id))

    def get_static_download_links(
        self, anime_id: str = None, episode_id: int = None
    ) -> List[DownloadLinkInfo]:
        return asyncio.run(
            self.get_static_download_links_async(anime_id, episode_id)
        )

    def get_dynamic_download_links(
        self,
        anime_id: str = None,
        episode_id: int = None,
        link_limit: int = None,
        browser: BrowserManager = None,
    ) -> List[DownloadLinkInfo]:
        return asyncio.run(
            self.get_dynamic_download_links_async(
                anime_id, episode_id, link_limit, browser
            )
        )
