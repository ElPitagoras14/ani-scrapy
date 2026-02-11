# Browser Usage

Some operations require a browser (Playwright) to resolve iframe or final file links. The browser is managed automatically by the scraper.

## Basic Usage

```python
import asyncio

from ani_scrapy import AnimeFLVScraper


async def main() -> None:
    async with AnimeFLVScraper() as scraper:
        links = await scraper.get_iframe_download_links(
            anime_id="one-punch-man-3",
            episode_number=1,
        )
        print(links)


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Manual Browser Usage (Advanced)

For advanced use cases where you need direct control over the browser page:

```python
import asyncio

from ani_scrapy import AsyncBrowser


async def main() -> None:
    async with AsyncBrowser(headless=True) as browser:
        page = await browser.new_page()
        await page.goto("https://example.com")
        # Your custom browser automation here


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Custom Browser (Brave Recommended)

You can configure a custom browser executable path. Brave is recommended because its native ad-blocker reduces blocking on sites with excessive advertisements, but any Chromium-based browser (Chrome, Chromium, Edge) will work.

### Benefits of Brave

- **Native Ad-Block**: Built-in protection reduces detection probability
- **Avoids Captchas**: Sites with aggressive ads may fail with Chromium's default configuration
- **Better Success Rate**: Sites with excessive advertising can fail or timeout with the default browser

### Configuration

```python
from ani_scrapy import AnimeFLVScraper

brave_path = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"

async with AnimeFLVScraper(executable_path=brave_path) as scraper:
    info = await scraper.get_anime_info(anime_id="anime-id")
```

### Path Examples

```python
# Brave (Recommended)
brave_path = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"

# Chrome
chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"

# Chromium
chromium_path = "C:/Program Files/Chromium/Application/chrome.exe"

# Linux
brave_path = "/usr/bin/brave"

# macOS
brave_path = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
```
