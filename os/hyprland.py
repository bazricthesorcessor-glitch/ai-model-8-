"""
Hyprland Manager - Core window manager integration
Controls Hyprland through hyprctl with full command support.
"""

import subprocess
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
import json
import os
import time


@dataclass
class Monitor:
    """Monitor information"""
    name: str
    width: int
    height: int
    refresh_rate: float
    x: int
    y: int
    active_workspace: int


@dataclass
class Window:
    """Window information"""
    address: str
    title: str
    class_name: str
    workspace: int
    x: int
    y: int
    width: int
    height: int
    floating: bool
    maximized: bool


@dataclass
class Workspace:
    """Workspace information"""
    id: int
    name: str
    monitor: str
    window_count: int


class HyprlandManager:
    """
    Hyprland Window Manager Control
    Full integration with hyprctl for window management, workspaces, monitors.
    """

    def __init__(self):
        """Initialize Hyprland manager"""
        self.is_available = self._check_hyprland()
        if not self.is_available:
            raise RuntimeError("Hyprland not available or not running")

    def _check_hyprland(self) -> bool:
        """Check if Hyprland is available"""
        try:
            # Check environment variable
            if not os.getenv('HYPRLAND_INSTANCE_SIGNATURE'):
                return False

            # Check hyprctl
            result = subprocess.run(
                ['hyprctl', 'version'],
                capture_output=True,
                text=True,
                timeout=2
            )
            return result.returncode == 0
        except Exception:
            return False

    def _execute_hyprctl(self, command: str) -> Tuple[bool, str, Optional[str]]:
        """Execute hyprctl command"""
        try:
            result = subprocess.run(
                ['hyprctl'] + command.split(),
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                return True, result.stdout.strip(), None
            else:
                return False, None, result.stderr.strip()

        except subprocess.TimeoutExpired:
            return False, None, "Command timeout"
        except Exception as e:
            return False, None, str(e)

    def dispatch(self, command: str) -> Tuple[bool, str, Optional[str]]:
        """Send dispatch command"""
        return self._execute_hyprctl(f"dispatch {command}")

    # ========================================================================
    # WINDOW MANAGEMENT
    # ========================================================================

    def get_active_window(self) -> Tuple[bool, Optional[Window], Optional[str]]:
        """Get currently active window"""
        success, output, error = self._execute_hyprctl("activewindow")
        if not success:
            return False, None, error

        try:
            # Parse output: Window 564fee7d0520 -> CLASS - TITLE
            parts = output.split(' -> ')
            if len(parts) >= 2:
                address = parts[0].replace('Window ', '')
                detail = parts[1]
                class_name = detail.split(' - ')[0] if ' - ' in detail else ""
                title = detail.split(' - ', 1)[1] if ' - ' in detail else detail

                window = Window(
                    address=address,
                    title=title,
                    class_name=class_name,
                    workspace=0,  # Would need additional query
                    x=0, y=0, width=0, height=0,
                    floating=False, maximized=False
                )
                return True, window, None
        except Exception as e:
            return False, None, str(e)

        return False, None, "Failed to parse window info"

    def list_windows(self) -> Tuple[bool, Optional[List[Window]], Optional[str]]:
        """List all windows"""
        success, output, error = self._execute_hyprctl("clients")
        if not success:
            return False, None, error

        windows = []
        # Parse output format
        return True, windows, None

    def maximize_window(self) -> Tuple[bool, str, Optional[str]]:
        """Maximize active window"""
        return self.dispatch("layoutmsg swapwithmaster")

    def minimize_window(self) -> Tuple[bool, str, Optional[str]]:
        """Minimize active window"""
        return self.dispatch("togglespecialworkspace minimized")

    def close_window(self) -> Tuple[bool, str, Optional[str]]:
        """Close active window"""
        return self.dispatch("killactive")

    def toggle_floating(self) -> Tuple[bool, str, Optional[str]]:
        """Toggle floating mode for active window"""
        return self.dispatch("togglefloating")

    def toggle_fullscreen(self) -> Tuple[bool, str, Optional[str]]:
        """Toggle fullscreen for active window"""
        return self.dispatch("fullscreen 0")

    def resize_window(self, width: int, height: int) -> Tuple[bool, str, Optional[str]]:
        """Resize active window"""
        return self.dispatch(f"resizewindowpixel {width} {height}")

    def move_window(self, x: int, y: int) -> Tuple[bool, str, Optional[str]]:
        """Move active window to position"""
        return self.dispatch(f"movewindowpixel {x} {y}")

    # ========================================================================
    # WORKSPACE MANAGEMENT
    # ========================================================================

    def get_workspaces(self) -> Tuple[bool, Optional[List[Workspace]], Optional[str]]:
        """Get all workspaces"""
        success, output, error = self._execute_hyprctl("workspaces")
        if not success:
            return False, None, error

        workspaces = []
        try:
            for line in output.split('\n'):
                if 'workspace ID' in line:
                    # Parse: workspace ID 1 (name: "1") on monitor DP-1
                    parts = line.split()
                    ws_id = int(parts[2])
                    monitor = parts[-1]
                    workspaces.append(Workspace(
                        id=ws_id,
                        name=str(ws_id),
                        monitor=monitor,
                        window_count=0
                    ))
            return True, workspaces, None
        except Exception as e:
            return False, None, str(e)

    def switch_workspace(self, workspace_id: int) -> Tuple[bool, str, Optional[str]]:
        """Switch to workspace"""
        return self.dispatch(f"workspace {workspace_id}")

    def move_window_to_workspace(self, workspace_id: int) -> Tuple[bool, str, Optional[str]]:
        """Move active window to workspace"""
        return self.dispatch(f"movetoworkspace {workspace_id}")

    def create_workspace(self, workspace_id: int) -> Tuple[bool, str, Optional[str]]:
        """Create new workspace"""
        return self.dispatch(f"workspace {workspace_id}")

    # ========================================================================
    # MONITOR/DISPLAY MANAGEMENT
    # ========================================================================

    def get_monitors(self) -> Tuple[bool, Optional[List[Monitor]], Optional[str]]:
        """Get all monitors"""
        success, output, error = self._execute_hyprctl("monitors")
        if not success:
            return False, None, error

        monitors = []
        try:
            current_monitor = None
            for line in output.split('\n'):
                if 'Monitor' in line and '(' in line:
                    # Monitor DP-1 (HDMI-1): 1920x1080@60.00
                    parts = line.split()
                    name = parts[1].rstrip(':')
                    res = parts[2].split('@')[0]  # 1920x1080
                    width, height = map(int, res.split('x'))

                    monitor = Monitor(
                        name=name,
                        width=width,
                        height=height,
                        refresh_rate=60.0,
                        x=0, y=0,
                        active_workspace=1
                    )
                    monitors.append(monitor)

            return True, monitors, None
        except Exception as e:
            return False, None, str(e)

    # ========================================================================
    # LAYOUT MANAGEMENT
    # ========================================================================

    def set_layout(self, layout: str) -> Tuple[bool, str, Optional[str]]:
        """Set layout (dwindle, master, etc.)"""
        return self.dispatch(f"layoutmsg preselect {layout}")

    def toggle_split(self, direction: str = "right") -> Tuple[bool, str, Optional[str]]:
        """Toggle split direction"""
        return self.dispatch(f"layoutmsg {direction}")

    def swap_window(self, target: str = "master") -> Tuple[bool, str, Optional[str]]:
        """Swap window with target"""
        return self.dispatch(f"layoutmsg swapwith {target}")

    # ========================================================================
    # UTILITY
    # ========================================================================

    def get_version(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """Get Hyprland version"""
        return self._execute_hyprctl("version")

    def reload_config(self) -> Tuple[bool, str, Optional[str]]:
        """Reload Hyprland configuration"""
        return self.dispatch("exec hyprctl reload")

    def execute_command(self, command: str) -> Tuple[bool, str, Optional[str]]:
        """Execute arbitrary Hyprland command"""
        return self.dispatch(command)

    def get_status(self) -> Dict[str, Any]:
        """Get full system status"""
        status = {
            "hyprland_available": self.is_available,
            "active_window": None,
            "workspaces": [],
            "monitors": [],
        }

        success, window, _ = self.get_active_window()
        if success:
            status["active_window"] = window

        success, workspaces, _ = self.get_workspaces()
        if success:
            status["workspaces"] = workspaces

        success, monitors, _ = self.get_monitors()
        if success:
            status["monitors"] = monitors

        return status
