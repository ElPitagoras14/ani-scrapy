## Why

Consumers cannot distinguish failure causes: a 404 or a 5xx surfaces as `ScraperTimeoutError`, and AnimeAV1 returns an empty `AnimeInfo` when the page has no media data. aniseek persists that empty result as valid, silently corrupting its data. aniseek needs a precise error hierarchy to map outcomes to HTTP codes (not found → 404, blocked → 429, everything else → 502). AnimeFLV also moved to `animeflv.or.at` with a different HTML structure, so its provider no longer works and must be flagged.

## What Changes

- Add `ScraperNotFoundError` (HTTP 404/410) and `ScraperHTTPError` (5xx, other 4xx, connection errors) as flat siblings of `ScraperTimeoutError`, `ScraperParseError` and `ScraperBlockedError`.
- `ScraperError` accepts an optional keyword-only `status_code: int | None`; the HTTP-related errors carry it.
- **BREAKING**: non-timeout HTTP failures (5xx, connection errors) are no longer raised as `ScraperTimeoutError`; `ScraperTimeoutError` is reserved for real timeouts.
- **BREAKING**: `AnimeAV1Parser.parse_anime_info` raises `ScraperParseError` instead of returning an empty `AnimeInfo` when media data is missing. `AnimeAV1Scraper.get_new_episodes` inherits this.
- JKAnime `get_anime_info(include_episodes=True)` (Playwright path) checks the `page.goto` status and raises `ScraperNotFoundError` / `ScraperHTTPError` / `ScraperBlockedError` consistently with the HTTP adapter.
- `AnimeAV1Scraper` accepts `schedule_cache_ttl: float | None` (default `None`, current behavior: never expires).
- Deprecate AnimeFLV: emit `DeprecationWarning` on `AnimeFLVScraper` instantiation (mentions the move to `animeflv.or.at`), document it in README and the agent skill, and remove it from the `ani-scrapy doctor` connectivity checks. Not removed in this version; no parser changes.
- Add tests for the HTTP adapter, the AnimeAV1 parser and the JKAnime goto path.
- Bump version to 0.8.0 with a changelog and migration notes for the two breaking changes.

## Capabilities

### New Capabilities
- `scraper-errors`: exception hierarchy, `status_code`, HTTP status mapping in the adapter and the JKAnime browser path, and parse failure on missing AnimeAV1 media data.
- `animeav1-schedule-cache`: optional expiry of the AnimeAV1 schedule cache.
- `animeflv-deprecation`: deprecation signalling for the AnimeFLV provider.

### Modified Capabilities

(none; `openspec/specs/` is empty)

## Impact

- Code: `core/exceptions.py`, `core/http.py`, `core/__init__.py`, `ani_scrapy/__init__.py`, `providers/animeav1/parser.py`, `providers/animeav1/scraper.py`, `providers/jkanime/scraper.py`, `providers/animeflv/scraper.py`, `cli/doctor.py`.
- Docs: `README.md`, `.agents/skills/ani-scrapy/SKILL.md`, new `CHANGELOG.md`.
- Tests: new unit tests; dev dependency for mocking HTTP (`aioresponses`) in `pyproject.toml`.
- Consumers: code catching `ScraperTimeoutError` for 5xx, or relying on an empty `AnimeInfo` from AnimeAV1, must be updated. aniseek backend upgrades to 0.8.0; its worker stays on 0.6.2 for now.
