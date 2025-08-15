from playwright.async_api import Page
from anime_scraper.scrapers.animeflv.constants import (
    SW_DOWNLOAD_URL,
)
from anime_scraper.constants import (
    YOURUPLOAD_DOWNLOAD_URL,
    YOURUPLOAD_TIMEOUT,
    SW_TIMEOUT,
)


async def get_sw_link(page: Page):
    video_element = await page.wait_for_selector(
        "div#video_box", timeout=SW_TIMEOUT
    )
    iframe_element = await video_element.query_selector("iframe")
    iframe_src = await iframe_element.get_attribute("src")
    video_id = iframe_src.split("/")[-1].split("?")[0]
    return f"{SW_DOWNLOAD_URL}/{video_id}"


async def get_yourupload_link(page: Page):
    video_element = await page.wait_for_selector(
        "div#video_box", timeout=YOURUPLOAD_TIMEOUT
    )
    iframe_element = await video_element.query_selector("iframe")
    iframe_src = await iframe_element.get_attribute("src")
    video_id = iframe_src.split("/")[-1].split("?")[0]
    return f"{YOURUPLOAD_DOWNLOAD_URL}/{video_id}"
