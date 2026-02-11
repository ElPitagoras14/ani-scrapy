#!/usr/bin/env python3
"""
Example 03: Download Links

Demonstrates how to retrieve download links from multiple servers:
- Table download links (direct server links)
- Iframe download links (embedded player links)
- Final file download links (resolved URLs)
"""

import asyncio
import time
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from ani_scrapy import AnimeFLVScraper
from ani_scrapy.jkanime import JKAnimeScraper
from ani_scrapy.core.base import generate_task_id

BRAVE_PATH = (
    r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
)

console = Console()


async def main():
    """Run the download links example."""
    rprint("[bold cyan]=== Example 03: Download Links[/bold cyan]\n")

    task_id = generate_task_id()
    rprint(f"[dim]Task ID: {task_id}[/dim]\n")

    anime_id = "gachiakuta"
    episode_number = 24

    rprint(
        f"[bold]Getting download links for:[/bold] {anime_id} - "
        + f"Episode {episode_number}\n"
    )

    async with AnimeFLVScraper(
        level="DEBUG",
        headless=True,
        executable_path=BRAVE_PATH,
    ) as scraper_flv:
        rprint(
            "[bold yellow]=== AnimeFLV Table Download Links ===[/bold yellow]"
        )
        start_flv = time.perf_counter()
        table_links = await scraper_flv.get_table_download_links(
            anime_id=anime_id, episode_number=episode_number, task_id=task_id
        )

        if table_links.download_links:
            table = Table(title="AnimeFLV Direct Download Links")
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
        else:
            rprint(
                "[yellow]No table download links found for AnimeFLV[/yellow]"
            )

        rprint(
            "\n[bold yellow]=== AnimeFLV Iframe Download Links "
            + "===[/bold yellow]"
        )
        iframe_links = await scraper_flv.get_iframe_download_links(
            anime_id=anime_id, episode_number=episode_number, task_id=task_id
        )

        if iframe_links.download_links:
            table2 = Table(title="AnimeFLV Iframe Download Links")
            table2.add_column("Server", style="cyan")
            table2.add_column("URL", style="magenta")

            for link in iframe_links.download_links:
                url_display = (
                    link.url[:60] + "..."
                    if link.url and len(link.url) > 60
                    else link.url or "N/A"
                )
                table2.add_row(link.server, url_display)

            console.print(table2)

            rprint(
                "\n[bold green]=== AnimeFLV Getting Final Download URL "
                + "===[/bold green]"
            )

            for link in iframe_links.download_links[:1]:
                if link.url:
                    final_url = await scraper_flv.get_file_download_link(
                        download_info=link, task_id=task_id
                    )
                    if final_url:
                        rprint(
                            f"\n[green]Final download URL for {link.server}:"
                            + "[/green]"
                        )
                        rprint(f"[cyan]{final_url}[/cyan]")
        else:
            rprint(
                "[yellow]No iframe download links found for AnimeFLV[/yellow]"
            )

        elapsed_flv = time.perf_counter() - start_flv
        rprint(f"\n[dim]AnimeFLV total time: {elapsed_flv:.2f}s[/dim]")

    async with JKAnimeScraper(
        level="DEBUG",
        headless=True,
        executable_path=BRAVE_PATH,
    ) as scraper_jk:
        rprint(
            f"\n[bold]Getting download links for JKAnime:[/bold] {anime_id} - "
            + f"Episode {episode_number}\n"
        )

        rprint(
            "[bold yellow]=== JKAnime Table Download Links ===[/bold yellow]"
        )
        start_jk = time.perf_counter()
        table_links = await scraper_jk.get_table_download_links(
            anime_id=anime_id, episode_number=episode_number, task_id=task_id
        )

        if table_links.download_links:
            table3 = Table(title="JKAnime Direct Download Links")
            table3.add_column("Server", style="cyan")
            table3.add_column("URL", style="magenta")

            for link in table_links.download_links:
                url_display = (
                    link.url[:60] + "..."
                    if link.url and len(link.url) > 60
                    else link.url or "N/A"
                )
                table3.add_row(link.server, url_display)

            console.print(table3)

            valid_download = next(
                (
                    link
                    for link in table_links.download_links
                    if link.server in scraper_jk._file_link_getters
                ),
                None,
            )

            if valid_download:
                rprint(
                    "\n[bold green]Getting file download link from "
                    + f"{valid_download.server}...[/bold green]"
                )

                file_link = await scraper_jk.get_file_download_link(
                    download_info=valid_download, task_id=task_id
                )

                if file_link:
                    rprint("[cyan]File download URL:[/cyan]")
                    print(file_link)
                else:
                    rprint("[yellow]Could not get file download link[/yellow]")
            else:
                rprint(
                    "[yellow]No supported servers found for file download"
                    + "[/yellow]"
                )
        else:
            rprint(
                "[yellow]No table download links found for JKAnime[/yellow]"
            )

        elapsed_jk = time.perf_counter() - start_jk
        rprint(f"\n[dim]JKAnime total time: {elapsed_jk:.2f}s[/dim]")

    rprint("\n[bold cyan]=== Example Complete ===[/bold cyan]")


if __name__ == "__main__":
    asyncio.run(main())
