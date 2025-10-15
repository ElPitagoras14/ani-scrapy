preference_order_tabs = [
    "SW",
    "YourUpload",
]


def get_order_idx(tabs: list[str]) -> list[int]:
    current_tabs = {tab: idx for idx, tab in enumerate(tabs)}

    order_idx = []
    for tab in preference_order_tabs:
        if tab in current_tabs:
            order_idx.append(current_tabs[tab])

    return order_idx
