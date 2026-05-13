"""
Mouse input tools - screen-aware coordinate handling.
"""

from typing import Dict, Any, Tuple
from ..tool import Tool
from ..schemas import ToolSchemas
from config import SCREEN_CONFIG


class MouseClickTool(Tool):
    """Click at specific coordinates."""

    def __init__(self):
        super().__init__(
            name="mouse_click",
            platform="mouse",
            description="Click at specific screen coordinates",
        )

    def validate_input(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate input - including coordinate bounds."""
        # First validate schema
        is_valid, error = ToolSchemas.validate("mouse_click", data)
        if not is_valid:
            return is_valid, error

        # Validate coordinates are within screen bounds
        x, y = data["x"], data["y"]
        max_x, max_y = SCREEN_CONFIG["width"] - 1, SCREEN_CONFIG["height"] - 1

        if x < 0 or x > max_x:
            return False, f"X coordinate {x} out of bounds (0-{max_x})"
        if y < 0 or y > max_y:
            return False, f"Y coordinate {y} out of bounds (0-{max_y})"

        return True, ""

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Click at coordinates."""
        x, y = data["x"], data["y"]
        button = data.get("button", "left")

        return {
            "success": False,
            "error": "mouse_click not implemented - requires ydotool or X11/Wayland integration",
            "result": {
                "x": x,
                "y": y,
                "button": button,
                "clicked": False,
                "screen_bounds": {
                    "width": SCREEN_CONFIG["width"],
                    "height": SCREEN_CONFIG["height"],
                },
            },
        }


class MouseMoveTool(Tool):
    """Move mouse cursor - screen-aware."""

    def __init__(self):
        super().__init__(
            name="mouse_move",
            platform="mouse",
            description="Move mouse cursor to coordinates",
        )

    def validate_input(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate input - including coordinate bounds."""
        # First validate schema
        is_valid, error = ToolSchemas.validate("mouse_move", data)
        if not is_valid:
            return is_valid, error

        # Validate coordinates are within screen bounds
        x, y = data["x"], data["y"]
        max_x, max_y = SCREEN_CONFIG["width"] - 1, SCREEN_CONFIG["height"] - 1

        if x < 0 or x > max_x:
            return False, f"X coordinate {x} out of bounds (0-{max_x})"
        if y < 0 or y > max_y:
            return False, f"Y coordinate {y} out of bounds (0-{max_y})"

        return True, ""

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Move cursor."""
        x, y = data["x"], data["y"]
        duration = data.get("duration", 0.5)

        return {
            "success": False,
            "error": "mouse_move not implemented - requires ydotool or X11/Wayland integration",
            "result": {
                "x": x,
                "y": y,
                "duration": duration,
                "moved": False,
                "screen_bounds": {
                    "width": SCREEN_CONFIG["width"],
                    "height": SCREEN_CONFIG["height"],
                },
            },
        }


class DragDropTool(Tool):
    """Drag and drop operation - screen-aware."""

    def __init__(self):
        super().__init__(
            name="drag_drop",
            platform="mouse",
            description="Drag element from source to destination",
        )

    def validate_input(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate input - including coordinate bounds."""
        # First validate schema
        is_valid, error = ToolSchemas.validate("drag_drop", data)
        if not is_valid:
            return is_valid, error

        # Validate all coordinates are within screen bounds
        coords = [
            ("src_x", data["src_x"]),
            ("src_y", data["src_y"]),
            ("dst_x", data["dst_x"]),
            ("dst_y", data["dst_y"]),
        ]
        max_x, max_y = SCREEN_CONFIG["width"] - 1, SCREEN_CONFIG["height"] - 1

        for name, coord in coords:
            if name in ["src_x", "dst_x"]:
                if coord < 0 or coord > max_x:
                    return False, f"{name} coordinate {coord} out of bounds (0-{max_x})"
            else:
                if coord < 0 or coord > max_y:
                    return False, f"{name} coordinate {coord} out of bounds (0-{max_y})"

        return True, ""

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Drag and drop."""
        src_x, src_y = data["src_x"], data["src_y"]
        dst_x, dst_y = data["dst_x"], data["dst_y"]
        duration = data.get("duration", 1.0)

        # Calculate distance
        distance = ((dst_x - src_x) ** 2 + (dst_y - src_y) ** 2) ** 0.5

        return {
            "success": False,
            "error": "drag_drop not implemented - requires ydotool or X11/Wayland integration",
            "result": {
                "from": (src_x, src_y),
                "to": (dst_x, dst_y),
                "distance": distance,
                "duration": duration,
                "dragged": False,
                "screen_bounds": {
                    "width": SCREEN_CONFIG["width"],
                    "height": SCREEN_CONFIG["height"],
                },
            },
        }

