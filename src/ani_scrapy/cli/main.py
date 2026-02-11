"""ani-scrapy CLI - Main entry point with subcommands."""

import sys
import typer

from ani_scrapy.cli.doctor import AniScrapyDoctor


app = typer.Typer(
    help="ani-scrapy - Anime scraping CLI",
    add_completion=False,
)


@app.callback(invoke_without_command=True)
def callback(ctx: typer.Context):
    """ani-scrapy CLI - Anime scraping tool."""
    if ctx.invoked_subcommand is None:
        ctx.get_help()


@app.command("doctor")
def doctor(
    output: str = typer.Option(
        "text",
        "--output",
        "-o",
        help="Output format (text or json)",
        case_sensitive=False,
    ),
    timeout: int = typer.Option(
        5, "--timeout", "-t", help="Timeout for connectivity checks in seconds"
    ),
):
    """Run ani-scrapy doctor diagnostic tool."""

    doctor_tool = AniScrapyDoctor(timeout=timeout)
    report = doctor_tool.run()

    if output == "json":
        import json

        typer.echo(json.dumps(report.to_dict(), indent=2))
    else:
        doctor_tool.print_report(report)

    sys.exit(report.exit_code)


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
