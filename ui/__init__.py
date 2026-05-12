"""UI module - Caelestia shell control, browser automation, and quick terminal utilities."""

from ui.caelestia_controller import (
    CaelestiaController,
    BrowserAutomation,
    ExecutorAdapter,
    ToggleState,
)
from ui.quick_terminal import QuickTerminal

__all__ = [
    "CaelestiaController",
    "BrowserAutomation",
    "ExecutorAdapter",
    "ToggleState",
    "QuickTerminal",
]
