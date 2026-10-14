## Context

See proposal.md for motivation. Current state observed in the code:

- `core/exceptions.py` has four exceptions with no attributes. `AsyncHttpAdapter._request` (`core/http.py`) raises `ScraperBlockedError` for 403/429 and wraps every other `aiohttp.ClientError` (including `ClientResponseError` from `raise_for_status`) as `ScraperTimeoutError`.
- `AnimeAV1Parser.parse_anime_info` returns an empty `AnimeInfo` when `_extract_media_data` returns `None`. JKAnime already raises `ScraperParseError` when its info container is missing.
- JKAnime `get_anime_info(include_episodes=True)` navigates with Playwright (`page.goto(..., wait_until="domcontentloaded")`, ignoring the response) and then waits for `div.col-lg-2.picd`, so a 404 only shows up as a Playwright timeout.
- `AnimeAV1Scraper._schedule_cache` is a plain dict that is reused whenever non-empty.
- The test suite only has parser tests for AnimeFLV and JKAnime and schema tests; `pytest.ini` declares an `asyncio` marker but no async plugin is installed.
- `docs/04-error-handling.md`, `README.md` and `.agents/skills/ani-scrapy/SKILL.md` describe the current behavior.

## Goals / Non-Goals

**Goals:**
- A flat, predictable exception hierarchy that maps one-to-one to aniseek's HTTP mapping (404 / 429 / 502).
- One place that translates HTTP status codes to exceptions, shared by the adapter and the JKAnime browser path.
- No silent empty results from AnimeAV1.

**Non-Goals:**
- No changes to AnimeFLV parsing or selectors, and no removal of the provider.
- No `D'` (empty-result error) for AnimeFLV.
- No retries or backoff.
- No change to JKAnime or AnimeAV1 search behavior (empty search results stay valid).

## Decisions

### D1 - Flat hierarchy with `status_code` on the base class

`ScraperError.__init__(self, message: str = "", *, status_code: int | None = None)`. Every subclass inherits it, so `exc.status_code` is always safe to read.

Alternative: make `ScraperHTTPError` the parent of NotFound/Blocked. Rejected: it changes `ScraperBlockedError`'s position in the tree and aniseek wants plain siblings.

### D2 - Status mapping lives in `core/http.py` as a small function

`raise_for_status_code(status, url)` is used by `_request` and by the JKAnime goto check. Mapping: 404/410 → NotFound; 403/429 → Blocked; any other status ≥ 400 → HTTPError.

Alternative: duplicate the mapping in JKAnime. Rejected: two copies would drift.

### D3 - `_request` stops relying on `raise_for_status`

It checks `response.status` itself. `aiohttp.ClientResponseError` is still handled defensively (using `e.status`), other `aiohttp.ClientError` (connection, DNS) become `ScraperHTTPError(status_code=None)`, and only `asyncio.TimeoutError` becomes `ScraperTimeoutError`. The original exception stays chained via `from e`.

### D4 - JKAnime goto status check

Capture the `Response` returned by `page.goto`. If it is not `None`, apply the shared mapping before waiting for selectors. `None` (no response, e.g. same-document navigation) is treated as success and falls through to the existing selector wait. Only the `include_episodes=True` path is touched; the HTTP path already goes through the adapter.

### D5 - AnimeAV1 parse error

`parse_anime_info` raises `ScraperParseError(f"No media data found for anime '{anime_id}'; possible layout change, error page served with HTTP 200 or anti-bot challenge")`. No change to the scraper beyond inheriting the raise. `get_anime_info` has no special handling, so the error propagates.

### D6 - Schedule TTL only in AnimeAV1

`AnimeAV1Scraper.__init__` gains `schedule_cache_ttl: float | None = None`, stored with a `time.monotonic()` timestamp when the cache is filled. `_get_schedule` reuses the cache only if it is non-empty and either `ttl is None` or the age is below `ttl`. The existing `except Exception` that returns `{}` stays as is.

Alternative: a default TTL such as 1 hour. Rejected for now: the default keeps today's behavior, as confirmed by the aniseek side.

### D7 - FLV deprecation via `warnings.warn`

`AnimeFLVScraper.__init__` calls `warnings.warn(..., DeprecationWarning, stacklevel=2)`, with a message naming `animeflv.or.at`. Python hides `DeprecationWarning` by default outside `__main__`; that is acceptable and standard.

Alternative: also log with loguru. Rejected: the library only logs, never configures, and a log line adds little over the warning.

### D8 - Remove FLV from `doctor`; keep its tests as legacy

Remove the `animeflv.net` entry from `CONNECTIVITY_SITES` in `cli/doctor.py`, since the provider is no longer supported and a connectivity check against the old domain says nothing useful. Keep the existing FLV parser tests and fixtures unchanged: they describe the old site and are not evidence that the provider works today. Revisit them in the release that removes the provider.

### D9 - HTTP mocking in tests

Add `aioresponses` to the dev dependency group and run async code from sync tests with `asyncio.run`, avoiding a second new plugin.

Alternative: `pytest-asyncio`. Rejected: one dependency is enough and the existing `asyncio` marker is unused.

### D10 - Changelog and error-handling docs

No changelog exists, so create `CHANGELOG.md` with a 0.8.0 entry and a migration section. Also update `docs/04-error-handling.md`.

## Risks / Trade-offs

- [Consumers catching `ScraperTimeoutError` for 5xx stop catching them] → documented as **BREAKING** with migration notes; the type is now accurate.
- [AnimeAV1 pages that legitimately lack media data now raise] → intended; message carries the anime id so callers can log and skip.
- [A 403 caused by a Cloudflare challenge still maps to Blocked] → unchanged from today.
- [`DeprecationWarning` is invisible by default] → the README and skill also state the deprecation; tests assert the warning explicitly.
- [Playwright `goto` returns `None` for some navigations] → treated as success so behavior matches today.
- [The FLV tests and fixtures still describe the old site] → accepted, tracked for the removal release.

## Migration Plan

1. Land the exception and adapter changes first, then AnimeAV1, JKAnime, schedule TTL, FLV deprecation, docs and tests.
2. Bump `pyproject.toml` to 0.8.0 in the last commit, per project convention.
3. Consumers: replace `except ScraperTimeoutError` used for HTTP failures with `ScraperHTTPError` (or `ScraperError`); handle `ScraperParseError` from AnimeAV1 instead of checking for empty titles. aniseek maps NotFound → 404, Blocked → 429, everything else → 502.
4. Rollback: revert the release; consumers pinned to 0.7.x keep the old behavior.
