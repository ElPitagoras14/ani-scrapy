from abc import abstractmethod
from typing import List, Optional

from ani_scrapy.core.base import BaseScraper
from ani_scrapy.core.schemas import (
    AnimeInfo,
    DownloadLinkInfo,
    EpisodeDownloadInfo,
    EpisodeInfo,
    PagedSearchAnimeInfo,
)
from ani_scrapy.sync_api.browser import SyncBrowser


class SyncBaseScraper(BaseScraper):
    """
    Abstract base class for sync anime scrapers.
    """

    @abstractmethod
    def search_anime(self, query: str, **kwargs) -> PagedSearchAnimeInfo:
        pass

    @abstractmethod
    def get_anime_info(
        self,
        anime_id: str,
        include_episodes: bool = True,
        tab_timeout: int = 200,
        **kwargs,
    ) -> AnimeInfo:
        pass

    @abstractmethod
    def get_new_episodes(
        self,
        anime_id: str,
        last_episode_number: int,
        tab_timeout: int = 200,
        browser: Optional[SyncBrowser] = None,
    ) -> List[EpisodeInfo]:
        pass

    @abstractmethod
    def get_table_download_links(
        self, anime_id: str, episode_number: int, **kwargs
    ) -> EpisodeDownloadInfo:
        pass

    @abstractmethod
    def get_iframe_download_links(
        self,
        anime_id: str,
        episode_number: int,
        browser: Optional[SyncBrowser] = None,
    ) -> EpisodeDownloadInfo:
        pass

    @abstractmethod
    def get_file_download_link(
        self,
        download_info: DownloadLinkInfo,
        browser: Optional[SyncBrowser] = None,
    ) -> Optional[str]:
        pass
