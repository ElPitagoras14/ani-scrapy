from playwright.async_api import Page
from anime_scraper.tab_link import get_sw_link, get_yourupload_link
from anime_scraper.constants import (
    SW_TIMEOUT,
    YOURUPLOAD_TIMEOUT,
)


async def get_sw_link_wrapper(page: Page, search_page: Page):
    video_element = await page.wait_for_selector(
        "div#video_box", timeout=SW_TIMEOUT
    )
    iframe_element = await video_element.query_selector("iframe")
    iframe_src = await iframe_element.get_attribute("src")
    video_id = iframe_src.split("/")[-1].split("?")[0]

    return await get_sw_link(search_page, video_id)


async def get_yourupload_link_wrapper(page: Page, search_page: Page):
    video_element = await page.wait_for_selector(
        "div#video_box", timeout=YOURUPLOAD_TIMEOUT
    )
    iframe_element = await video_element.query_selector("iframe")
    iframe_src = await iframe_element.get_attribute("src")

    return await get_yourupload_link(search_page, iframe_src)
