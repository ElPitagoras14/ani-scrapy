# Ani Scrapy

[![PyPI Version](https://img.shields.io/pypi/v/ani-scrapy.svg)](https://pypi.org/project/ani-scrapy/)

[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

<!-- [![Build Status](https://github.com/your_username/py-anime-scraper/actions/workflows/main.yml/badge.svg)](https://github.com/your_username/py-anime-scraper/actions) -->

**Ani-Scrapy** is a Python library for scraping anime websites, designed to provide both synchronous and asynchronous interfaces. It currently supports **AnimeFLV** and **JKAnime**, and makes it easy to switch between different platforms.

Ani-Scrapy helps developers automate anime downloads and build applications. It provides detailed anime and episode information, along with download links from multiple servers, supporting dynamic and static content across several sites.

## 🚀 Features

### Core Functionality

- **Dual Interface**: Synchronous and asynchronous APIs for flexible integration.
- **Multi-Platform Support**: Unified interface for different platforms.
- **Comprehensive Data**: Detailed anime metadata, episode information, and download links.

### Content Handling

- **Static Content Extraction**: Direct server links using `request + cloudscraper + curl_cffi + aiohttp + bs4`
- **Dynamic Content Processing**: JavaScript-rendered links using `Playwright`
- **Mixed Approach**: Smart fallback between static and dynamic methods

### Technical Capabilities

- **Concurrent Scraping**: Built-in support for asynchronous batch processing
- **Automatic Resource Management**: Browser instances handled automatically when not provided
- **Custom Browser Support**: Configurable browser paths and headless/headed modes via `executable_path` and `headless` options

### Development Experience

- **Modular Design**: Easy to extend with new scrapers and platforms
- **Configurable Logging**: Verbose mode and multiple log levels (`DEBUG`, `INFO`, `SUCCESS`, `WARNING`, `ERROR`)
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
pip install -e .
playwright install chromium
```

## 🐍 Requirements

- Python >= 3.9 (tested with 3.12)

Install Chromium (only once):

```bash
playwright install chromium
```

## 📊 Supported Websites

### Currently Supported

- **AnimeFLV**: Full support
- **JKAnime**: Supports search, info, table downloads, file downloads | ~~iframe downloads~~

## 🚀 Basic Usage

### Asynchronous API Example

```python
from ani_scrapy.async_api import AnimeFLVScraper, JKAnimeScraper, AsyncBrowser
import asyncio


async def main():
    # Initialize scrapers
    animeflv_scraper = AnimeFLVScraper(verbose=True)
    jkanime_scraper = JKAnimeScraper(verbose=True)

    # Search anime
    an_results = await animeflv_scraper.search_anime(query="naruto", page=1)
    jk_results = await jkanime_scraper.search_anime(query="naruto")
    print(f"AnimeFLV results: {len(an_results.animes)} animes found")
    print(f"JKAnime results: {len(jk_results.animes)} animes found")


    # Get dynamic content
    async with AsyncBrowser(headless=False) as browser:
        # Get anime info
        an_info = await animeflv_scraper.get_anime_info(
            anime_id=an_results.animes[0].id, include_episodes=True
        )
        jk_info = await jkanime_scraper.get_anime_info(
            anime_id=jk_results.animes[0].id, include_episodes=True, browser=browser
        )
        print(f"AnimeFLV info: {an_info.title}")
        print(f"JKAnime info: {jk_info.title}")

        # Get new episodes
        an_new_episodes = await animeflv_scraper.get_new_episodes(
            anime_id=an_info.id, last_episode_number=an_info.episodes[-1].number
        )
        jk_new_episodes = await jkanime_scraper.get_new_episodes(
            anime_id=jk_info.id, last_episode_number=jk_info.episodes[-1].number, browser=browser
        )
        print(f"AnimeFLV new episodes: {len(an_new_episodes)} episodes found")
        print(f"JKAnime new episodes: {len(jk_new_episodes)} episodes found")

        # Table download links
        an_table_links = await animeflv_scraper.get_table_download_links(
            anime_id=an_info.id, episode_number=1
        )
        jk_table_links = await jkanime_scraper.get_table_download_links(
            anime_id=jk_info.id, episode_number=1, browser=browser
        )

        # Iframe download links (requires browser for JS content)
        an_iframe_links = await animeflv_scraper.get_iframe_download_links(
            anime_id=an_info.id, episode_number=1, browser=browser
        )

        # Get final file download links
        if an_iframe_links.download_links:
            file_link = await animeflv_scraper.get_file_download_link(
                download_info=an_iframe_links.download_links[0],
                browser=browser,
            )
            print(f"Download URL: {file_link}")


if __name__ == "__main__":
    asyncio.run(main())

```

### Synchronous API Example

```python
from ani_scrapy.sync_api import AnimeFLVScraper, JKAnimeScraper, SyncBrowser

# Initialize scrapers

animeflv_scraper = AnimeFLVScraper(verbose=True)
jkanime_scraper = JKAnimeScraper(verbose=True)

# Search anime

an_results = animeflv_scraper.search_anime(query="naruto", page=1)
jk_results = jkanime_scraper.search_anime(query="naruto")
print(f"AnimeFLV results: {len(an_results.animes)} animes found")
print(f"JKAnime results: {len(jk_results.animes)} animes found")


# Get dynamic content
with SyncBrowser(headless=False) as browser:
    # Get anime info
    an_info = animeflv_scraper.get_anime_info(anime_id=an_results.animes[0].id)
    jk_info = jkanime_scraper.get_anime_info(
        anime_id=jk_results.animes[0].id, browser=browser
    )
    print(f"AnimeFLV info: {an_info.title}")
    print(f"JKAnime info: {jk_info.title}")

    # Get new episodes
    an_new_episodes = animeflv_scraper.get_new_episodes(
        anime_id=an_info.id, last_episode_number=1
    )
    jk_new_episodes = jkanime_scraper.get_new_episodes(
        anime_id=jk_info.id, last_episode_number=1, browser=browser
    )
    print(f"AnimeFLV new episodes: {len(an_new_episodes)} episodes found")
    print(f"JKAnime new episodes: {len(jk_new_episodes)} episodes found")

    # Table download links
    an_table_links = animeflv_scraper.get_table_download_links(
    anime_id=an_info.id, episode_number=1
    )
    jk_table_links = jkanime_scraper.get_table_download_links(
    anime_id=jk_info.id, episode_number=1, browser=browser
    )

    # Iframe download links (requires browser for JS content)
    an_iframe_links = animeflv_scraper.get_iframe_download_links(
        anime_id=an_info.id, episode_number=1, browser=browser
    )

    # Get final file download links
    if an_iframe_links.download_links:
        file_link = animeflv_scraper.get_file_download_link(
            download_info=an_iframe_links.download_links[0], browser=browser
        )
        print(f"Download URL: {file_link}")

```

## 📖 API Reference

For complete documentation: [API Reference](https://github.com/ElPitagoras14/ani-scrapy/blob/main/docs/API_REFERENCE.md)

### Methods Overview:

- `search_anime` - Search for anime
- `get_anime_info` - Get detailed anime information
- `get_table_download_links` - Get direct server links
- `get_iframe_download_links` - Get iframe links
- `get_file_download_link` - Get final download URL

### Browser Classes:

- `AsyncBrowser` - Automatic resource management for async operations
- `SyncBrowser` - Context manager for synchronous scraping

## 🛠️ Advanced Usage

### Custom Browser Configuration

```python
from ani_scrapy import AsyncBrowser, SyncBrowser

# Custom Brave browser path
brave_path = ""

async with AsyncBrowser(
    headless=False,
    executable_path=brave_path,
) as browser:
    # Your scraping code here
    pass
```

### Error Handling Example

```python
try:
    results = await scraper.search_anime("naruto")
    if results.animes:
        anime_info = await scraper.get_anime_info(results.animes[0].id)
        print(f"Success: {anime_info.title}")
except Exception as e:
    print(f"Error occurred: {e}")
    # Implement retry logic or fallback here
```

### Concurrent Scraping

```python
import asyncio

async def scrape_multiple_animes(anime_ids):
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
- Writing tests to ensure code quality.

### How to contribute

1. Fork the repository.
2. Create a new branch for your feature or fix:

```bash
git checkout -b my-feature
```

3. Make your changes and commit with clear messages.
4. Push your branch to your fork.
5. Open a Pull Request against the `main` branch of the original repository.

Please ensure that all tests pass before submitting a PR. Contributions are expected to respect the license and coding style.

## 🧪 Development and Testing

Install development dependencies:

```bash
pip install -r requirements.txt
```

## 🚧 Coming Soon

Support for more anime websites and further unification of scraper methods is planned.

If you want to contribute by adding new scrapers for other sites, contributions are welcome!

## ⚠️ Disclaimer

This library is intended for **educational and personal use only**. Please respect the terms of service of the websites being scraped and the applicable laws. The author is not responsible for any misuse.

## 📄 License

MIT © 2025 El Pitágoras
