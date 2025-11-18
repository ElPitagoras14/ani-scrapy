from abc import abstractmethod

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
        **kwargs,
    ) -> AnimeInfo:
        pass

    @abstractmethod
    def get_new_episodes(
        self,
        anime_id: str,
        last_episode_number: int,
        browser: SyncBrowser | None = None,
    ) -> list[EpisodeInfo]:
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
        browser: SyncBrowser | None = None,
    ) -> EpisodeDownloadInfo:
        pass

    @abstractmethod
    def get_file_download_link(
        self,
        download_info: DownloadLinkInfo,
        browser: SyncBrowser | None = None,
    ) -> str | None:
        pass
