from playwright.async_api import Page


allowed_popups = [
    "www.yourupload.com",
]


async def close_not_allowed_popups(page: Page):
    try:
        await page.wait_for_load_state("domcontentloaded")
        allowed = False
        for allowed_popup in allowed_popups:
            if allowed_popup in page.url:
                allowed = True
                break

        if not allowed:
            await page.close()
    except Exception:
        try:
            await page.close()
        except Exception:
            pass
