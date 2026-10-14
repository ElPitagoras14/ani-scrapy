## Purpose

Defines that the data read from an AnimeAV1 anime page is complete and correctly decoded, so consumers do not store truncated lists or malformed text as valid.

## Requirements

### Requirement: Complete relations
AnimeAV1 SHALL report every related anime listed on the page, in page order, regardless of how many there are.

#### Scenario: Many relations
- **WHEN** a page lists 29 related animes
- **THEN** all 29 are reported

#### Scenario: Few relations
- **WHEN** a page lists 2 related animes
- **THEN** exactly those 2 are reported

### Requirement: Complete genres
AnimeAV1 SHALL report every genre listed on the page, regardless of how many there are.

#### Scenario: Many genres
- **WHEN** a page lists 9 genres
- **THEN** all 9 are reported

### Requirement: Complete episode list
AnimeAV1 SHALL report every episode listed on the page, regardless of how many there are, when episodes are requested.

#### Scenario: Very long series
- **WHEN** a page lists 3000 episodes and episodes are requested
- **THEN** all 3000 are reported

#### Scenario: Episodes not requested
- **WHEN** episodes are not requested
- **THEN** no episodes are reported

### Requirement: Correct text decoding
AnimeAV1 SHALL report titles and synopses as the text the site shows: escaped quotes are kept as quotes, and escaped line breaks become real line breaks.

#### Scenario: Quotes in a title
- **WHEN** an anime title contains double quotes
- **THEN** the reported title contains the quotes and is not cut at the first one

#### Scenario: Quotes in a related anime title
- **WHEN** a related anime title contains double quotes
- **THEN** the reported related title contains the quotes and is not cut

#### Scenario: Line breaks in a synopsis
- **WHEN** a synopsis contains line breaks
- **THEN** the reported synopsis contains real line breaks and no literal backslash-n sequences

#### Scenario: Structural characters inside text
- **WHEN** a title or synopsis contains braces, brackets, commas or colons
- **THEN** the surrounding data is still read completely and correctly

### Requirement: Unreadable media data
AnimeAV1 SHALL raise a parse error, naming the anime, when the media data is present but cannot be read, and MUST NOT return partial data.

#### Scenario: Corrupted media data
- **WHEN** a page's media data is malformed
- **THEN** a parse error is raised and its message contains the anime id
