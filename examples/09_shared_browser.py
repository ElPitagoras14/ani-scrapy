#!/usr/bin/env python3
"""
Example 09: Shared Browser

Demonstrates how to reuse the browser across multiple operations:
- Manual browser control with start_browser() / stop_browser()
- Multiple operations with single browser instance
- Custom browser (Brave) in all three scenarios
"""

import asyncio
import time
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from ani_scrapy.jkanime import JKAnimeScraper

BRAVE_PATH = (
    r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
)

console = Console()


async def automatic_browser_with_brave():
    """Scenario 1: Automatic browser with Brave."""
    rprint(
        "[bold cyan]=== Scenario 1: Automatic Browser + Brave ===[/bold cyan]\n"
    )
    rprint("[dim]Browser created automatically on first use...[/dim]\n")

    async with JKAnimeScraper(
        headless=True, executable_path=BRAVE_PATH
    ) as scraper:
        start = time.perf_counter()

        anime_id = "gachiakuta"
        episode = 1

        info = await scraper.get_anime_info(anime_id, include_episodes=True)
        links = await scraper.get_table_download_links(anime_id, episode)

        elapsed = time.perf_counter() - start

    table = Table(title="Results")
    table.add_column("Operation", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Title", info.title or "N/A")
    table.add_row("Episodes", str(len(info.episodes) if info.episodes else 0))
    table.add_row("Download Links", str(len(links.download_links)))

    console.print(table)
    rprint(f"\n[bold]Time: {elapsed:.2f}s[/bold]")


async def manual_browser_with_brave():
    """Scenario 2: Manual start/stop with Brave."""
    rprint(
        "\n[bold cyan]=== Scenario 2: Manual Browser + Brave ===[/bold cyan]\n"
    )
    rprint("[bold]Starting browser manually...[/bold]\n")

    async with JKAnimeScraper(
        headless=True, executable_path=BRAVE_PATH
    ) as scraper:
        start = time.perf_counter()

        await scraper.start_browser()

        anime_id = "gachiakuta"
        episode = 1

        info = await scraper.get_anime_info(anime_id, include_episodes=True)
        links = await scraper.get_table_download_links(anime_id, episode)
        if links.download_links:
            final_url = await scraper.get_file_download_link(
                links.download_links[0]
            )
            rprint(f"[bold]Final URL:[/bold] {final_url}")

        await scraper.stop_browser()

        elapsed = time.perf_counter() - start

        table = Table(title="Results")
        table.add_column("Operation", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Title", info.title or "N/A")
        table.add_row(
            "Episodes", str(len(info.episodes) if info.episodes else 0)
        )
        table.add_row("Download Links", str(len(links.download_links)))

        console.print(table)
        rprint(f"\n[bold]Time: {elapsed:.2f}s[/bold]")


async def external_browser_with_brave():
    """Scenario 3: External browser with Brave."""
    rprint(
        "\n[bold cyan]=== Scenario 3: External Browser + Brave ===[/bold cyan]\n"
    )
    rprint("[bold]Creating external AsyncBrowser with Brave...[/bold]\n")

    from ani_scrapy import AsyncBrowser

    async with AsyncBrowser(
        headless=True, executable_path=BRAVE_PATH
    ) as browser:
        async with JKAnimeScraper(external_browser=browser) as scraper:
            start = time.perf_counter()

            anime_id = "gachiakuta"
            episode = 1

            info = await scraper.get_anime_info(
                anime_id, include_episodes=True
            )
            links = await scraper.get_table_download_links(anime_id, episode)
            if links.download_links:
                final_url = await scraper.get_file_download_link(
                    links.download_links[0]
                )
                rprint(f"[bold]Final URL:[/bold] {final_url}")

            elapsed = time.perf_counter() - start

            table = Table(title="Results")
            table.add_column("Operation", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("Title", info.title or "N/A")
            table.add_row(
                "Episodes", str(len(info.episodes) if info.episodes else 0)
            )
            table.add_row("Download Links", str(len(links.download_links)))

            console.print(table)
            rprint(f"\n[bold]Time: {elapsed:.2f}s[/bold]")


async def main():
    """Run all three scenarios."""
    await automatic_browser_with_brave()
    await manual_browser_with_brave()
    await external_browser_with_brave()

    rprint("\n[bold cyan]=== All Scenarios Complete ===[/bold cyan]")
    rprint("\n[bold]Summary:[/bold]")
    rprint(
        "  1. Automatic: Browser created on first use, closed on scraper exit"
    )
    rprint("  2. Manual:    Control start/stop for better resource management")
    rprint("  3. External:  Inject your own browser instance for full control")


if __name__ == "__main__":
    asyncio.run(main())
