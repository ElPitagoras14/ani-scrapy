# Browser Classes

## AsyncBrowser

Asynchronous browser context manager for JavaScript-rendered content.

### Constructor

```python
class AsyncBrowser:
    def __init__(
        self,
        headless: bool = True,
        executable_path: str | None = None,
        args: list[str] | None = None
    ) -> None
```

**Parameters:**

- `headless`: Run in headless mode (default: `True`)
- `executable_path`: Custom browser path (e.g., path to Chrome/Chromium/Brave executable)
- `args`: Additional browser arguments (list of strings)

### Methods

- `new_page() -> Page`: Creates a new browser page
- `context: BrowserContext`: Playwright browser context (for advanced usage)

### Usage

```python
from ani_scrapy import AsyncBrowser

async with AsyncBrowser(headless=False) as browser:
    page = await browser.new_page()
    await page.goto("https://example.com")
```

---

## Custom Browser Configuration

You can configure a custom browser executable path. Brave is recommended because its native ad-blocker reduces blocking on sites with excessive advertisements, but any Chromium-based browser (Chrome, Chromium, Edge) will work.

### Brave Browser (Recommended)

```python
from ani_scrapy import AsyncBrowser

brave_path = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"

async with AsyncBrowser(
    headless=True,
    executable_path=brave_path,
) as browser:
    page = await browser.new_page()
    # Your scraping code here
```

### Path Examples

```python
# Brave (Recommended)
brave_path = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"

# Chrome
chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"

# Chromium
chromium_path = "C:/Program Files/Chromium/Application/chrome.exe"

# Linux
brave_path = "/usr/bin/brave"

# macOS
brave_path = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
```

### Additional Browser Arguments

```python
from ani_scrapy import AsyncBrowser

async with AsyncBrowser(
    headless=True,
    args=["--disable-blink-features=Automation", "--window-size=1920,1080"]
) as browser:
    page = await browser.new_page()
    await page.goto("https://example.com")
```
