#!/usr/bin/env python3
"""
Example 07: Logging with Loguru

This example shows how to use Loguru for logging when using ani-scrapy.
The library does NOT configure logging automatically - you must configure
Loguru in your application if you want logs.

Options:
1. Configure Loguru globally (recommended for applications)
2. Use the library without logging configuration (logs go to default stderr)
"""

import asyncio
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich import print as rprint

from ani_scrapy import AnimeFLVScraper

console = Console()


async def main():
    """Run the logging configuration example."""
    rprint("[bold cyan]=== Example 07: Logging with Loguru[/bold cyan]\n")

    rprint("[bold]Option 1: Configure Loguru Once (Recommended)[/bold]")
    rprint("-" * 50)
    rprint(
        "[dim]# Configure at application startup, all scrapers inherit config[/dim]\n"
    )
    # Configure Loguru globally
    logger.configure(
        handlers=[
            {"sink": "app.log", "level": "DEBUG", "enqueue": True},
            {"sink": lambda msg: rprint(msg, end=""), "level": "INFO"},
        ]
    )
    rprint("[green]✓ Loguru configured globally[/green]\n")

    async with AnimeFLVScraper() as scraper:
        await scraper.search_anime(query="test")
    rprint()

    rprint("[bold]Option 2: Use Default (no configuration)[/bold]")
    rprint("-" * 50)
    rprint("[dim]# Logs go to stderr with default Loguru settings[/dim]\n")
    async with AnimeFLVScraper() as scraper:
        await scraper.search_anime(query="test")
    rprint()

    rprint("[bold]Configuration Summary[/bold]")
    summary = """from loguru import logger
import sys

# Configure Loguru at application startup
logger.configure(
    handlers=[
        {"sink": "app.log", "level": "DEBUG", "enqueue": True},
        {"sink": sys.stderr, "level": "INFO"},
    ]
)

# Use scrapers - they automatically use the configured logger
from ani_scrapy import AnimeFLVScraper

async with AnimeFLVScraper() as scraper:
    results = await scraper.search_anime("naruto")
"""
    console.print(
        Panel(
            Syntax(summary, "python", line_numbers=True),
            title="Logging Best Practices",
            expand=False,
        )
    )

    rprint("\n[bold cyan]=== Example Complete ===[/bold cyan]")


if __name__ == "__main__":
    asyncio.run(main())
