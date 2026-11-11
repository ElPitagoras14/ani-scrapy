## Context

See proposal.md for motivation and `specs/supported-servers/spec.md` for requirements. Today each `providers/<site>/constants.py` defines `SUPPORTED_SERVERS` as a list. AnimeFLV and JKAnime scrapers import it to validate `get_file_download_link`; AnimeAV1 does not validate (it dispatches by server name). Live tests, `examples/03_download_links.py` and the usage skill import the per-provider lists. `ani_scrapy/__init__.py` exports no constants today. The AnimeAV1 list includes `MP4Upload` through the uncommitted `animeav1-mp4upload-v0-10-0` change.

## Goals / Non-Goals

**Goals:**
- One public object, readable at a glance, as the single source of truth.

**Non-Goals:**
- Changing the supported servers, or deriving them from the scrapers' dispatch code.

## Decisions

### D1 - One dict in `core/constants`, exported from `ani_scrapy`

New `core/constants/servers.py` holds `SUPPORTED_SERVERS: dict[str, list[str]]`, re-exported by `core/constants/__init__.py` and `ani_scrapy/__init__.py` (added to `__all__`). The usage skill already tells users to prefer top-level imports; this removes the one exception. Alternative: one dict per provider module (`{"animeav1": [...]}`). Rejected: it does not give the at-a-glance view.

### D2 - Remove the per-provider constants, no alias

Decided with the maintainer. Keeping aliases would leave two ways to read the same data and a risk of drift. The cost is a breaking change, accepted as a minor bump on 0.x with Before/After code in the changelog.

### D3 - Platform keys are lowercase provider names

`animeflv`, `jkanime`, `animeav1`: the provider package names and the prefix of anime ids (`animeav1:one-piece`), so consumers can index with an id prefix. Alternative: class names (`AnimeAV1Scraper`). Rejected: longer, and tied to the class rather than the platform.

### D4 - Plain `dict[str, list[str]]`, scrapers index their key

Lists stay lists, as the maintainer described. The AnimeFLV and JKAnime scrapers use `SUPPORTED_SERVERS["animeflv"]` / `["jkanime"]` inline; no helper. Alternative: `MappingProxyType` and tuples to prevent mutation. Rejected: over-engineering for a constants table.

### D5 - Ships in 0.10.0 with the MP4Upload change

Neither change is released yet, so both go out as 0.10.0 (the breaking change would otherwise need its own minor on 0.x). The version bump is owned by `animeav1-mp4upload-v0-10-0`; this change adds a `Breaking changes` item to the same 0.10.0 changelog entry and does not bump the version.

## Risks / Trade-offs

- [Downstream code importing the old constants breaks] → Breaking entry in the changelog with Before/After; ask before notifying consumers (per `ani-scrapy-dev`).
- [A platform key typo in a scraper raises `KeyError` at call time] → Unit test asserts the three keys and a scraper-level test exercises the validation path.
- [Merge order with `animeav1-mp4upload-v0-10-0`] → Both edit the AnimeAV1 constant; apply after that change is committed or archived so the `MP4Upload` value is carried over.

## Migration Plan

Consumers replace `from ani_scrapy.providers.<site>.constants import SUPPORTED_SERVERS` with `from ani_scrapy import SUPPORTED_SERVERS` and index the platform key. Rollback is reverting the release.
