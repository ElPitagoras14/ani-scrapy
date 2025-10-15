from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from ani_scrapy.core.constants.general import SW_TIMEOUT, MEDIAFIRE_TIMEOUT
from ani_scrapy.core.constants.jkanime import SW_DOWNLOAD_URL


def get_streamwish_file_link(page: Page, url: str):
    page.goto(url)
    current_url = page.url
    video_id = current_url.split("/")[-1]

    try_urls = [
        f"{SW_DOWNLOAD_URL}/{video_id}_h",
        f"{SW_DOWNLOAD_URL}/{video_id}_n",
        f"{SW_DOWNLOAD_URL}/{video_id}_l",
    ]

    for url in try_urls:
        retries = 3
        for _ in range(retries):
            try:
                page.goto(url)
                download_button = page.wait_for_selector(
                    "form#F1 button", timeout=3000
                )
                download_button.click(delay=1000)

                try:
                    error_label = page.wait_for_selector(
                        "div.text-danger.text-center.mb-5", timeout=SW_TIMEOUT
                    )
                    text_label = error_label.inner_text()
                    print(text_label)
                    if text_label.strip() == "Downloads disabled 620":
                        continue
                    else:
                        break
                except PlaywrightTimeoutError:
                    pass

                download_link_el = page.wait_for_selector(
                    "div.text-center a.btn", timeout=SW_TIMEOUT
                )
                download_link = download_link_el.get_attribute("href")

                return download_link
            except Exception:
                continue

    return None


def get_mediafire_file_link(page: Page, url: str):
    page.goto(url)

    try:
        download_button = page.wait_for_selector(
            "a#downloadButton", timeout=MEDIAFIRE_TIMEOUT
        )
    except PlaywrightTimeoutError:
        return None

    with page.expect_download() as download_info:
        download_button.click()

    download = download_info.value
    real_url = download.url
    download.cancel()
    return real_url
