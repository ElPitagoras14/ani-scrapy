from playwright.async_api import Page

preference_order_tabs = [
    "YourUpload",
    "SW",
]

allowed_popups = [
    "www.yourupload.com",
]


async def close_not_allowed_popups(page: Page):
    await page.wait_for_load_state("domcontentloaded")
    allowed = False
    for allowed_popup in allowed_popups:
        if allowed_popup in page.url:
            allowed = True
            break

    if not allowed:
        await page.close()


def get_order_idx(tabs: list[str]) -> list[int]:
    current_tabs = {tab: idx for idx, tab in enumerate(tabs)}

    order_idx = []
    for tab in preference_order_tabs:
        if tab in current_tabs:
            order_idx.append(current_tabs[tab])

    return order_idx
