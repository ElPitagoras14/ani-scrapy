from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError
from ani_scrapy.core.constants.animeflv import (
    SW_DOWNLOAD_URL,
)
from ani_scrapy.core.constants.general import (
    SW_TIMEOUT,
    YOURUPLOAD_TIMEOUT,
)


async def get_sw_file_link(page: Page, url: str):
    await page.goto(url)
    video_id = url.split("/")[-1]
    try_urls = [
        f"{SW_DOWNLOAD_URL}/{video_id}_h",
        f"{SW_DOWNLOAD_URL}/{video_id}_n",
        f"{SW_DOWNLOAD_URL}/{video_id}_l",
    ]

    for url in try_urls:
        retries = 3
        for _ in range(retries):
            try:
                await page.goto(url)

                download_button = await page.wait_for_selector(
                    "form#F1 button", timeout=3000
                )
                await download_button.click()

                try:
                    error_label = await page.wait_for_selector(
                        "div.text-danger.text-center.mb-5", timeout=SW_TIMEOUT
                    )
                    text_label = await error_label.inner_text()
                    if text_label.strip() == "Downloads disabled 620":
                        continue
                    else:
                        break
                except PlaywrightTimeoutError:
                    pass

                download_link = await page.wait_for_selector(
                    "div.text-center a.btn", timeout=SW_TIMEOUT
                )
                download_link = await download_link.get_attribute("href")

                return download_link
            except Exception:
                break
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
