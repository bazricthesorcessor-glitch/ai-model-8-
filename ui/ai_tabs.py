"""
AI Tabs Manager - Multi-provider tab management via Firefox address bar.

Design:
- Use Firefox address bar "Switch to Tab" feature (most reliable)
- Focus Firefox
- Ctrl+L opens address bar
- Type provider name/URL
- Firefox auto-suggest shows "Switch to Tab" if open, else opens URL
- Press Down/Enter to switch or open

Why not wmctrl:
- Only shows active tab title
- Misses inactive tabs
- Unreliable for detecting existing tabs

Why not complex tab detection:
- Too fragile
- Different browsers have different tab APIs
- Address bar approach is UI-first and universal
"""

from typing import Dict, Any, Optional
import subprocess
import time


class AITabsManager:
    """Manages AI provider tabs using Firefox address bar."""

    # Provider configuration
    PROVIDERS = {
        "claude": {
            "names": ["claude", "claude.ai"],
            "url": "claude.ai",
            "search_text": "claude",
        },
        "chatgpt": {
            "names": ["chatgpt", "chat.openai"],
            "url": "chat.openai.com",
            "search_text": "chatgpt",
        },
        "gemini": {
            "names": ["gemini", "bard"],
            "url": "gemini.google.com",
            "search_text": "gemini",
        },
        "grok": {
            "names": ["grok"],
            "url": "grok.x.ai",
            "search_text": "grok",
        },
        "deepseek": {
            "names": ["deepseek"],
            "url": "chat.deepseek.com",
            "search_text": "deepseek",
        },
        "perplexity": {
            "names": ["perplexity"],
            "url": "perplexity.ai",
            "search_text": "perplexity",
        },
    }

    def __init__(self):
        """Initialize AI tabs manager."""
        self.current_provider: Optional[str] = None

    # ========================================================================
    # CORE PRIMITIVES
    # ========================================================================

    def focus_or_open_provider(self, provider: str) -> Dict[str, Any]:
        """
        Focus existing provider tab OR open if not exists.

        Uses Firefox address bar "Switch to Tab" feature:
        1. Focus Firefox
        2. Ctrl+L (open address bar)
        3. Type provider search text
        4. Firefox suggests "Switch to Tab" if open
        5. Press Down/Enter to switch or open

        Args:
            provider: Provider name (claude, chatgpt, etc.)

        Returns:
            {
                "success": bool,
                "provider": str,
                "action": "focused",
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

        try:
            from executor.input_controller import InputController

            # Step 1: Focus Firefox
            self._focus_firefox()
            time.sleep(0.3)

            # Step 2: Open address bar (Ctrl+L)
            InputController.key_combination("ctrl+l")
            time.sleep(0.2)

            # Step 3: Type provider search text
            InputController.type_text(config["search_text"])
            time.sleep(0.5)

            # Step 4: Press Down to highlight "Switch to Tab" suggestion (if exists)
            InputController.press_key("Down")
            time.sleep(0.2)

            # Step 5: Press Enter to switch tab or open URL
            InputController.press_key("Return")
            time.sleep(1.0)  # Wait for tab switch/page load

            self.current_provider = provider

            # We don't know if it switched or opened, but either way provider is now focused
            return {
                "success": True,
                "provider": provider,
                "action": "focused",
                "url": f"https://{config['url']}",
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to focus {provider}: {str(e)}",
            }

    def list_providers(self) -> Dict[str, Any]:
        """List all available providers."""
        return {
            "success": True,
            "providers": list(self.PROVIDERS.keys()),
            "count": len(self.PROVIDERS),
        }

    def get_current_provider(self) -> Dict[str, Any]:
        """Get currently focused provider."""
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
        """
        Detect which provider a window title belongs to.

        Args:
            window_title: Window/tab title

        Returns:
            Provider name or None
        """
        title_lower = window_title.lower()

        for provider_name, config in self.PROVIDERS.items():
            for name in config["names"]:
                if name in title_lower:
                    return provider_name

        return None

    # ========================================================================
    # INTERNAL IMPLEMENTATION
    # ========================================================================

    @staticmethod
    def _focus_firefox() -> None:
        """Focus Firefox window using standard methods."""
        try:
            # Try wmctrl first (works on most Linux desktop environments)
            if _command_exists("wmctrl"):
                subprocess.run(
                    ["wmctrl", "-a", "firefox"],
                    capture_output=True,
                    timeout=2,
                )
                return

            # Fallback: try xdotool
            if _command_exists("xdotool"):
                subprocess.run(
                    ["xdotool", "search", "--name", "firefox", "windowactivate"],
                    capture_output=True,
                    timeout=2,
                )
                return

        except Exception:
            pass

        # If no focus method works, that's OK - Firefox might already be focused

    @staticmethod
    def _command_exists(command: str) -> bool:
        """Check if command exists in PATH."""
        try:
            result = subprocess.run(
                ["which", command],
                capture_output=True,
                timeout=1,
            )
            return result.returncode == 0
        except Exception:
            return False


def _command_exists(command: str) -> bool:
    """Module-level helper for command existence check."""
    try:
        result = subprocess.run(
            ["which", command],
            capture_output=True,
            timeout=1,
        )
        return result.returncode == 0
    except Exception:
        return False
