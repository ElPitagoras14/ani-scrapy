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
ani-scrapy doctor

✅ Environment
  - System Info: Python 3.11.0 (Windows) - 16GB RAM
✅ Playwright
  - Chromium: Installed
  - Browsers: Playwright ready
✅ Browsers
  - * Brave (Recommended): Detected: C:\Program Files\BraveSoftware\Brave-Browser\Applicationrave.exe
✅ Connectivity
  - jkanime.net: Reachable (HTTP 200)
  - animeav1.com: Reachable (HTTP 200)
✅ No issues found. Use Brave for better success rates!
```

**JSON (for CI/CD):**

```bash
ani-scrapy doctor --output json
```

Output example:

```json
{
  "timestamp": "2026-11-10T22:50:02.383228",
  "environment": {
    "python_version": "3.11.0",
    "platform": "Windows",
    "architecture": "AMD64",
    "timestamp": "2026-11-10T22:50:02.383241"
  },
  "results": [
    {
      "category": "Playwright",
      "name": "Chromium",
      "status": "pass",
      "message": "Installed",
      "details": {"browser": "chromium"}
    },
    {
      "category": "Connectivity",
      "name": "jkanime.net",
      "status": "pass",
      "message": "Reachable (HTTP 200)",
      "details": {"url": "https://jkanime.net", "status_code": 200}
    },
    {
      "category": "Connectivity",
      "name": "animeav1.com",
      "status": "pass",
      "message": "Reachable (HTTP 200)",
      "details": {"url": "https://animeav1.com", "status_code": 200}
    }
  ],
  "exit_code": 0,
  "summary": "No issues found. Use Brave for better success rates!"
}
```

#### Exit Codes

| Code | Meaning           |
| ---- | ----------------- |
| 0    | All checks passed |
| 1    | Warnings found    |
| 2    | Errors found      |

#### Checks Performed

- **Python version**: Reports the Python version
- **Platform**: Detects OS (Windows/Linux/macOS)
- **Playwright**: Checks if Playwright and Chromium are installed
- **Custom browser**: Looks for Brave browser (recommended for ad-block)
- **Site connectivity**: Tests reachability to supported providers

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
