## Purpose

Lets consumers bound how long the AnimeAV1 schedule data is reused so long-lived scraper instances do not serve stale next-episode dates.

## ADDED Requirements

### Requirement: Configurable schedule cache expiry
`AnimeAV1Scraper` SHALL accept `schedule_cache_ttl` as a number of seconds or `None`. With `None` (the default) the cached schedule never expires. With a number, a cached schedule older than that many seconds MUST be refetched.

#### Scenario: Default keeps current behavior
- **WHEN** the scraper is created without `schedule_cache_ttl` and the schedule is requested twice
- **THEN** the schedule page is fetched once

#### Scenario: Expired cache
- **WHEN** `schedule_cache_ttl` is set and more than that many seconds pass after the schedule was cached
- **THEN** the next request fetches the schedule page again

#### Scenario: Failed refresh
- **WHEN** refetching an expired schedule fails
- **THEN** the failure is logged and an empty schedule is used, as today
