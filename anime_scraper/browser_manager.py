from playwright.async_api import async_playwright


class BrowserManager:
    def __init__(self, headless=True, args=None):
        self.headless = headless
        self.args = args
        self.playwright = None
        self.browser = None
        self.context = None

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=(self.args if self.args else []),
        )
        self.context = await self.browser.new_context(ignore_https_errors=True)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.context.close()
        await self.browser.close()
        await self.playwright.stop()

    async def new_page(self):
        page = await self.context.new_page()
        return page
