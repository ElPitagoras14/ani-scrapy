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
from anime_scraper.scrapers.jkanime.scraper import JKAnimeScraper
import asyncio


async def main():
    animeflv_scraper = AnimeFLVScraper(verbose=False)
    jkanime_scraper = JKAnimeScraper(verbose=False)

    # Search anime
    an_results = await animeflv_scraper.search_anime_async(query="naruto", page=1)
    print(an_results)
    jk_results = await jkanime_scraper.search_anime_async(query="naruto")
    print(jk_results)

    # Get anime info
    an_info = await animeflv_scraper.get_anime_info_async(anime_id=an_results.animes[0].id)
    print(an_info)
    jk_info = await jkanime_scraper.get_anime_info_async(anime_id=jk_results.animes[0].id)
    print(jk_info)

    # Get table download links
    an_table_links = await animeflv_scraper.get_table_download_links_async(
        anime_id=an_info.id, episode_id=1
    )
    print(an_table_links)
    jk_table_links = await jkanime_scraper.get_table_download_links_async(
        anime_id=jk_info.id, episode_id=1
    )
    print(jk_table_links)

    # Get iframe download links
    an_iframe_links = await animeflv_scraper.get_iframe_download_links_async(
        anime_id=an_info.id, episode_id=1
    )
    print(an_iframe_links)

    # Note: Not supported yet
    # jk_iframe_links = await jkanime_scraper.get_iframe_download_links_async(
    #     anime_id=jk_info.id, episode_id=1
    # )
    # print(jk_iframe_links)

    # Get file download links
    an_file_links = await animeflv_scraper.get_file_download_links_async(
        download_info=an_iframe_links.download_links[0]
    )
    print(an_file_links)
    jk_file_links = await jkanime_scraper.get_file_download_links_async(
        download_info=jk_table_links.download_links[0]
    )
    print(jk_file_links)


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
