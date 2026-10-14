from __future__ import annotations

import pytest

import ani_scrapy
from ani_scrapy import (
    ScraperBlockedError,
    ScraperError,
    ScraperHTTPError,
    ScraperNotFoundError,
    ScraperParseError,
    ScraperTimeoutError,
)

SUBCLASSES = [
    ScraperNotFoundError,
    ScraperBlockedError,
    ScraperHTTPError,
    ScraperTimeoutError,
    ScraperParseError,
]


@pytest.mark.parametrize("exc_class", SUBCLASSES)
def test_direct_subclass_of_scraper_error(exc_class: type[ScraperError]) -> None:
    assert exc_class.__bases__ == (ScraperError,)
    assert exc_class.__name__ in ani_scrapy.__all__


@pytest.mark.parametrize("exc_class", SUBCLASSES)
def test_status_code_defaults_to_none(exc_class: type[ScraperError]) -> None:
    assert exc_class("boom").status_code is None


@pytest.mark.parametrize("exc_class", SUBCLASSES)
def test_status_code_is_keyword_only(exc_class: type[ScraperError]) -> None:
    exc = exc_class("boom", status_code=503)
    assert exc.status_code == 503
    assert str(exc) == "boom"
    with pytest.raises(TypeError):
        exc_class("boom", 503)


def test_http_error_does_not_catch_siblings() -> None:
    for exc_class in SUBCLASSES:
        if exc_class is ScraperHTTPError:
            continue
        assert not issubclass(exc_class, ScraperHTTPError)
