"""
Screenshot Manager - Manages temporary screenshot buffer and clipboard integration.

Design:
- Maintains latest screenshot reference (for clipboard workflow)
- Auto-deletes old temporary screenshots
- Provides primitives: capture, get_latest, clear_buffer
- Supports temporary (clipboard-first) and persistent modes

Workflow:
1. User presses PrintScreen
2. capture_screen() -> saves to temp buffer, copies to clipboard
3. User does Ctrl+Super+V
4. latest_screenshot_reference pasted from buffer
5. Old temp screenshots auto-deleted by cleanup_old()
"""

import subprocess
import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import os


class ScreenshotManager:
    """Manages screenshot buffer and temporary screenshot lifecycle."""

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        max_temp_screenshots: int = 5,
        temp_retention_seconds: int = 3600,
    ):
        """
        Initialize screenshot manager.

        Args:
            cache_dir: Directory for temporary screenshots (default: ~/.cache/caelestia/screenshots)
            max_temp_screenshots: Max temporary screenshots to keep (older deleted)
            temp_retention_seconds: Delete temp screenshots older than this
        """
        if cache_dir is None:
            cache_dir = Path.home() / ".cache" / "caelestia" / "screenshots"

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.max_temp_screenshots = max_temp_screenshots
        self.temp_retention_seconds = temp_retention_seconds

        # Current latest screenshot (for clipboard reference)
        self.latest_screenshot: Optional[Path] = None
        self.latest_timestamp: Optional[float] = None

    # ========================================================================
    # CORE PRIMITIVES
    # ========================================================================

    def capture_screen(
        self,
        region: Optional[Tuple[int, int, int, int]] = None,
        persistent: bool = False,
    ) -> Dict[str, Any]:
        """
        Capture screenshot and optionally save.

        Args:
            region: Optional (x, y, width, height) for partial screenshot
            persistent: If False (default), save to temp buffer. If True, save permanently.

        Returns:
            {
                "success": bool,
                "path": str,
                "timestamp": float,
                "is_temporary": bool,
                "buffer_reference": str (for clipboard)
            }
        """
        try:
            timestamp = int(time.time() * 1000)

            if persistent:
                # Persistent save mode - user chooses location
                save_path = (
                    self.cache_dir
                    / f"screenshot_persistent_{timestamp}.png"
                )
            else:
                # Temporary buffer mode
                save_path = self.cache_dir / f"screenshot_temp_{timestamp}.png"

            # Take screenshot using available tool
            success = self._take_screenshot_impl(save_path, region)

            if not success:
                return {
                    "success": False,
                    "error": "No screenshot tool available",
                }

            # If temporary mode, update buffer and auto-copy to clipboard
            if not persistent:
                self.latest_screenshot = save_path
                self.latest_timestamp = time.time()

                # Copy to clipboard immediately
                clipboard_result = self._copy_to_clipboard(save_path)
                if not clipboard_result["success"]:
                    return clipboard_result

                # Auto-cleanup old temporary screenshots
                self._cleanup_old_temp()

            return {
                "success": True,
                "path": str(save_path),
                "timestamp": time.time(),
                "is_temporary": not persistent,
                "buffer_reference": str(save_path) if not persistent else None,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_latest_screenshot(self) -> Dict[str, Any]:
        """
        Get latest screenshot from buffer without capturing new one.

        Returns:
            {
                "success": bool,
                "path": str,
                "timestamp": float,
                "in_clipboard": bool
            }
        """
        if not self.latest_screenshot or not self.latest_screenshot.exists():
            return {
                "success": False,
                "error": "No screenshot in buffer",
            }

        return {
            "success": True,
            "path": str(self.latest_screenshot),
            "timestamp": self.latest_timestamp,
            "in_clipboard": True,  # Latest screenshot is always in clipboard
        }

    def clear_buffer(self) -> Dict[str, Any]:
        """Clear screenshot buffer and cleanup temporary files."""
        try:
            self.latest_screenshot = None
            self.latest_timestamp = None

            # Delete all temporary screenshots
            temp_files = list(self.cache_dir.glob("screenshot_temp_*.png"))
            for f in temp_files:
                try:
                    f.unlink()
                except Exception:
                    pass

            return {
                "success": True,
                "cleared_count": len(temp_files),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def copy_latest_to_clipboard(self) -> Dict[str, Any]:
        """Copy latest screenshot to clipboard."""
        if not self.latest_screenshot:
            return {
                "success": False,
                "error": "No screenshot in buffer",
            }

        return self._copy_to_clipboard(self.latest_screenshot)

    # ========================================================================
    # INTERNAL IMPLEMENTATION
    # ========================================================================

    def _take_screenshot_impl(
        self, save_path: Path, region: Optional[Tuple[int, int, int, int]] = None
    ) -> bool:
        """Take actual screenshot using available tool."""
        try:
            # Try gnome-screenshot first (GNOME standard)
            if self._command_exists("gnome-screenshot"):
                cmd = ["gnome-screenshot", "-f", str(save_path)]
                if region:
                    x, y, w, h = region
                    cmd.extend(["-a", f"{x},{y},{w},{h}"])
                subprocess.run(cmd, capture_output=True, timeout=10)
                return save_path.exists()

            # Try scrot (lightweight, works everywhere)
            if self._command_exists("scrot"):
                cmd = ["scrot", str(save_path)]
                if region:
                    x, y, w, h = region
                    # scrot uses -c for crop: geometry WIDTHxHEIGHT+X+Y
                    cmd.extend(["-c"])
                subprocess.run(cmd, capture_output=True, timeout=10)
                return save_path.exists()

            # Try ImageMagick import
            if self._command_exists("import"):
                if region:
                    x, y, w, h = region
                    cmd = [
                        "import",
                        "-window",
                        "root",
                        "-crop",
                        f"{w}x{h}+{x}+{y}",
                        str(save_path),
                    ]
                else:
                    cmd = ["import", "-window", "root", str(save_path)]
                subprocess.run(cmd, capture_output=True, timeout=10)
                return save_path.exists()

            return False

        except Exception:
            return False

    def _copy_to_clipboard(self, image_path: Path) -> Dict[str, Any]:
        """Copy image to clipboard using available tool."""
        try:
            image_path = Path(image_path)

            if not image_path.exists():
                return {
                    "success": False,
                    "error": f"Image not found: {image_path}",
                }

            # Try wl-copy first (Wayland standard - your system)
            if self._command_exists("wl-copy"):
                with open(image_path, "rb") as f:
                    result = subprocess.run(
                        ["wl-copy"],
                        stdin=f,
                        capture_output=True,
                        timeout=5,
                    )
                    if result.returncode == 0:
                        return {
                            "success": True,
                            "path": str(image_path),
                            "clipboard_tool": "wl-copy",
                        }

            # Try xclip (X11)
            if self._command_exists("xclip"):
                with open(image_path, "rb") as f:
                    result = subprocess.run(
                        ["xclip", "-selection", "clipboard", "-t", "image/png"],
                        stdin=f,
                        capture_output=True,
                        timeout=5,
                    )
                    if result.returncode == 0:
                        return {
                            "success": True,
                            "path": str(image_path),
                            "clipboard_tool": "xclip",
                        }

            return {
                "success": False,
                "error": "No clipboard tool available (wl-copy or xclip)",
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _cleanup_old_temp(self) -> None:
        """Auto-delete old temporary screenshots."""
        try:
            now = time.time()
            temp_files = sorted(
                self.cache_dir.glob("screenshot_temp_*.png"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )

            # Keep only max_temp_screenshots files
            for f in temp_files[self.max_temp_screenshots :]:
                try:
                    f.unlink()
                except Exception:
                    pass

            # Delete files older than retention period
            for f in temp_files:
                try:
                    age = now - f.stat().st_mtime
                    if age > self.temp_retention_seconds:
                        f.unlink()
                except Exception:
                    pass

        except Exception:
            pass

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
