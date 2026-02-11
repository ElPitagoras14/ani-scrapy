"""ani-scrapy CLI tools."""

__all__ = ["app", "main"]


def __getattr__(name):
    """Lazy import to avoid circular import warnings."""
    if name in ("app", "main"):
        from ani_scrapy.cli.main import app, main

        globals()["app"] = app
        globals()["main"] = main
        return globals()[name]

    raise AttributeError(f"module 'ani_scrapy.cli' has no attribute '{name}'")
