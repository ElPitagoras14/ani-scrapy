#!/usr/bin/env python3
"""
Example 07: Logging with Loguru

This example shows how to use Loguru for logging when using ani-scrapy.
The library does NOT configure logging automatically - it is silent by default.
You must explicitly enable logging using enable_logging().

Options:
1. Use enable_logging() to activate ani-scrapy logs (recommended)
2. Configure Loguru globally for your application
"""

import asyncio
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich import print as rprint

from ani_scrapy import AnimeFLVScraper, enable_logging

console = Console()


async def main():
    """Run the logging configuration example."""
    rprint("[bold cyan]=== Example 07: Logging with Loguru[/bold cyan]\n")

    rprint("[bold]Option 1: Enable ani-scrapy Logging (Recommended)[/bold]")
    rprint("-" * 50)
    rprint("[dim]# Enable logging for ani-scrapy library[/dim]\n")
    enable_logging(level="DEBUG")
    rprint("[green]✓ ani-scrapy logging enabled[/green]\n")

    async with AnimeFLVScraper() as scraper:
        await scraper.search_anime(query="test")
    rprint()

    rprint("[bold]Option 2: Configure Custom Sink[/bold]")
    rprint("-" * 50)
    rprint("[dim]# Enable with custom sink (e.g., file)[/dim]\n")
    enable_logging(level="DEBUG", sink="ani_scrapy.log")
    rprint("[green]✓ Logging to file enabled[/green]\n")

    async with AnimeFLVScraper() as scraper:
        await scraper.search_anime(query="test")
    rprint()

    rprint("[bold]Option 3: Disable Logging (Silent)[/bold]")
    rprint("-" * 50)
    rprint("[dim]# By default, ani-scrapy is silent[/dim]\n")
    rprint(
        "[yellow]Note: To fully disable, remove the handler added by enable_logging()[/yellow]\n"
    )

    rprint("[bold]Configuration Summary[/bold]")
    summary = """from loguru import logger
from ani_scrapy import AnimeFLVScraper, enable_logging

# Configure your application logger
logger.add("app.log", level="DEBUG")

# Enable ani-scrapy library logging (optional)
enable_logging(level="DEBUG")

# Use scrapers - library is silent by default
async with AnimeFLVScraper() as scraper:
    results = await scraper.search_anime("naruto")

# Enable with custom sink
enable_logging(level="DEBUG", sink="ani_scrapy.log")"""
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
