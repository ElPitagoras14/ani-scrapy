from __future__ import annotations

import asyncio
import importlib

import pytest

from ani_scrapy import AnimeFLVScraper, JKAnimeScraper
from ani_scrapy.core.schemas import DownloadLinkInfo


@pytest.mark.parametrize("scraper_cls", [AnimeFLVScraper, JKAnimeScraper])
def test_unsupported_server_returns_none(scraper_cls: type) -> None:
    link = DownloadLinkInfo(server="Nope", url="https://example.test/file")

    assert asyncio.run(scraper_cls().get_file_download_link(link)) is None


@pytest.mark.parametrize("site", ["animeflv", "jkanime", "animeav1"])
def test_per_provider_constant_is_removed(site: str) -> None:
    constants = importlib.import_module(f"ani_scrapy.providers.{site}.constants")

    assert not hasattr(constants, "SUPPORTED_SERVERS")
    with pytest.raises(ImportError):
        exec(f"from ani_scrapy.providers.{site}.constants import SUPPORTED_SERVERS")
