"""
Memory module - lightweight task state tracking and persistent logging.

Two components:
1. Memory (real-time): Current task, action, status (in-memory, fast)
2. Logging (persistent): Action log for debugging and replay (on-disk)
"""

from .core import Memory, MEMORY
from .memory import log_action, get_log_file, get_action_log

__all__ = ["Memory", "MEMORY", "log_action", "get_log_file", "get_action_log"]

