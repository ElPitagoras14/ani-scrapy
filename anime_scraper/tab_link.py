from playwright.async_api import Page
from anime_scraper.constants import (
    SW_TIMEOUT,
    SW_DOWNLOAD_URL,
    YOURUPLOAD_TIMEOUT,
)


async def get_sw_link(search_page: Page, video_id: str):
    try_links = [
        f"{SW_DOWNLOAD_URL}/{video_id}_n",
        f"{SW_DOWNLOAD_URL}/{video_id}_l",
    ]

    for link in try_links:
        try:
            await search_page.goto(link)
            download_button = await search_page.wait_for_selector(
                "form#F1 button", timeout=SW_TIMEOUT
            )
            await download_button.click()

            download_link = await search_page.wait_for_selector(
                "div.text-center a.btn", timeout=SW_TIMEOUT
            )
            download_link = await download_link.get_attribute("href")

            return download_link
        except Exception:
            continue

    return None


async def get_yourupload_link(search_page: Page, link: str):
    await search_page.goto(link)

    video_element = await search_page.wait_for_selector(
        "div.jw-media video.jw-video", timeout=YOURUPLOAD_TIMEOUT
    )
    video_src = await video_element.get_attribute("src")

    return video_src


async def get_stape_link(search_page: Page, link: str):
    await search_page.goto(link)

    video_element = await search_page.wait_for_selector(
        "div.plyr__video-wrapper video", timeout=YOURUPLOAD_TIMEOUT
    )
    video_src = await video_element.get_attribute("src")

    return f"https:{video_src}"
