# Ani Scrapy

[![PyPI Version](https://img.shields.io/pypi/v/ani-scrapy.svg)](https://pypi.org/project/ani-scrapy/)

[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## ⚠️ Disclaimer

> **Warning**: This library is intended for **educational and personal use only**. Please respect the terms of service of the websites being scraped and the applicable laws. The author is not responsible for any misuse.

**Ani-Scrapy** is a Python async-first library for scraping anime websites. It makes easy to switch between different platforms.

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

## 🐍 Requirements

- Python >= 3.10.14

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

- Python version and platform
- Playwright and Chromium available
- Brave browser (recommended for sites with ads)
- Network connectivity to supported sites (AnimeFLV, JKAnime, AnimeAV1)

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

Ani-Scrapy uses **Loguru** for all logging. By default, logging is **silent** (no output). To enable logging, use the `enable_logging()` function.

### Enable Logging

```python
from ani_scrapy import AnimeFLVScraper, enable_logging

enable_logging(level="DEBUG")  # Enable with DEBUG level to stdout

async with AnimeFLVScraper() as scraper:
    await scraper.log("naruto")
```

### Custom Configuration

You can customize the log output:

```python
from ani_scrapy import enable_logging

# Log to file
enable_logging(level="INFO", sink="ani_scrapy.log")

# Log to stdout with custom level
enable_logging(level="DEBUG", sink=None)  # None = stdout
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
- `AnimeAV1Scraper` - Scraper for AnimeAV1

### Method Status Comparison

| Method                      | AnimeFLV    | JKAnime         | AnimeAV1    |
| --------------------------- | ----------- | --------------- | ----------- |
| `search_anime`              | ✅ Estatico | ✅ Estatico     | ✅ Estatico |
| `get_anime_info`            | ✅ Estatico | ⚠️ Dinamico     | ✅ Estatico |
| `get_new_episodes`          | ✅ Estatico | ⚠️ Dinamico     | ✅ Estatico |
| `get_table_download_links`  | ✅ Estatico | ⚠️ Dinamico     | ✅ Estatico |
| `get_iframe_download_links` | ⚠️ Dinamico | ❌ No soportado | ✅ Estatico |
| `get_file_download_link`    | ⚠️ Dinamico | ⚠️ Dinamico     | ⚠️ Dinamico |

**Leyenda:**

- ✅ Estatico: Metodo funciona sin navegador (solo HTTP)
- ⚠️ Dinamico: Metodo requiere navegador (Playwright)
- ❌ No soportado: Metodo no disponible

### Performance Benchmark

Test conditions: Anime "Gachiakuta", Episode 22

| Provider | search_anime | get_anime_info | get_table_download_links | get_iframe_download_links |
| -------- | ------------ | -------------- | ------------------------ | ------------------------- |
| AnimeFLV | 642.36 ms    | 612.21 ms      | 447.42 ms                | ERROR                     |
| JKAnime  | 465.78 ms    | 28571.15 ms    | 1431.62 ms               | -                         |
| AnimeAV1 | 583.60 ms    | 319.22 ms      | 273.42 ms                | 275.51 ms                 |

\*JKAnime `get_iframe_download_links` returns empty result (not supported)

### Browser Classes:

- `AsyncBrowser` - Manual browser control for advanced use cases

## 🛠️ Advanced Usage

### Browser Usage Patterns

The library supports 3 ways to manage the browser for JavaScript-rendered content.

#### 1. Automatic (Default)

The browser is created automatically when needed and reused within the same context. Functions like `get_anime_info`, `get_table_download_links`, etc. will open the browser if not already open, or reuse it if another function already opened it within the same `async with` block:

```python
import asyncio
from ani_scrapy import JKAnimeScraper

async def main():
    async with JKAnimeScraper() as scraper:
        # get_anime_info opens the browser internally
        info = await scraper.get_anime_info("gachiakuta", include_episodes=True)
        # get_table_download_links reuses the same browser
        links = await scraper.get_table_download_links("gachiakuta", episode=1)
    # Browser automatically closed when exiting context

asyncio.run(main())
```

#### 2. Manual Start/Stop

Use this pattern when you need explicit control over the browser lifecycle without using `async with`, or for programmatic usage. All functions in the scraper will use the same manually opened browser:

```python
import asyncio
from ani_scrapy import JKAnimeScraper

async def scrape_anime(anime_id: str):
    scraper = JKAnimeScraper()

    await scraper.start_browser()  # Open browser explicitly

    # All functions use the same browser instance
    info = await scraper.get_anime_info(anime_id, include_episodes=True)
    links = await scraper.get_table_download_links(anime_id, episode=1)
    final_url = await scraper.get_file_download_link(links.download_links[0])

    await scraper.stop_browser()  # Close browser explicitly
    await scraper.aclose()         # Close scraper resources

asyncio.run(scrape_anime("gachiakuta"))
```

#### 3. External Browser Injection

Use an externally created `AsyncBrowser` instance. All scraper functions will use the injected browser:

```python
import asyncio
from ani_scrapy import AsyncBrowser, JKAnimeScraper

async def main():
    # Create browser with custom executable
    brave_path = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"

    async with AsyncBrowser(headless=True, executable_path=brave_path) as browser:
        # Inject external browser into scraper
        async with JKAnimeScraper(external_browser=browser) as scraper:
            # All functions use the injected browser
            info = await scraper.get_anime_info("gachiakuta")
            print(f"Title: {info.title}")
        # Browser stays open - controlled externally

asyncio.run(main())
```

### When to Use Each Pattern

| Pattern          | Use Case                                                    |
| ---------------- | ----------------------------------------------------------- |
| **1. Automatic** | Most cases - simple and automatic                           |
| **2. Manual**    | Programmatic use without `async with`, fine-grained control |
| **3. External**  | Share browser across scrapers, custom browser config        |

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

## 📄 License

MIT © 2025 El Pitágoras
