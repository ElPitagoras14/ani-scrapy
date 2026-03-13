from abc import ABC, abstractmethod
from typing import Optional

from ani_scrapy.core.browser import AsyncBrowser
from ani_scrapy.core.schemas import (
    AnimeInfo,
    DownloadLinkInfo,
    EpisodeDownloadInfo,
    EpisodeInfo,
    PagedSearchAnimeInfo,
)


class BaseScraper(ABC):
    """Base class for anime scrapers."""

    def __init__(
        self,
        headless: bool = True,
        executable_path: str = "",
        external_browser: Optional[AsyncBrowser] = None,
    ) -> None:
        self.headless = headless
        self.executable_path = executable_path
        self._external_browser = external_browser
        self._browser: Optional[AsyncBrowser] = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.aclose()

    async def _get_browser(self) -> AsyncBrowser:
        """Get browser instance, creating one if needed."""
        if self._external_browser is not None:
            return self._external_browser

        if self._browser is None:
            self._browser = AsyncBrowser(
                headless=self.headless,
                executable_path=(
                    self.executable_path if self.executable_path else None
                ),
            )
            await self._browser.__aenter__()
        return self._browser

    async def start_browser(self) -> None:
        """Manually start the browser for reuse across operations."""
        if self._external_browser is not None:
            return

        if self._browser is None:
            self._browser = AsyncBrowser(
                headless=self.headless,
                executable_path=(
                    self.executable_path if self.executable_path else None
                ),
            )
            await self._browser.__aenter__()

    async def stop_browser(self) -> None:
        """Manually stop the browser."""
        if self._external_browser is not None:
            self._external_browser = None
            return

        if self._browser is not None:
            await self._browser.__aexit__(None, None, None)
            self._browser = None

    async def aclose(self):
        """Close resources."""
        if self._browser is not None:
            await self._browser.__aexit__(None, None, None)
            self._browser = None
        self._external_browser = None

    @abstractmethod
    async def search_anime(
        self,
        query: str,
        page: int = 1,
    ) -> PagedSearchAnimeInfo:
        """Search anime by query."""
        ...

    @abstractmethod
    async def get_anime_info(
        self,
        anime_id: str,
        include_episodes: bool = True,
    ) -> AnimeInfo:
        """Get detailed anime information."""
        ...

    @abstractmethod
    async def get_new_episodes(
        self,
        anime_id: str,
        last_episode_number: int,
    ) -> list[EpisodeInfo]:
        """Get episodes newer than last_episode_number."""
        ...

    @abstractmethod
    async def get_table_download_links(
        self,
        anime_id: str,
        episode_number: int,
    ) -> EpisodeDownloadInfo:
        """Get table download links for an episode."""
        ...

    @abstractmethod
    async def get_iframe_download_links(
        self,
        anime_id: str,
        episode_number: int,
    ) -> EpisodeDownloadInfo:
        """Get iframe download links for an episode."""
        ...

    @abstractmethod
    async def get_file_download_link(
        self,
        download_info: DownloadLinkInfo,
    ) -> str | None:
        """Get direct file download link from download info."""
        ...
