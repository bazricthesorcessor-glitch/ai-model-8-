"""
OS Integration Module - Desktop Automation and System Control
Hyprland integration with window management, keyboard shortcuts, mouse gestures, and split operations.
"""

from .hyprland import HyprlandManager
from .keyboard_shortcuts import KeyboardShortcutHandler
from .mouse_gestures import MouseGestureRecognizer
from .window_manager import WindowManager
from .split_manager import SplitManager

__all__ = [
    "HyprlandManager",
    "KeyboardShortcutHandler",
    "MouseGestureRecognizer",
    "WindowManager",
    "SplitManager",
]
