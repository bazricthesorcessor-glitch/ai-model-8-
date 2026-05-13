"""
Caelestia UI Controller - Complete system control for Caelestia shell.

Controls:
- Brightness, volume, audio
- Window management (layout, splits, gaps)
- Gestures and keyboard shortcuts
- Workspace management
- Browser automation
- System settings
- UI toggles for everything

Usage:
    from ui.caelestia_controller import CaelestiaController

    controller = CaelestiaController()
    controller.increase_brightness()
    controller.toggle_fullscreen()
    controller.set_volume(0.5)
"""

import json
import subprocess
import time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from executor.input_controller import InputController
from config.paths import path_of


# ============================================================================
# ENUMS AND DATA CLASSES
# ============================================================================

class ToggleState(Enum):
    """Toggle state values"""
    ON = True
    OFF = False
    TOGGLE = "toggle"


@dataclass
class BrightnessConfig:
    """Brightness control configuration"""
    min_level: float = 0.0
    max_level: float = 1.0
    current_level: float = 0.8
    increment: float = 0.1
    enabled: bool = True


@dataclass
class VolumeConfig:
    """Volume control configuration"""
    min_level: float = 0.0
    max_level: float = 1.0
    current_level: float = 0.7
    increment: float = 0.05
    muted: bool = False
    enabled: bool = True


@dataclass
class WindowLayoutConfig:
    """Window layout configuration"""
    layout: str = "master-slave"  # master-slave, tile, floating
    master_ratio: float = 0.6
    gaps: int = 10
    auto_focus: bool = True
    focus_new_windows: bool = True
    enabled: bool = True


@dataclass
class SplitConfig:
    """Split management configuration"""
    enabled: bool = True
    default_mode: str = "master_slave"
    directions: List[str] = None
    resize_step: int = 50
    gap_step: int = 5

    def __post_init__(self):
        if self.directions is None:
            self.directions = ["left", "right", "up", "down"]


@dataclass
class GestureConfig:
    """Gesture configuration"""
    enabled: bool = True
    celestial_dots: bool = True
    swipe_threshold: int = 20
    circle_threshold: int = 100
    timeout_ms: int = 500
    mappings: Dict[str, str] = None

    def __post_init__(self):
        if self.mappings is None:
            self.mappings = {
                "swipe_up": "maximize_window",
                "swipe_down": "minimize_window",
                "swipe_left": "prev_workspace",
                "swipe_right": "next_workspace",
                "circle_cw": "rotate_windows",
                "circle_ccw": "rotate_windows_reverse",
            }


@dataclass
class KeyboardConfig:
    """Keyboard shortcuts configuration"""
    enabled: bool = True
    modifier: str = "super"
    bindings: Dict[str, str] = None

    def __post_init__(self):
        if self.bindings is None:
            self.bindings = {
                "super+q": "close_window",
                "super+f": "toggle_fullscreen",
                "super+space": "open_dolphin",
                "super+1": "workspace_1",
                "super+2": "workspace_2",
                "super+3": "workspace_3",
                "super+h": "split_left",
                "super+j": "split_down",
                "super+k": "split_up",
                "super+l": "split_right",
            }


@dataclass
class WorkspaceConfig:
    """Workspace configuration"""
    count: int = 10
    auto_create: bool = True
    persistent: bool = True
    current_workspace: int = 1
    enabled: bool = True


# ============================================================================
# CAELESTIA CONTROLLER
# ============================================================================

