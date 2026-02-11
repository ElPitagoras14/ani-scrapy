#!/usr/bin/env python3
"""
Example 09: File Download Links

Demonstrates how to get final download URLs from download link info:
- Resolving Streamwish links
- Resolving Mediafire links
- Working with DownloadLinkInfo objects
"""

import asyncio
import time
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from ani_scrapy.jkanime import JKAnimeScraper
from ani_scrapy.core.base import generate_task_id

BRAVE_PATH = (
    r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
)

console = Console()


async def main():
    """Run the file download links example."""
    rprint("[bold cyan]=== Example 09: File Download Links[/bold cyan]\n")

    task_id = generate_task_id()
    rprint(f"[dim]Task ID: {task_id}[/dim]\n")

    async with JKAnimeScraper(
        level="INFO",
        headless=True,
        executable_path=BRAVE_PATH,
    ) as scraper:
        anime_id = "gachiakuta"
        episode_number = 24

        rprint(
            f"[bold]Getting download links for:[/bold] {anime_id} - "
            + f"Episode {episode_number}\n"
        )

        rprint(
            "[bold yellow]=== Step 1: Get Table Download Links ==="
            + "[/bold yellow]"
        )
        start = time.perf_counter()
        table_links = await scraper.get_table_download_links(
            anime_id=anime_id, episode_number=episode_number, task_id=task_id
        )
        elapsed = time.perf_counter() - start

        if table_links.download_links:
            table = Table(title="Direct Download Links")
            table.add_column("Server", style="cyan")
            table.add_column("URL", style="magenta")

            for link in table_links.download_links:
                url_display = (
                    link.url[:60] + "..."
                    if link.url and len(link.url) > 60
                    else link.url or "N/A"
                )
                table.add_row(link.server, url_display)

            console.print(table)
            rprint(f"[dim]Time: {elapsed:.2f}s[/dim]\n")
        else:
            rprint("[yellow]No download links found[/yellow]\n")
            return

        rprint(
            "[bold yellow]=== Step 2: Resolve Final Download URLs ==="
            + "[/bold yellow]"
        )
        rprint(
            "[dim]This opens the download page and extracts the actual file URL"
            + "[/dim]\n"
        )

        results_table = Table(title="Final Download URLs")
        results_table.add_column("Server", style="cyan")
        results_table.add_column("Final URL", style="green")

        for link in table_links.download_links:
            if not link.url:
                continue

            rprint(f"[bold]Resolving {link.server}...[/bold]")
            start_link = time.perf_counter()

            try:
                final_url = await scraper.get_file_download_link(
                    download_info=link, task_id=task_id
                )
                elapsed_link = time.perf_counter() - start_link

                if final_url:
                    url_display = (
                        final_url[:60] + "..."
                        if len(final_url) > 60
                        else final_url
                    )
                    results_table.add_row(link.server, url_display)
                    rprint(f"  [green]✓ Got URL[/green] ({elapsed_link:.2f}s)")
                else:
                    results_table.add_row(
                        link.server, "[red]Failed to resolve[/red]"
                    )
                    rprint(
                        "  [red]✗ Failed to resolve[/red] "
                        + f"({elapsed_link:.2f}s)"
                    )
            except Exception as e:
                rprint(f"  [red]✗ Error: {e}[/red]")
                results_table.add_row(link.server, f"[red]Error: {e}[/red]")

        console.print(results_table)

    rprint("\n[bold cyan]=== Example Complete ===[/bold cyan]")


if __name__ == "__main__":
    asyncio.run(main())
