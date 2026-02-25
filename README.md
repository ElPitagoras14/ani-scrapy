# Ani Scrapy

[![PyPI Version](https://img.shields.io/pypi/v/ani-scrapy.svg)](https://pypi.org/project/ani-scrapy/)

[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

<!-- [![Build Status](https://github.com/your_username/py-anime-scraper/actions/workflows/main.yml/badge.svg)](https://github.com/your_username/py-anime-scraper/actions) -->

**Ani-Scrapy** is a Python async-first library for scraping anime websites. It currently supports **AnimeFLV** and **JKAnime**, and makes it easy to switch between different platforms.

> **Note**: The synchronous API was removed due to maintainability complexity. Keeping two native implementations duplicated code without sufficient benefits.

Ani-Scrapy helps developers automate anime downloads and build applications. It provides detailed anime and episode information, along with download links from multiple servers, supporting dynamic and static content across several sites.

## 🚀 Features

### Core Functionality

- **Async-First Design**: Built from the ground up for asynchronous Python
- **Multi-Platform Support**: Unified interface for different platforms
- **Comprehensive Data**: Detailed anime metadata, episode information, and download links

### Content Handling

- **Static Content Extraction**: Direct server links using `aiohttp` and `BeautifulSoup`
- **Dynamic Content Processing**: JavaScript-rendered links using `Playwright`
- **Mixed Approach**: Smart fallback between static and dynamic methods

### Technical Capabilities

- **Concurrent Scraping**: Built-in support for asynchronous batch processing
- **Automatic Resource Management**: Browser instances handled automatically
- **Custom Browser Support**: Configurable browser paths via `executable_path`

### Development Experience

- **Modular Design**: Easy to extend with new scrapers and platforms
- **Logging**: Uses Loguru; respects global configuration
- **Performance Optimization**: Connection reuse and caching capabilities

## 📦 Installation

### From PyPI:

```bash
pip install ani-scrapy
```

### From GitHub:

```bash
pip install git+https://github.com/ElPitagoras14/ani-scrapy.git
```

### Development Installation:

```bash
git clone https://github.com/ElPitagoras14/ani-scrapy.git
cd ani-scrapy
pip install -e ".[dev]"
playwright install chromium
```

## 🐍 Requirements

- Python >= 3.10.14 (tested with 3.12)

Install browser (only once):

```bash
playwright install chromium
```

> **Recommendation**: Use Brave browser for sites with excessive advertising. See [Custom Browser](#custom-browser-brave-recommended) below.

## 🔍 Diagnostics

Run the diagnostic tool to check your environment:

```bash
ani-scrapy doctor
```

This checks:

- Python version, platform, RAM
- Required dependencies installed
- Playwright and Chromium available
- Recommended browsers (Brave)
- Network connectivity to supported sites

### Options

```bash
ani-scrapy doctor --output json  # JSON output for CI/CD
ani-scrapy doctor --timeout 10   # Increase timeout for slow connections
```

### Exit Codes

| Code | Meaning           |
| ---- | ----------------- |
| 0    | All checks passed |
| 1    | Warnings found    |
| 2    | Errors found      |

## 📝 Logging

Ani-Scrapy uses **Loguru** for all logging. The library does **not** configure Loguru automatically - you must configure it in your application if you want custom logging.

### Basic Usage (No Configuration)

By default, all logs go to stderr using Loguru's default configuration:

```python
from ani_scrapy import AnimeFLVScraper

async with AnimeFLVScraper() as scraper:
    await scraper.search_anime("naruto")
# Logs appear on stderr automatically
```

### Configure Loguru in Your Application

For production applications, configure Loguru once at startup:

```python
from loguru import logger
import sys

# Configure globally
logger.configure(
    handlers=[
        {"sink": "app.log", "level": "DEBUG", "enqueue": True},
        {"sink": sys.stderr, "level": "INFO"},
    ]
)

# All scrapers will use this configuration
from ani_scrapy import AnimeFLVScraper
```

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

## 📖 API Reference

For complete documentation: [Docs index](https://github.com/ElPitagoras14/ani-scrapy/blob/main/docs/README.md)

### Methods Overview:

- `search_anime` - Search for anime
- `get_anime_info` - Get detailed anime information
- `get_table_download_links` - Get direct server links
- `get_iframe_download_links` - Get iframe links
- `get_file_download_link` - Get final download URL
- `get_new_episodes` - Get new episodes since last known

### Scraper Classes:

- `AnimeFLVScraper` - Scraper for AnimeFLV
- `JKAnimeScraper` - Scraper for JKAnime

### Browser Classes:

- `AsyncBrowser` - Manual browser control for advanced use cases

## 🛠️ Advanced Usage

### Manual Browser Usage

For advanced use cases where you need direct control over the browser:

```python
import asyncio

from ani_scrapy import AsyncBrowser


async def main():
    async with AsyncBrowser(headless=True) as browser:
        page = await browser.new_page()
        await page.goto("https://example.com")
        # Your custom browser automation here


if __name__ == "__main__":
    asyncio.run(main())
```

### Error Handling

```python
from ani_scrapy.core.exceptions import (
    ScraperBlockedError,
    ScraperTimeoutError,
    ScraperParseError,
    ScraperError
)

try:
    results = await scraper.search_anime("naruto")
    if results.animes:
        anime_info = await scraper.get_anime_info(results.animes[0].id)
        print(f"Success: {anime_info.title}")
except ScraperBlockedError:
    print("Access blocked - try again later or use a different IP")
except ScraperTimeoutError:
    print("Request timed out - check your connection")
except ScraperParseError:
    print("Failed to parse response - website structure may have changed")
except ScraperError as e:
    print(f"Scraping error occurred: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Concurrent Scraping

```python
import asyncio

async def scrape_multiple_animes(anime_ids, scraper):
    tasks = []
    for anime_id in anime_ids:
        task = scraper.get_anime_info(anime_id)
        tasks.append(task)

    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

## 🤝 Contributing

Contributions to Ani-Scrapy are welcome! You can help by:

- Reporting bugs or suggesting new features via GitHub Issues.
- Improving documentation.
- Adding new scrapers or enhancing existing ones.
- Ensuring code quality and following coding standards.

### How to contribute

1. Fork the repository.
2. Create a new branch for your feature or fix:

```bash
git checkout -b my-feature
```

3. Make your changes and commit with clear messages.
4. Push your branch to your fork.
5. Open a Pull Request against the `main` branch of the original repository.

Contributions are expected to respect the license and coding style.

## 🧪 Development

Install development dependencies:

```bash
pip install -e ".[dev]"
```

## 🚧 Coming Soon

Support for more anime websites and further unification of scraper methods is planned.

If you want to contribute by adding new scrapers for other sites, contributions are welcome!

## ⚠️ Disclaimer

This library is intended for **educational and personal use only**. Please respect the terms of service of the websites being scraped and the applicable laws. The author is not responsible for any misuse.

## 📄 License

MIT © 2025 El Pitágoras
