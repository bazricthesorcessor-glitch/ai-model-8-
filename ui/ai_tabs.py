"""
AI provider tab management through Brave's Chrome DevTools Protocol.

Brave now runs on the normal shared profile. Elzyra's isolation boundary is
Hyprland workspaces, not a dedicated browser profile directory.
"""

from __future__ import annotations

import json
import importlib.util
from pathlib import Path
import shutil
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

from config import (
    ALLOWED_WORKSPACES,
    endpoint_of,
    ensure_runtime_dirs,
    get_available_workspace,
    get_workspace_name,
    get_workspace_priority_order,
    is_allowed_workspace,
)
class AITabsManager:
    """Manage AI provider tabs using Brave CDP with workspace boundaries."""

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
        "zai": {
            "names": ["zai", "z.ai", "chat.z.ai"],
            "url": "https://chat.z.ai",
            "match_hosts": ["chat.z.ai", "z.ai"],
        },
    }

    def __init__(
        self,
        cdp_base_url: Optional[str] = None,
        tabs_url: Optional[str] = None,
        hyprland_manager: Optional[HyprlandManager] = None,
    ):
        """Initialize AI tabs manager."""
        self.cdp_base_url = (cdp_base_url or endpoint_of("brave_cdp")).rstrip("/")
        self.tabs_url = tabs_url or endpoint_of("brave_tabs")
        self.current_provider: Optional[str] = None
        self._hyprland_manager = hyprland_manager

    # ========================================================================
    # CORE CDP PRIMITIVES
    # ========================================================================

    def launch_brave(self) -> Dict[str, Any]:
        """
        Attach to CDP if Brave is already available, otherwise launch Brave.

        Brave uses the normal shared session. Elzyra relies on workspace-level
        isolation instead of a dedicated profile.
        """
        ensure_runtime_dirs()

        if self._cdp_ready():
            return {
                "success": True,
                "browser": "brave",
                "cdp": self.cdp_base_url,
                "cdp_ready": True,
                "attached_existing": True,
                "workspace_boundary": list(ALLOWED_WORKSPACES),
            }

        workspace_result = self._prepare_workspace_for_browser(create_window=False)
        if not workspace_result["success"]:
            return workspace_result

        spawn_result = self._spawn_brave_window(workspace_result["workspace"], enable_cdp=True)
        if not spawn_result["success"]:
            return spawn_result

        cdp_ready = False
        for _ in range(10):
            if self._cdp_ready():
                cdp_ready = True
                break
            time.sleep(0.5)

        return {
            "success": cdp_ready,
            "browser": "brave",
            "cdp": self.cdp_base_url,
            "cdp_ready": cdp_ready,
            "attached_existing": False,
            "workspace": workspace_result["workspace"],
            "workspace_name": workspace_result["workspace_name"],
            "workspace_boundary": list(ALLOWED_WORKSPACES),
            "error": None if cdp_ready else "Brave launched but CDP did not become ready",
        }

    def list_tabs(self) -> Dict[str, Any]:
        """List open Brave tabs through CDP."""
        success, tabs, error = self._fetch_tabs()
        if not success:
            return {
                "success": False,
                "error": error,
                "tabs": [],
                "allowed_workspaces": list(ALLOWED_WORKSPACES),
            }

        return {
            "success": True,
            "tabs": tabs,
            "count": len(tabs),
            "allowed_workspaces": list(ALLOWED_WORKSPACES),
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
        """
        Open a new Brave tab through CDP inside an Elzyra-owned workspace.

        The browser session is shared, but tab creation is prepared from an
        allowed workspace so Elzyra stays inside its workspace boundary.
        """
        if not url:
            return {"success": False, "error": "url is required"}

        normalized_url = self._normalize_url(url)
        workspace_result = self._prepare_workspace_for_browser(create_window=True)
        if not workspace_result["success"]:
            return workspace_result

        encoded = urllib.parse.quote(normalized_url, safe="")
        endpoints = [
            f"{self.cdp_base_url}/json/new/{encoded}",
            f"{self.cdp_base_url}/json/new?{encoded}",
            f"{self.cdp_base_url}/json/new?url={encoded}",
        ]

        last_error = None
        for endpoint in endpoints:
            success, body, error = self._http_get(endpoint)
            if success:
                tab = self._parse_json(body)
                return {
                    "success": True,
                    "action": "opened",
                    "url": normalized_url,
                    "tab": tab,
                    "tab_id": tab.get("id") if isinstance(tab, dict) else None,
                    "endpoint": endpoint,
                    "workspace": workspace_result["workspace"],
                    "workspace_name": workspace_result["workspace_name"],
                }
            last_error = error

        return {
            "success": False,
            "error": last_error,
            "url": normalized_url,
            "attempted_endpoints": endpoints,
            "workspace": workspace_result["workspace"],
            "workspace_name": workspace_result["workspace_name"],
        }

    def focus_provider(self, provider: str) -> Dict[str, Any]:
        """
        Focus a provider tab only when it lives inside an allowed workspace.

        If a matching tab cannot be proven to be inside an Elzyra workspace,
        open a fresh provider tab inside the workspace boundary instead of
        activating or disturbing unrelated user workflow.
        """
        provider = provider.lower().strip()

        if provider not in self.PROVIDERS:
            return {
                "success": False,
                "error": f"Unknown provider: {provider}. Available: {list(self.PROVIDERS.keys())}",
            }

        tabs_result = self.list_tabs()
        if not tabs_result["success"]:
            launch_result = self.launch_brave()
            if launch_result.get("success"):
                tabs_result = self.list_tabs()
            else:
                return tabs_result

        if not tabs_result["success"]:
            return tabs_result

        allowed_match = self._find_allowed_provider_tab(provider, tabs_result["tabs"])
        if allowed_match:
            target_workspace = allowed_match.get("workspace")
            hyprland = self._get_hyprland_manager()
            active_workspace = self._get_active_workspace_id()
            if hyprland is not None and target_workspace and active_workspace != target_workspace:
                success, _, error = hyprland.switch_workspace(target_workspace)
                if not success:
                    return {
                        "success": False,
                        "error": error,
                        "workspace": target_workspace,
                    }

            activate_result = self.activate_tab(allowed_match["id"])
            if not activate_result["success"]:
                return activate_result

            self.current_provider = provider
            return {
                "success": True,
                "provider": provider,
                "action": "focused",
                "tab": allowed_match,
                "workspace": allowed_match.get("workspace"),
                "workspace_name": allowed_match.get("workspace_name"),
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
            "workspace": open_result.get("workspace"),
            "workspace_name": open_result.get("workspace_name"),
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
            "allowed_workspaces": list(ALLOWED_WORKSPACES),
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

    def _cdp_ready(self) -> bool:
        success, _, _ = self._http_get(self.tabs_url)
        return success

    def _prepare_workspace_for_browser(self, create_window: bool) -> Dict[str, Any]:
        hyprland = self._get_hyprland_manager()
        if hyprland is None:
            return {
                "success": False,
                "error": "Hyprland is required to enforce Elzyra workspace boundaries",
            }

        brave_windows = self._list_brave_windows()
        allowed_windows = [window for window in brave_windows if is_allowed_workspace(window.workspace)]

        if allowed_windows:
            target_workspace = self._choose_workspace_from_windows(allowed_windows)
        else:
            target_workspace = self._choose_available_workspace()
            if target_workspace is None:
                return {
                    "success": False,
                    "error": "No available workspace found for Elzyra browser isolation",
                }

        active_workspace = self._get_active_workspace_id()
        if active_workspace is not None and active_workspace != target_workspace:
            success, _, error = hyprland.switch_workspace(target_workspace)
            if not success:
                return {
                    "success": False,
                    "error": error,
                    "workspace": target_workspace,
                }

        needs_window = create_window and not any(window.workspace == target_workspace for window in allowed_windows)
        if needs_window:
            spawn_result = self._spawn_brave_window(target_workspace, enable_cdp=not self._cdp_ready())
            if not spawn_result["success"]:
                return spawn_result

        return {
            "success": True,
            "workspace": target_workspace,
            "workspace_name": get_workspace_name(target_workspace),
        }

    def _spawn_brave_window(self, workspace: int, enable_cdp: bool) -> Dict[str, Any]:
        brave_binary = self._find_brave_binary()
        if not brave_binary:
            return {
                "success": False,
                "error": "Brave browser executable not found",
            }

        command = [brave_binary]
        if enable_cdp:
            command.append(f"--remote-debugging-port={self._remote_debugging_port()}")
        command.extend(["--new-window", "about:blank"])

        try:
            subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception as exc:
            return {
                "success": False,
                "error": f"Failed to launch Brave: {exc}",
            }

        time.sleep(0.75)
        return {
            "success": True,
            "workspace": workspace,
            "workspace_name": get_workspace_name(workspace),
        }

    def _get_hyprland_manager(self) -> Optional[Any]:
        if self._hyprland_manager is not None:
            return self._hyprland_manager

        try:
            hyprland_class = self._load_hyprland_manager_class()
            self._hyprland_manager = hyprland_class()
        except Exception:
            self._hyprland_manager = None

        return self._hyprland_manager

    def _choose_available_workspace(self) -> Optional[int]:
        hyprland = self._get_hyprland_manager()
        if hyprland is None:
            return None

        success, windows, error = hyprland.list_windows()
        if not success:
            return None

        occupied_workspaces = {window.workspace for window in windows or [] if window.workspace > 0}
        known_workspaces = self._known_workspace_ids()
        return get_available_workspace(
            occupied_workspaces=occupied_workspaces,
            known_workspaces=known_workspaces,
        )

    def _known_workspace_ids(self) -> list[int]:
        hyprland = self._get_hyprland_manager()
        if hyprland is None:
            return list(range(1, 11))

        success, workspaces, _ = hyprland.get_workspaces()
        if not success or not workspaces:
            return list(range(1, 11))

        return sorted({workspace.id for workspace in workspaces if workspace.id > 0})

    def _choose_workspace_from_windows(self, windows: List[Any]) -> int:
        priority = get_workspace_priority_order(self._known_workspace_ids())
        windows_by_workspace = {window.workspace: window for window in windows}
        for workspace in priority:
            if workspace in windows_by_workspace:
                return workspace
        return windows[0].workspace

    def _get_active_workspace_id(self) -> Optional[int]:
        hyprland = self._get_hyprland_manager()
        if hyprland is None:
            return None

        success, workspace_id, _ = hyprland.get_active_workspace_id()
        if success:
            return workspace_id
        return None

    def _list_brave_windows(self) -> List[Any]:
        hyprland = self._get_hyprland_manager()
        if hyprland is None:
            return []

        success, windows, _ = hyprland.list_windows()
        if not success or not windows:
            return []

        return [window for window in windows if self._is_brave_window(window)]

    @staticmethod
    def _is_brave_window(window: Any) -> bool:
        class_name = window.class_name.lower()
        title = window.title.lower()
        return "brave" in class_name or "brave" in title

    def _find_allowed_provider_tab(
        self,
        provider: str,
        tabs: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        config = self.PROVIDERS[provider]
        candidate_tabs = []

        for tab in tabs:
            tab_url = tab.get("url", "")
            tab_title = tab.get("title", "").lower()
            if self._host_matches(tab_url, config["match_hosts"]) or any(
                name in tab_title for name in config["names"]
            ):
                candidate_tabs.append(tab)

        allowed_windows = [window for window in self._list_brave_windows() if is_allowed_workspace(window.workspace)]

        for tab in candidate_tabs:
            mapped_window = self._map_tab_to_allowed_window(tab, allowed_windows)
            if mapped_window:
                enriched = dict(tab)
                enriched["workspace"] = mapped_window.workspace
                enriched["workspace_name"] = get_workspace_name(mapped_window.workspace)
                return enriched

        return None

    def _map_tab_to_allowed_window(
        self,
        tab: Dict[str, Any],
        windows: List[Any],
    ) -> Optional[Any]:
        tab_title = (tab.get("title") or "").lower()
        provider = self.detect_provider_tab(f"{tab.get('title', '')} {tab.get('url', '')}")

        for window in windows:
            window_title = (window.title or "").lower()
            if tab_title and tab_title == window_title:
                return window
            if tab_title and tab_title in window_title:
                return window
            if provider and self.detect_provider_tab(window.title or "") == provider:
                return window

        return None

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

    @staticmethod
    def _load_hyprland_manager_class():
        module_path = Path(__file__).resolve().parents[1] / "os" / "hyprland.py"
        spec = importlib.util.spec_from_file_location("elzyra_hyprland", module_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Unable to load Hyprland module from {module_path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.HyprlandManager

    def _remote_debugging_port(self) -> int:
        parsed = urllib.parse.urlparse(self.cdp_base_url)
        return parsed.port or 9222

    @staticmethod
    def _host_matches(url: str, hosts: List[str]) -> bool:
        parsed = urllib.parse.urlparse(url)
        host = (parsed.netloc or parsed.path).lower()
        return any(host == host_name or host.endswith(f".{host_name}") for host_name in hosts)

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
