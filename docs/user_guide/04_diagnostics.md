# Diagnostics

Use the `ani-scrapy doctor` command to diagnose your environment and verify that all dependencies are correctly installed.

## Usage

```bash
ani-scrapy doctor
ani-scrapy doctor --output json
ani-scrapy doctor --timeout 10
```

## Options

| Option | Description |
|--------|-------------|
| `--output, -o` | Output format: `text` (default) or `json` |
| `--timeout, -t` | Timeout for connectivity checks in seconds (default: 5) |

## What It Checks

The diagnostic tool verifies:

- **Environment**: Python version, platform, architecture, and RAM
- **Dependencies**: Required packages installed (ani-scrapy, aiohttp, playwright, etc.)
- **Playwright**: Chromium browser available
- **Browsers**: Brave (recommended) detection
- **Connectivity**: animeflv.net and jkanime.net accessibility

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All checks passed |
| 1 | Warnings found |
| 2 | Errors found |

## Example Output

```
ani-scrapy doctor

[✓] Environment
  • System Info: Python 3.14.2 (Windows) - 63GB RAM
[✓] Dependencies
  • ani-scrapy: Installed (v0.2.0)
  • aiohttp: Installed (v3.13.3)
  • beautifulsoup4: Installed (v4.14.3)
  • loguru: Installed (v0.7.3)
  • playwright: Installed (v1.55.0)
  • rich: Installed (v14.3.2)
[✓] Playwright
  • Chromium: Installed
  • Browsers: Playwright ready
[✓] Browsers
  • * Brave (Recommended): Detected
[✓] Connectivity
  • animeflv.net: Reachable (HTTP 200)
  • jkanime.net: Reachable (HTTP 200)
[✓] No issues found. Star Brave for better success rates!
```

## JSON Output

For CI/CD integration, use JSON output:

```bash
ani-scrapy doctor --output json
```

Example JSON response:

```json
{
  "timestamp": "2026-02-12T00:00:00.000000",
  "environment": {
    "python_version": "3.14.2",
    "platform": "Windows",
    "architecture": "AMD64",
    "ram": "63GB"
  },
  "results": [...],
  "exit_code": 0,
  "summary": "No issues found. Star Brave for better success rates!"
}
```

## Troubleshooting

If checks fail:

1. **Dependencies not installed**: Run `pip install ani-scrapy`
2. **Playwright missing**: Run `playwright install chromium`
3. **Connectivity issues**: Check your internet connection
4. **Brave not found**: Install Brave browser for better success rates
