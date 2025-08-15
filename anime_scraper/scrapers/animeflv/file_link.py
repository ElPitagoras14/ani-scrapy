from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError
from anime_scraper.scrapers.animeflv.constants import (
    SW_DOWNLOAD_URL,
)
from anime_scraper.constants import (
    SW_TIMEOUT,
    YOURUPLOAD_TIMEOUT,
)


async def get_sw_file_link(page: Page, url: str):
    await page.goto(url)
    video_id = url.split("/")[-1]
    try_urls = [
        f"{SW_DOWNLOAD_URL}/{video_id}_n",
        f"{SW_DOWNLOAD_URL}/{video_id}_l",
    ]

    for url in try_urls:
        try:
            await page.goto(url)
            download_button = await page.wait_for_selector(
                "form#F1 button", timeout=SW_TIMEOUT
            )
            await download_button.click()

            download_link = await page.wait_for_selector(
                "div.text-center a.btn", timeout=SW_TIMEOUT
            )
            download_link = await download_link.get_attribute("href")

            return download_link
        except Exception:
            continue

    return None


async def get_yourupload_file_link(page: Page, url: str):
    await page.goto(url)

    try:
        video_element = await page.wait_for_selector(
            "div.jw-media video.jw-video", timeout=YOURUPLOAD_TIMEOUT
        )
    except PlaywrightTimeoutError:
        return None
    video_src = await video_element.get_attribute("src")

    return video_src


async def get_stape_file_link(page: Page, url: str):
    await page.goto(url)

    video_element = await page.wait_for_selector(
        "div.plyr__video-wrapper video", timeout=YOURUPLOAD_TIMEOUT
    )
    video_src = await video_element.get_attribute("src")

    return f"https:{video_src}"
