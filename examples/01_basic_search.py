#!/usr/bin/env python3
"""
Example 01: Basic Anime Search

Demonstrates how to search for anime using both AnimeFLV and JKAnime scrapers.
Shows how to configure Loguru for logging (users must configure Loguru themselves).
"""

import asyncio
import time
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from ani_scrapy import AnimeFLVScraper, JKAnimeScraper, AnimeAV1Scraper

console = Console()


# === CONFIGURATION ===
# Enable/disable scrapers
ENABLE_ANIMEFLV = True
ENABLE_JKANIME = True
ENABLE_ANIMEAV1 = True

# Variables for AnimeFLV
ANIMEFLV_QUERY = "naruto"

# Variables for JKAnime
JKANIME_QUERY = "naruto"

# Variables for AnimeAV1
ANIMEAV1_QUERY = "naruto"


async def main():
    """Run the basic search example."""
    rprint("[bold cyan]=== Example 01: Basic Anime Search[/bold cyan]\n")

    if ENABLE_ANIMEFLV:
        rprint(f"[bold]Searching AnimeFLV for:[/bold] '{ANIMEFLV_QUERY}'\n")
        async with AnimeFLVScraper() as scraper_flv:
            rprint("[bold yellow]AnimeFLV:[/bold yellow]")
            start_flv = time.perf_counter()
            results_flv = await scraper_flv.search_anime(query=ANIMEFLV_QUERY)
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
    else:
        rprint("[dim][yellow]AnimeFLV disabled[/yellow][/dim]")

    if ENABLE_JKANIME:
        rprint(f"\n[bold]Searching JKAnime for:[/bold] '{JKANIME_QUERY}'\n")
        async with JKAnimeScraper() as scraper_jk:
            rprint("[bold yellow]JKAnime:[/bold yellow]")
            start_jk = time.perf_counter()
            results_jk = await scraper_jk.search_anime(query=JKANIME_QUERY)
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
    else:
        rprint("[dim][yellow]JKAnime disabled[/yellow][/dim]")

    if ENABLE_ANIMEAV1:
        rprint(f"\n[bold]Searching AnimeAV1 for:[/bold] '{ANIMEAV1_QUERY}'\n")
        async with AnimeAV1Scraper() as scraper_av1:
            rprint("[bold yellow]AnimeAV1:[/bold yellow]")
            start_av1 = time.perf_counter()
            results_av1 = await scraper_av1.search_anime(query=ANIMEAV1_QUERY)
            elapsed_av1 = time.perf_counter() - start_av1

            table3 = Table(title="AnimeAV1 Results")
            table3.add_column("ID", style="cyan")
            table3.add_column("Title", style="magenta")
            table3.add_column("Type", style="green")

            for anime in results_av1.animes[:10]:
                table3.add_row(
                    anime.id,
                    anime.title,
                    anime.type.value or "-",
                )

            console.print(table3)
            console.print(
                f"\n[green]Found {len(results_av1.animes)} results on "
                + f"AnimeAV1[/green] ({elapsed_av1:.2f}s)"
            )
    else:
        rprint("[dim][yellow]AnimeAV1 disabled[/yellow][/dim]")

    rprint("\n[bold cyan]=== Example Complete ===[/bold cyan]")


if __name__ == "__main__":
    asyncio.run(main())
