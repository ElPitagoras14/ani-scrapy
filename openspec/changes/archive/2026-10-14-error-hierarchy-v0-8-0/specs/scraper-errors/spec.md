## Purpose

Defines how scrapers report failures so consumers can distinguish not-found, blocked, HTTP, timeout and parse errors without inspecting exception causes.

## ADDED Requirements

### Requirement: Flat exception hierarchy
The library SHALL expose `ScraperNotFoundError`, `ScraperBlockedError`, `ScraperHTTPError`, `ScraperTimeoutError` and `ScraperParseError`, each a direct subclass of `ScraperError`, importable from the top-level package.

#### Scenario: Siblings, not nested
- **WHEN** a consumer catches `ScraperHTTPError`
- **THEN** `ScraperNotFoundError`, `ScraperBlockedError`, `ScraperTimeoutError` and `ScraperParseError` are not caught by it

### Requirement: Optional status code
`ScraperError` SHALL accept an optional keyword-only `status_code` and expose it as an attribute that defaults to `None`.

#### Scenario: Existing construction still works
- **WHEN** an exception is created with only a message
- **THEN** `status_code` is `None`

#### Scenario: Status carried by HTTP errors
- **WHEN** an HTTP request fails with a status code
- **THEN** the raised exception's `status_code` equals that status

### Requirement: HTTP status mapping
The HTTP adapter SHALL map responses and failures to exceptions as follows: 404 and 410 to `ScraperNotFoundError`; 403 and 429 to `ScraperBlockedError`; any other error status and any connection error to `ScraperHTTPError`; a timeout to `ScraperTimeoutError`.

#### Scenario: Missing anime
- **WHEN** a request returns HTTP 404
- **THEN** `ScraperNotFoundError` is raised with `status_code` 404

#### Scenario: Blocked
- **WHEN** a request returns HTTP 429
- **THEN** `ScraperBlockedError` is raised with `status_code` 429

#### Scenario: Server error
- **WHEN** a request returns HTTP 503
- **THEN** `ScraperHTTPError` is raised with `status_code` 503 and it is not a `ScraperTimeoutError`

#### Scenario: Connection failure
- **WHEN** the connection fails without any HTTP response
- **THEN** `ScraperHTTPError` is raised with `status_code` `None`

#### Scenario: Timeout
- **WHEN** a request exceeds the configured timeout
- **THEN** `ScraperTimeoutError` is raised

### Requirement: JKAnime browser path status handling
When fetching anime info with episodes through the browser, JKAnime SHALL apply the same status mapping as the HTTP adapter to the navigation response.

#### Scenario: Missing anime in browser path
- **WHEN** navigating to the anime page returns HTTP 404
- **THEN** `ScraperNotFoundError` is raised instead of waiting for page elements to time out

#### Scenario: Successful navigation
- **WHEN** navigation returns a success status
- **THEN** anime info is parsed as before

### Requirement: AnimeAV1 fails on missing media data
AnimeAV1 SHALL raise `ScraperParseError` when the anime page contains no media data, with a message that includes the anime id and the likely causes (layout change, error page served with HTTP 200, or anti-bot challenge). It MUST NOT return an empty `AnimeInfo`.

#### Scenario: Page without media data
- **WHEN** parsing an HTML page that has no media data
- **THEN** `ScraperParseError` is raised and its message contains the anime id

#### Scenario: New episodes check
- **WHEN** `get_new_episodes` fetches a page without media data
- **THEN** `ScraperParseError` is raised
