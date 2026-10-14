## 1. Exceptions and HTTP adapter

- [x] 1.1 In `core/exceptions.py` add `status_code` to `ScraperError` and the new `ScraperNotFoundError` and `ScraperHTTPError`; export them from `core/__init__.py` and `ani_scrapy/__init__.py`. Verify with a test that all five are direct subclasses of `ScraperError`, importable from `ani_scrapy`, and that `status_code` defaults to `None`.
- [x] 1.2 In `core/http.py` add the shared status-to-exception function and use it in `_request`; map connection errors to `ScraperHTTPError` and keep `ScraperTimeoutError` only for timeouts. Verify with adapter tests for 404, 410, 403, 429, 503, a connection error and a timeout, checking exception type and `status_code`.
- [x] 1.3 Add `aioresponses` to the dev dependency group (edit `pyproject.toml` only here for the dependency; version bump is done in task 6.3) and verify `uv sync` and the new adapter tests run with `.venv`.

## 2. AnimeAV1

- [x] 2.1 Make `AnimeAV1Parser.parse_anime_info` raise `ScraperParseError` with the anime id and likely causes when media data is missing. Verify with a parser test using minimal HTML without media data (message contains the id) and one with minimal valid media data that still parses.
- [x] 2.2 Verify `get_new_episodes` and `get_anime_info` propagate the error with a test that mocks `http.get` to return a page without media data.
- [x] 2.3 Add `schedule_cache_ttl` to `AnimeAV1Scraper` and apply it in `_get_schedule`. Verify with tests for default `None` (one fetch for two calls), expired cache (second fetch) and failed refresh (empty schedule, no exception).

## 3. JKAnime browser path

- [x] 3.1 In `_get_anime_info_with_episodes` apply the shared status mapping to the `page.goto` response (a `None` response continues as today). Verify with tests using a fake page whose `goto` returns responses with status 404, 429, 500 and 200, and one returning `None`.

## 4. AnimeFLV deprecation

- [x] 4.1 Emit `DeprecationWarning` from `AnimeFLVScraper.__init__` mentioning `animeflv.or.at`. Verify with a test using `pytest.warns(DeprecationWarning)` that also confirms the scraper is created and its parser is unchanged.
- [x] 4.2 Remove the `animeflv.net` entry from `CONNECTIVITY_SITES` in `cli/doctor.py`; verify with a test that the doctor connectivity targets contain only `jkanime.net` and `animeav1.com`, and that `ani-scrapy doctor --help` still works.
- [x] 4.3 Leave the existing FLV parser tests and fixtures unchanged; verify the existing test suite still passes.

## 5. Documentation

- [x] 5.1 Update `docs/04-error-handling.md` with the new hierarchy, `status_code` and the HTTP mapping table; verify it lists all five exceptions.
- [x] 5.2 Mark AnimeFLV as deprecated (with the domain move) in `README.md` and `.agents/skills/ani-scrapy/SKILL.md`, and document the new exceptions and `schedule_cache_ttl` in the skill; verify by grepping both files for the deprecation note.
- [x] 5.3 Create `CHANGELOG.md` with a 0.8.0 entry and migration notes for the two breaking changes; verify both breaking items are labeled and have a before/after example.

## 6. Release prep

- [x] 6.1 Run the full test suite with `.venv` and `ruff check`; verify everything passes.
- [x] 6.2 Run `openspec validate error-hierarchy-v0-8-0` and verify it reports no errors.
- [x] 6.3 Bump `version` to 0.8.0 in `pyproject.toml` (last commit, only when asked to commit) and verify `uv lock` is consistent. Publishing to PyPI and notifying "orquestador" happen only after the user asks for them.
