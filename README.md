# Py Anime Scraper

[![PyPI Version](https://img.shields.io/pypi/v/py-anime-scraper.svg)](https://pypi.org/project/py-anime-scraper/)

[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

<!-- [![Build Status](https://github.com/your_username/py-anime-scraper/actions/workflows/main.yml/badge.svg)](https://github.com/your_username/py-anime-scraper/actions) -->

Python library for scraping anime websites, designed to be async-first with sync support. Currently supports only **AnimeFLV**.

---

## 🚀 Features

- Asynchronous and synchronous anime search
- Retrieve detailed anime and episode information
- Download static links (aiohttp + bs4) and dynamic links (playwright for JS)
- Support for concurrent and controlled scraping
- Easily extendable to add more scrapers

---

## 📦 Installation

From PyPI:

```bash
pip install py-anime-scraper
```

From GitHub:

```bash
pip install git+https://github.com/ElPitagoras14/py-anime-scraper.git
```

---

## 🐍 Requirements

- Python >= 3.9 (tested with 3.12)
- Main dependencies: `aiohttp`, `beautifulsoup4`, `playwright`, `lxml`, `loguru`

Optional manual install:

```bash
pip install aiohttp beautifulsoup4 playwright lxml loguru
```

Then, install Chromium (only once):

```bash
playwright install chromium
```

---

## ⚙️ Basic Usage

```python
from anime_scraper.scrapers.animeflv import AnimeFLVScraper
import asyncio


async def main():
    scraper = AnimeFLVScraper()

    # Search anime
    results = await scraper.search_anime_async("naruto")
    print(results)

    # Get anime info
    info = await scraper.get_anime_info_async(results.animes[0].id)
    print(info)

    # Get static download links
    links_static = await scraper.get_static_download_links_async(
        info.id, episode_id=1
    )
    print(links_static)

    # Get dynamic download links (requires Chromium installed)
    links_dynamic = await scraper.get_dynamic_download_links_async(
        info.id, episode_id=1
    )
    print(links_dynamic)


if __name__ == "__main__":
    asyncio.run(main())
```

For synchronous use, you can do:

```python
scraper = AnimeFLVScraper()
results = scraper.search_anime("naruto")
```

---

## ⚠️ Disclaimer

This library is **for educational and personal use only**. Scraping should be done respecting the websites' terms of service and applicable laws. The author is not responsible for any misuse.

---

## 🛠️ How to add a new scraper

1. Create a class inheriting from `BaseAnimeScraper`.
2. Implement the required async methods (`search_anime_async`, `get_anime_info_async`, etc.).
3. Use `aiohttp` and `bs4` for static scraping and `playwright` for dynamic scraping when JS execution is needed.
4. Register your scraper in the package for easy use.

---

## 🧪 Development and Testing

Install development dependencies:

```bash
pip install -r requirements.txt
```

---

## 🚧 Coming Soon

Currently, **py-anime-scraper** only supports **AnimeFLV**, but support for more anime websites is in progress and will be added soon.

If you want to contribute by adding new scrapers for other sites, contributions are welcome!

---

## 📄 License

MIT © 2025 El Pitágoras
