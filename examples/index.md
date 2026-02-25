# ani-scrapy Examples

This directory contains executable examples demonstrating various use cases of the ani-scrapy library.

## Examples Index

| #   | File                          | Description                                        |
| --- | ----------------------------- | -------------------------------------------------- |
| 01  | `01_basic_search.py`          | Basic anime search using AnimeFLV and JKAnime      |
| 02  | `02_anime_info.py`            | Get detailed anime information including episodes  |
| 03  | `03_download_links.py`        | Retrieve download links from multiple servers      |
| 04  | `04_browser_usage.py`         | Use browser for dynamic JavaScript content         |
| 05  | `05_concurrent_scraping.py`   | Concurrent scraping of multiple anime              |
| 06  | `06_error_handling.py`        | Handle exceptions (blocked, timeout, parse errors) |
| 07  | `07_logging_configuration.py` | Using Loguru for logging (user-configured)         |
| 08  | `08_file_download_links.py`   | Get final download URLs from download link info    |

## Quick Start

Install with examples dependencies:

```bash
pip install ani-scrapy[examples]
```

Run an example:

```bash
python examples/01_basic_search.py
```

## Requirements

- Python >= 3.10
- ani-scrapy library installed
- Optional: Playwright browser (`playwright install chromium`)
