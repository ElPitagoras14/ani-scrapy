from abc import ABC


class BaseScraper(ABC):
    """Base class for anime scrapers."""

    def __init__(
        self,
        headless: bool = True,
        executable_path: str = "",
    ) -> None:
        self.headless = headless
        self.executable_path = executable_path

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.aclose()

    def close(self):
        """Close resources. Override in subclasses."""
        pass

    async def aclose(self):
        """Async close resources. Override in subclasses."""
        pass
