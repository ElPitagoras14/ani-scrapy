from playwright.async_api import async_playwright
from playwright_stealth import Stealth

from ani_scrapy.core.constants.general import CONTEXT_OPTIONS

stealth = Stealth()


class AsyncBrowser:
    """Async browser manager."""

    def __init__(
        self,
        headless: bool = True,
        executable_path: str | None = None,
        args: list[str] = [],
    ):
        self.headless = headless
        self.executable_path = executable_path
        self.args = args
        self.playwright = None
        self.browser = None
        self._playwright_cm = None

    async def __aenter__(self):
        self._playwright_cm = async_playwright()
        self.playwright = await self._playwright_cm.__aenter__()
        launch_options = {
            "headless": self.headless,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                *self.args,
            ],
        }
        if self.executable_path:
            launch_options["executable_path"] = self.executable_path
        self.browser = await self.playwright.chromium.launch(**launch_options)
        self.context = await self.browser.new_context(**CONTEXT_OPTIONS)
        await stealth.apply_stealth_async(self.context)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self._playwright_cm:
            await self._playwright_cm.__aexit__(exc_type, exc_val, exc_tb)

    async def new_page(self):
        """Create a new page in the browser."""
        page = await self.context.new_page()
        return page
