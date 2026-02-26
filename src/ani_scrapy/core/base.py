from abc import ABC
from typing import Optional

from ani_scrapy.core.browser import AsyncBrowser


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
