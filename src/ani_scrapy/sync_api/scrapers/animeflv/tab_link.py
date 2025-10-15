from playwright.sync_api import Page
from ani_scrapy.core.constants.animeflv import (
    SW_DOWNLOAD_URL,
)
from ani_scrapy.core.constants.general import (
    YOURUPLOAD_DOWNLOAD_URL,
    YOURUPLOAD_TIMEOUT,
    SW_TIMEOUT,
)


def get_sw_link(page: Page) -> str:
    video_element = page.wait_for_selector("div#video_box", timeout=SW_TIMEOUT)
    iframe_element = video_element.query_selector("iframe")
    iframe_src = iframe_element.get_attribute("src")
    video_id = iframe_src.split("/")[-1].split("?")[0]
    return f"{SW_DOWNLOAD_URL}/{video_id}"


def get_yourupload_link(page: Page) -> str:
    video_element = page.wait_for_selector(
        "div#video_box", timeout=YOURUPLOAD_TIMEOUT
    )
    iframe_element = video_element.query_selector("iframe")
    iframe_src = iframe_element.get_attribute("src")
    video_id = iframe_src.split("/")[-1].split("?")[0]
    return f"{YOURUPLOAD_DOWNLOAD_URL}/{video_id}"
