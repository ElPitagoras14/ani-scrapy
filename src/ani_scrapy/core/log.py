from loguru import logger as _logger
import sys

_logger.disable("ani_scrapy")

logger = _logger.bind(library="ani-scrapy")


def enable_logging(level: str = "INFO", sink=None):
    _logger.enable("ani_scrapy")
    if sink is None:
        sink = sys.stdout
    _logger.add(
        sink,
        level=level,
        enqueue=True,
        filter=lambda record: record["extra"].get("library") == "ani-scrapy",
    )
