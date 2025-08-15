from playwright.async_api import Page

preference_order_tabs = [
    "SW",
    "YourUpload",
]

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


def get_order_idx(tabs: list[str]) -> list[int]:
    current_tabs = {tab: idx for idx, tab in enumerate(tabs)}

    order_idx = []
    for tab in preference_order_tabs:
        if tab in current_tabs:
            order_idx.append(current_tabs[tab])

    return order_idx
