from playwright.sync_api import Page

allowed_popups = [
    "www.yourupload.com",
]


def close_not_allowed_popups(page: Page):
    try:
        page.wait_for_load_state("domcontentloaded")
        allowed = False
        for allowed_popup in allowed_popups:
            if allowed_popup in page.url:
                allowed = True
                break

        if not allowed:
            page.close()
    except Exception:
        try:
            page.close()
        except Exception:
            pass
