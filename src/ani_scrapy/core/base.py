from abc import ABC
from loguru import logger
import sys
from pathlib import Path
from typing import Optional
import random

_TASK_ID_CHARS = (
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
)

DEFAULT_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> "
    "| <level>{level: <8}</level> "
    "| <cyan>{extra[task_id]:-<12}</cyan> "
    "| <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> "
    "- <level>{message}</level>"
)


def create_scraper_logger(task_id: str = ""):
    """Create logger bound to task_id for consistent log context."""
    return logger.bind(task_id=task_id)


def generate_task_id() -> str:
    """Generate a random 12-character task ID for tracking related logs.

    Uses only English alphabet characters and digits.

    Example:
        task_id = generate_task_id()  # "Ab3xK9mNp2Qr"
    """
    return "".join(random.choices(_TASK_ID_CHARS, k=12))


class BaseScraper(ABC):
    """Base class for anime scrapers."""

    def __init__(
        self,
        log_file: Optional[str] = None,
        level: str = "INFO",
        headless: bool = True,
        executable_path: str = "",
    ) -> None:
        self.log_level = level.upper()
        self.headless = headless
        self.executable_path = executable_path

        logger.remove()

        logger.add(
            sys.stderr,
            level=self.log_level,
            format=DEFAULT_FORMAT,
            colorize=True,
            backtrace=True,
            diagnose=False,
        )

        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            logger.add(
                str(log_path),
                level=self.log_level,
                format=DEFAULT_FORMAT,
                colorize=False,
                rotation="1 day",
                retention="7 days",
                compression="gz",
            )

    def __enter__(self):
        """Sync context manager entry."""
        return self

    def __exit__(self, *args):
        self.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args):
        await self.aclose()

    def close(self):
        """Close resources. Override in subclasses."""
        pass

    async def aclose(self):
        """Async close resources. Override in subclasses."""
        pass
