# Changelog

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
