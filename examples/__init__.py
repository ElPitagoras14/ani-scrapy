"""Examples package for ani-scrapy library.

This package contains executable examples demonstrating various use cases
of the ani-scrapy library for scraping anime websites.

Usage:
    python examples/01_basic_search.py
    python examples/02_anime_info.py
    ...

All examples use AnimeFLV and JKAnime scrapers with proper logging
and task tracking configuration.
"""

from ani_scrapy import AnimeFLVScraper, JKAnimeScraper, AsyncBrowser
from ani_scrapy.core.base import generate_task_id

__all__ = [
    "AnimeFLVScraper",
    "JKAnimeScraper",
    "AsyncBrowser",
    "generate_task_id",
]
