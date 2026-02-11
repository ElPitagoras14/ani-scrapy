#!/usr/bin/env python3
"""
Example 07: Error Handling

Demonstrates how to properly handle exceptions that may occur during scraping:
- ScraperBlockedError: Website blocked the request
- ScraperTimeoutError: Request timed out
- ScraperParseError: Failed to parse the response
- Generic ScraperError: Base exception class
"""

import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from rich import print as rprint

from ani_scrapy.core.base import generate_task_id

console = Console()


def format_error(error_type, message, recovery=""):
    """Format error information into a panel."""
    text = Text()
    text.append(f"[bold red]Error Type:[/bold red] {error_type}\n\n")
    text.append(f"[bold yellow]Message:[/bold yellow]\n{message}")
    if recovery:
        text.append(f"\n\n[bold green]Recovery:[/bold green]\n{recovery}")
    return Panel(text, title="Exception Details", expand=False)


async def main():
    """Run the error handling example."""
    rprint("[bold cyan]=== Example 07: Error Handling[/bold cyan]\n")

    task_id = generate_task_id()
    rprint(f"[dim]Task ID: {task_id}[/dim]\n")

    rprint("[bold]Handling common scraping exceptions...[/bold]\n")

    rprint("[yellow]1. ScraperBlockedError[/yellow]")
    rprint("-" * 50)
    console.print(
        format_error(
            "ScraperBlockedError",
            "The website has blocked access. This may happen due to:\n"
            "- Too many requests\n"
            "- Missing User-Agent header\n"
            "- IP blocking by the website",
            recovery="1. Wait before retrying\n"
            "2. Use a proxy/VPN\n"
            "3. Add custom headers\n"
            "4. Use browser automation",
        )
    )
    rprint()

    rprint("[yellow]2. ScraperTimeoutError[/yellow]")
    rprint("-" * 50)
    console.print(
        format_error(
            "ScraperTimeoutError",
            "The request timed out. This may happen due to:\n"
            "- Slow network connection\n"
            "- Website is down or slow\n"
            "- Request timeout value too low",
            recovery="1. Increase timeout value\n"
            "2. Check network connection\n"
            "3. Implement retry logic\n"
            "4. Use exponential backoff",
        )
    )
    rprint()

    rprint("[yellow]3. ScraperParseError[/yellow]")
    rprint("-" * 50)
    console.print(
        format_error(
            "ScraperParseError",
            "Failed to parse the website response. This may happen due to:\n"
            "- Website structure changed\n"
            "- Missing required elements\n"
            "- Unexpected HTML format",
            recovery="1. Update the scraper code\n"
            "2. Check the website for changes\n"
            "3. Make parsing more robust\n"
            "4. Add fallback parsing",
        )
    )
    rprint()

    rprint("[yellow]4. Generic Exception Handling[/yellow]")
    rprint("-" * 50)

    code_example = '''try:
    results = await scraper.search_anime(query="test")
except ScraperBlockedError:
    print("Access blocked - try again later or use a proxy")
except ScraperTimeoutError:
    print("Request timed out - check your connection")
except ScraperParseError:
    print("Failed to parse - website structure may have changed")
except ScraperError as e:
    print(f"Scraping error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
'''
    console.print(
        Panel(
            Syntax(code_example, "python", line_numbers=True),
            title="Best Practice Example",
            expand=False
        )
    )

    rprint("\n[bold cyan]=== Example Complete ===[/bold cyan]")


if __name__ == "__main__":
    asyncio.run(main())
