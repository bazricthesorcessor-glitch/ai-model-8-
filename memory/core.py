"""
Memory system - lightweight, real-time task state tracking.
NOT conversation history - only current system state.
"""

import threading
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from copy import deepcopy


class Memory:
    """Lightweight in-memory storage for current task state."""

    VALID_STATUSES = ["idle", "executing", "waiting_approval", "error"]

    def __init__(self):
        """Initialize empty memory."""
        self._state = {
            "current_task": None,
            "last_action": None,
            "current_status": "idle",
            "context": {},
            "user_preferences": {},
        }
        self._lock = threading.RLock()
        self._change_log = []  # Track last 10 changes
        self._subscribers = {}  # Field → [callbacks]
        self._created_at = datetime.now()

    # ========================================================================
    # READ OPERATIONS (thread-safe, returns copies)
    # ========================================================================

    def get_state(self) -> Dict[str, Any]:
        """Get complete memory state as snapshot."""
        with self._lock:
            return deepcopy(self._state)

    def get(self, field: str) -> Any:
        """Get specific field value."""
        with self._lock:
            if field not in self._state:
                raise KeyError(f"Unknown field: {field}")
            return deepcopy(self._state[field])

    def get_task(self) -> Optional[Dict[str, Any]]:
        """Get current task."""
        return self.get("current_task")

    def get_action(self) -> Optional[Dict[str, Any]]:
        """Get last action."""
        return self.get("last_action")

    def get_status(self) -> str:
        """Get current status."""
        return self.get("current_status")

    def get_context(self) -> Dict[str, Any]:
        """Get context dict."""
        return self.get("context")

    def get_preferences(self) -> Dict[str, Any]:
        """Get user preferences."""
        return self.get("user_preferences")

    # ========================================================================
    # WRITE OPERATIONS (atomic, thread-safe)
    # ========================================================================

    def update_task(self, task: Optional[Dict[str, Any]]) -> None:
        """Update current task (atomic)."""
        with self._lock:
            old_value = self._state["current_task"]
            self._state["current_task"] = deepcopy(task) if task else None
            self._record_change("current_task", old_value, self._state["current_task"])
            self._notify_subscribers("current_task", self._state["current_task"])

    def update_action(self, action: Optional[Dict[str, Any]]) -> None:
        """Update last action (atomic)."""
        with self._lock:
            old_value = self._state["last_action"]
            self._state["last_action"] = deepcopy(action) if action else None
            self._record_change("last_action", old_value, self._state["last_action"])
            self._notify_subscribers("last_action", self._state["last_action"])

    def set_status(self, status: str) -> None:
        """Set current status (atomic)."""
        if status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status: {status}. Must be one of: {self.VALID_STATUSES}")

        with self._lock:
            old_value = self._state["current_status"]
            self._state["current_status"] = status
            self._record_change("current_status", old_value, status)
            self._notify_subscribers("current_status", status)

    def update_context(self, context: Dict[str, Any]) -> None:
        """Merge context updates (merges, doesn't overwrite)."""
        if not isinstance(context, dict):
            raise TypeError("Context must be a dict")

        with self._lock:
            old_value = deepcopy(self._state["context"])
            self._state["context"].update(context)
            self._record_change("context", old_value, deepcopy(self._state["context"]))
            self._notify_subscribers("context", deepcopy(self._state["context"]))

    def set_context_value(self, key: str, value: Any) -> None:
        """Set single context value."""
        self.update_context({key: value})

    def set_preferences(self, prefs: Dict[str, Any]) -> None:
        """Update user preferences (merges)."""
        if not isinstance(prefs, dict):
            raise TypeError("Preferences must be a dict")

        with self._lock:
            old_value = deepcopy(self._state["user_preferences"])
            self._state["user_preferences"].update(prefs)
            self._record_change("user_preferences", old_value, deepcopy(self._state["user_preferences"]))
            self._notify_subscribers("user_preferences", deepcopy(self._state["user_preferences"]))

    def set_preference(self, key: str, value: Any) -> None:
        """Set single preference."""
        self.set_preferences({key: value})

    # ========================================================================
    # DEBUGGING
    # ========================================================================

    def get_change_log(self) -> List[Dict[str, Any]]:
        """Get last 10 changes for debugging."""
        with self._lock:
            return deepcopy(self._change_log)

    def debug_view(self) -> str:
        """Get formatted debug view of current state."""
        with self._lock:
            task = self._state["current_task"]
            action = self._state["last_action"]
            status = self._state["current_status"]
            context = self._state["context"]

            task_str = f"{task.get('name', 'N/A')}" if task else "None"
            action_str = (
                f"{action.get('tool', 'N/A')} ({action.get('result', {}).get('duration_ms', 0):.1f}ms)"
                if action
                else "None"
            )

            return f"""
╔─ Memory State ─────────────────────────╗
║ Status:        {status:30}║
║ Task:          {task_str:30}║
║ Last Action:   {action_str:30}║
║ Context Keys:  {len(context):30}║
║ Prefs:         {len(self._state['user_preferences']):30}║
║ Changes:       {len(self._change_log):30}║
╚────────────────────────────────────────╝
"""

    def debug_changes(self) -> str:
        """Get formatted change log."""
        with self._lock:
            if not self._change_log:
                return "No changes recorded yet."

            lines = ["📝 Change Log (Last 10):"]
            for i, change in enumerate(self._change_log, 1):
                timestamp = change["timestamp"].split("T")[1][:8]  # HH:MM:SS
                field = change["field"]
                old_val = str(change["old_value"])[:20]
                new_val = str(change["new_value"])[:20]
                lines.append(f"{i}. {field}: {old_val} → {new_val} ({timestamp})")

            return "\n".join(lines)

    def debug_field_history(self, field: str) -> str:
        """Get history of a specific field."""
        with self._lock:
            changes = [c for c in self._change_log if c["field"] == field]

            if not changes:
                return f"No changes for field: {field}"

            lines = [f"📋 History of '{field}':"]
            for change in changes:
                timestamp = change["timestamp"].split("T")[1][:8]
                value = str(change["new_value"])[:30]
                lines.append(f"  {value} ({timestamp})")

            return "\n".join(lines)

    def get_snapshot(self) -> Dict[str, Any]:
        """Get state snapshot for comparison."""
        return self.get_state()

    def debug_diff(self, old_state: Dict[str, Any]) -> str:
        """Compare current state with old snapshot."""
        current = self.get_state()

        changed = []
        unchanged = []

        for key in current.keys():
            if current[key] != old_state.get(key):
                changed.append(key)
            else:
                unchanged.append(key)

        lines = ["🔄 State Comparison:"]
        lines.append(f"Changed: {', '.join(changed) if changed else 'None'}")
        lines.append(f"Unchanged: {', '.join(unchanged) if unchanged else 'None'}")

        return "\n".join(lines)

    # ========================================================================
    # SUBSCRIBERS (change notifications)
    # ========================================================================

    def on_change(self, field: str, callback: Callable) -> None:
        """Subscribe to field changes."""
        if field not in self._state:
            raise KeyError(f"Unknown field: {field}")

        if field not in self._subscribers:
            self._subscribers[field] = []

        self._subscribers[field].append(callback)

    def _notify_subscribers(self, field: str, value: Any) -> None:
        """Notify all subscribers of field change."""
        for callback in self._subscribers.get(field, []):
            try:
                callback(value)
            except Exception as e:
                # Log error but don't raise (don't break execution)
                pass

    # ========================================================================
    # HOUSEKEEPING
    # ========================================================================

    def _record_change(self, field: str, old_value: Any, new_value: Any) -> None:
        """Record change for debugging (keep last 10)."""
        change = {
            "field": field,
            "old_value": old_value,
            "new_value": new_value,
            "timestamp": datetime.now().isoformat(),
        }
        self._change_log.append(change)

        # Keep only last 10
        if len(self._change_log) > 10:
            self._change_log.pop(0)

    def clear(self) -> None:
        """Reset memory between sessions."""
        with self._lock:
            self._state = {
                "current_task": None,
                "last_action": None,
                "current_status": "idle",
                "context": {},
                "user_preferences": {},
            }
            self._change_log.clear()
            self._created_at = datetime.now()

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        with self._lock:
            return {
                "created_at": self._created_at.isoformat(),
                "uptime_seconds": (datetime.now() - self._created_at).total_seconds(),
                "change_log_size": len(self._change_log),
                "subscribers": {k: len(v) for k, v in self._subscribers.items() if v},
                "state_size_bytes": len(str(self._state).encode()),
            }


# Global memory instance
MEMORY = Memory()
