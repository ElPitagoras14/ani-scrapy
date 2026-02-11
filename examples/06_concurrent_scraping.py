#!/usr/bin/env python3
"""
Example 06: Concurrent Scraping

Demonstrates how to efficiently scrape multiple anime concurrently.
This is useful for batch operations like getting info for many anime at once.
"""

import asyncio
import time
from rich.console import Console
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich import print as rprint

from ani_scrapy.jkanime import JKAnimeScraper
from ani_scrapy.core.base import generate_task_id

BRAVE_PATH = (
    r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
)

console = Console()


async def scrape_anime_info(scraper, anime_id, task_id):
    """Scrape info for a single anime."""
    start = time.perf_counter()
    try:
        anime = await scraper.get_anime_info(
            anime_id=anime_id, task_id=task_id
        )
        elapsed = time.perf_counter() - start
        return (
            anime_id,
            anime.title,
            len(anime.episodes) if anime.episodes else 0,
            elapsed,
        )
    except Exception as e:
        elapsed = time.perf_counter() - start
        return (anime_id, str(e), -1, elapsed)


async def main():
    """Run the concurrent scraping demo."""
    rprint("[bold cyan]=== Example 06: Concurrent Scraping[/bold cyan]\n")

    task_id = generate_task_id()
    rprint(f"[dim]Task ID: {task_id}[/dim]\n")

    async with JKAnimeScraper(
        level="WARNING",
        headless=True,
        executable_path=BRAVE_PATH,
    ) as scraper:
        anime_ids = [
            "spy-x-family",
            "gachiakuta",
            "jigokuraku",
            "kaoru-hana-wa-rin-to-saku",
            "shingeki-no-kyojin",
        ]

        rprint(
            f"[bold]Scraping info for {len(anime_ids)} anime concurrently..."
            + "[/bold]\n"
        )

        with Progress(
            TextColumn(
                "[bold cyan]Scraping: {task.completed}/{task.total} anime"
                + "[/bold cyan]"
            ),
            BarColumn(bar_width=None),
            TaskProgressColumn(),
            console=console,
            transient=True,
        ) as progress:
            main_task = progress.add_task("Scraping", total=len(anime_ids))

            results = []
            for anime_id in anime_ids:
                result = await scrape_anime_info(scraper, anime_id, task_id)
                results.append(result)
                progress.advance(main_task, 1)

        rprint("\n[bold]Results:[/bold]\n")

        table = Table(title="Scraped Anime")
        table.add_column("ID", style="cyan")
        table.add_column("Title", style="magenta")
        table.add_column("Episodes", style="green")
        table.add_column("Time", style="dim")

        for anime_id, title, episodes, elapsed in results:
            if episodes == -1:
                table.add_row(
                    anime_id, "[red]Error[/red]", "-", f"{elapsed:.2f}s"
                )
            else:
                table.add_row(
                    anime_id, title or "N/A", str(episodes), f"{elapsed:.2f}s"
                )

        console.print(table)

        successful = sum(1 for _, _, e, _ in results if e > 0)
        rprint(
            f"\n[green]Successfully scraped {successful} / {len(results)} anime"
            + "[/green]"
        )

    rprint("\n[bold cyan]=== Example Complete ===[/bold cyan]")


if __name__ == "__main__":
    asyncio.run(main())
