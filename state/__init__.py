"""
State module - system status and memory.
Stores current execution state, NOT conversation history.
Provides context for brain and execution results for logging.
"""

from .state import (
    update_state,
    get_state,
    get_last_actions,
    clear_state,
    SystemState,
)

__all__ = ["update_state", "get_state", "get_last_actions", "clear_state", "SystemState"]
