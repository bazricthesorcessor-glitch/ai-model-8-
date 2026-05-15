"""
Quick Terminal Utilities - Fast command-line access to common tasks.

Usage:
    # Open YouTube
    python ui/quick_terminal.py youtube

    # Screenshot and copy
    python ui/quick_terminal.py screenshot

    # Send screenshot to ChatGPT
    python ui/quick_terminal.py screenshot-to-chatgpt

    # Control brightness
    python ui/quick_terminal.py brightness-up
    python ui/quick_terminal.py brightness-down
    python ui/quick_terminal.py brightness 75  # Set to 75%

    # Or use as library
    from ui.quick_terminal import QuickTerminal
    qt = QuickTerminal()
    qt.open_youtube()
    qt.screenshot_and_copy()
    qt.paste_screenshot_into_chatgpt()
"""

import subprocess
import sys
import time
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from executor.input_controller import InputController
from .ai_tabs import AITabsManager


class QuickTerminal:
    """Quick terminal utilities for common tasks."""

    def __init__(self):
        """Initialize quick terminal utilities."""
        self.controller = None
        self._browser_pid = None
        self.tabs = AITabsManager()
        self.screenshot_path = Path.home() / ".cache" / "caelestia" / "screenshots"
        self.screenshot_path.mkdir(parents=True, exist_ok=True)

    # ========================================================================
    # YOUTUBE
    # ========================================================================

    def open_youtube(self) -> Dict[str, Any]:
        """Open YouTube in Elzyra's Brave profile."""
        print("[→] Opening YouTube...")

        try:
            result = self.tabs.open_tab("https://youtube.com")
            if not result["success"] and "unavailable" in result.get("error", "").lower():
                launch_result = self.tabs.launch_brave()
                if not launch_result["success"]:
                    return launch_result
                time.sleep(2)
                result = self.tabs.open_tab("https://youtube.com")

            if not result["success"]:
                return result

            return {
                "success": True,
                "action": "open_youtube",
                "url": "https://youtube.com",
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    # ========================================================================
    # SCREENSHOT UTILITIES
    # ========================================================================

    def take_screenshot(
        self, region: Optional[tuple] = None, save_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Take a screenshot.

        Args:
            region: Optional (x, y, width, height) for partial screenshot
            save_path: Custom save path (default: ~/.cache/caelestia/screenshots/)

        Returns:
            Dict with screenshot info
        """
        try:
            if save_path is None:
                timestamp = int(time.time() * 1000)
                save_path = str(self.screenshot_path / f"screenshot_{timestamp}.png")

            print(f"[→] Taking screenshot...")

            # Use gnome-screenshot or scrot
            if self._command_exists("gnome-screenshot"):
                cmd = ["gnome-screenshot", "-f", save_path]
                if region:
                    x, y, w, h = region
                    cmd.extend(["-a", f"{x},{y},{w},{h}"])
            elif self._command_exists("scrot"):
                cmd = ["scrot", save_path]
            elif self._command_exists("import"):  # ImageMagick
                if region:
                    x, y, w, h = region
                    cmd = ["import", "-window", "root", save_path]
                else:
                    cmd = ["import", "-window", "root", save_path]
            else:
                return {
                    "success": False,
                    "error": "No screenshot tool available (gnome-screenshot, scrot, or ImageMagick)",
                }

            subprocess.run(cmd, capture_output=True, timeout=10)

            return {
                "success": True,
                "action": "take_screenshot",
                "path": save_path,
                "timestamp": time.time(),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def copy_image_to_clipboard(self, image_path: str) -> Dict[str, Any]:
        """Copy image to clipboard."""
        try:
            print(f"[→] Copying image to clipboard...")

            # Use xclip with image support
            if self._command_exists("xclip"):
                with open(image_path, "rb") as f:
                    subprocess.run(
                        ["xclip", "-selection", "clipboard", "-t", "image/png"],
                        stdin=f,
                        capture_output=True,
                    )
            elif self._command_exists("wl-copy"):  # Wayland
                with open(image_path, "rb") as f:
                    subprocess.run(
                        ["wl-copy"],
                        stdin=f,
                        capture_output=True,
                    )
            else:
                return {
                    "success": False,
                    "error": "No clipboard tool available (xclip or wl-copy)",
                }

            print(f"  [✓] Image copied to clipboard")

            return {
                "success": True,
                "action": "copy_to_clipboard",
                "path": image_path,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def screenshot_and_copy(
        self, region: Optional[tuple] = None
    ) -> Dict[str, Any]:
        """Take screenshot and copy to clipboard."""
        print("[→] Screenshot + Copy workflow started...")

        # Take screenshot
        screenshot_result = self.take_screenshot(region)
        if not screenshot_result["success"]:
            return screenshot_result

        screenshot_path = screenshot_result["path"]

        # Copy to clipboard
        copy_result = self.copy_image_to_clipboard(screenshot_path)
        if not copy_result["success"]:
            return copy_result

        print(f"  [✓] Screenshot taken and copied: {screenshot_path}")

        return {
            "success": True,
            "action": "screenshot_and_copy",
            "path": screenshot_path,
        }

    # ========================================================================
    # CHATGPT INTEGRATION
    # ========================================================================

    def open_chatgpt(self) -> Dict[str, Any]:
        """Open or focus ChatGPT in Elzyra's Brave profile."""
        print("[→] Opening ChatGPT...")

        try:
            result = self.tabs.focus_provider("chatgpt")
            if not result["success"] and "unavailable" in result.get("error", "").lower():
                launch_result = self.tabs.launch_brave()
                if not launch_result["success"]:
                    return launch_result
                time.sleep(2)
                result = self.tabs.focus_provider("chatgpt")

            if not result["success"]:
                return result

            print(f"  [✓] ChatGPT {result.get('action', 'ready')}")
            return {
                "success": True,
                "action": "open_chatgpt",
                "status": result.get("action", "ready"),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def paste_screenshot_into_chatgpt(
        self, region: Optional[tuple] = None
    ) -> Dict[str, Any]:
        """
        Compose screenshot primitives to paste an image into ChatGPT.

        Usage:
            qt = QuickTerminal()
            qt.paste_screenshot_into_chatgpt()
        """
        print("\n" + "=" * 60)
        print("SCREENSHOT → CHATGPT WORKFLOW")
        print("=" * 60)

        # Step 1: Take screenshot
        print("\n[1/4] Taking screenshot...")
        screenshot_result = self.take_screenshot(region)
        if not screenshot_result["success"]:
            print(f"  [✗] Failed: {screenshot_result['error']}")
            return screenshot_result

        screenshot_path = screenshot_result["path"]
        print(f"  [✓] Screenshot saved: {screenshot_path}")

        # Step 2: Copy to clipboard
        print("\n[2/4] Copying to clipboard...")
        copy_result = self.copy_image_to_clipboard(screenshot_path)
        if not copy_result["success"]:
            print(f"  [✗] Failed: {copy_result['error']}")
            return copy_result

        print(f"  [✓] Image copied to clipboard")

        # Step 3: Open ChatGPT
        print("\n[3/4] Opening ChatGPT...")
        chatgpt_result = self.open_chatgpt()
        if not chatgpt_result["success"]:
            print(f"  [✗] Failed: {chatgpt_result['error']}")
            return chatgpt_result

        print(f"  [✓] ChatGPT ready")
        time.sleep(2)

        # Step 4: Paste screenshot
        print("\n[4/4] Pasting screenshot...")
        try:
            # Click in message input area (usually at bottom)
            print("  [*] Finding message input area...")
            time.sleep(1)

            # Try Ctrl+V to paste
            print("  [*] Pasting image (Ctrl+V)...")
            InputController.key_combination("ctrl+v")
            time.sleep(2)

            print(f"  [✓] Image pasted in ChatGPT")

            # Optional: Auto-send message
            print("\n[Optional] Auto-sending message...")
            user_input = input("  [?] Send message now? (y/n): ").strip().lower()

            if user_input == "y":
                print("  [*] Sending message...")
                InputController.key_combination("ctrl+Return")
                time.sleep(1)
                print(f"  [✓] Message sent!")

            print("\n" + "=" * 60)
            print("✓ WORKFLOW COMPLETE")
            print("=" * 60)

            return {
                "success": True,
                "action": "paste_screenshot_into_chatgpt",
                "screenshot_path": screenshot_path,
                "status": "completed",
            }

        except Exception as e:
            print(f"  [✗] Error during paste: {e}")
            return {"success": False, "error": str(e)}

    def send_screenshot_to_chatgpt(
        self, region: Optional[tuple] = None
    ) -> Dict[str, Any]:
        """Deprecated compatibility wrapper for the composable primitive flow."""
        result = self.paste_screenshot_into_chatgpt(region)
        if result.get("success"):
            result["deprecated_action"] = "send_screenshot_to_chatgpt"
        return result

    # ========================================================================
    # BRIGHTNESS CONTROL
    # ========================================================================

    def brightness_up(self, amount: Optional[float] = None) -> Dict[str, Any]:
        """Increase brightness."""
        amount = amount or 0.1

        try:
            print(f"[→] Brightness up ({int(amount * 100)}%)...")

            # Use brightnessctl
            result = subprocess.run(
                ["brightnessctl", "set", f"+{int(amount * 100)}%"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                print(f"  [✓] Brightness increased")
                return {"success": True, "action": "brightness_up"}
            else:
                return {"success": False, "error": result.stderr}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def brightness_down(self, amount: Optional[float] = None) -> Dict[str, Any]:
        """Decrease brightness."""
        amount = amount or 0.1

        try:
            print(f"[→] Brightness down ({int(amount * 100)}%)...")

            result = subprocess.run(
                ["brightnessctl", "set", f"{int(amount * 100)}%-"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                print(f"  [✓] Brightness decreased")
                return {"success": True, "action": "brightness_down"}
            else:
                return {"success": False, "error": result.stderr}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def set_brightness(self, percent: int) -> Dict[str, Any]:
        """Set brightness to specific percentage."""
        try:
            percent = max(1, min(percent, 100))
            print(f"[→] Setting brightness to {percent}%...")

            result = subprocess.run(
                ["brightnessctl", "set", f"{percent}%"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                print(f"  [✓] Brightness set to {percent}%")
                return {"success": True, "action": "set_brightness", "percent": percent}
            else:
                return {"success": False, "error": result.stderr}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_brightness(self) -> Dict[str, Any]:
        """Get current brightness."""
        try:
            result = subprocess.run(
                ["brightnessctl", "get"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                current = int(result.stdout.strip())
                max_result = subprocess.run(
                    ["brightnessctl", "max"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                max_brightness = int(max_result.stdout.strip())
                percent = int((current / max_brightness) * 100)

                return {
                    "success": True,
                    "action": "get_brightness",
                    "current": current,
                    "max": max_brightness,
                    "percent": percent,
                }
            else:
                return {"success": False, "error": result.stderr}

        except Exception as e:
            return {"success": False, "error": str(e)}

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _command_exists(self, command: str) -> bool:
        """Check if command exists in PATH."""
        result = subprocess.run(
            ["which", command],
            capture_output=True,
        )
        return result.returncode == 0

    def _check_browser_running(self, browser: str = "brave") -> bool:
        """Check if browser is running."""
        try:
            result = subprocess.run(
                ["pgrep", "-f", browser],
                capture_output=True,
            )
            return result.returncode == 0
        except:
            return False

    # ========================================================================
    # QUICK SHORTCUTS
    # ========================================================================

    def screenshot_quick(self) -> Dict[str, Any]:
        """Quick screenshot (take + copy)."""
        return self.screenshot_and_copy()

    def chatgpt_screenshot(self) -> Dict[str, Any]:
        """Quick ChatGPT screenshot (take + copy + paste)."""
        return self.paste_screenshot_into_chatgpt()

    def yt(self) -> Dict[str, Any]:
        """Quick YouTube shortcut."""
        return self.open_youtube()

    # ========================================================================
    # BATCH OPERATIONS
    # ========================================================================

    def get_all_brightness_info(self) -> Dict[str, Any]:
        """Get detailed brightness information."""
        brightness_info = self.get_brightness()

        return {
            "action": "get_all_brightness_info",
            "brightness": brightness_info,
        }

    def show_help(self) -> None:
        """Show help message."""
        help_text = """
╔════════════════════════════════════════════════════════════════╗
║          QUICK TERMINAL UTILITIES - HELP                       ║
╚════════════════════════════════════════════════════════════════╝

USAGE:
    python ui/quick_terminal.py [command] [args]

COMMANDS:

YouTube:
    youtube              - Open YouTube in Elzyra Brave

Screenshots:
    screenshot           - Take screenshot and copy to clipboard
    screenshot-to-chatgpt - Take screenshot, open ChatGPT, paste

Brightness:
    brightness-up        - Increase brightness by 10%
    brightness-down      - Decrease brightness by 10%
    brightness [0-100]   - Set brightness to specific %
    brightness-info      - Show current brightness

ChatGPT:
    chatgpt              - Open ChatGPT in Elzyra Brave
    screenshot-chatgpt   - Take screenshot and send to ChatGPT

EXAMPLES:

    # Open YouTube
    python ui/quick_terminal.py youtube

    # Take screenshot (copied to clipboard)
    python ui/quick_terminal.py screenshot

    # Send screenshot to ChatGPT (auto workflow)
    python ui/quick_terminal.py screenshot-to-chatgpt

    # Brightness control
    python ui/quick_terminal.py brightness-up
    python ui/quick_terminal.py brightness-down
    python ui/quick_terminal.py brightness 75

    # Get brightness info
    python ui/quick_terminal.py brightness-info

LIBRARY USAGE:

    from ui.quick_terminal import QuickTerminal

    qt = QuickTerminal()

    # YouTube
    qt.open_youtube()

    # Screenshots
    qt.screenshot_and_copy()
    qt.paste_screenshot_into_chatgpt()

    # Brightness
    qt.brightness_up()
    qt.brightness_down()
    qt.set_brightness(75)
    qt.get_brightness()

FEATURES:

    ✓ Uses Elzyra's dedicated Brave profile
    ✓ Reuses existing ChatGPT tab via CDP if open
    ✓ Copies screenshots to clipboard automatically
    ✓ Keyboard/mouse automation for pasting
    ✓ Works with Wayland (wl-copy) and X11 (xclip)
    ✓ Supports multiple screenshot tools

DEPENDENCIES:

    Required:
    - Brave
    - brightnessctl (for brightness control)
    - xclip or wl-copy (for clipboard)
    - gnome-screenshot, scrot, or ImageMagick (for screenshots)

    Optional:
    - Brave remote debugging on port 9222

        """
        print(help_text)


# ============================================================================
# CLI INTERFACE
# ============================================================================


def main():
    """Command-line interface."""
    if len(sys.argv) < 2:
        QuickTerminal().show_help()
        return

    command = sys.argv[1].lower()
    qt = QuickTerminal()

    # YouTube
    if command == "youtube":
        result = qt.open_youtube()
        print(json.dumps(result, indent=2))

    # Screenshots
    elif command == "screenshot":
        result = qt.screenshot_and_copy()
        print(json.dumps(result, indent=2))

    elif command == "screenshot-to-chatgpt" or command == "screenshot-chatgpt":
        result = qt.paste_screenshot_into_chatgpt()
        print(json.dumps(result, indent=2))

    # ChatGPT
    elif command == "chatgpt":
        result = qt.open_chatgpt()
        print(json.dumps(result, indent=2))

    # Brightness
    elif command == "brightness-up":
        result = qt.brightness_up()
        print(json.dumps(result, indent=2))

    elif command == "brightness-down":
        result = qt.brightness_down()
        print(json.dumps(result, indent=2))

    elif command == "brightness":
        if len(sys.argv) > 2:
            try:
                percent = int(sys.argv[2])
                result = qt.set_brightness(percent)
                print(json.dumps(result, indent=2))
            except ValueError:
                print(f"Error: Invalid brightness value '{sys.argv[2]}'")
        else:
            print("Usage: python ui/quick_terminal.py brightness [0-100]")

    elif command == "brightness-info":
        result = qt.get_brightness()
        if result["success"]:
            print(f"Current brightness: {result['percent']}%")
            print(f"Current: {result['current']} / Max: {result['max']}")
        else:
            print(f"Error: {result['error']}")

    # Help
    elif command == "help" or command == "-h" or command == "--help":
        qt.show_help()

    else:
        print(f"Unknown command: {command}")
        print("Use 'python ui/quick_terminal.py help' for usage")


if __name__ == "__main__":
    main()
