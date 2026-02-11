#!/usr/bin/env python3
"""
Example 01: Basic Anime Search

Demonstrates how to search for anime using both AnimeFLV and JKAnime scrapers.
Shows how to use task_id for log correlation and format results with tabulate.
"""

import asyncio
import time
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from ani_scrapy import AnimeFLVScraper, JKAnimeScraper
from ani_scrapy.core.base import generate_task_id

console = Console()


async def main():
    """Run the basic search example."""
    rprint("[bold cyan]=== Example 01: Basic Anime Search[/bold cyan]\n")

    task_id = generate_task_id()
    rprint(f"[dim]Task ID: {task_id}[/dim]\n")

    query = "naruto"
    rprint(f"[bold]Searching for:[/bold] '{query}'\n")

    async with AnimeFLVScraper(level="DEBUG") as scraper_flv:
        rprint("[bold yellow]AnimeFLV:[/bold yellow]")
        start_flv = time.perf_counter()
        results_flv = await scraper_flv.search_anime(
            query=query, task_id=task_id
        )
        elapsed_flv = time.perf_counter() - start_flv

        table = Table(title="AnimeFLV Results")
        table.add_column("ID", style="cyan")
        table.add_column("Title", style="magenta")
        table.add_column("Type", style="green")

        for anime in results_flv.animes[:10]:
            table.add_row(
                anime.id,
                anime.title,
                anime.type.value or "-",
            )

        console.print(table)
        console.print(
            f"\n[green]Found {len(results_flv.animes)} results on "
            + f"AnimeFLV[/green] ({elapsed_flv:.2f}s)"
        )

    async with JKAnimeScraper(level="DEBUG") as scraper_jk:
        rprint("\n[bold yellow]JKAnime:[/bold yellow]")
        start_jk = time.perf_counter()
        results_jk = await scraper_jk.search_anime(
            query=query, task_id=task_id
        )
        elapsed_jk = time.perf_counter() - start_jk

        table2 = Table(title="JKAnime Results")
        table2.add_column("ID", style="cyan")
        table2.add_column("Title", style="magenta")
        table2.add_column("Type", style="green")

        for anime in results_jk.animes[:10]:
            table2.add_row(
                anime.id,
                anime.title,
                anime.type.value or "-",
            )

        console.print(table2)
        console.print(
            f"\n[green]Found {len(results_jk.animes)} results on "
            + f"JKAnime[/green] ({elapsed_jk:.2f}s)"
        )

    rprint("\n[bold cyan]=== Example Complete ===[/bold cyan]")


if __name__ == "__main__":
    asyncio.run(main())
