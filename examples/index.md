# ani-scrapy Examples

This directory contains executable examples demonstrating various use cases of the ani-scrapy library.

## Examples Index

| # | File | Description |
|---|------|-------------|
| 01 | `01_basic_search.py` | Basic anime search with task tracking |
| 02 | `02_anime_info.py` | Get detailed anime information |
| 03 | `03_download_links.py` | Retrieve download links from multiple servers |
| 04 | `04_browser_usage.py` | Use browser for dynamic JavaScript content |
| 05 | `05_task_tracking.py` | Complete demo of task_id tracking across operations |
| 06 | `06_concurrent_scraping.py` | Concurrent scraping of multiple anime |
| 07 | `07_error_handling.py` | Handle exceptions (blocked, timeout, parse errors) |
| 08 | `08_logging_configuration.py` | Configure logging levels and output formats |
| 09 | `09_file_download_links.py` | Get final download URLs from download link info |

## Quick Start

Install with examples dependencies:

```bash
pip install ani-scrapy[examples]
```

Run an example:

```bash
python examples/01_basic_search.py
```

## Features Demonstrated

- **Async API**: Asynchronous interface for concurrent operations
- **Task Tracking**: Use `task_id` to correlate logs across operations
- **Logging Configuration**: Custom log levels and file output
- **Browser Integration**: Handle JavaScript-rendered content with Playwright
- **Error Handling**: Robust exception handling for production use
- **Concurrent Operations**: Efficient batch processing with asyncio

## Requirements

- Python >= 3.10
- ani-scrapy library installed
- Optional: Playwright browser (`playwright install chromium`)
