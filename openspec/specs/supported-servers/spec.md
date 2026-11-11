## Purpose

Lets consumers see at a glance which download servers each platform can resolve to a file URL, from one public object, and filter links accordingly.

## Requirements

### Requirement: Supported servers keyed by platform
The library SHALL expose `SUPPORTED_SERVERS`, a mapping from platform key to the list of server names that platform's `get_file_download_link` can resolve. The keys SHALL be `animeflv`, `jkanime` and `animeav1`. The object SHALL be importable from `ani_scrapy` and from `ani_scrapy.core.constants`.

#### Scenario: Read one platform
- **WHEN** a consumer reads `SUPPORTED_SERVERS["animeav1"]`
- **THEN** it gets the server names AnimeAV1 resolves, including `MP4Upload`

#### Scenario: Filter links
- **WHEN** a consumer keeps only links whose `server` is in `SUPPORTED_SERVERS["jkanime"]`
- **THEN** every kept link is one JKAnime can resolve

#### Scenario: All platforms present
- **WHEN** a consumer lists the keys of `SUPPORTED_SERVERS`
- **THEN** they are exactly `animeflv`, `jkanime` and `animeav1`

### Requirement: No per-provider supported servers constant
The per-provider modules `ani_scrapy.providers.<site>.constants` SHALL NOT define `SUPPORTED_SERVERS`.

#### Scenario: Old import
- **WHEN** code runs `from ani_scrapy.providers.jkanime.constants import SUPPORTED_SERVERS`
- **THEN** an `ImportError` is raised

### Requirement: Server validation uses the platform entry
The AnimeFLV and JKAnime scrapers SHALL reject, with `None` and an error log, any server not in their platform's entry, as before.

#### Scenario: Unsupported server
- **WHEN** JKAnime's `get_file_download_link` receives a link whose server is not in `SUPPORTED_SERVERS["jkanime"]`
- **THEN** `None` is returned and the supported servers are logged
