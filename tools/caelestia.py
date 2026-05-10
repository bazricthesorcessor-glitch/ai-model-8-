"""
Caelestia Shell Commands API

High-level API for controlling Caelestia shell and system.
Wraps caelestia CLI commands for programmatic access.

Example:
    from tools.caelestia import CaelestiaShell

    shell = CaelestiaShell()
    shell.clear_notifications()
    shell.set_wallpaper("/path/to/image.jpg")
    shell.send_toast("Success", "Operation completed", icon="emblem-ok")
"""

import subprocess
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class ToastType(Enum):
    """Toast notification types"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warn"
    ERROR = "error"


class GameMode(Enum):
    """Game mode state"""
    TOGGLE = "toggle"
    ENABLE = "enable"
    DISABLE = "disable"


class MediaAction(Enum):
    """Media player actions"""
    PLAY = "play"
    PAUSE = "pause"
    PLAY_PAUSE = "playPause"
    STOP = "stop"
    NEXT = "next"
    PREVIOUS = "previous"


@dataclass
class ResizeConfig:
    """Window resize configuration"""
    pattern: str  # 'active', 'pip', or title pattern
    match_type: str  # titleContains, titleExact, titleRegex, initialTitle
    width: int
    height: int
    actions: List[str]  # float, center, pip


class CaelestiaShell:
    """Interface to Caelestia shell control"""

    def __init__(self, timeout: int = 5):
        """
        Initialize Caelestia shell interface

        Args:
            timeout: Command execution timeout in seconds
        """
        self.timeout = timeout
        self._ensure_running()

    def _execute(self, *args) -> str:
        """Execute caelestia command"""
        try:
            result = subprocess.run(
                ["caelestia"] + list(args),
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Caelestia command timed out: {args}")
        except Exception as e:
            raise RuntimeError(f"Caelestia command failed: {e}")

    def _shell_ipc(self, command: str) -> str:
        """Send IPC message to shell"""
        return self._execute("shell", command)

    def _ensure_running(self) -> None:
        """Ensure shell daemon is running"""
        try:
            self._shell_ipc("notifs.isDndEnabled")
        except:
            # Start daemon if not running
            subprocess.run(
                ["caelestia", "shell", "-d"],
                capture_output=True,
                timeout=5
            )

    # ===== NOTIFICATIONS =====

    def clear_notifications(self) -> bool:
        """Clear all notifications"""
        try:
            self._shell_ipc("notifs.clear")
            return True
        except:
            return False

    def toggle_dnd(self) -> bool:
        """Toggle Do Not Disturb mode"""
        try:
            self._shell_ipc("notifs.toggleDnd")
            return True
        except:
            return False

    def enable_dnd(self) -> bool:
        """Enable Do Not Disturb mode"""
        try:
            self._shell_ipc("notifs.enableDnd")
            return True
        except:
            return False

    def disable_dnd(self) -> bool:
        """Disable Do Not Disturb mode"""
        try:
            self._shell_ipc("notifs.disableDnd")
            return True
        except:
            return False

    def is_dnd_enabled(self) -> bool:
        """Check if DND mode is enabled"""
        try:
            result = self._shell_ipc("notifs.isDndEnabled")
            return result.lower() in ("true", "1", "yes")
        except:
            return False

    def send_toast(
        self,
        title: str,
        message: str,
        toast_type: ToastType = ToastType.INFO,
        icon: str = "dialog-information"
    ) -> bool:
        """
        Send a toast notification

        Args:
            title: Toast title
            message: Toast message
            toast_type: Type of toast (INFO, SUCCESS, WARNING, ERROR)
            icon: Icon name (see CAELESTIA_COMMAND_REFERENCE.md)

        Returns:
            True if successful
        """
        try:
            cmd = f"toaster.{toast_type.value} \"{title}\" \"{message}\" \"{icon}\""
            self._shell_ipc(cmd)
            return True
        except:
            return False

    # ===== DISPLAY & APPEARANCE =====

    def set_wallpaper(self, path: str, smart_scheme: bool = True) -> bool:
        """
        Set wallpaper from file

        Args:
            path: Full path to wallpaper image
            smart_scheme: Auto-adjust color scheme based on wallpaper

        Returns:
            True if successful
        """
        try:
            args = ["wallpaper", "-f", path]
            if not smart_scheme:
                args.append("-N")
            self._execute(*args)
            return True
        except:
            return False

    def set_random_wallpaper(
        self,
        directory: str,
        smart_scheme: bool = True,
        threshold: int = 0
    ) -> bool:
        """
        Set random wallpaper from directory

        Args:
            directory: Directory containing wallpapers
            smart_scheme: Auto-adjust color scheme
            threshold: Minimum image size threshold (0-100%)

        Returns:
            True if successful
        """
        try:
            args = ["wallpaper", "-r", directory]
            if not smart_scheme:
                args.append("-N")
            if threshold > 0:
                args.extend(["-t", str(threshold)])
            self._execute(*args)
            return True
        except:
            return False

    def get_wallpaper(self) -> Optional[str]:
        """Get current wallpaper path"""
        try:
            return self._shell_ipc("wallpaper.get")
        except:
            return None

    def list_wallpapers(self) -> List[str]:
        """List available wallpapers"""
        try:
            result = self._shell_ipc("wallpaper.list")
            return result.split("\n") if result else []
        except:
            return []

    def set_brightness(self, value: int) -> bool:
        """
        Set display brightness

        Args:
            value: Brightness 0-100

        Returns:
            True if successful
        """
        try:
            cmd = f"brightness.set \"{value}\""
            self._shell_ipc(cmd)
            return True
        except:
            return False

    def get_brightness(self) -> Optional[float]:
        """Get current brightness level (0-100)"""
        try:
            result = self._shell_ipc("brightness.get")
            return float(result)
        except:
            return None

    def set_brightness_for_monitor(self, monitor: str, value: int) -> bool:
        """Set brightness for specific monitor"""
        try:
            cmd = f"brightness.setFor \"{monitor}\" \"{value}\""
            self._shell_ipc(cmd)
            return True
        except:
            return False

    def get_brightness_for_monitor(self, monitor: str) -> Optional[float]:
        """Get brightness for specific monitor"""
        try:
            cmd = f"brightness.getFor \"{monitor}\""
            result = self._shell_ipc(cmd)
            return float(result)
        except:
            return None

    # ===== MEDIA CONTROL =====

    def media_action(self, action: MediaAction) -> bool:
        """Execute media player action"""
        try:
            self._shell_ipc(f"mpris.{action.value}")
            return True
        except:
            return False

    def play_media(self) -> bool:
        """Play media"""
        return self.media_action(MediaAction.PLAY)

    def pause_media(self) -> bool:
        """Pause media"""
        return self.media_action(MediaAction.PAUSE)

    def toggle_media(self) -> bool:
        """Toggle play/pause"""
        return self.media_action(MediaAction.PLAY_PAUSE)

    def next_track(self) -> bool:
        """Skip to next track"""
        return self.media_action(MediaAction.NEXT)

    def previous_track(self) -> bool:
        """Go to previous track"""
        return self.media_action(MediaAction.PREVIOUS)

    def stop_media(self) -> bool:
        """Stop media"""
        return self.media_action(MediaAction.STOP)

    def get_active_player(self) -> Optional[str]:
        """Get active media player name"""
        try:
            return self._shell_ipc("mpris.getActive \"identity\"")
        except:
            return None

    def list_players(self) -> List[str]:
        """List all available media players"""
        try:
            result = self._shell_ipc("mpris.list")
            return result.split("\n") if result else []
        except:
            return []

    # ===== SCREEN CONTROL =====

    def lock_screen(self) -> bool:
        """Lock the screen"""
        try:
            self._shell_ipc("lock.lock")
            return True
        except:
            return False

    def unlock_screen(self) -> bool:
        """Unlock the screen"""
        try:
            self._shell_ipc("lock.unlock")
            return True
        except:
            return False

    def is_screen_locked(self) -> bool:
        """Check if screen is locked"""
        try:
            result = self._shell_ipc("lock.isLocked")
            return result.lower() in ("true", "1", "yes")
        except:
            return False

    # ===== SYSTEM MODES =====

    def toggle_game_mode(self) -> bool:
        """Toggle game mode"""
        try:
            self._shell_ipc("gameMode.toggle")
            return True
        except:
            return False

    def enable_game_mode(self) -> bool:
        """Enable game mode (no notifications, optimize perf)"""
        try:
            self._shell_ipc("gameMode.enable")
            return True
        except:
            return False

    def disable_game_mode(self) -> bool:
        """Disable game mode"""
        try:
            self._shell_ipc("gameMode.disable")
            return True
        except:
            return False

    def is_game_mode_enabled(self) -> bool:
        """Check if game mode is enabled"""
        try:
            result = self._shell_ipc("gameMode.isEnabled")
            return result.lower() in ("true", "1", "yes")
        except:
            return False

    def toggle_idle_inhibitor(self) -> bool:
        """Toggle idle inhibitor (prevent sleep)"""
        try:
            self._shell_ipc("idleInhibitor.toggle")
            return True
        except:
            return False

    def enable_idle_inhibitor(self) -> bool:
        """Prevent system from sleeping"""
        try:
            self._shell_ipc("idleInhibitor.enable")
            return True
        except:
            return False

    def disable_idle_inhibitor(self) -> bool:
        """Allow system to sleep"""
        try:
            self._shell_ipc("idleInhibitor.disable")
            return True
        except:
            return False

    # ===== SCREENSHOTS & RECORDING =====

    def screenshot(self, region: bool = False, freeze: bool = False) -> bool:
        """
        Take a screenshot

        Args:
            region: Select region to screenshot
            freeze: Freeze screen while selecting

        Returns:
            True if successful
        """
        try:
            args = ["screenshot"]
            if region:
                args.append("-r")
            if freeze:
                args.append("-f")
            self._execute(*args)
            return True
        except:
            return False

    def start_recording(
        self,
        region: bool = False,
        audio: bool = False,
        pause: bool = False
    ) -> bool:
        """
        Start screen recording

        Args:
            region: Record selected region
            audio: Include audio
            pause: Pause/resume recording

        Returns:
            True if successful
        """
        try:
            args = ["record"]
            if region:
                args.append("-r")
            if audio:
                args.append("-s")
            if pause:
                args.append("-p")
            self._execute(*args)
            return True
        except:
            return False

    # ===== WINDOW MANAGEMENT =====

    def resize_window(self, config: ResizeConfig) -> bool:
        """
        Resize and reposition window

        Args:
            config: ResizeConfig with pattern, match type, dimensions, actions

        Returns:
            True if successful
        """
        try:
            args = [
                "resizer",
                config.pattern,
                config.match_type,
                str(config.width),
                str(config.height),
                ",".join(config.actions)
            ]
            self._execute(*args)
            return True
        except:
            return False

    def start_resizer_daemon(self) -> bool:
        """Start the window resizer daemon"""
        try:
            self._execute("resizer", "-d")
            return True
        except:
            return False

    # ===== UTILITIES =====

    def open_clipboard_manager(self) -> bool:
        """Open clipboard history manager"""
        try:
            self._execute("clipboard")
            return True
        except:
            return False

    def open_emoji_picker(self) -> bool:
        """Open emoji/glyph picker"""
        try:
            self._execute("emoji", "-p")
            return True
        except:
            return False

    def open_color_picker(self) -> bool:
        """Open color picker"""
        try:
            self._shell_ipc("picker.open")
            return True
        except:
            return False

    def toggle_special_workspace(self) -> bool:
        """Toggle special/overlay workspace"""
        try:
            self._execute("toggle", "specialws")
            return True
        except:
            return False

    def toggle_drawer(self, drawer_name: str) -> bool:
        """
        Toggle UI drawer

        Args:
            drawer_name: Name of drawer (dashboard, settings, launcher, etc)

        Returns:
            True if successful
        """
        try:
            self._shell_ipc(f"drawers.toggle \"{drawer_name}\"")
            return True
        except:
            return False

    def list_drawers(self) -> List[str]:
        """List available drawers"""
        try:
            result = self._shell_ipc("drawers.list")
            return result.split("\n") if result else []
        except:
            return []

    def open_control_center(self) -> bool:
        """Open system control center"""
        try:
            self._shell_ipc("controlCenter.open")
            return True
        except:
            return False


# Convenience singleton
_shell: Optional[CaelestiaShell] = None


def get_shell() -> CaelestiaShell:
    """Get or create shell instance"""
    global _shell
    if _shell is None:
        _shell = CaelestiaShell()
    return _shell
