#!/usr/bin/env python3
"""
Example 02: Get Anime Information

Demonstrates how to get detailed anime information including:
- Title, synopsis, genres
- Episode list with thumbnails
- Rating and status information
"""

import asyncio
import time
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import print as rprint

from ani_scrapy import AnimeFLVScraper
from ani_scrapy.jkanime import JKAnimeScraper
from ani_scrapy.core.base import generate_task_id
from ani_scrapy.core.schemas import AnimeInfo

BRAVE_PATH = (
    r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
)

console = Console()


def format_info(anime: AnimeInfo):
    """Format anime info into a rich panel."""
    text = Text()

    text.append("Title: ", style="bold green")
    text.append(anime.title or "N/A", style="white")
    text.append("\n\n")

    text.append("Is Finished: ", style="bold cyan")
    text.append(str(anime.is_finished) or "N/A", style="white")
    text.append("\n\n")

    text.append("Type: ", style="bold cyan")
    text.append(anime.type.value or "N/A", style="white")
    text.append("\n\n")

    text.append("Rating: ", style="bold cyan")
    text.append(str(anime.rating) or "N/A", style="white")
    text.append("\n\n")

    text.append("Genres: ", style="bold cyan")
    text.append(
        ", ".join(anime.genres) if anime.genres else "N/A", style="white"
    )
    text.append("\n\n")

    text.append("Synopsis:\n", style="bold yellow")
    text.append(
        anime.synopsis[:500] + "..."
        if anime.synopsis and len(anime.synopsis) > 500
        else anime.synopsis or "N/A"
    )

    return Panel(text, title="Anime Information", expand=False)


async def main():
    """Run the anime info example."""
    rprint("[bold cyan]=== Example 02: Get Anime Information[/bold cyan]\n")

    task_id = generate_task_id()
    rprint(f"[dim]Task ID: {task_id}[/dim]\n")

    async with AnimeFLVScraper(
        level="DEBUG", headless=True, executable_path=BRAVE_PATH
    ) as scraper:
        anime_id = "gachiakuta"

        rprint(f"[bold]Fetching info for:[/bold] '{anime_id}'\n")

        start_time = time.perf_counter()
        anime = await scraper.get_anime_info(
            anime_id=anime_id, task_id=task_id
        )
        elapsed = time.perf_counter() - start_time

        console.print(format_info(anime))

        if anime.episodes:
            table = Table(title="Episodes")
            table.add_column("#", style="cyan", width=5)
            table.add_column("Title", style="magenta")
            table.add_column("Image", style="dim")

            for ep in anime.episodes[:10]:
                table.add_row(
                    str(ep.number),
                    f"Episode {ep.number}",
                    ep.image_preview[:50] + "..." if ep.image_preview else "-",
                )

            console.print(table)

            if len(anime.episodes) > 10:
                console.print(
                    f"\n[dim]... and {len(anime.episodes) - 10} more "
                    + "episodes[/dim]"
                )

        rprint(f"\n[dim]Elapsed time: {elapsed:.2f}s[/dim]")

    # JKAnime with local Brave browser

    async with JKAnimeScraper(
        level="DEBUG",
        headless=True,
        executable_path=BRAVE_PATH,
    ) as scraper:
        anime_id = "gachiakuta"

        rprint(
            f"[bold]Fetching info for:[/bold] '{anime_id}' "
            + "(using Brave browser)"
        )
        rprint(f"[dim]Browser: {BRAVE_PATH}[/dim]\n")

        start_time = time.perf_counter()
        anime = await scraper.get_anime_info(
            anime_id=anime_id, task_id=task_id
        )
        elapsed = time.perf_counter() - start_time

        console.print(format_info(anime))

        if anime.episodes:
            table = Table(title="Episodes")
            table.add_column("#", style="cyan", width=5)
            table.add_column("Title", style="magenta")
            table.add_column("Image", style="dim")

            for ep in anime.episodes[:10]:
                table.add_row(
                    str(ep.number),
                    f"Episode {ep.number}",
                    ep.image_preview[:50] + "..." if ep.image_preview else "-",
                )

            console.print(table)

            if len(anime.episodes) > 10:
                console.print(
                    f"\n[dim]... and {len(anime.episodes) - 10} more "
                    + "episodes[/dim]"
                )

        rprint(f"\n[dim]Elapsed time: {elapsed:.2f}s[/dim]")

    rprint("\n[bold cyan]=== Example Complete ===[/bold cyan]")


if __name__ == "__main__":
    asyncio.run(main())
