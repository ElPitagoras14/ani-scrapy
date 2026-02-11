# Common Issues

## Playwright Not Installed

```bash
playwright install chromium
```

## Tests Are Trying to Use Network

Prefer writing tests using `MockHttp` and HTML fixtures in `tests/fixtures/html/`.
