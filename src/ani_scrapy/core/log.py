from loguru import logger as _logger
import sys

logger = _logger.bind(library="ani-scrapy")
logger.remove()


def enable_logging(level: str = "INFO", sink=None):
    if sink is None:
        sink = sys.stdout
    logger.add(sink, level=level, enqueue=True)
