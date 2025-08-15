from playwright.async_api import async_playwright
from playwright_stealth import Stealth


stealth = Stealth()


class BrowserManager:
    """
    A class for managing a browser instance.

    Attributes
    ----------
    headless : bool, optional
        Whether to run the browser in headless mode. Defaults to True.
    args : list[str], optional
        Additional arguments to pass to the browser. Defaults to an empty list.
    """

    def __init__(
        self,
        headless: bool = True,
        args: list[str] = [],
    ):
        self.headless = headless
        self.args = args
        self.playwright = None
        self.browser = None

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        final_args = [
            "--disable-blink-features=AutomationControlled",
            *self.args,
        ]
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless, args=final_args, slow_mo=500
        )
        self.context = await self.browser.new_context(
            ignore_https_errors=True,
            color_scheme="dark",
            locale="es-EC",
            no_viewport=True,
            timezone_id="America/Guayaquil",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit"
            + "/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 "
            + "Edg/139.0.0.0",
            viewport={"width": 1080, "height": 720},
        )
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
