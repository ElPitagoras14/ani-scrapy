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

## Reusing Browser for Multiple Operations

By default, the browser is created automatically when needed and closed after each operation. For better performance when performing multiple browser-based operations, you can manually control the browser lifecycle.

### Manual Start/Stop

```python
import asyncio

from ani_scrapy import JKAnimeScraper


async def main() -> None:
    async with JKAnimeScraper(headless=True) as scraper:
        # Start browser manually
        await scraper.start_browser()

        # Multiple operations use the same browser
        info = await scraper.get_anime_info("anime-id", include_episodes=True)
        links = await scraper.get_table_download_links("anime-id", episode=1)
        final_url = await scraper.get_file_download_link(links.download_links[0])

        # Stop when done (optional - also called automatically on scraper close)
        await scraper.stop_browser()


if __name__ == "__main__":
    asyncio.run(main())
```

### Benefits

- **Performance**: Reuses a single browser instance instead of creating new ones
- **Resource efficient**: Lower memory and CPU usage
- **Faster**: Avoids browser startup overhead for each operation

### Injecting External Browser

You can also inject an external `AsyncBrowser` instance:

```python
import asyncio

from ani_scrapy import AsyncBrowser, JKAnimeScraper


async def main() -> None:
    async with AsyncBrowser(headless=True) as browser:
        # Inject external browser into scraper
        async with JKAnimeScraper(external_browser=browser) as scraper:
            # All browser operations use the injected browser
            info = await scraper.get_anime_info("anime-id")


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
