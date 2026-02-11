# Documentation

This folder contains the official documentation for `ani-scrapy`.

## Contents

| Section | Path | Description |
|---------|------|-------------|
| User Guide | `docs/user_guide/` | Installation, quickstart, browser usage |
| API Reference | `docs/api_reference/` | Complete API documentation |
| Contributor Guide | `docs/contributor_guide/` | Contributing, adding scrapers, testing |
| Troubleshooting | `docs/troubleshooting/` | Common issues and solutions |

## Structure

```
docs/
├── user_guide/
│   ├── index.md               # Table of contents
│   ├── 01_getting_started.md # Installation
│   ├── 02_quickstart.md      # First scraping script
│   └── 03_browser_usage.md    # Browser configuration
├── api_reference/
│   ├── index.md              # Table of contents
│   ├── 01_architecture.md   # Core classes, modules, data flow
│   ├── 02_schemas.md         # Data models and types
│   ├── 03_scrapers.md        # Scraper methods
│   ├── 04_browser.md         # Browser configuration
│   └── 05_exceptions.md      # Exception handling
├── contributor_guide/
│   ├── index.md              # Table of contents
│   ├── 01_contributing.md    # Setup, code style, conventions
│   ├── 02_adding_scrapers.md # Adding new scrapers
│   └── 03_testing.md        # Testing guidelines
└── troubleshooting/
    └── 01_common_issues.md   # Known issues and solutions
```

## Quick Links

### New to ani-scrapy?

1. [Installation](../README.md#-installation) - Install the package
2. [Quickstart](./user_guide/02_quickstart.md) - Your first scraping script

### Looking for something specific?

- [API Reference Index](./api_reference/index.md)
- [Scraper Methods](./api_reference/03_scrapers.md)
- [Browser Setup](./api_reference/04_browser.md)
- [Exception Handling](./api_reference/05_exceptions.md)

### Want to contribute?

- [Contributing Guidelines](./contributor_guide/01_contributing.md)
- [Adding Scrapers](./contributor_guide/02_adding_scrapers.md)
- [Testing](./contributor_guide/03_testing.md)
