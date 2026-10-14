from __future__ import annotations

import pytest

from ani_scrapy import AnimeFLVScraper
from ani_scrapy.providers.animeflv.parser import AnimeFLVParser


def test_scraper_emits_deprecation_warning() -> None:
    with pytest.warns(DeprecationWarning, match="animeflv.or.at"):
        scraper = AnimeFLVScraper()

    assert isinstance(scraper.parser, AnimeFLVParser)
