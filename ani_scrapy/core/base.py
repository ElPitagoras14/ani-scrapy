from abc import ABC
from loguru import logger
import sys


class BaseScraper(ABC):
    """
    Base class for anime scrapers.
    """

    def __init__(self, verbose: bool = False, level: str = "INFO") -> None:
        self.verbose = verbose
        self.level = level.upper()

        logger.remove()

        if self.verbose:
            logger.add(
                sink=sys.stderr,  # usa stderr para que conserve colores
                level=self.level,
                backtrace=True,
                diagnose=False,
                format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> "
                "| <level>{level: <8}</level> "
                "| <cyan>{name}</cyan>:<cyan>{function}</cyan>:"
                "<cyan>{line}</cyan> "
                "- <level>{message}</level>",
            )

    def _log(self, message: str, level: str = "INFO") -> None:
        """
        Log a message at the given level, showing the correct caller line.
        """
        if not self.verbose:
            return
        log_fn = getattr(logger.opt(depth=1), level.lower(), logger.info)
        log_fn(message)
