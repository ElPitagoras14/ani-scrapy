# ani-scrapy Examples

This directory contains executable examples demonstrating various use cases of the ani-scrapy library.

## Examples Index

| #   | File                        | Description                                      |
| --- | --------------------------- | ------------------------------------------------ |
| 01  | `01_basic_search.py`        | Basic anime search using AnimeFLV and JKAnime    |
| 02  | `02_anime_info.py`          | Get detailed anime information including episodes |
| 03  | `03_download_links.py`      | Retrieve download links from multiple servers    |
| 04  | `04_concurrent_scraping.py` | Concurrent scraping of multiple anime            |
| 05  | `05_logging_configuration.py` | Using Loguru for logging (user-configured)      |
| 06  | `06_shared_browser.py`      | Share browser across multiple scrapers           |
| 07  | `07_benchmark.py`           | Performance benchmark across all providers       |

## Quick Start

Install with uv and run an example:

```bash
cd ani-scrapy
uv sync
uv run python examples/01_basic_search.py
```

## Requirements

- Python >= 3.10
- Playwright browser (`playwright install chromium`)
