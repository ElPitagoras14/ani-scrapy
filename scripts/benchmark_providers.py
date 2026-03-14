"""Benchmark script for comparing provider performance."""

import asyncio
import time

from rich.console import Console
from rich.table import Table

from ani_scrapy import AnimeFLVScraper, JKAnimeScraper, AnimeAV1Scraper


ANIME_ID = "gachiakuta"
EPISODE_NUMBER = 22
QUERY = "mus"


async def benchmark_scraper(name: str, scraper, console: Console) -> dict:
    """Benchmark all public methods of a scraper."""
    results = {name: {}}

    console.print(f"\n[bold]Benchmarking {name}[/bold]")

    console.print("  - search_anime...")
    start = time.perf_counter()
    try:
        await scraper.search_anime(QUERY)
        elapsed = time.perf_counter() - start
        results[name]["search_anime"] = round(elapsed * 1000, 2)
        console.print(f"    [green]OK[/green] {elapsed * 1000:.2f}ms")
    except Exception as e:
        results[name]["search_anime"] = f"ERROR: {type(e).__name__}"
        console.print(f"    [red]FAIL[/red] {type(e).__name__}")

    console.print("  - get_anime_info...")
    start = time.perf_counter()
    try:
        await scraper.get_anime_info(ANIME_ID, include_episodes=True)
        elapsed = time.perf_counter() - start
        results[name]["get_anime_info"] = round(elapsed * 1000, 2)
        console.print(f"    [green]OK[/green] {elapsed * 1000:.2f}ms")
    except Exception as e:
        results[name]["get_anime_info"] = f"ERROR: {type(e).__name__}"
        console.print(f"    [red]FAIL[/red] {type(e).__name__}")

    console.print("  - get_table_download_links...")
    start = time.perf_counter()
    try:
        await scraper.get_table_download_links(ANIME_ID, EPISODE_NUMBER)
        elapsed = time.perf_counter() - start
        results[name]["get_table_download_links"] = round(elapsed * 1000, 2)
        console.print(f"    [green]OK[/green] {elapsed * 1000:.2f}ms")
    except Exception as e:
        results[name]["get_table_download_links"] = f"ERROR: {type(e).__name__}"
        console.print(f"    [red]FAIL[/red] {type(e).__name__}")

    console.print("  - get_iframe_download_links...")
    start = time.perf_counter()
    try:
        await scraper.get_iframe_download_links(ANIME_ID, EPISODE_NUMBER)
        elapsed = time.perf_counter() - start
        results[name]["get_iframe_download_links"] = round(elapsed * 1000, 2)
        console.print(f"    [green]OK[/green] {elapsed * 1000:.2f}ms")
    except Exception as e:
        results[name]["get_iframe_download_links"] = f"ERROR: {type(e).__name__}"
        console.print(f"    [red]FAIL[/red] {type(e).__name__}")

    return results


async def main():
    """Run benchmark for all providers."""
    console = Console()
    all_results = {}

    async with AnimeFLVScraper() as scraper:
        results = await benchmark_scraper("AnimeFLV", scraper, console)
        all_results.update(results)

    async with JKAnimeScraper() as scraper:
        results = await benchmark_scraper("JKAnime", scraper, console)
        all_results.update(results)

    async with AnimeAV1Scraper() as scraper:
        results = await benchmark_scraper("AnimeAV1", scraper, console)
        all_results.update(results)

    table = Table(title="Benchmark Results")
    table.add_column("Provider", style="cyan")
    table.add_column("search_anime", justify="right")
    table.add_column("get_anime_info", justify="right")
    table.add_column("get_table_download_links", justify="right")
    table.add_column("get_iframe_download_links", justify="right")

    for provider, methods in all_results.items():
        search = methods.get("search_anime", "N/A")
        info = methods.get("get_anime_info", "N/A")
        table_dl = methods.get("get_table_download_links", "N/A")
        iframe = methods.get("get_iframe_download_links", "N/A")

        table.add_row(
            provider,
            f"{search} ms" if isinstance(search, (int, float)) else str(search),
            f"{info} ms" if isinstance(info, (int, float)) else str(info),
            f"{table_dl} ms" if isinstance(table_dl, (int, float)) else str(table_dl),
            f"{iframe} ms" if isinstance(iframe, (int, float)) else str(iframe),
        )

    console.print("\n")
    console.print(table)


if __name__ == "__main__":
    asyncio.run(main())
