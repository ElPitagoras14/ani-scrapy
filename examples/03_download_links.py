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

from ani_scrapy import AnimeFLVScraper, JKAnimeScraper, AnimeAV1Scraper
from ani_scrapy.providers.animeflv.constants import (
    SUPPORTED_SERVERS as ANIMEFLV_SUPPORTED_SERVERS,
)
from ani_scrapy.providers.jkanime.constants import (
    SUPPORTED_SERVERS as JKANIME_SUPPORTED_SERVERS,
)
from ani_scrapy.providers.animeav1.constants import (
    SUPPORTED_SERVERS as ANIMEAV1_SUPPORTED_SERVERS,
)

BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

console = Console()


# === CONFIGURATION ===
# Enable/disable scrapers
ENABLE_ANIMEFLV = False
ENABLE_JKANIME = True
ENABLE_ANIMEAV1 = True

# Variables for AnimeFLV
ANIMEFLV_ANIME_ID = "gachiakuta"
ANIMEFLV_EPISODE = 24

# Variables for JKAnime
JKANIME_ANIME_ID = "gachiakuta"
JKANIME_EPISODE = 24

# Variables for AnimeAV1
ANIMEAV1_ANIME_ID = "sousou-no-frieren-2nd-season"
ANIMEAV1_EPISODE = 7


