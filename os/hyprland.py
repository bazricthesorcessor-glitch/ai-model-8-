"""
Hyprland Manager - Core window manager integration
Controls Hyprland through hyprctl with full command support.
"""

import subprocess
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
import json
import os


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

    def _execute_hyprctl_json(self, command: str) -> Tuple[bool, Any, Optional[str]]:
        """Execute hyprctl JSON command."""
        success, output, error = self._execute_hyprctl(f"-j {command}")
        if not success:
            return False, None, error

        try:
            return True, json.loads(output or "null"), None
        except json.JSONDecodeError as exc:
            return False, None, f"Invalid JSON from hyprctl {command}: {exc}"

    def dispatch(self, command: str) -> Tuple[bool, str, Optional[str]]:
        """Send dispatch command"""
        return self._execute_hyprctl(f"dispatch {command}")

    # ========================================================================
    # WINDOW MANAGEMENT
    # ========================================================================

    def get_active_window(self) -> Tuple[bool, Optional[Window], Optional[str]]:
        """Get currently active window"""
        success, payload, error = self._execute_hyprctl_json("activewindow")
        if not success:
            return False, None, error

        try:
            if not isinstance(payload, dict):
                return False, None, "Failed to parse active window info"

            workspace = payload.get("workspace", {})
            size = payload.get("size", [0, 0])
            at = payload.get("at", [0, 0])
            window = Window(
                address=str(payload.get("address", "")),
                title=str(payload.get("title", "")),
                class_name=str(payload.get("class", "")),
                workspace=int(workspace.get("id", 0) or 0),
                x=int(at[0] if len(at) > 0 else 0),
                y=int(at[1] if len(at) > 1 else 0),
                width=int(size[0] if len(size) > 0 else 0),
                height=int(size[1] if len(size) > 1 else 0),
                floating=bool(payload.get("floating", False)),
                maximized=bool(payload.get("fullscreen", False)),
            )
            return True, window, None
        except Exception as e:
            return False, None, str(e)

    def list_windows(self) -> Tuple[bool, Optional[List[Window]], Optional[str]]:
        """List all windows"""
        success, payload, error = self._execute_hyprctl_json("clients")
        if not success:
            return False, None, error

        if not isinstance(payload, list):
            return False, None, "Failed to parse Hyprland clients list"

        windows = []
        try:
            for item in payload:
                workspace = item.get("workspace", {})
                size = item.get("size", [0, 0])
                at = item.get("at", [0, 0])
                windows.append(
                    Window(
                        address=str(item.get("address", "")),
                        title=str(item.get("title", "")),
                        class_name=str(item.get("class", "")),
                        workspace=int(workspace.get("id", 0) or 0),
                        x=int(at[0] if len(at) > 0 else 0),
                        y=int(at[1] if len(at) > 1 else 0),
                        width=int(size[0] if len(size) > 0 else 0),
                        height=int(size[1] if len(size) > 1 else 0),
                        floating=bool(item.get("floating", False)),
                        maximized=bool(item.get("fullscreen", False)),
                    )
                )
            return True, windows, None
        except Exception as exc:
            return False, None, f"Failed to normalize Hyprland clients: {exc}"

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
        success, payload, error = self._execute_hyprctl_json("workspaces")
        if not success:
            return False, None, error

        if not isinstance(payload, list):
            return False, None, "Failed to parse Hyprland workspaces list"

        workspaces = []
        try:
            for item in payload:
                workspaces.append(Workspace(
                    id=int(item.get("id", 0) or 0),
                    name=str(item.get("name", item.get("id", ""))),
                    monitor=str(item.get("monitor", "")),
                    window_count=int(item.get("windows", 0) or 0),
                ))
            return True, workspaces, None
        except Exception as e:
            return False, None, str(e)

    def get_active_workspace_id(self) -> Tuple[bool, Optional[int], Optional[str]]:
        """Get the currently active workspace id."""
        success, payload, error = self._execute_hyprctl_json("activeworkspace")
        if not success:
            return False, None, error
        if not isinstance(payload, dict):
            return False, None, "Failed to parse active workspace"
        return True, int(payload.get("id", 0) or 0), None

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
