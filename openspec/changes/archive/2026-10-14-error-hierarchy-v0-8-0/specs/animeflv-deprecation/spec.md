## Purpose

Signals that the AnimeFLV provider no longer works after the site moved to a new domain and HTML structure, without removing it yet.

## ADDED Requirements

### Requirement: Deprecation warning on instantiation
Creating an `AnimeFLVScraper` SHALL emit a `DeprecationWarning` stating that the provider is deprecated and that the site moved to `animeflv.or.at` with a different structure.

#### Scenario: Warning emitted
- **WHEN** an `AnimeFLVScraper` is instantiated
- **THEN** a `DeprecationWarning` is emitted that mentions `animeflv.or.at`

### Requirement: Provider remains available
The AnimeFLV provider SHALL remain importable and instantiable in this version, and its parsing behavior MUST NOT change.

#### Scenario: Still importable
- **WHEN** a consumer imports and instantiates `AnimeFLVScraper`
- **THEN** it is created successfully, only with the warning

### Requirement: Excluded from diagnostics
The `ani-scrapy doctor` command SHALL NOT check connectivity to AnimeFLV.

#### Scenario: Doctor skips AnimeFLV
- **WHEN** `ani-scrapy doctor` runs its connectivity checks
- **THEN** no result is reported for AnimeFLV and the other providers are still checked

### Requirement: Deprecation documented
The README and the agent skill SHALL state that AnimeFLV is deprecated and why.

#### Scenario: Docs mention it
- **WHEN** a reader checks the provider list in the README or the skill
- **THEN** AnimeFLV is marked deprecated with the reason
