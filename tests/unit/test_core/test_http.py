from __future__ import annotations

import pytest
from ani_scrapy.core.http import AsyncHttpAdapter, BaseHttpAdapter


@pytest.mark.asyncio
async def test_async_http_adapter_records_calls() -> None:
    http = AsyncHttpAdapter(base_url="https://example.com")
    http.register_response = pytest.fail  # Not available in real adapter
