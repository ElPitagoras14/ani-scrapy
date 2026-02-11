#!/usr/bin/env python3
"""
Example 08: Logging Configuration

Demonstrates how to configure logging for different environments:
- Console output with colors
- File output with rotation
- Log levels (DEBUG, INFO, WARNING, ERROR)
- Custom log formats
"""

import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich import print as rprint

from ani_scrapy import AnimeFLVScraper

console = Console()


def show_log_levels():
    """Display log level descriptions."""
    levels = [
        ("DEBUG", "Detailed information for debugging", "Gray"),
        ("INFO", "General informational messages", "White"),
        ("WARNING", "Recoverable issues or unexpected behavior", "Yellow"),
        ("ERROR", "Errors that may still allow operation", "Red"),
        ("CRITICAL", "Severe errors that prevent operation", "Bold Red"),
    ]

    panel_text = ""
    for level, description, color in levels:
        panel_text += f"[{color}][bold]{level}[/bold]: {description}\n"

    return Panel(panel_text.rstrip(), title="Log Levels", expand=False)


async def main():
    """Run the logging configuration example."""
    rprint("[bold cyan]=== Example 08: Logging Configuration[/bold cyan]\n")

    rprint("[bold]Log Levels[/bold]")
    console.print(show_log_levels())
    rprint()

    rprint("[bold]Example 1: INFO Level (Default)[/bold]")
    rprint("-" * 50)
    rprint("[dim]# Shows general operation info[/dim]\n")
    async with AnimeFLVScraper(level="INFO") as scraper1:
        await scraper1.search_anime(query="test", task_id="INFOEXAMPLE")
    rprint()

    rprint("[bold]Example 2: DEBUG Level (Verbose)[/bold]")
    rprint("-" * 50)
    rprint("[dim]# Shows detailed debug info including HTTP requests[/dim]\n")
    async with AnimeFLVScraper(level="DEBUG") as scraper2:
        await scraper2.search_anime(query="test", task_id="DEBUGEXAMPLE")
    rprint()

    rprint("[bold]Example 3: WARNING Level (Minimal)[/bold]")
    rprint("-" * 50)
    rprint("[dim]# Shows only warnings and errors[/dim]\n")
    async with AnimeFLVScraper(level="WARNING") as scraper3:
        await scraper3.search_anime(query="test", task_id="WAREXAMPLE")
    rprint()

    rprint("[bold]Example 4: File Output with Rotation[/bold]")
    rprint("-" * 50)
    rprint("[dim]# Logs are saved to file with daily rotation[/dim]\n")
    async with AnimeFLVScraper(
        log_file="scraper.log", level="INFO"
    ) as scraper4:
        await scraper4.search_anime(query="test", task_id="FILEEXAMPLE")
    rprint("\n[green]Logs saved to: scraper.log[/green]")
    rprint("[dim]# Check the file for output[/dim]\n")

    rprint("[bold]Configuration Summary[/bold]")
    summary = '''from ani_scrapy import AnimeFLVScraper

# Development (verbose)
scraper = AnimeFLVScraper(level="DEBUG")

# Production (minimal)
scraper = AnimeFLVScraper(level="WARNING")

# With file output
scraper = AnimeFLVScraper(
    log_file="logs/scraper.log",
    level="INFO"
)

# All options
scraper = AnimeFLVScraper(
    log_file="logs/scraper.log",   # File output (optional)
    level="DEBUG"                   # Log level (default: INFO)
)

# Using context manager (recommended)
async with AnimeFLVScraper(level="DEBUG") as scraper:
    results = await scraper.search_anime("query")
'''
    console.print(
        Panel(
            Syntax(summary, "python", line_numbers=True),
            title="Configuration Options",
            expand=False
        )
    )

    rprint("\n[bold cyan]=== Example Complete ===[/bold cyan]")


if __name__ == "__main__":
    asyncio.run(main())
