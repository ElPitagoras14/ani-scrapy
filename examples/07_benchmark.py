#!/usr/bin/env python3
"""
Example 07: Benchmark

Runs performance benchmark across all providers using:
- Search query: "gach"
- Anime ID: "gachiakuta"
- Episode: 24
"""

import asyncio
import time
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from ani_scrapy import AnimeFLVScraper, JKAnimeScraper, AnimeAV1Scraper
from ani_scrapy import enable_logging

console = Console()
enable_logging(level="DEBUG")

QUERY = "gach"
ANIME_ID = "gachiakuta"
EPISODE = 24

ENABLE_ANIMEFLV = True
ENABLE_JKANIME = True
ENABLE_ANIMEAV1 = True


async def benchmark_scraper(
    name: str, scraper_class, query: str, anime_id: str, episode: int
):
    """Run benchmark for a single scraper."""
    results = {
        "name": name,
        "search_anime": None,
        "get_anime_info": None,
        "get_table_download_links": None,
        "get_iframe_download_links": None,
    }

    async with scraper_class() as scraper:
        start = time.perf_counter()
        await scraper.search_anime(query)
        results["search_anime"] = (time.perf_counter() - start) * 1000

        start = time.perf_counter()
        await scraper.get_anime_info(anime_id)
        results["get_anime_info"] = (time.perf_counter() - start) * 1000

        start = time.perf_counter()
        await scraper.get_table_download_links(anime_id, episode)
        results["get_table_download_links"] = (time.perf_counter() - start) * 1000

        start = time.perf_counter()
        await scraper.get_iframe_download_links(anime_id, episode)
        results["get_iframe_download_links"] = (time.perf_counter() - start) * 1000

    return results


async def main():
    """Run benchmark across all providers."""
    rprint("[bold cyan]=== Benchmark ===[/bold cyan]\n")
    rprint(f"Query: '{QUERY}' | Anime ID: '{ANIME_ID}' | Episode: {EPISODE}\n")

    benchmarks = []

    if ENABLE_ANIMEFLV:
        rprint("[bold]Running AnimeFLV benchmark...[/bold]")
        try:
            results = await benchmark_scraper(
                "AnimeFLV", AnimeFLVScraper, QUERY, ANIME_ID, EPISODE
            )
            benchmarks.append(results)
        except Exception as e:
            rprint(f"[red]AnimeFLV failed: {e}[/red]")
    else:
        rprint("[dim][yellow]AnimeFLV disabled[/yellow][/dim]")

    if ENABLE_JKANIME:
        rprint("[bold]Running JKAnime benchmark...[/bold]")
        try:
            results = await benchmark_scraper(
                "JKAnime", JKAnimeScraper, QUERY, ANIME_ID, EPISODE
            )
            benchmarks.append(results)
        except Exception as e:
            rprint(f"[red]JKAnime failed: {e}[/red]")
    else:
        rprint("[dim][yellow]JKAnime disabled[/yellow][/dim]")

    if ENABLE_ANIMEAV1:
        rprint("[bold]Running AnimeAV1 benchmark...[/bold]")
        try:
            results = await benchmark_scraper(
                "AnimeAV1", AnimeAV1Scraper, QUERY, ANIME_ID, EPISODE
            )
            benchmarks.append(results)
        except Exception as e:
            rprint(f"[red]AnimeAV1 failed: {e}[/red]")
    else:
        rprint("[dim][yellow]AnimeAV1 disabled[/yellow][/dim]")

    table = Table(title="Benchmark Results (ms)")
    table.add_column("Provider", style="cyan")
    table.add_column("search_anime", justify="right")
    table.add_column("get_anime_info", justify="right")
    table.add_column("get_table_download_links", justify="right")
    table.add_column("get_iframe_download_links", justify="right")

    for b in benchmarks:
        table.add_row(
            b["name"],
            f"{b['search_anime']:.2f}" if b["search_anime"] else "-",
            f"{b['get_anime_info']:.2f}" if b["get_anime_info"] else "-",
            f"{b['get_table_download_links']:.2f}"
            if b["get_table_download_links"]
            else "-",
            f"{b['get_iframe_download_links']:.2f}"
            if b["get_iframe_download_links"]
            else "-",
        )

    console.print(table)
    rprint("\n[bold cyan]=== Benchmark Complete ===[/bold cyan]")


if __name__ == "__main__":
    asyncio.run(main())
