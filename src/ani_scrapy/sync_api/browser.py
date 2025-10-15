from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

from ani_scrapy.core.constants.general import CONTEXT_OPTIONS

stealth = Stealth()


class SyncBrowser:
    """
    A class for managing a synchronous browser instance.

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
    ) -> None:
        self.headless = headless
        self.executable_path = executable_path
        self.args = args
        self.playwright = None
        self.browser = None

    def __enter__(self):
        self.playwright = sync_playwright().start()
        launch_options = {
            "headless": self.headless,
            "args": [
                "--disable-blink-features=AutomationControlled",
                *self.args,
            ],
            "slow_mo": 500,
        }
        if self.executable_path:
            launch_options["executable_path"] = self.executable_path
        self.browser = self.playwright.chromium.launch(
            **launch_options,
        )
        self.context = self.browser.new_context(
            **CONTEXT_OPTIONS,
        )
        stealth.apply_stealth_sync(self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.context.close()
        self.browser.close()
        self.playwright.stop()

    def new_page(self):
        """
        Create a new page in the browser.

        Returns
        -------
        Page
            The new page.
        """
        page = self.context.new_page()
        return page