class CaelestiaController:
    """
    Master controller for Caelestia UI, browser automation, and system control.

    Every action can be toggled on/off. Executor sends simple commands like
    "increase brightness" which get translated to actual system actions.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Caelestia controller.

        Args:
            config_path: Path to shell.json config file
        """
        self.config_path = Path(config_path) if config_path else path_of("shell")
        self.shell_config = self._load_config()

        # Initialize all configuration sections
        self.brightness = BrightnessConfig()
        self.volume = VolumeConfig()
        self.window_layout = WindowLayoutConfig()
        self.splits = SplitConfig()
        self.gestures = GestureConfig()
        self.keyboard = KeyboardConfig()
        self.workspaces = WorkspaceConfig()

        # State tracking
        self.state: Dict[str, Any] = {
            "fullscreen": False,
            "floating": False,
            "game_mode": False,
            "dnd_mode": False,
            "vpn_connected": False,
            "wifi_enabled": True,
            "bluetooth_enabled": True,
            "microphone_enabled": True,
        }

        # Browser automation
        self.browser = BrowserAutomation()

        # Load shell config values
        self._apply_shell_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load shell.json configuration."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}

    def _apply_shell_config(self) -> None:
        """Apply shell.json settings to controller."""
        if not self.shell_config:
            return

        # Apply window management config
        wm = self.shell_config.get("window_management", {})
        if wm:
            self.window_layout.layout = wm.get("layout", self.window_layout.layout)
            self.window_layout.master_ratio = wm.get("master_ratio", self.window_layout.master_ratio)
            self.window_layout.gaps = wm.get("gaps", self.window_layout.gaps)
            self.window_layout.auto_focus = wm.get("auto_focus", self.window_layout.auto_focus)

        # Apply split config
        sm = self.shell_config.get("split_management", {})
        if sm:
            self.splits.enabled = sm.get("enabled", self.splits.enabled)
            self.splits.resize_step = sm.get("resize_step", self.splits.resize_step)
            self.splits.gap_step = sm.get("gap_step", self.splits.gap_step)

        # Apply gesture config
        g = self.shell_config.get("gestures", {})
        if g:
            self.gestures.enabled = g.get("enabled", self.gestures.enabled)
            self.gestures.swipe_threshold = g.get("swipe_threshold", self.gestures.swipe_threshold)
            self.gestures.circle_threshold = g.get("circle_threshold", self.gestures.circle_threshold)

        # Apply workspace config
        ws = self.shell_config.get("workspaces", {})
        if ws:
            self.workspaces.count = ws.get("count", self.workspaces.count)
            self.workspaces.auto_create = ws.get("auto_create", self.workspaces.auto_create)
            self.workspaces.persistent = ws.get("persistent", self.workspaces.persistent)

    # ========================================================================
    # BRIGHTNESS CONTROL
    # ========================================================================

    def increase_brightness(self, amount: Optional[float] = None) -> Dict[str, Any]:
        """Increase brightness."""
        if not self.brightness.enabled:
            return {"success": False, "error": "Brightness control disabled"}

        amount = amount or self.brightness.increment
        new_level = min(self.brightness.current_level + amount, self.brightness.max_level)
        return self._set_brightness(new_level)

    def decrease_brightness(self, amount: Optional[float] = None) -> Dict[str, Any]:
        """Decrease brightness."""
        if not self.brightness.enabled:
            return {"success": False, "error": "Brightness control disabled"}

        amount = amount or self.brightness.increment
        new_level = max(self.brightness.current_level - amount, self.brightness.min_level)
        return self._set_brightness(new_level)

    def set_brightness(self, level: float) -> Dict[str, Any]:
        """Set brightness to specific level (0.0-1.0)."""
        level = max(self.brightness.min_level, min(level, self.brightness.max_level))
        return self._set_brightness(level)

    def _set_brightness(self, level: float) -> Dict[str, Any]:
        """Internal brightness setter."""
        try:
            # Use brightnessctl
            percent = int(level * 100)
            subprocess.run(
                ["brightnessctl", "set", f"{percent}%"],
                capture_output=True,
                timeout=5
            )
            self.brightness.current_level = level
            return {
                "success": True,
                "action": "set_brightness",
                "level": level,
                "percent": percent,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def toggle_brightness(self) -> Dict[str, Any]:
        """Toggle brightness on/off."""
        if not self.brightness.enabled:
            return {"success": False, "error": "Brightness control disabled"}

        self.brightness.enabled = not self.brightness.enabled
        return {"success": True, "brightness_enabled": self.brightness.enabled}

    # ========================================================================
    # VOLUME CONTROL
    # ========================================================================

    def increase_volume(self, amount: Optional[float] = None) -> Dict[str, Any]:
        """Increase volume."""
        if not self.volume.enabled:
            return {"success": False, "error": "Volume control disabled"}

        amount = amount or self.volume.increment
        new_level = min(self.volume.current_level + amount, self.volume.max_level)
        return self._set_volume(new_level)

    def decrease_volume(self, amount: Optional[float] = None) -> Dict[str, Any]:
        """Decrease volume."""
        if not self.volume.enabled:
            return {"success": False, "error": "Volume control disabled"}

        amount = amount or self.volume.increment
        new_level = max(self.volume.current_level - amount, self.volume.min_level)
        return self._set_volume(new_level)

    def set_volume(self, level: float) -> Dict[str, Any]:
        """Set volume to specific level (0.0-1.0)."""
        level = max(self.volume.min_level, min(level, self.volume.max_level))
        return self._set_volume(level)

    def _set_volume(self, level: float) -> Dict[str, Any]:
        """Internal volume setter."""
        try:
            percent = int(level * 100)
            subprocess.run(
                ["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{percent}%"],
                capture_output=True,
                timeout=5
            )
            self.volume.current_level = level
            return {
                "success": True,
                "action": "set_volume",
                "level": level,
                "percent": percent,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def toggle_mute(self) -> Dict[str, Any]:
        """Toggle mute."""
        if not self.volume.enabled:
            return {"success": False, "error": "Volume control disabled"}

        try:
            subprocess.run(
                ["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"],
                capture_output=True,
                timeout=5
            )
            self.volume.muted = not self.volume.muted
            return {"success": True, "muted": self.volume.muted}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def toggle_volume(self) -> Dict[str, Any]:
        """Toggle volume control on/off."""
        self.volume.enabled = not self.volume.enabled
        return {"success": True, "volume_enabled": self.volume.enabled}

    # ========================================================================
    # WINDOW MANAGEMENT
    # ========================================================================

    def toggle_fullscreen(self) -> Dict[str, Any]:
        """Toggle fullscreen mode."""
        if not self.window_layout.enabled:
            return {"success": False, "error": "Window management disabled"}

        try:
            InputController.key_combination("super+f")
            self.state["fullscreen"] = not self.state["fullscreen"]
            return {"success": True, "fullscreen": self.state["fullscreen"]}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def toggle_floating(self) -> Dict[str, Any]:
        """Toggle floating window mode."""
        if not self.window_layout.enabled:
            return {"success": False, "error": "Window management disabled"}

        try:
            # Note: super+space is now mapped to open_dolphin
            # For toggle_floating, use a different approach or keybind
            # This function is kept for API compatibility but needs keybind mapping update
            return {"success": False, "error": "toggle_floating keybind not configured"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def close_window(self) -> Dict[str, Any]:
        """Close active window."""
        if not self.window_layout.enabled:
            return {"success": False, "error": "Window management disabled"}

        try:
            InputController.key_combination("super+q")
            return {"success": True, "action": "close_window"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def maximize_window(self) -> Dict[str, Any]:
        """Maximize active window."""
        try:
            subprocess.run(
                ["hyprctl", "dispatch", "fullscreen", "1"],
                capture_output=True,
                timeout=5
            )
            return {"success": True, "action": "maximize_window"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def minimize_window(self) -> Dict[str, Any]:
        """Minimize active window."""
        try:
            subprocess.run(
                ["hyprctl", "dispatch", "movetoworkspace", "special"],
                capture_output=True,
                timeout=5
            )
            return {"success": True, "action": "minimize_window"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def set_layout(self, layout: str) -> Dict[str, Any]:
        """Set window layout (master-slave, tile, floating)."""
        if layout not in ["master-slave", "tile", "floating"]:
            return {"success": False, "error": f"Unknown layout: {layout}"}

        self.window_layout.layout = layout
        return {"success": True, "layout": layout}

    def set_master_ratio(self, ratio: float) -> Dict[str, Any]:
        """Set master window ratio (0.0-1.0)."""
        ratio = max(0.1, min(ratio, 0.9))
        self.window_layout.master_ratio = ratio
        return {"success": True, "master_ratio": ratio}

    def increase_gaps(self, amount: Optional[int] = None) -> Dict[str, Any]:
        """Increase window gaps."""
        amount = amount or self.splits.gap_step
        new_gap = self.window_layout.gaps + amount
        self.window_layout.gaps = new_gap
        return {"success": True, "gaps": new_gap}

    def decrease_gaps(self, amount: Optional[int] = None) -> Dict[str, Any]:
        """Decrease window gaps."""
        amount = amount or self.splits.gap_step
        new_gap = max(0, self.window_layout.gaps - amount)
        self.window_layout.gaps = new_gap
        return {"success": True, "gaps": new_gap}

    def toggle_window_management(self) -> Dict[str, Any]:
        """Toggle window management on/off."""
        self.window_layout.enabled = not self.window_layout.enabled
        return {"success": True, "window_management_enabled": self.window_layout.enabled}

    # ========================================================================
    # SPLIT MANAGEMENT
    # ========================================================================

    def split_left(self) -> Dict[str, Any]:
        """Create left split."""
        if not self.splits.enabled:
            return {"success": False, "error": "Split management disabled"}

        try:
            InputController.key_combination("super+h")
            return {"success": True, "action": "split_left"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def split_right(self) -> Dict[str, Any]:
        """Create right split."""
        if not self.splits.enabled:
            return {"success": False, "error": "Split management disabled"}

        try:
            InputController.key_combination("super+l")
            return {"success": True, "action": "split_right"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def split_up(self) -> Dict[str, Any]:
        """Create up split."""
        if not self.splits.enabled:
            return {"success": False, "error": "Split management disabled"}

        try:
            InputController.key_combination("super+k")
            return {"success": True, "action": "split_up"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def split_down(self) -> Dict[str, Any]:
        """Create down split."""
        if not self.splits.enabled:
            return {"success": False, "error": "Split management disabled"}

        try:
            InputController.key_combination("super+j")
            return {"success": True, "action": "split_down"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def resize_split(self, direction: str, amount: Optional[int] = None) -> Dict[str, Any]:
        """Resize split in direction (left, right, up, down)."""
        if not self.splits.enabled:
            return {"success": False, "error": "Split management disabled"}

        amount = amount or self.splits.resize_step
        # Hyprland resize dispatch
        try:
            subprocess.run(
                ["hyprctl", "dispatch", "resizeactive", f"{amount} 0"],
                capture_output=True,
                timeout=5
            )
            return {"success": True, "action": "resize_split", "direction": direction, "amount": amount}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def toggle_splits(self) -> Dict[str, Any]:
        """Toggle split management on/off."""
        self.splits.enabled = not self.splits.enabled
        return {"success": True, "splits_enabled": self.splits.enabled}

    # ========================================================================
    # WORKSPACE MANAGEMENT
    # ========================================================================

    def switch_workspace(self, number: int) -> Dict[str, Any]:
        """Switch to workspace N (1-10)."""
        if not self.workspaces.enabled:
            return {"success": False, "error": "Workspace management disabled"}

        if not 1 <= number <= self.workspaces.count:
            return {"success": False, "error": f"Invalid workspace: {number}"}

        try:
            InputController.key_combination(f"super+{number}")
            self.workspaces.current_workspace = number
            return {"success": True, "workspace": number}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def next_workspace(self) -> Dict[str, Any]:
        """Switch to next workspace."""
        if not self.workspaces.enabled:
            return {"success": False, "error": "Workspace management disabled"}

        next_ws = self.workspaces.current_workspace + 1
        if next_ws > self.workspaces.count:
            next_ws = 1
        return self.switch_workspace(next_ws)

    def prev_workspace(self) -> Dict[str, Any]:
        """Switch to previous workspace."""
        if not self.workspaces.enabled:
            return {"success": False, "error": "Workspace management disabled"}

        prev_ws = self.workspaces.current_workspace - 1
        if prev_ws < 1:
            prev_ws = self.workspaces.count
        return self.switch_workspace(prev_ws)

    def toggle_workspaces(self) -> Dict[str, Any]:
        """Toggle workspace management on/off."""
        self.workspaces.enabled = not self.workspaces.enabled
        return {"success": True, "workspaces_enabled": self.workspaces.enabled}

    # ========================================================================
    # GESTURE CONTROL
    # ========================================================================

    def enable_gestures(self) -> Dict[str, Any]:
        """Enable gesture recognition."""
        self.gestures.enabled = True
        return {"success": True, "gestures_enabled": True}

    def disable_gestures(self) -> Dict[str, Any]:
        """Disable gesture recognition."""
        self.gestures.enabled = False
        return {"success": True, "gestures_enabled": False}

    def toggle_gestures(self) -> Dict[str, Any]:
        """Toggle gestures on/off."""
        self.gestures.enabled = not self.gestures.enabled
        return {"success": True, "gestures_enabled": self.gestures.enabled}

    def set_gesture_mapping(self, gesture: str, action: str) -> Dict[str, Any]:
        """Map gesture to action."""
        if gesture not in self.gestures.mappings:
            return {"success": False, "error": f"Unknown gesture: {gesture}"}

        self.gestures.mappings[gesture] = action
        return {"success": True, "gesture": gesture, "action": action}

    # ========================================================================
    # KEYBOARD SHORTCUTS
    # ========================================================================

    def enable_keyboard(self) -> Dict[str, Any]:
        """Enable keyboard shortcuts."""
        self.keyboard.enabled = True
        return {"success": True, "keyboard_enabled": True}

    def disable_keyboard(self) -> Dict[str, Any]:
        """Disable keyboard shortcuts."""
        self.keyboard.enabled = False
        return {"success": True, "keyboard_enabled": False}

    def toggle_keyboard(self) -> Dict[str, Any]:
        """Toggle keyboard shortcuts on/off."""
        self.keyboard.enabled = not self.keyboard.enabled
        return {"success": True, "keyboard_enabled": self.keyboard.enabled}

    # ========================================================================
    # STATE TOGGLES
    # ========================================================================

    def toggle_game_mode(self) -> Dict[str, Any]:
        """Toggle game mode."""
        self.state["game_mode"] = not self.state["game_mode"]
        return {"success": True, "game_mode": self.state["game_mode"]}

    def toggle_dnd_mode(self) -> Dict[str, Any]:
        """Toggle Do Not Disturb mode."""
        self.state["dnd_mode"] = not self.state["dnd_mode"]
        return {"success": True, "dnd_mode": self.state["dnd_mode"]}

    def toggle_wifi(self) -> Dict[str, Any]:
        """Toggle WiFi."""
        try:
            subprocess.run(
                ["nmcli", "radio", "wifi", "on" if not self.state["wifi_enabled"] else "off"],
                capture_output=True,
                timeout=5
            )
            self.state["wifi_enabled"] = not self.state["wifi_enabled"]
            return {"success": True, "wifi_enabled": self.state["wifi_enabled"]}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def toggle_bluetooth(self) -> Dict[str, Any]:
        """Toggle Bluetooth."""
        try:
            subprocess.run(
                ["nmcli", "radio", "bluetooth", "on" if not self.state["bluetooth_enabled"] else "off"],
                capture_output=True,
                timeout=5
            )
            self.state["bluetooth_enabled"] = not self.state["bluetooth_enabled"]
            return {"success": True, "bluetooth_enabled": self.state["bluetooth_enabled"]}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def toggle_microphone(self) -> Dict[str, Any]:
        """Toggle microphone."""
        self.state["microphone_enabled"] = not self.state["microphone_enabled"]
        return {"success": True, "microphone_enabled": self.state["microphone_enabled"]}

    # ========================================================================
    # BROWSER AUTOMATION
    # ========================================================================

    def get_browser(self) -> 'BrowserAutomation':
        """Get browser automation interface."""
        return self.browser

    # ========================================================================
    # STATE AND CONFIG
    # ========================================================================

    def get_state(self) -> Dict[str, Any]:
        """Get current controller state."""
        return {
            "brightness": {
                "level": self.brightness.current_level,
                "enabled": self.brightness.enabled,
            },
            "volume": {
                "level": self.volume.current_level,
                "muted": self.volume.muted,
                "enabled": self.volume.enabled,
            },
            "window_layout": {
                "layout": self.window_layout.layout,
                "master_ratio": self.window_layout.master_ratio,
                "gaps": self.window_layout.gaps,
                "enabled": self.window_layout.enabled,
            },
            "splits": {
                "enabled": self.splits.enabled,
                "resize_step": self.splits.resize_step,
            },
            "workspaces": {
                "current": self.workspaces.current_workspace,
                "count": self.workspaces.count,
                "enabled": self.workspaces.enabled,
            },
            "gestures_enabled": self.gestures.enabled,
            "keyboard_enabled": self.keyboard.enabled,
            "state": self.state,
        }

    def save_config(self, path: Optional[str] = None) -> Dict[str, Any]:
        """Save current configuration to file."""
        path = path or self.config_path
        config = {
            "brightness": asdict(self.brightness),
            "volume": asdict(self.volume),
            "window_layout": asdict(self.window_layout),
            "splits": asdict(self.splits),
            "gestures": asdict(self.gestures),
            "keyboard": asdict(self.keyboard),
            "workspaces": asdict(self.workspaces),
        }

        try:
            with open(path, 'w') as f:
                json.dump(config, f, indent=2, default=str)
            return {"success": True, "saved_to": str(path)}
        except Exception as e:
            return {"success": False, "error": str(e)}


# ============================================================================
# BROWSER AUTOMATION
# ============================================================================

class BrowserAutomation:
    """Browser automation using Selenium-like patterns with keyboard/mouse control."""

    def __init__(self):
        """Initialize browser automation."""
        self.current_url = None
        self.input = InputController

    def navigate(self, url: str) -> Dict[str, Any]:
        """Navigate to URL."""
        try:
            # Open browser (assumes Firefox/Chrome is available)
            subprocess.Popen(["firefox", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.current_url = url
            time.sleep(3)  # Wait for browser to load
            return {"success": True, "url": url}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def click(self, x: int, y: int) -> Dict[str, Any]:
        """Click at coordinates."""
        try:
            self.input.click_at(x, y)
            return {"success": True, "action": "click", "x": x, "y": y}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def type_text(self, text: str, delay: float = 0.05) -> Dict[str, Any]:
        """Type text."""
        try:
            self.input.type_text(text, delay=delay)
            return {"success": True, "action": "type_text", "text_length": len(text)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def scroll(self, direction: str = "down", amount: int = 5) -> Dict[str, Any]:
        """Scroll page."""
        try:
            self.input.scroll_wheel(direction=direction, amount=amount)
            return {"success": True, "action": "scroll", "direction": direction, "amount": amount}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def press_key(self, key: str) -> Dict[str, Any]:
        """Press a key."""
        try:
            self.input.press_key(key)
            return {"success": True, "action": "press_key", "key": key}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def submit_form(self) -> Dict[str, Any]:
        """Submit form (press Enter)."""
        return self.press_key("Return")

    def search(self, term: str) -> Dict[str, Any]:
        """Search (Ctrl+F, type term, press Enter)."""
        try:
            self.input.search_and_type(term)
            return {"success": True, "action": "search", "term": term}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def refresh(self) -> Dict[str, Any]:
        """Refresh page (F5)."""
        try:
            self.input.press_key("F5")
            time.sleep(2)
            return {"success": True, "action": "refresh"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def go_back(self) -> Dict[str, Any]:
        """Go back (Alt+Left)."""
        try:
            self.input.key_combination("alt+Left")
            time.sleep(1)
            return {"success": True, "action": "go_back"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def go_forward(self) -> Dict[str, Any]:
        """Go forward (Alt+Right)."""
        try:
            self.input.key_combination("alt+Right")
            time.sleep(1)
            return {"success": True, "action": "go_forward"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def open_devtools(self) -> Dict[str, Any]:
        """Open developer tools (F12)."""
        try:
            self.input.press_key("F12")
            time.sleep(1)
            return {"success": True, "action": "open_devtools"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def close_tab(self) -> Dict[str, Any]:
        """Close current tab (Ctrl+W)."""
        try:
            self.input.key_combination("ctrl+w")
            return {"success": True, "action": "close_tab"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def new_tab(self) -> Dict[str, Any]:
        """Open new tab (Ctrl+T)."""
        try:
            self.input.key_combination("ctrl+t")
            time.sleep(1)
            return {"success": True, "action": "new_tab"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def select_all(self) -> Dict[str, Any]:
        """Select all (Ctrl+A)."""
        return self.input.select_all()


# ============================================================================
# EXECUTOR INTEGRATION
# ============================================================================

class ExecutorAdapter:
    """Adapt Caelestia commands for executor model."""

    def __init__(self):
        """Initialize adapter."""
        self.controller = CaelestiaController()
        self.command_map = {
            # Brightness
            "increase_brightness": self.controller.increase_brightness,
            "decrease_brightness": self.controller.decrease_brightness,
            "set_brightness": self.controller.set_brightness,
            "toggle_brightness": self.controller.toggle_brightness,

            # Volume
            "increase_volume": self.controller.increase_volume,
            "decrease_volume": self.controller.decrease_volume,
            "set_volume": self.controller.set_volume,
            "toggle_mute": self.controller.toggle_mute,
            "toggle_volume": self.controller.toggle_volume,

            # Windows
            "toggle_fullscreen": self.controller.toggle_fullscreen,
            "toggle_floating": self.controller.toggle_floating,
            "close_window": self.controller.close_window,
            "maximize_window": self.controller.maximize_window,
            "minimize_window": self.controller.minimize_window,

            # Workspaces
            "next_workspace": self.controller.next_workspace,
            "prev_workspace": self.controller.prev_workspace,
            "switch_workspace": self.controller.switch_workspace,

            # Splits
            "split_left": self.controller.split_left,
            "split_right": self.controller.split_right,
            "split_up": self.controller.split_up,
            "split_down": self.controller.split_down,

            # Toggles
            "toggle_game_mode": self.controller.toggle_game_mode,
            "toggle_dnd_mode": self.controller.toggle_dnd_mode,
            "toggle_wifi": self.controller.toggle_wifi,
            "toggle_bluetooth": self.controller.toggle_bluetooth,
            "toggle_microphone": self.controller.toggle_microphone,
        }

    def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Execute command from executor model.

        Example:
            adapter.execute("increase_brightness")
            adapter.execute("set_volume", level=0.5)
            adapter.execute("switch_workspace", number=2)
        """
        handler = self.command_map.get(command)
        if not handler:
            return {"success": False, "error": f"Unknown command: {command}"}

        try:
            return handler(**kwargs) if kwargs else handler()
        except Exception as e:
            return {"success": False, "error": str(e)}


# ============================================================================
# DEMO / TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("CAELESTIA CONTROLLER TEST")
    print("=" * 80)

    controller = CaelestiaController()

    # Test brightness
    print("\n[TEST] Brightness Control")
    print(f"Current brightness: {controller.brightness.current_level}")
    print(controller.increase_brightness())
    print(f"New brightness: {controller.brightness.current_level}")

    # Test volume
    print("\n[TEST] Volume Control")
    print(f"Current volume: {controller.volume.current_level}")
    print(controller.increase_volume())
    print(f"New volume: {controller.volume.current_level}")

    # Test state
    print("\n[TEST] State Information")
    state = controller.get_state()
    print(json.dumps(state, indent=2))

    # Test executor adapter
    print("\n[TEST] Executor Adapter")
    adapter = ExecutorAdapter()
    print(adapter.execute("toggle_game_mode"))
    print(adapter.execute("toggle_wifi"))

    print("\n" + "=" * 80)
    print("TESTS COMPLETE")
    print("=" * 80)
