"""ani-scrapy doctor - Diagnostic tool for ani-scrapy."""

import asyncio
import platform
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import aiohttp
from rich import print as rprint

# Force UTF-8 for Windows
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace"
    )
    sys.stderr = io.TextIOWrapper(
        sys.stderr.buffer, encoding="utf-8", errors="replace"
    )

try:
    import playwright

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


@dataclass
class DiagnosticResult:
    """Result of a diagnostic check."""

    category: str
    name: str
    status: str  # "pass", "warn", "fail"
    message: str = ""
    details: Dict = field(default_factory=dict)


@dataclass
class DoctorReport:
    """Complete doctor report."""

    timestamp: str
    environment: Dict
    results: List[DiagnosticResult]
    exit_code: int
    summary: str

    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "environment": self.environment,
            "results": [
                {
                    "category": r.category,
                    "name": r.name,
                    "status": r.status,
                    "message": r.message,
                    "details": r.details,
                }
                for r in self.results
            ],
            "exit_code": self.exit_code,
            "summary": self.summary,
        }


class AniScrapyDoctor:
    """ani-scrapy diagnostic tool."""

    # Status constants
    STATUS_PASS = "pass"
    STATUS_WARN = "warn"
    STATUS_FAIL = "fail"

    # Browser paths by operating system
    BRAVE_PATHS = {
        "windows": [
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
        ],
        "linux": [
            "/usr/bin/brave",
            "/usr/bin/brave-browser",
            "/opt/brave/brave",
        ],
        "darwin": [
            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser (Arm)",
        ],
    }

    # Python dependencies to check
    DEPENDENCIES = {
        "ani-scrapy": "ani_scrapy",
        "aiohttp": "aiohttp",
        "beautifulsoup4": "bs4",
        "loguru": "loguru",
        "playwright": "playwright",
        "rich": "rich",
        "typer": "typer",
    }

    # Sites to check connectivity
    CONNECTIVITY_SITES = {
        "animeflv.net": "https://animeflv.net",
        "jkanime.net": "https://jkanime.net",
    }

    def __init__(self, timeout: int = 5):
        self.timeout = timeout
        self.results: List[DiagnosticResult] = []

    def run(self) -> DoctorReport:
        """Run all diagnostic checks."""
        self._check_environment()
        self._check_dependencies()
        self._check_playwright()
        self._check_brave()
        asyncio.run(self._check_connectivity())

        exit_code = self._calculate_exit_code()
        summary = self._generate_summary()

        return DoctorReport(
            timestamp=datetime.now().isoformat(),
            environment=self._get_environment_info(),
            results=self.results,
            exit_code=exit_code,
            summary=summary,
        )

    def _add_result(
        self,
        category: str,
        name: str,
        status: str,
        message: str,
        details: Optional[Dict] = None,
    ) -> None:
        """Add a diagnostic result."""
        self.results.append(
            DiagnosticResult(
                category=category,
                name=name,
                status=status,
                message=message,
                details=details or {},
            )
        )

    def _get_status_summary(self) -> Tuple[bool, bool]:
        """Get summary of current results status."""
        has_fail = any(r.status == self.STATUS_FAIL for r in self.results)
        has_warn = any(r.status == self.STATUS_WARN for r in self.results)
        return has_fail, has_warn

    def _check_environment(self) -> None:
        """Check environment info."""
        env_info = {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": platform.system(),
            "architecture": platform.machine(),
            "os_version": platform.version(),
        }

        ram = self._get_system_ram()
        env_info["ram"] = ram

        message = f"Python {env_info['python_version']} ({env_info['platform']}) - {ram} RAM"

        self._add_result(
            category="Environment",
            name="System Info",
            status=self.STATUS_PASS,
            message=message,
            details=env_info,
        )

    def _get_system_ram(self) -> str:
        """Get system RAM information."""
        try:
            if platform.system() == "Windows":
                output = subprocess.check_output(
                    [
                        "wmic",
                        "OS",
                        "Get",
                        "TotalVisibleMemorySize",
                        "/Value",
                    ],
                    text=True,
                )
                for line in output.splitlines():
                    if "TotalVisibleMemorySize" in line:
                        kb = int(line.split("=")[1])
                        return f"{kb // (1024*1024)}GB"
            else:
                output = subprocess.check_output(["free", "-m"], text=True)
                lines = output.split("\n")
                if lines and len(lines) > 1:
                    mem = lines[1].split()
                    if len(mem) >= 2:
                        mb = int(mem[1])
                        return f"{mb // 1024}GB"
        except Exception:
            pass

        return "Unknown"

    def _check_dependencies(self) -> None:
        """Check Python dependencies."""
        for package, module in self.DEPENDENCIES.items():
            try:
                mod = self._import_module(module)
                version = getattr(mod, "__version__", "unknown")
                self._add_result(
                    category="Dependencies",
                    name=package,
                    status=self.STATUS_PASS,
                    message=f"Installed (v{version})",
                    details={"version": version},
                )
            except ImportError:
                self._add_result(
                    category="Dependencies",
                    name=package,
                    status=self.STATUS_FAIL,
                    message="Not installed",
                )

    def _check_playwright(self) -> None:
        """Check Playwright installation."""
        if not PLAYWRIGHT_AVAILABLE:
            self._add_result(
                category="Playwright",
                name="Installation",
                status=self.STATUS_FAIL,
                message="Playwright not installed",
            )
            return

        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                try:
                    p.chromium.launch()
                    self._add_result(
                        category="Playwright",
                        name="Chromium",
                        status=self.STATUS_PASS,
                        message="Installed",
                        details={"browser": "chromium"},
                    )
                except Exception:
                    self._add_result(
                        category="Playwright",
                        name="Chromium",
                        status=self.STATUS_WARN,
                        message="Not installed - run: playwright install chromium",
                    )

                self._add_result(
                    category="Playwright",
                    name="Browsers",
                    status=self.STATUS_PASS,
                    message="Playwright ready",
                    details={"ready": True},
                )
        except Exception as e:
            self._add_result(
                category="Playwright",
                name="Installation",
                status=self.STATUS_FAIL,
                message=f"Error: {str(e)}",
            )

    def _check_brave(self) -> None:
        """Check for Brave browser installation."""
        system = platform.system().lower()
        brave_paths = self.BRAVE_PATHS.get(system, [])

        detected = None
        for path in brave_paths:
            if Path(path).exists():
                detected = path
                break

        if detected:
            self._add_result(
                category="Browsers",
                name="Brave (Recommended)",
                status=self.STATUS_PASS,
                message=f"Detected: {detected}",
                details={"path": detected, "recommended": True},
            )
        else:
            self._add_result(
                category="Browsers",
                name="Brave (Recommended)",
                status=self.STATUS_WARN,
                message="Brave not found - using Chromium by default",
                details={
                    "recommended": True,
                    "search_paths": brave_paths,
                    "hint": "Brave's native ad-blocker reduces blocking",
                },
            )

    async def _check_connectivity(self) -> None:
        """Check network connectivity to anime sites."""
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        ) as session:
            for site_name, url in self.CONNECTIVITY_SITES.items():
                try:
                    async with session.get(url, ssl=False) as response:
                        status = (
                            self.STATUS_PASS
                            if response.status == 200
                            else self.STATUS_WARN
                        )
                        self._add_result(
                            category="Connectivity",
                            name=site_name,
                            status=status,
                            message=f"Reachable (HTTP {response.status})",
                            details={
                                "url": url,
                                "status_code": response.status,
                            },
                        )
                except asyncio.TimeoutError:
                    self._add_result(
                        category="Connectivity",
                        name=site_name,
                        status=self.STATUS_FAIL,
                        message="Connection timed out",
                        details={"url": url, "error": "timeout"},
                    )
                except Exception as e:
                    self._add_result(
                        category="Connectivity",
                        name=site_name,
                        status=self.STATUS_FAIL,
                        message="Connection failed",
                        details={"url": url, "error": str(e)[:50]},
                    )

    def _import_module(self, module_name: str):
        """Import a module by name."""
        if module_name == "ani_scrapy":
            import ani_scrapy

            return ani_scrapy
        elif module_name == "bs4":
            import bs4

            return bs4
        else:
            return __import__(module_name)

    def _get_environment_info(self) -> Dict:
        """Get environment information."""
        return {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": platform.system(),
            "architecture": platform.machine(),
            "timestamp": datetime.now().isoformat(),
        }

    def _calculate_exit_code(self) -> int:
        """Calculate exit code based on results."""
        has_fail, has_warn = self._get_status_summary()

        if has_fail:
            return 2
        elif has_warn:
            return 1
        return 0

    def _generate_summary(self) -> str:
        """Generate summary message."""
        has_fail, has_warn = self._get_status_summary()
        fail_count = sum(
            1 for r in self.results if r.status == self.STATUS_FAIL
        )
        warn_count = sum(
            1 for r in self.results if r.status == self.STATUS_WARN
        )

        if not has_fail and not has_warn:
            return "No issues found. Star Brave for better success rates!"
        elif has_fail:
            return f"{fail_count} issue(s) found."
        else:
            return f"{warn_count} warning(s) found."

    def print_report(self, report: DoctorReport) -> None:
        """Print the diagnostic report."""
        self._print_header()
        self._print_by_category(report.results)
        self._print_summary(report.summary)

    def _print_header(self) -> None:
        """Print report header."""
        print()
        rprint("[bold cyan]ani-scrapy doctor[/bold cyan]")
        print()

    def _print_summary(self, summary: str) -> None:
        """Print final summary."""
        has_fail, has_warn = self._get_status_summary()

        if not has_fail and not has_warn:
            icon = "✓"
        elif has_fail:
            icon = "✗"
        else:
            icon = "•"

        print(f"[{icon}] {summary}")

    def _print_by_category(self, results: List[DiagnosticResult]) -> None:
        """Print results grouped by category."""
        categories: Dict[str, List[DiagnosticResult]] = {}
        for result in results:
            if result.category not in categories:
                categories[result.category] = []
            categories[result.category].append(result)

        for category, cat_results in categories.items():
            self._print_category(category, cat_results)

    def _print_category(
        self, category: str, results: List[DiagnosticResult]
    ) -> None:
        """Print a category section."""
        # Get statuses for category
        statuses = [r.status for r in results]
        category_icon = self._get_category_icon(statuses)

        print(f"[{category_icon}] {category}")

        for r in results:
            icon = self._get_icon(r.status)
            prefix = "* " if r.details.get("recommended") else ""
            rprint(f"  {icon} {prefix}{r.name}: {r.message}")

    def _get_icon(self, status: str) -> str:
        """Get icon for a status."""
        icons = {
            self.STATUS_PASS: "•",
            self.STATUS_WARN: "•",
            self.STATUS_FAIL: "•",
        }
        return icons.get(status, "?")

    def _get_category_icon(self, statuses: List[str]) -> str:
        """Get icon for a category based on its statuses."""
        if all(s == self.STATUS_PASS for s in statuses):
            return "✓"
        elif any(s == self.STATUS_FAIL for s in statuses):
            return "✗"
        return "•"


if __name__ == "__main__":
    pass
