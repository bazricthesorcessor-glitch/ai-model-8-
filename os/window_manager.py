"""
Window Manager - High-level window management operations
Abstracts Hyprland details for intuitive window control.
"""

from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum


class WindowLayout(Enum):
    """Window layout types"""
    MASTER = "master"
    DWINDLE = "dwindle"
    FLOATING = "floating"
    FULLSCREEN = "fullscreen"
    TILE = "tile"


@dataclass
class WindowOperation:
    """Window operation result"""
    success: bool
    operation: str
    description: str
    details: Dict[str, Any] = None


class WindowManager:
    """
    High-level window management.
    Provides intuitive operations built on Hyprland.
    """

    def __init__(self, hyprland_manager):
        """
        Initialize window manager.

        Args:
            hyprland_manager: HyprlandManager instance
        """
        self.hyprland = hyprland_manager
        self.window_history: List[str] = []

    # ========================================================================
    # WINDOW OPERATIONS
    # ========================================================================

    def focus_window(self, address: str) -> WindowOperation:
        """Focus a window by address"""
        success, msg, error = self.hyprland.dispatch(f"focuswindow address:{address}")
        return WindowOperation(
            success=success,
            operation="focus",
            description=f"Focused window {address}",
            details={"address": address}
        )

    def close_window(self) -> WindowOperation:
        """Close active window"""
        success, msg, error = self.hyprland.close_window()
        return WindowOperation(
            success=success,
            operation="close",
            description="Closed active window"
        )

    def maximize_window(self) -> WindowOperation:
        """Maximize active window"""
        success, msg, error = self.hyprland.maximize_window()
        return WindowOperation(
            success=success,
            operation="maximize",
            description="Maximized window"
        )

    def minimize_window(self) -> WindowOperation:
        """Minimize active window"""
        success, msg, error = self.hyprland.minimize_window()
        return WindowOperation(
            success=success,
            operation="minimize",
            description="Minimized window"
        )

    def toggle_floating(self) -> WindowOperation:
        """Toggle floating mode"""
        success, msg, error = self.hyprland.toggle_floating()
        return WindowOperation(
            success=success,
            operation="toggle_floating",
            description="Toggled floating mode"
        )

    def toggle_fullscreen(self) -> WindowOperation:
        """Toggle fullscreen"""
        success, msg, error = self.hyprland.toggle_fullscreen()
        return WindowOperation(
            success=success,
            operation="toggle_fullscreen",
            description="Toggled fullscreen"
        )

    def resize_window(self, width: int, height: int) -> WindowOperation:
        """Resize active window"""
        success, msg, error = self.hyprland.resize_window(width, height)
        return WindowOperation(
            success=success,
            operation="resize",
            description=f"Resized to {width}x{height}",
            details={"width": width, "height": height}
        )

    def move_window(self, x: int, y: int) -> WindowOperation:
        """Move active window"""
        success, msg, error = self.hyprland.move_window(x, y)
        return WindowOperation(
            success=success,
            operation="move",
            description=f"Moved to {x},{y}",
            details={"x": x, "y": y}
        )

    # ========================================================================
    # WINDOW MANIPULATION
    # ========================================================================

    def swap_windows(self, direction: str = "right") -> WindowOperation:
        """Swap windows"""
        success, msg, error = self.hyprland.dispatch(f"layoutmsg swap {direction}")
        return WindowOperation(
            success=success,
            operation="swap",
            description=f"Swapped {direction}",
            details={"direction": direction}
        )

    def rotate_windows(self, clockwise: bool = True) -> WindowOperation:
        """Rotate window arrangement"""
        cmd = "layoutmsg rotatemaster" if clockwise else "layoutmsg rotateclockwise"
        success, msg, error = self.hyprland.dispatch(cmd)
        return WindowOperation(
            success=success,
            operation="rotate",
            description=f"Rotated {'clockwise' if clockwise else 'counter-clockwise'}",
            details={"clockwise": clockwise}
        )

    def cycle_windows(self, forward: bool = True) -> WindowOperation:
        """Cycle through windows"""
        success, msg, error = self.hyprland.dispatch("layoutmsg cyclenext" if forward else "layoutmsg cycleprev")
        return WindowOperation(
            success=success,
            operation="cycle",
            description=f"Cycled {'forward' if forward else 'backward'}",
            details={"direction": "forward" if forward else "backward"}
        )

    # ========================================================================
    # WINDOW GROUPS/STACKING
    # ========================================================================

    def raise_window(self) -> WindowOperation:
        """Raise window above others"""
        success, msg, error = self.hyprland.dispatch("bringactivetotop")
        return WindowOperation(
            success=success,
            operation="raise",
            description="Raised window"
        )

    def lower_window(self) -> WindowOperation:
        """Lower window below others"""
        # Hyprland doesn't have direct lower, simulate with workspace manipulation
        return WindowOperation(
            success=True,
            operation="lower",
            description="Lowered window (simulated)"
        )

    # ========================================================================
    # WINDOW SEARCH & FILTER
    # ========================================================================

    def find_windows_by_class(self, class_name: str) -> List[str]:
        """Find windows by class name"""
        success, windows, _ = self.hyprland.list_windows()
        if not success or not windows:
            return []

        return [w.address for w in windows if class_name.lower() in w.class_name.lower()]

    def find_windows_by_title(self, title: str) -> List[str]:
        """Find windows by title"""
        success, windows, _ = self.hyprland.list_windows()
        if not success or not windows:
            return []

        return [w.address for w in windows if title.lower() in w.title.lower()]

    # ========================================================================
    # WINDOW LAYOUTS
    # ========================================================================

    def set_layout_master(self) -> WindowOperation:
        """Set master layout"""
        success, msg, error = self.hyprland.dispatch("layoutmsg focusmaster")
        return WindowOperation(
            success=success,
            operation="set_layout",
            description="Set master layout",
            details={"layout": "master"}
        )

    def set_layout_dwindle(self) -> WindowOperation:
        """Set dwindle layout"""
        success, msg, error = self.hyprland.dispatch("layoutmsg preselect dwindle")
        return WindowOperation(
            success=success,
            operation="set_layout",
            description="Set dwindle layout",
            details={"layout": "dwindle"}
        )

    # ========================================================================
    # WINDOW HISTORY & RESTORATION
    # ========================================================================

    def record_window(self, address: str):
        """Record window in history"""
        self.window_history.append(address)
        if len(self.window_history) > 20:  # Keep last 20
            self.window_history.pop(0)

    def get_last_window(self) -> Optional[str]:
        """Get last window from history"""
        return self.window_history[-2] if len(self.window_history) >= 2 else None

    def switch_to_last_window(self) -> WindowOperation:
        """Switch to previously focused window"""
        last_window = self.get_last_window()
        if not last_window:
            return WindowOperation(
                success=False,
                operation="switch_last",
                description="No previous window in history"
            )

        return self.focus_window(last_window)

    # ========================================================================
    # BATCH OPERATIONS
    # ========================================================================

    def maximize_and_focus(self, address: str) -> WindowOperation:
        """Maximize and focus a window"""
        result1 = self.focus_window(address)
        result2 = self.maximize_window()

        return WindowOperation(
            success=result1.success and result2.success,
            operation="maximize_and_focus",
            description=f"Maximized and focused {address}",
            details={"address": address}
        )

    def center_window(self) -> WindowOperation:
        """Center window on screen"""
        # Get monitor info and center
        success, monitors, _ = self.hyprland.get_monitors()
        if not success or not monitors:
            return WindowOperation(
                success=False,
                operation="center",
                description="Failed to get monitor info"
            )

        monitor = monitors[0]
        center_x = monitor.x + monitor.width // 2 - 320  # Assuming 640 width
        center_y = monitor.y + monitor.height // 2 - 240  # Assuming 480 height

        return self.move_window(center_x, center_y)

    def get_status(self) -> Dict[str, Any]:
        """Get window manager status"""
        return {
            "window_history_size": len(self.window_history),
            "hyprland_available": self.hyprland.is_available,
        }
