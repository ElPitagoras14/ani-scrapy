# CLI Commands

ani-scrapy provides a command-line interface for diagnostics and troubleshooting.

## Installation

The CLI is automatically installed with the package:

```bash
pip install ani-scrapy
```

## Commands

### doctor

Run diagnostic checks to verify your environment is properly configured.

```bash
ani-scrapy doctor
```

#### Options

| Option       | Alias | Description                                    | Default |
|--------------|-------|------------------------------------------------|---------|
| `--output`   | `-o`  | Output format: `text` or `json`               | `text`  |
| `--timeout`  | `-t`  | Timeout for connectivity checks in seconds    | `5`     |

#### Output Formats

**Text (default):**

```bash
ani-scrapy doctor
```

Output example:

```
ani-scrapy Doctor Report
========================

[✓] Python version: 3.11.0
[✓] Platform: Windows
[✓] Playwright installed: chromium
[✓] Brave browser found: C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe
[✓] AnimeFLV: Reachable
[✓] JKAnime: Reachable
[✓] AnimeAV1: Reachable

Result: All checks passed (exit code 0)
```

**JSON (for CI/CD):**

```bash
ani-scrapy doctor --output json
```

Output example:

```json
{
  "python_version": "3.11.0",
  "platform": "Windows",
  "playwright": {
    "installed": true,
    "browser": "chromium"
  },
  "custom_browser": {
    "found": true,
    "path": "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
  },
  "sites": {
    "animeflv": {"reachable": true, "latency_ms": 142},
    "jkanime": {"reachable": true, "latency_ms": 89},
    "animeav1": {"reachable": true, "latency_ms": 201}
  },
  "result": "All checks passed",
  "exit_code": 0
}
```

#### Exit Codes

| Code | Meaning           |
| ---- | ----------------- |
| 0    | All checks passed |
| 1    | Warnings found    |
| 2    | Errors found      |

#### Checks Performed

- **Python version**: Verifies Python >= 3.10.14
- **Platform**: Detects OS (Windows/Linux/macOS)
- **Playwright**: Checks if Playwright and Chromium are installed
- **Custom browser**: Looks for Brave browser (recommended for ad-block)
- **Site connectivity**: Tests reachability to supported providers
- **Latency**: Measures response time for each site

## CI/CD Integration

Use JSON output to integrate with CI pipelines:

```yaml
# Example GitHub Actions
- name: Run ani-scrapy doctor
  run: ani-scrapy doctor --output json --timeout 10
```

## Troubleshooting

If doctor reports issues:

1. **Playwright not installed**: Run `playwright install chromium`
2. **Sites unreachable**: Check your network connection
3. **High latency**: Consider increasing timeout with `--timeout 15`
