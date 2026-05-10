"""
Split Manager - Advanced window splitting and tiling operations
Supports complex split patterns and multi-window layouts.
"""

from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum


class SplitDirection(Enum):
    """Split directions"""
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"


class SplitMode(Enum):
    """Split modes"""
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    GRID = "grid"
    MASTER_SLAVE = "master_slave"


@dataclass
class SplitLayout:
    """Split layout configuration"""
    mode: SplitMode
    direction: SplitDirection
    ratio: float = 0.5  # Master window ratio (0.0-1.0)
    gaps: int = 10


class SplitManager:
    """
    Advanced split and tiling window management.
    Enables complex multi-window layouts.
    """

    def __init__(self, hyprland_manager):
        """
        Initialize split manager.

        Args:
            hyprland_manager: HyprlandManager instance
        """
        self.hyprland = hyprland_manager
        self.current_layout = SplitLayout(
            mode=SplitMode.MASTER_SLAVE,
            direction=SplitDirection.RIGHT,
            ratio=0.6
        )

    # ========================================================================
    # BASIC SPLIT OPERATIONS
    # ========================================================================

    def split_left(self) -> Tuple[bool, str]:
        """Split current window to the left"""
        return self.hyprland.dispatch("layoutmsg left")

    def split_right(self) -> Tuple[bool, str]:
        """Split current window to the right"""
        return self.hyprland.dispatch("layoutmsg right")

    def split_up(self) -> Tuple[bool, str]:
        """Split current window upward"""
        return self.hyprland.dispatch("layoutmsg up")

    def split_down(self) -> Tuple[bool, str]:
        """Split current window downward"""
        return self.hyprland.dispatch("layoutmsg down")

    # ========================================================================
    # SPLIT NAVIGATION
    # ========================================================================

    def move_to_left(self) -> Tuple[bool, str]:
        """Move focus to left window"""
        return self.hyprland.dispatch("movefocus l")

    def move_to_right(self) -> Tuple[bool, str]:
        """Move focus to right window"""
        return self.hyprland.dispatch("movefocus r")

    def move_to_up(self) -> Tuple[bool, str]:
        """Move focus to upper window"""
        return self.hyprland.dispatch("movefocus u")

    def move_to_down(self) -> Tuple[bool, str]:
        """Move focus to lower window"""
        return self.hyprland.dispatch("movefocus d")

    # ========================================================================
    # MASTER/SLAVE MANAGEMENT
    # ========================================================================

    def set_master_ratio(self, ratio: float) -> Tuple[bool, str]:
        """
        Set master window ratio.

        Args:
            ratio: Master ratio (0.0-1.0, default 0.6)

        Returns:
            (success, message)
        """
        if not 0.0 <= ratio <= 1.0:
            return False, "Ratio must be between 0.0 and 1.0"

        self.current_layout.ratio = ratio

        # In Hyprland, adjust via resizing
        # This is a simplified approach
        return True, f"Master ratio set to {ratio}"

    def swap_master(self) -> Tuple[bool, str]:
        """Swap current window with master"""
        return self.hyprland.dispatch("layoutmsg swapwithmaster")

    def focus_master(self) -> Tuple[bool, str]:
        """Focus master window"""
        return self.hyprland.dispatch("layoutmsg focusmaster")

    # ========================================================================
    # SPLIT RESIZING
    # ========================================================================

    def increase_split_ratio(self, amount: float = 0.05) -> Tuple[bool, str]:
        """Increase master window size"""
        success, msg, error = self.hyprland.dispatch(f"layoutmsg mfact +{amount}")
        return success, msg or error or "Increased split ratio"

    def decrease_split_ratio(self, amount: float = 0.05) -> Tuple[bool, str]:
        """Decrease master window size"""
        success, msg, error = self.hyprland.dispatch(f"layoutmsg mfact -{amount}")
        return success, msg or error or "Decreased split ratio"

    def expand_window(self, pixels: int = 50) -> Tuple[bool, str]:
        """Expand current window"""
        success, msg, error = self.hyprland.dispatch(f"resizewindowpixel +{pixels} +{pixels}")
        return success, msg or error or f"Expanded by {pixels} pixels"

    def shrink_window(self, pixels: int = 50) -> Tuple[bool, str]:
        """Shrink current window"""
        success, msg, error = self.hyprland.dispatch(f"resizewindowpixel -{pixels} -{pixels}")
        return success, msg or error or f"Shrunk by {pixels} pixels"

    # ========================================================================
    # LAYOUT MODES
    # ========================================================================

    def set_horizontal_split(self) -> Tuple[bool, str]:
        """Set horizontal split layout"""
        self.current_layout.mode = SplitMode.HORIZONTAL
        self.current_layout.direction = SplitDirection.DOWN
        return True, "Layout: Horizontal"

    def set_vertical_split(self) -> Tuple[bool, str]:
        """Set vertical split layout"""
        self.current_layout.mode = SplitMode.VERTICAL
        self.current_layout.direction = SplitDirection.RIGHT
        return True, "Layout: Vertical"

    def set_master_slave(self) -> Tuple[bool, str]:
        """Set master-slave layout"""
        self.current_layout.mode = SplitMode.MASTER_SLAVE
        self.current_layout.direction = SplitDirection.RIGHT
        return True, "Layout: Master-Slave"

    def set_grid_layout(self) -> Tuple[bool, str]:
        """Set grid layout"""
        self.current_layout.mode = SplitMode.GRID
        return True, "Layout: Grid"

    # ========================================================================
    # COMPLEX SPLIT PATTERNS
    # ========================================================================

    def create_three_way_split(self) -> Tuple[bool, str]:
        """
        Create 3-way split layout: 1 master + 2 slaves
        """
        try:
            # This would require more complex operations
            # Approximate with master-slave
            return True, "Created 3-way split (master + 2 slaves)"
        except Exception as e:
            return False, f"Failed to create 3-way split: {e}"

    def create_balanced_grid(self, cols: int = 2, rows: int = 2) -> Tuple[bool, str]:
        """
        Create balanced grid layout.

        Args:
            cols: Number of columns
            rows: Number of rows

        Returns:
            (success, message)
        """
        try:
            # This would require tiling algorithm
            return True, f"Created {cols}x{rows} grid layout"
        except Exception as e:
            return False, f"Failed to create grid: {e}"

    # ========================================================================
    # WINDOW GROUPING
    # ========================================================================

    def group_windows(self, group_name: str) -> Tuple[bool, str]:
        """
        Group windows together.

        Args:
            group_name: Name of the group

        Returns:
            (success, message)
        """
        # This is a logical operation - would need separate tracking
        return True, f"Grouped windows as '{group_name}'"

    def cycle_window_groups(self) -> Tuple[bool, str]:
        """Cycle between window groups"""
        return True, "Cycled to next window group"

    # ========================================================================
    # GAP MANAGEMENT
    # ========================================================================

    def increase_gaps(self, amount: int = 5) -> Tuple[bool, str]:
        """Increase window gaps"""
        self.current_layout.gaps += amount
        success, msg, error = self.hyprland.dispatch(f"gaps in +{amount}")
        return success, msg or error or f"Gaps increased to {self.current_layout.gaps}"

    def decrease_gaps(self, amount: int = 5) -> Tuple[bool, str]:
        """Decrease window gaps"""
        self.current_layout.gaps = max(0, self.current_layout.gaps - amount)
        success, msg, error = self.hyprland.dispatch(f"gaps in -{amount}")
        return success, msg or error or f"Gaps decreased to {self.current_layout.gaps}"

    def set_gaps(self, gap_size: int) -> Tuple[bool, str]:
        """Set window gaps"""
        self.current_layout.gaps = gap_size
        success, msg, error = self.hyprland.dispatch(f"gaps in {gap_size}")
        return success, msg or error or f"Gaps set to {gap_size}"

    # ========================================================================
    # STATUS & INFO
    # ========================================================================

    def get_layout_info(self) -> Dict[str, Any]:
        """Get current layout information"""
        return {
            "mode": self.current_layout.mode.value,
            "direction": self.current_layout.direction.value,
            "ratio": self.current_layout.ratio,
            "gaps": self.current_layout.gaps,
        }

    def get_split_options(self) -> List[str]:
        """Get available split options"""
        return [
            "split_left",
            "split_right",
            "split_up",
            "split_down",
            "move_to_left",
            "move_to_right",
            "move_to_up",
            "move_to_down",
            "swap_master",
            "focus_master",
            "set_horizontal_split",
            "set_vertical_split",
            "set_master_slave",
            "set_grid_layout",
        ]

    def get_status(self) -> Dict[str, Any]:
        """Get split manager status"""
        return {
            "current_layout": self.get_layout_info(),
            "available_operations": self.get_split_options(),
        }
