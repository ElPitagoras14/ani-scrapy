# Changelog

While the library is on 0.x, breaking changes bump the minor version and fixes bump the patch version. Releases before 0.8.0 are listed in [GitHub Releases](https://github.com/ElPitagoras14/ani-scrapy/releases).

## 0.10.0

### Breaking changes

- **`SUPPORTED_SERVERS` is now one dict keyed by platform.** The per-provider constants in `ani_scrapy.providers.<site>.constants` are removed; importing them raises `ImportError`. The dict is exported from `ani_scrapy` and has the keys `animeflv`, `jkanime` and `animeav1`.

  Before:

  ```python
  from ani_scrapy.providers.jkanime.constants import SUPPORTED_SERVERS as JKANIME_SUPPORTED_SERVERS

  valid = [l for l in links.download_links if l.server in JKANIME_SUPPORTED_SERVERS]
  ```

  After:

  ```python
  from ani_scrapy import SUPPORTED_SERVERS

  valid = [l for l in links.download_links if l.server in SUPPORTED_SERVERS["jkanime"]]
  ```

### Added

- **AnimeAV1 resolves MP4Upload.** `get_file_download_link` now returns a direct `.mp4` URL for the `MP4Upload` links from `get_table_download_links`, over HTTP only (no browser). `MP4Upload` is now in AnimeAV1's `SUPPORTED_SERVERS`, so AnimeAV1 episodes can be downloaded again (part of #30; UPNShare is still not working).
  - Iframe MP4Upload links (`embed-<id>.html`) are not resolved and return `None`.
  - Downloading the returned URL needs the `Referer` header, otherwise the host answers 403. Resolve right before downloading:

    ```python
    links = await scraper.get_table_download_links("black-clover", 1)
    link = next(l for l in links.download_links if l.server == "MP4Upload")
    url = await scraper.get_file_download_link(link)
    headers = {"Referer": "https://www.mp4upload.com/"}
    ```

## 0.9.1

No changes to the library. This release only updates the project's CI and release tooling.

## 0.9.0

### Breaking changes

- **Python 3.11 or newer is required.** Python 3.10 reached end of life, so `requires-python` is now `>=3.11`. If you are on Python 3.10, pip keeps installing 0.8.x.

### Changed

- Package metadata is complete: SPDX license, Python 3.11 to 3.14 classifiers, development status, `Typing :: Typed` (the package ships `py.typed`) and Changelog, Issues and Documentation links on PyPI.
- The `examples` extra only installs `tabulate`.

## 0.8.1

### Fixed

- **AnimeAV1 returns complete relations, genres and episodes.** The parser used fixed-size windows over the page data, so large franchises lost entries (for example `one-piece` returned 5 of 29 relations, `naruto-shippuuden` 5 of 14, and `psyren` 5 of 9 genres). The whole media object is now read structurally, so any number of entries is returned.
- **AnimeAV1 titles with quotes are no longer cut.** A title such as `Kashita Maryoku wa "Revo Barai" de Kyousei Choushuu` used to end at the first escaped quote (`Kashita Maryoku wa \`). The same applies to related anime titles.
- **AnimeAV1 synopses have real line breaks.** Line breaks used to appear as the literal characters `\n`; they are now real newlines. If your code removed or replaced those literal `\n` sequences, you can drop that step.
- **AnimeAV1 raises `ScraperParseError` when the media data cannot be read** (the message includes the anime id) instead of returning partial data.

The API is unchanged; consumers receive more and better data. Expect more relations and genres for large franchises and different text in synopses.

## 0.8.0

### Breaking changes

- **HTTP failures are no longer `ScraperTimeoutError`.** Error statuses (5xx, other 4xx) and connection failures now raise `ScraperHTTPError`. `ScraperTimeoutError` is only raised for real timeouts.

  Before:

  ```python
  try:
      info = await scraper.get_anime_info(anime_id)
  except ScraperTimeoutError:
      ...  # also caught 5xx and connection errors
  ```

  After:

  ```python
  try:
      info = await scraper.get_anime_info(anime_id)
  except (ScraperTimeoutError, ScraperHTTPError):
      ...
  ```

- **AnimeAV1 raises `ScraperParseError` instead of returning an empty `AnimeInfo`** when the page has no media data (layout change, error page served with HTTP 200, anti-bot challenge). This also affects `get_new_episodes`.

  Before:

  ```python
  info = await scraper.get_anime_info(anime_id)
  if not info.title:
      ...  # empty result
  ```

  After:

  ```python
  try:
      info = await scraper.get_anime_info(anime_id)
  except ScraperParseError:
      ...
  ```

### Added

- `ScraperNotFoundError` for HTTP 404/410.
- `ScraperHTTPError` for other HTTP error statuses and connection failures.
- `status_code` attribute (`int | None`) on every `ScraperError`, set when the error comes from an HTTP response.
- JKAnime `get_anime_info(include_episodes=True)` now maps the navigation status (404/410 to `ScraperNotFoundError`, 403/429 to `ScraperBlockedError`, other errors to `ScraperHTTPError`) instead of timing out waiting for page elements.
- `AnimeAV1Scraper(schedule_cache_ttl=...)`: seconds the `/horario` schedule is cached. The default `None` keeps the previous behavior (never expires).

### Deprecated

- `AnimeFLVScraper`: AnimeFLV moved to `https://animeflv.or.at/` with a different HTML structure and the provider no longer works. It emits a `DeprecationWarning` on creation and is not removed yet.

### Changed

- `ani-scrapy doctor` no longer checks connectivity to AnimeFLV.

### Exception hierarchy

```
ScraperError
├── ScraperNotFoundError   (404, 410)
├── ScraperBlockedError    (403, 429)
├── ScraperHTTPError       (other HTTP errors, connection failures)
├── ScraperTimeoutError    (timeouts)
└── ScraperParseError      (unexpected HTML or missing data)
```
