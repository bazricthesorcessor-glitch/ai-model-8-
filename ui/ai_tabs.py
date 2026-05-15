"""
AI provider tab management through Brave's Chrome DevTools Protocol.

The manager uses a dedicated Elzyra Brave profile and CDP tab endpoints.
It does not inspect or drive the user's personal browser profile.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

from config import BRAVE_PROFILE_DIR, endpoint_of, ensure_runtime_dirs


class AITabsManager:
    """Manage AI provider tabs using Brave CDP primitives."""

    PROVIDERS = {
        "claude": {
            "names": ["claude", "claude.ai"],
            "url": "https://claude.ai",
            "match_hosts": ["claude.ai"],
        },
        "chatgpt": {
            "names": ["chatgpt", "chat.openai"],
            "url": "https://chat.openai.com",
            "match_hosts": ["chat.openai.com", "chatgpt.com"],
        },
        "gemini": {
            "names": ["gemini", "bard"],
            "url": "https://gemini.google.com",
            "match_hosts": ["gemini.google.com"],
        },
        "grok": {
            "names": ["grok"],
            "url": "https://grok.x.ai",
            "match_hosts": ["grok.x.ai"],
        },
        "deepseek": {
            "names": ["deepseek"],
            "url": "https://chat.deepseek.com",
            "match_hosts": ["chat.deepseek.com"],
        },
        "perplexity": {
            "names": ["perplexity"],
            "url": "https://perplexity.ai",
            "match_hosts": ["perplexity.ai"],
        },
    }

    def __init__(
        self,
        cdp_base_url: Optional[str] = None,
        tabs_url: Optional[str] = None,
    ):
        """Initialize AI tabs manager."""
        self.cdp_base_url = (cdp_base_url or endpoint_of("brave_cdp")).rstrip("/")
        self.tabs_url = tabs_url or endpoint_of("brave_tabs")
        self.current_provider: Optional[str] = None

    # ========================================================================
    # CORE CDP PRIMITIVES
    # ========================================================================

    def launch_brave(self) -> Dict[str, Any]:
        """Launch Brave with Elzyra's dedicated profile and CDP enabled."""
        brave_binary = self._find_brave_binary()
        if not brave_binary:
            return {
                "success": False,
                "error": "Brave browser executable not found",
            }

        ensure_runtime_dirs()

        try:
            subprocess.Popen(
                [
                    brave_binary,
                    f"--remote-debugging-port={self._remote_debugging_port()}",
                    f"--user-data-dir={BRAVE_PROFILE_DIR}",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception as exc:
            return {
                "success": False,
                "error": f"Failed to launch Brave: {exc}",
            }

        return {
            "success": True,
            "browser": "brave",
            "profile_dir": str(BRAVE_PROFILE_DIR),
            "cdp": self.cdp_base_url,
        }

    def list_tabs(self) -> Dict[str, Any]:
        """List open Brave tabs through CDP."""
        success, tabs, error = self._fetch_tabs()
        if not success:
            return {
                "success": False,
                "error": error,
                "tabs": [],
            }

        return {
            "success": True,
            "tabs": tabs,
            "count": len(tabs),
        }

    def activate_tab(self, tab_id: str) -> Dict[str, Any]:
        """Activate an existing tab by CDP target id."""
        if not tab_id:
            return {"success": False, "error": "tab_id is required"}

        url = f"{self.cdp_base_url}/json/activate/{urllib.parse.quote(tab_id)}"
        success, _, error = self._http_get(url)
        if not success:
            return {
                "success": False,
                "error": error,
                "tab_id": tab_id,
            }

        return {
            "success": True,
            "tab_id": tab_id,
            "action": "activated",
        }

    def open_tab(self, url: str) -> Dict[str, Any]:
        """Open a new Brave tab through CDP."""
        if not url:
            return {"success": False, "error": "url is required"}

        normalized_url = self._normalize_url(url)
        endpoint = (
            f"{self.cdp_base_url}/json/new/"
            f"{urllib.parse.quote(normalized_url, safe='')}"
        )

        success, body, error = self._http_get(endpoint)
        if not success:
            return {
                "success": False,
                "error": error,
                "url": normalized_url,
            }

        tab = self._parse_json(body)
        return {
            "success": True,
            "action": "opened",
            "url": normalized_url,
            "tab": tab,
            "tab_id": tab.get("id") if isinstance(tab, dict) else None,
        }

    def focus_provider(self, provider: str) -> Dict[str, Any]:
        """Activate an existing provider tab or open one if needed."""
        provider = provider.lower().strip()

        if provider not in self.PROVIDERS:
            return {
                "success": False,
                "error": f"Unknown provider: {provider}. Available: {list(self.PROVIDERS.keys())}",
            }

        tabs_result = self.list_tabs()
        if not tabs_result["success"]:
            return tabs_result

        match = self._find_provider_tab(provider, tabs_result["tabs"])
        if match:
            activate_result = self.activate_tab(match["id"])
            if not activate_result["success"]:
                return activate_result

            self.current_provider = provider
            return {
                "success": True,
                "provider": provider,
                "action": "focused",
                "tab": match,
            }

        open_result = self.open_tab(self.PROVIDERS[provider]["url"])
        if not open_result["success"]:
            return open_result

        self.current_provider = provider
        return {
            "success": True,
            "provider": provider,
            "action": "opened",
            "tab": open_result.get("tab"),
            "tab_id": open_result.get("tab_id"),
            "url": self.PROVIDERS[provider]["url"],
        }

    # ========================================================================
    # COMPATIBILITY / DISCOVERY PRIMITIVES
    # ========================================================================

    def focus_or_open_provider(self, provider: str) -> Dict[str, Any]:
        """Backward-compatible alias for focus_provider."""
        return self.focus_provider(provider)

    def list_providers(self) -> Dict[str, Any]:
        """List all configured AI providers."""
        return {
            "success": True,
            "providers": list(self.PROVIDERS.keys()),
            "count": len(self.PROVIDERS),
        }

    def get_current_provider(self) -> Dict[str, Any]:
        """Get currently tracked provider."""
        if not self.current_provider:
            return {
                "success": False,
                "error": "No provider currently tracked",
            }

        return {
            "success": True,
            "provider": self.current_provider,
        }

    def detect_provider_tab(self, window_title: str) -> Optional[str]:
        """Detect provider name from a title or URL fragment."""
        text = window_title.lower()

        for provider_name, config in self.PROVIDERS.items():
            names = config["names"] + config["match_hosts"]
            if any(name in text for name in names):
                return provider_name

        return None

    # ========================================================================
    # INTERNAL IMPLEMENTATION
    # ========================================================================

    def _fetch_tabs(self) -> tuple[bool, List[Dict[str, Any]], Optional[str]]:
        success, body, error = self._http_get(self.tabs_url)
        if not success:
            return False, [], error

        tabs = self._parse_json(body)
        if not isinstance(tabs, list):
            return False, [], "Brave CDP returned non-list tabs payload"

        pages = [tab for tab in tabs if tab.get("type") == "page"]
        return True, pages, None

    @staticmethod
    def _parse_json(body: str) -> Any:
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def _normalize_url(url: str) -> str:
        if "://" in url:
            return url
        return f"https://{url}"

    @staticmethod
    def _find_brave_binary() -> Optional[str]:
        for binary in ("brave", "brave-browser", "brave-bin"):
            resolved = shutil.which(binary)
            if resolved:
                return resolved
        return None

    def _remote_debugging_port(self) -> int:
        parsed = urllib.parse.urlparse(self.cdp_base_url)
        return parsed.port or 9222

    @staticmethod
    def _host_matches(url: str, hosts: List[str]) -> bool:
        parsed = urllib.parse.urlparse(url)
        host = (parsed.netloc or parsed.path).lower()
        return any(host == h or host.endswith(f".{h}") for h in hosts)

    def _find_provider_tab(
        self,
        provider: str,
        tabs: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        config = self.PROVIDERS[provider]
        hosts = config["match_hosts"]
        names = config["names"]

        for tab in tabs:
            tab_url = tab.get("url", "")
            tab_title = tab.get("title", "").lower()
            if self._host_matches(tab_url, hosts):
                return tab
            if any(name in tab_title for name in names):
                return tab

        return None

    @staticmethod
    def _http_get(url: str) -> tuple[bool, str, Optional[str]]:
        try:
            request = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(request, timeout=2) as response:
                body = response.read().decode("utf-8", errors="replace")
                return True, body, None
        except urllib.error.URLError as exc:
            return (
                False,
                "",
                f"Brave CDP unavailable at {url}: {exc.reason}",
            )
        except Exception as exc:
            return False, "", f"Brave CDP request failed at {url}: {exc}"
