## Purpose

Defines how AnimeAV1 turns a download link from an episode page into a direct file URL that consumers can download, and which servers it supports.

## ADDED Requirements

### Requirement: MP4Upload table links resolve to a direct file
AnimeAV1 SHALL list `MP4Upload` in its supported servers. Resolving a link whose server is `MP4Upload` and whose URL has the table form `https://www.mp4upload.com/<file_id>` SHALL return a direct HTTPS URL to the video file, without opening a browser and without waiting for the page's countdown.

#### Scenario: Table link resolves
- **WHEN** the MP4Upload table link of an episode is resolved and the file exists on MP4Upload
- **THEN** a direct `https://` URL to the video file is returned

#### Scenario: No browser needed
- **WHEN** an MP4Upload table link is resolved
- **THEN** no browser is started

#### Scenario: Supported servers
- **WHEN** a consumer reads AnimeAV1's supported servers
- **THEN** the list contains `MP4Upload`

### Requirement: MP4Upload iframe links are not resolved
Resolving an `MP4Upload` link whose URL is not in the table form, such as the iframe form `https://www.mp4upload.com/embed-<file_id>.html`, SHALL return `None` and log a warning, without any network request.

#### Scenario: Iframe link
- **WHEN** an MP4Upload link with URL `https://www.mp4upload.com/embed-<file_id>.html` is resolved
- **THEN** `None` is returned and a warning is logged

### Requirement: MP4Upload missing files and failures
When MP4Upload does not provide a file URL for a table link (for example, the file was deleted), resolving it SHALL return `None` and log a warning. HTTP failures while resolving SHALL raise the scraper exception given by the HTTP status mapping.

#### Scenario: Deleted file
- **WHEN** the MP4Upload table link points to a file that no longer exists
- **THEN** `None` is returned and a warning is logged

#### Scenario: Blocked request
- **WHEN** MP4Upload answers the resolution request with HTTP 403
- **THEN** `ScraperBlockedError` is raised

### Requirement: MP4Upload download Referer is documented
The library documentation and usage skill SHALL state that downloading an MP4Upload file URL requires the header `Referer: https://www.mp4upload.com/`.

#### Scenario: Consumer reads the docs
- **WHEN** a consumer reads the supported servers section of the docs or the usage skill
- **THEN** it states the `Referer` header needed to download MP4Upload file URLs
