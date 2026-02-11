#!/usr/bin/env python3
"""
Example 05: Task Tracking Demo

Demonstrates how to use task_id for correlating logs across multiple operations.
The same task_id is passed through all function calls, allowing you to filter
all related logs.
"""

import asyncio
import time
from rich.console import Console
from rich import print as rprint

from ani_scrapy import AnimeFLVScraper, JKAnimeScraper
from ani_scrapy.core.base import generate_task_id

BRAVE_PATH = (
    r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
)

console = Console()


async def demo_multiple_tasks():
    """Demonstrate tracking with multiple task_ids using concurrent scrapers."""
    rprint("\n\n[bold cyan]=== Multiple Tasks Demo ===[/bold cyan]\n")

    task1 = generate_task_id()
    task2 = generate_task_id()

    rprint(f"[yellow]Task 1:[/yellow] {task1}")
    rprint(f"[yellow]Task 2:[/yellow] {task2}\n")

    async def animeflv_task():
        rprint("[cyan][AnimeFLV] Searching for naruto...[/cyan]")
        start = time.perf_counter()
        async with AnimeFLVScraper(
            level="DEBUG", executable_path=BRAVE_PATH
        ) as scraper:
            results = await scraper.search_anime(query="naruto", task_id=task1)
        elapsed = time.perf_counter() - start
        rprint(
            f"[green][AnimeFLV] Found {len(results.animes)} "
            + f"results[/green] ({elapsed:.2f}s)"
        )

        anime_id = "gachiakuta"
        rprint(f"[cyan][AnimeFLV] Getting anime info for: {anime_id}[/cyan]")
        start_info = time.perf_counter()
        async with AnimeFLVScraper(
            level="DEBUG", executable_path=BRAVE_PATH
        ) as scraper:
            anime = await scraper.get_anime_info(
                anime_id=anime_id, task_id=task1
            )
        elapsed_info = time.perf_counter() - start_info
        rprint(
            f"[green][AnimeFLV] Got info: {anime.title} "
            + f"({len(anime.episodes) if anime.episodes else 0} episodes)"
            + "[/green] "
            + f"({elapsed_info:.2f}s)"
        )

    async def jkanime_task():
        rprint("[magenta][JKAnime] Searching for naruto...[/magenta]")
        start = time.perf_counter()
        async with JKAnimeScraper(
            level="DEBUG", executable_path=BRAVE_PATH
        ) as scraper:
            results = await scraper.search_anime(query="naruto", task_id=task2)
        elapsed = time.perf_counter() - start
        rprint(
            f"[green][JKAnime] Found {len(results.animes)} "
            + f"results[/green] ({elapsed:.2f}s)"
        )

        anime_id = "gachiakuta"
        rprint(
            f"[magenta][JKAnime] Getting anime info for: {anime_id}[/magenta]"
        )
        start_info = time.perf_counter()
        async with JKAnimeScraper(
            level="DEBUG", executable_path=BRAVE_PATH
        ) as scraper:
            anime = await scraper.get_anime_info(
                anime_id=anime_id, task_id=task2
            )
        elapsed_info = time.perf_counter() - start_info
        rprint(
            f"[green][JKAnime] Got info: {anime.title} "
            + f"({len(anime.episodes) if anime.episodes else 0} episodes)"
            + "[/green] "
            + f"({elapsed_info:.2f}s)"
        )

    rprint("[bold]Running concurrent operations...[/bold]\n")
    await asyncio.gather(animeflv_task(), jkanime_task())

    rprint(
        "\n[dim]Logs are now interleaved but each operation can be "
        + "filtered by task_id[/dim]"
    )


async def main():
    """Run the task tracking demo."""
    await demo_multiple_tasks()

    rprint("\n[bold cyan]=== All Demos Complete ===[/bold cyan]")


if __name__ == "__main__":
    asyncio.run(main())
