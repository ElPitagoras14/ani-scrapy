#!/usr/bin/env python3
"""
Example 04: Browser Usage

Demonstrates how to use the browser for JavaScript-rendered content:
- Getting anime info with browser
- Handling dynamic content
- Browser is configured through the scraper constructor
"""

import asyncio
import time
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

from ani_scrapy import JKAnimeScraper

BRAVE_PATH = (
    r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
)

console = Console()


async def main():
    """Run the browser usage example."""
    rprint("[bold cyan]=== Example 04: Browser Usage[/bold cyan]\n")

    async with JKAnimeScraper(
        headless=True,
        executable_path=BRAVE_PATH,
    ) as scraper:
        anime_id = "gachiakuta"

        rprint(f"[bold]Using browser for dynamic content:[/bold] {anime_id}\n")

        rprint("[dim]Browser started...[/dim]")
        start = time.perf_counter()
        anime_info = await scraper.get_anime_info(anime_id=anime_id)
        elapsed = time.perf_counter() - start
        rprint("[dim]Browser closed[/dim]")

    panel = Panel(
        f"[bold green]Title:[/bold green] {anime_info.title or 'N/A'}\n"
        f"[bold cyan]Status:[/bold cyan] {anime_info.is_finished or 'N/A'}\n"
        "[bold cyan]Episodes:[/bold cyan] "
        + f"{len(anime_info.episodes) if anime_info.episodes else 0}",
        title="Anime Info (from Browser)",
        expand=False,
    )
    console.print(panel)

    rprint(f"\n[dim]Execution time: {elapsed:.2f}s[/dim]")
    rprint("\n[bold cyan]=== Example Complete ===[/bold cyan]")


if __name__ == "__main__":
    asyncio.run(main())
