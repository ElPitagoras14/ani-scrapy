from playwright.async_api import async_playwright
from playwright_stealth import Stealth


from ani_scrapy.core.constants.general import CONTEXT_OPTIONS

stealth = Stealth()


class AsyncBrowser:
    """
    A class for managing an asynchronous browser instance.

    Attributes
    ----------
    headless : bool, optional
        Whether to run the browser in headless mode. Defaults to True.
    executable_path : str, optional
        The path to the browser executable. If not provided, the default
        browser will be chromium.
    args : list[str], optional
        Additional arguments to pass to the browser. Defaults to an empty list.
    """

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

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
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
        await self.context.close()
        await self.browser.close()
        await self.playwright.stop()

    async def new_page(self):
        """
        Create a new page in the browser.

        Returns
        -------
        Page
            The new page.
        """
        page = await self.context.new_page()
        return page