async def main():
    """Run the download links example."""
    rprint("[bold cyan]=== Example 03: Download Links[/bold cyan]\n")

    if ENABLE_ANIMEFLV:
        rprint(
            f"[bold]Getting AnimeFLV download links for:[/bold] {ANIMEFLV_ANIME_ID} - "
            + f"Episode {ANIMEFLV_EPISODE}\n"
        )
        async with AnimeFLVScraper(
            headless=True,
            executable_path=BRAVE_PATH,
        ) as scraper_flv:
            rprint("[bold yellow]=== AnimeFLV Table Download Links ===[/bold yellow]")
            start_flv = time.perf_counter()
            table_links = await scraper_flv.get_table_download_links(
                anime_id=ANIMEFLV_ANIME_ID, episode_number=ANIMEFLV_EPISODE
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
                rprint("[yellow]No table download links found for AnimeFLV[/yellow]")

            rprint(
                "\n[bold yellow]=== AnimeFLV Iframe Download Links "
                + "===[/bold yellow]"
            )
            iframe_links = await scraper_flv.get_iframe_download_links(
                anime_id=ANIMEFLV_ANIME_ID, episode_number=ANIMEFLV_EPISODE
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

                valid_links = [
                    link
                    for link in iframe_links.download_links
                    if link.server in ANIMEFLV_SUPPORTED_SERVERS
                ]

                for link in valid_links:
                    if link.url:
                        final_url = await scraper_flv.get_file_download_link(
                            download_info=link
                        )
                        if final_url:
                            rprint(
                                f"\n[green]Final download URL for {link.server}:"
                                + "[/green]"
                            )
                            rprint(f"[cyan]{final_url}[/cyan]")
            else:
                rprint("[yellow]No iframe download links found for AnimeFLV[/yellow]")

            elapsed_flv = time.perf_counter() - start_flv
            rprint(f"\n[dim]AnimeFLV total time: {elapsed_flv:.2f}s[/dim]")
    else:
        rprint("[dim][yellow]AnimeFLV disabled[/yellow][/dim]")

    if ENABLE_JKANIME:
        rprint(
            f"\n[bold]Getting JKAnime download links for:[/bold] {JKANIME_ANIME_ID} - "
            + f"Episode {JKANIME_EPISODE}\n"
        )
        async with JKAnimeScraper(
            headless=True,
            executable_path=BRAVE_PATH,
        ) as scraper_jk:
            rprint("[bold yellow]=== JKAnime Table Download Links ===[/bold yellow]")
            start_jk = time.perf_counter()
            table_links = await scraper_jk.get_table_download_links(
                anime_id=JKANIME_ANIME_ID, episode_number=JKANIME_EPISODE
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

                valid_downloads = [
                    link
                    for link in table_links.download_links
                    if link.server in JKANIME_SUPPORTED_SERVERS
                ]

                if valid_downloads:
                    for valid_download in valid_downloads:
                        rprint(
                            "\n[bold green]Getting file download link from "
                            + f"{valid_download.server}...[/bold green]"
                        )

                        file_link = await scraper_jk.get_file_download_link(
                            download_info=valid_download
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
                rprint("[yellow]No table download links found for JKAnime[/yellow]")

            elapsed_jk = time.perf_counter() - start_jk
            rprint(f"\n[dim]JKAnime total time: {elapsed_jk:.2f}s[/dim]")
    else:
        rprint("[dim][yellow]JKAnime disabled[/yellow][/dim]")

    if ENABLE_ANIMEAV1:
        rprint(
            f"\n[bold]Getting AnimeAV1 download links for:[/bold] {ANIMEAV1_ANIME_ID} - "
            + f"Episode {ANIMEAV1_EPISODE}\n"
        )
        async with AnimeAV1Scraper(executable_path=BRAVE_PATH) as scraper_av1:
            rprint("[bold yellow]=== AnimeAV1 Table Download Links ===[/bold yellow]")
            start_av1 = time.perf_counter()
            table_links = await scraper_av1.get_table_download_links(
                anime_id=ANIMEAV1_ANIME_ID, episode_number=ANIMEAV1_EPISODE
            )

            if table_links.download_links:
                table_av1 = Table(title="AnimeAV1 Direct Download Links")
                table_av1.add_column("Server", style="cyan")
                table_av1.add_column("URL", style="magenta")

                for link in table_links.download_links:
                    url_display = (
                        link.url[:60] + "..."
                        if link.url and len(link.url) > 60
                        else link.url or "N/A"
                    )
                    table_av1.add_row(link.server, url_display)

                console.print(table_av1)

                valid_downloads = [
                    link
                    for link in table_links.download_links
                    if link.server in ANIMEAV1_SUPPORTED_SERVERS
                ]

                if valid_downloads:
                    for valid_download in valid_downloads:
                        rprint(
                            "\n[bold green]Getting file download link from "
                            + f"{valid_download.server}...[/bold green]"
                        )

                        file_link = await scraper_av1.get_file_download_link(
                            download_info=valid_download
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
                rprint("[yellow]No table download links found for AnimeAV1[/yellow]")

            rprint(
                "\n[bold yellow]=== AnimeAV1 Iframe Download Links ===[/bold yellow]"
            )
            iframe_links = await scraper_av1.get_iframe_download_links(
                anime_id=ANIMEAV1_ANIME_ID, episode_number=ANIMEAV1_EPISODE
            )

            if iframe_links.download_links:
                table_iframe = Table(title="AnimeAV1 Iframe Download Links")
                table_iframe.add_column("Server", style="cyan")
                table_iframe.add_column("URL", style="magenta")

                for link in iframe_links.download_links:
                    url_display = (
                        link.url[:60] + "..."
                        if link.url and len(link.url) > 60
                        else link.url or "N/A"
                    )
                    table_iframe.add_row(link.server, url_display)

                console.print(table_iframe)

                valid_iframes = [
                    link
                    for link in iframe_links.download_links
                    if link.server in ANIMEAV1_SUPPORTED_SERVERS
                ]

                if valid_iframes:
                    for valid_iframe in valid_iframes:
                        rprint(
                            f"\n[bold green]Getting file download link from "
                            f"{valid_iframe.server}...[/bold green]"
                        )

                        file_link = await scraper_av1.get_file_download_link(
                            download_info=valid_iframe
                        )

                        if file_link:
                            rprint("[cyan]File download URL:[/cyan]")
                            print(file_link)
                        else:
                            rprint("[yellow]Could not get file download link[/yellow]")
                else:
                    rprint(
                        "[yellow]No iframe download links found for AnimeAV1[/yellow]"
                    )

            elapsed_av1 = time.perf_counter() - start_av1
            rprint(f"\n[dim]AnimeAV1 total time: {elapsed_av1:.2f}s[/dim]")
    else:
        rprint("[dim][yellow]AnimeAV1 disabled[/yellow][/dim]")

    rprint("\n[bold cyan]=== Example Complete ===[/bold cyan]")


if __name__ == "__main__":
    asyncio.run(main())
