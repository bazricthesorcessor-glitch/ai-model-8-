"""
AI Tabs Manager - Unified interface for multiple AI providers.

Design:
- Detects provider tabs (Claude, ChatGPT, Gemini, Grok, DeepSeek, etc.)
- Focuses correct provider tab
- Provides provider-agnostic interface

Example:
    focus_provider("claude")
    -> Finds Claude tab (or opens it)
    -> Focuses window/tab
    -> Returns success

This enables Scout/Brain to compose workflows without knowing specific provider UIs.
"""

from typing import Dict, Any, Optional
import subprocess
import time


class AITabsManager:
    """Manages AI provider tabs and detection."""

    # Provider configuration - maps provider name to detection patterns
    PROVIDERS = {
        "claude": {
            "names": ["claude", "claude.ai"],
            "urls": ["claude.ai", "claude"],
            "search_text": "claude",
            "browser": "firefox",
        },
        "chatgpt": {
            "names": ["chatgpt", "chat.openai"],
            "urls": ["chat.openai.com", "chatgpt.com"],
            "search_text": "ChatGPT",
            "browser": "firefox",
        },
        "gemini": {
            "names": ["gemini", "bard"],
            "urls": ["gemini.google.com", "bard.google.com"],
            "search_text": "Gemini",
            "browser": "firefox",
        },
        "grok": {
            "names": ["grok", "grok.ai"],
            "urls": ["grok.x.ai"],
            "search_text": "Grok",
            "browser": "firefox",
        },
        "deepseek": {
            "names": ["deepseek", "chat.deepseek"],
            "urls": ["chat.deepseek.com"],
            "search_text": "DeepSeek",
            "browser": "firefox",
        },
        "perplexity": {
            "names": ["perplexity", "pplx"],
            "urls": ["perplexity.ai"],
            "search_text": "Perplexity",
            "browser": "firefox",
        },
    }

    def __init__(self):
        """Initialize AI tabs manager."""
        self.current_provider: Optional[str] = None
        self.provider_tabs: Dict[str, Optional[str]] = {
            name: None for name in self.PROVIDERS.keys()
        }

    # ========================================================================
    # CORE PRIMITIVES
    # ========================================================================

    def focus_provider(self, provider: str) -> Dict[str, Any]:
        """
        Focus tab for specific AI provider.

        Args:
            provider: Provider name (claude, chatgpt, gemini, grok, deepseek, perplexity)

        Returns:
            {
                "success": bool,
                "provider": str,
                "action": "focused" | "opened" | "already_focused",
                "url": str
            }
        """
        provider = provider.lower().strip()

        if provider not in self.PROVIDERS:
            return {
                "success": False,
                "error": f"Unknown provider: {provider}. Available: {list(self.PROVIDERS.keys())}",
            }

        config = self.PROVIDERS[provider]

        # Try to find existing tab
        tab_found = self._find_tab(provider)

        if tab_found:
            # Tab exists, focus it
            self._focus_window()
            self.current_provider = provider
            return {
                "success": True,
                "provider": provider,
                "action": "focused",
                "url": config["urls"][0],
            }
        else:
            # Tab doesn't exist, open it
            open_result = self._open_provider(provider)
            if open_result["success"]:
                self.current_provider = provider
                return {
                    "success": True,
                    "provider": provider,
                    "action": "opened",
                    "url": config["urls"][0],
                }
            else:
                return open_result

    def get_current_provider(self) -> Dict[str, Any]:
        """Get currently focused provider."""
        if not self.current_provider:
            return {
                "success": False,
                "error": "No provider currently focused",
            }

        return {
            "success": True,
            "provider": self.current_provider,
            "config": self.PROVIDERS.get(self.current_provider),
        }

    def list_providers(self) -> Dict[str, Any]:
        """List all available providers."""
        return {
            "success": True,
            "providers": list(self.PROVIDERS.keys()),
            "count": len(self.PROVIDERS),
        }

    def detect_provider_tab(self, window_title: str) -> Optional[str]:
        """
        Detect which provider a window title belongs to.

        Args:
            window_title: Window/tab title

        Returns:
            Provider name or None
        """
        title_lower = window_title.lower()

        for provider_name, config in self.PROVIDERS.items():
            # Check names
            for name in config["names"]:
                if name in title_lower:
                    return provider_name

            # Check URLs
            for url in config["urls"]:
                if url in title_lower:
                    return provider_name

        return None

    # ========================================================================
    # INTERNAL IMPLEMENTATION
    # ========================================================================

    def _find_tab(self, provider: str) -> bool:
        """Check if tab for provider already exists."""
        try:
            config = self.PROVIDERS[provider]

            # Try to find window using wmctrl
            if self._command_exists("wmctrl"):
                result = subprocess.run(
                    ["wmctrl", "-l"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                for line in result.stdout.split("\n"):
                    # Check for provider names in window list
                    for name in config["names"]:
                        if name.lower() in line.lower():
                            return True
                    # Check for URLs
                    for url in config["urls"]:
                        if url in line:
                            return True

            return False

        except Exception:
            return False

    def _open_provider(self, provider: str) -> Dict[str, Any]:
        """Open provider in browser."""
        try:
            config = self.PROVIDERS[provider]
            url = config["urls"][0]

            # Check if browser is running
            browser = config["browser"]

            if self._command_exists(browser):
                # Open in new tab if browser running, else start browser
                try:
                    # Try to use ydotool to open new tab (future enhancement)
                    subprocess.Popen(
                        [browser, f"https://{url}"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    time.sleep(3)  # Wait for browser to load

                    return {
                        "success": True,
                        "provider": provider,
                        "url": f"https://{url}",
                    }

                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Failed to open {provider}: {str(e)}",
                    }
            else:
                return {
                    "success": False,
                    "error": f"Browser '{browser}' not found",
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def _focus_window() -> None:
        """Focus the current window (basic implementation)."""
        try:
            # On Wayland/KDE, can use:
            # xdotool search --name . windowfocus (X11)
            # ydotool (Wayland-safe)
            pass
        except Exception:
            pass

    @staticmethod
    def _command_exists(command: str) -> bool:
        """Check if command exists in PATH."""
        try:
            subprocess.run(
                ["which", command],
                capture_output=True,
                timeout=1,
            )
            return True
        except Exception:
            return False
