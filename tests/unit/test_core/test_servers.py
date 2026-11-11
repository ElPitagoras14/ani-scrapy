from __future__ import annotations

import ani_scrapy
from ani_scrapy.core import constants


def test_supported_servers_is_exported_and_keyed_by_platform() -> None:
    assert ani_scrapy.SUPPORTED_SERVERS is constants.SUPPORTED_SERVERS
    assert set(ani_scrapy.SUPPORTED_SERVERS) == {"animeflv", "jkanime", "animeav1"}
    assert "MP4Upload" in ani_scrapy.SUPPORTED_SERVERS["animeav1"]
