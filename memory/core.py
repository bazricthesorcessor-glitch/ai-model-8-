"""
Runtime memory facade for Elzyra.

This object is the single strong entrypoint used by `main.py` and any module
that needs memory during execution. It keeps the old lightweight API
(`update_task`, `set_status`, `get_context`, ...) but adds:

- persistent daily journaling
- pinned / important memory
- recall and search helpers
- large context packing for 10M-token-class windows
- state snapshots for recovery
"""

from __future__ import annotations

import threading
import uuid
from copy import deepcopy
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from . import paths
from .reader import MemoryReader
from .search import MemorySearch
from .writer import MemoryWriter, initialize_memory_system


class Memory:
    """Persistent runtime memory with a backward-compatible API."""

    VALID_STATUSES = [
        "idle",
        "executing",
        "waiting_approval",
        "error",
        "paused",
        "complete",
    ]
    DEFAULT_CONTEXT_TOKEN_LIMIT = 10_000_000
    DEFAULT_RECENT_ENTRY_LIMIT = 2_000
    DEFAULT_ARCHIVE_RESULT_LIMIT = 100

    def __init__(self):
        initialize_memory_system()
        self._lock = threading.RLock()
        self._subscribers: Dict[str, List[Callable]] = {}
        self._change_log: List[Dict[str, Any]] = []
        self._created_at = datetime.now()
        self._search = MemorySearch()
        self._state = self._build_initial_state()
        self._hydrate_from_disk()

    # =====================================================================
    # READ OPERATIONS
    # =====================================================================

    def get_state(self) -> Dict[str, Any]:
        """Get a full memory snapshot."""
        with self._lock:
            return deepcopy(self._state)

    def get(self, field: str) -> Any:
        with self._lock:
            if field not in self._state:
                raise KeyError(f"Unknown field: {field}")
            return deepcopy(self._state[field])

    def get_task(self) -> Optional[Dict[str, Any]]:
        return self.get("current_task")

    def get_action(self) -> Optional[Dict[str, Any]]:
        return self.get("last_action")

    def get_status(self) -> str:
        return self.get("current_status")

    def get_context(self) -> Dict[str, Any]:
        return self.get("context")

    def get_preferences(self) -> Dict[str, Any]:
        return self.get("user_preferences")

    def get_change_log(self) -> List[Dict[str, Any]]:
        with self._lock:
            return deepcopy(self._change_log)

    def get_snapshot(self) -> Dict[str, Any]:
        return self.get_state()

    # =====================================================================
    # WRITE OPERATIONS
    # =====================================================================

    def update_task(self, task: Optional[Dict[str, Any]]) -> None:
        with self._lock:
            previous = self._state["current_task"]
            self._state["current_task"] = deepcopy(task) if task else None
            self._record_change("current_task", previous, self._state["current_task"])
            self._notify_subscribers("current_task", self._state["current_task"])
            self._persist_runtime_state()

        if task:
            self.remember(
                speaker="system",
                message=f"Task updated: {task.get('name') or task.get('id') or 'unnamed task'}",
                importance=7,
                tags=["task", "runtime"],
                category="task",
                data={"task": deepcopy(task)},
            )

    def update_action(self, action: Optional[Dict[str, Any]]) -> None:
        with self._lock:
            previous = self._state["last_action"]
            self._state["last_action"] = deepcopy(action) if action else None
            self._record_change("last_action", previous, self._state["last_action"])
            self._append_recent_history("action", self._state["last_action"])
            self._notify_subscribers("last_action", self._state["last_action"])
            self._persist_runtime_state()

        if action:
            self.remember(
                speaker="system",
                message=f"Action recorded: {action.get('tool', 'unknown')}",
                importance=6,
                tags=["action", "runtime"],
                category="action",
                data={"action": deepcopy(action)},
            )

    def set_status(self, status: str) -> None:
        if status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status: {status}. Must be one of: {self.VALID_STATUSES}")

        with self._lock:
            previous = self._state["current_status"]
            self._state["current_status"] = status
            self._record_change("current_status", previous, status)
            self._notify_subscribers("current_status", status)
            self._persist_runtime_state()

        self.remember(
            speaker="system",
            message=f"Status changed from {previous} to {status}",
            importance=4,
            tags=["status", "runtime"],
            category="state",
            data={"old_status": previous, "new_status": status},
        )

    def update_context(self, context: Dict[str, Any]) -> None:
        if not isinstance(context, dict):
            raise TypeError("Context must be a dict")

        with self._lock:
            previous = deepcopy(self._state["context"])
            self._state["context"].update(deepcopy(context))
            self._record_change("context", previous, deepcopy(self._state["context"]))
            self._notify_subscribers("context", deepcopy(self._state["context"]))
            self._persist_runtime_state()

    def set_context_value(self, key: str, value: Any) -> None:
        self.update_context({key: value})

    def set_preferences(self, prefs: Dict[str, Any]) -> None:
        if not isinstance(prefs, dict):
            raise TypeError("Preferences must be a dict")

        with self._lock:
            previous = deepcopy(self._state["user_preferences"])
            self._state["user_preferences"] = deepcopy(prefs)
            self._record_change("user_preferences", previous, deepcopy(self._state["user_preferences"]))
            self._notify_subscribers("user_preferences", deepcopy(self._state["user_preferences"]))
            MemoryWriter.save_user_preferences(self._state["user_preferences"])
            self._persist_runtime_state()

    def set_preference(self, key: str, value: Any) -> None:
        current_preferences = self.get_preferences()
        current_preferences[key] = value
        self.set_preferences(current_preferences)

    # =====================================================================
    # PERSISTENT MEMORY OPERATIONS
    # =====================================================================

    def start_session(self, session_name: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> str:
        with self._lock:
            if not self._state["session_id"]:
                self._state["session_id"] = uuid.uuid4().hex
            if session_name:
                self._state["context"]["session_name"] = session_name
            if metadata:
                self._state["context"]["session_metadata"] = deepcopy(metadata)
            self._persist_runtime_state()

        self.remember(
            speaker="system",
            message=f"Session started: {session_name or self._state['session_id']}",
            importance=8,
            tags=["session", "startup"],
            category="session",
            data={"session_id": self._state["session_id"], "metadata": metadata or {}},
        )
        return self._state["session_id"]

    def remember(
        self,
        message: str,
        speaker: str = "system",
        importance: int = 5,
        tags: Optional[List[str]] = None,
        category: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        severity: str = "info",
    ) -> Dict[str, Any]:
        """Persist a memory event and keep it in the runtime working set."""
        entry = MemoryWriter.create_daily_log_entry(
            log_type="memory_event",
            message=message,
            category=category or "general",
            data={
                "speaker": speaker,
                "importance": max(0, min(10, importance)),
                "tags": tags or [],
                "session_id": self._state.get("session_id"),
                **(data or {}),
            },
            severity=severity,
        )
        MemoryWriter.log_to_daily(entry)

        with self._lock:
            self._append_recent_history("memory_event", entry)
            self._state["metrics"]["memory_events"] += 1
            self._state["last_memory_event"] = deepcopy(entry)
            self._persist_runtime_state()

        return entry

    def record_user_message(self, message: str, tags: Optional[List[str]] = None, importance: int = 6) -> Dict[str, Any]:
        return self.remember(
            speaker="user",
            message=message,
            importance=importance,
            tags=(tags or []) + ["user_message"],
            category="conversation",
        )

    def record_agent_message(
        self,
        agent: str,
        message: str,
        tags: Optional[List[str]] = None,
        importance: int = 5,
    ) -> Dict[str, Any]:
        return self.remember(
            speaker=agent,
            message=message,
            importance=importance,
            tags=(tags or []) + ["agent_message"],
            category="conversation",
        )

    def record_execution_result(
        self,
        action: str,
        result: Dict[str, Any],
        success: bool = True,
    ) -> None:
        execution = {
            "action": action,
            "result": deepcopy(result),
            "success": success,
            "session_id": self._state.get("session_id"),
        }
        MemoryWriter.log_execution_history(execution)
        self.remember(
            speaker="executor",
            message=f"Execution {'succeeded' if success else 'failed'}: {action}",
            importance=7 if success else 9,
            tags=["execution", "result", "success" if success else "failure"],
            category="execution",
            data={"execution": execution},
            severity="info" if success else "error",
        )

    def pin_memory(
        self,
        content: str,
        category: str = "general",
        tags: Optional[List[str]] = None,
        priority: str = "high",
    ) -> Dict[str, Any]:
        item = {
            "content": content,
            "category": category,
            "tags": tags or [],
            "priority": priority,
        }
        MemoryWriter.save_important_memory(item)
        with self._lock:
            self._state["pinned_memories"] = MemoryReader.load_important_memory().get("items", [])
            self._state["metrics"]["pinned_memories"] = len(self._state["pinned_memories"])
            self._persist_runtime_state()
        return item

    def search_memory(self, query: str, limit: int = 20) -> Dict[str, Any]:
        daily = self._filter_entries_by_terms(MemoryReader.load_14_day_memory(), query, limit)
        important = self._filter_entries_by_terms(
            MemoryReader.load_important_memory().get("items", []),
            query,
            limit,
        )
        archives = self._filter_entries_by_terms(
            self._search.search_archives(query=query, limit=limit * 5),
            query,
            limit,
        )
        return {
            "query": query,
            "recent": daily[:limit],
            "important": important[:limit],
            "archive": archives[:limit],
            "total_matches": len(daily) + len(important) + len(archives),
        }

    def build_context_window(
        self,
        query: str,
        max_tokens: int = DEFAULT_CONTEXT_TOKEN_LIMIT,
        recent_limit: int = DEFAULT_RECENT_ENTRY_LIMIT,
        archive_limit: int = DEFAULT_ARCHIVE_RESULT_LIMIT,
    ) -> Dict[str, Any]:
        """
        Build a large context package for downstream reasoning.

        We do not try to exactly tokenize here. We budget by approximate chars,
        which is enough for packing and testing the 10M-token regime.
        """
        important = MemoryReader.load_important_memory().get("items", [])
        recent = MemoryReader.load_14_day_memory()[:recent_limit]
        search = self.search_memory(query, limit=archive_limit)

        payload = {
            "query": query,
            "session_id": self._state.get("session_id"),
            "status": self._state.get("current_status"),
            "task": deepcopy(self._state.get("current_task")),
            "context": deepcopy(self._state.get("context")),
            "preferences": deepcopy(self._state.get("user_preferences")),
            "important_memory": important,
            "recent_memory": recent,
            "relevant_archive": search["archive"],
        }

        approx_chars = len(str(payload))
        approx_tokens = max(1, approx_chars // 4)
        with self._lock:
            self._state["compiled_context"] = {
                "query": query,
                "approx_tokens": approx_tokens,
                "max_tokens": max_tokens,
                "sections": {
                    "important_count": len(important),
                    "recent_count": len(recent),
                    "archive_count": len(search["archive"]),
                },
                "built_at": datetime.now().isoformat(),
            }
            self._state["metrics"]["context_builds"] += 1
            self._persist_runtime_state()

        return {
            "payload": payload,
            "approx_tokens": approx_tokens,
            "max_tokens": max_tokens,
            "fits_budget": approx_tokens <= max_tokens,
        }

    def sync_from_persistent_storage(self) -> None:
        with self._lock:
            self._hydrate_from_disk()
            current_state = MemoryReader.load_current_state().get("state", {})
            if isinstance(current_state, dict):
                self._state["context"].update(deepcopy(current_state.get("context", {})))
                self._state["current_task"] = deepcopy(current_state.get("current_task"))
                self._state["last_action"] = deepcopy(current_state.get("last_action"))
                self._state["current_status"] = current_state.get("current_status", self._state["current_status"])
            self._persist_runtime_state()

    def save_snapshot(self) -> Dict[str, Any]:
        snapshot = {
            "state": self.get_state(),
            "snapshot_reason": "manual_save",
        }
        MemoryWriter.save_state_snapshot(snapshot)
        return snapshot

    # =====================================================================
    # DEBUG / INSPECTION
    # =====================================================================

    def debug_view(self) -> str:
        with self._lock:
            task = self._state["current_task"]
            action = self._state["last_action"]
            status = self._state["current_status"]
            context = self._state["context"]
            pinned = len(self._state["pinned_memories"])
            recent = len(self._state["recent_history"])

            task_str = f"{task.get('name', 'N/A')}" if task else "None"
            action_str = (
                f"{action.get('tool', 'N/A')} ({action.get('result', {}).get('duration_ms', 0):.1f}ms)"
                if action
                else "None"
            )

            return f"""
╔─ Perfect Memory ──────────────────────╗
║ Session:       {self._state['session_id'][:12] if self._state['session_id'] else 'None':30}║
║ Status:        {status:30}║
║ Task:          {task_str:30}║
║ Last Action:   {action_str:30}║
║ Context Keys:  {len(context):30}║
║ Prefs:         {len(self._state['user_preferences']):30}║
║ Pinned:        {pinned:30}║
║ Recent Events: {recent:30}║
║ Token Budget:  {self.DEFAULT_CONTEXT_TOKEN_LIMIT:30}║
╚───────────────────────────────────────╝
"""

    def debug_changes(self) -> str:
        with self._lock:
            if not self._change_log:
                return "No changes recorded yet."
            lines = ["Change Log (Last 10):"]
            for i, change in enumerate(self._change_log, 1):
                timestamp = change["timestamp"].split("T")[1][:8]
                lines.append(
                    f"{i}. {change['field']}: {str(change['old_value'])[:20]} -> {str(change['new_value'])[:20]} ({timestamp})"
                )
            return "\n".join(lines)

    def debug_field_history(self, field: str) -> str:
        with self._lock:
            changes = [c for c in self._change_log if c["field"] == field]
            if not changes:
                return f"No changes for field: {field}"
            lines = [f"History of '{field}':"]
            for change in changes:
                timestamp = change["timestamp"].split("T")[1][:8]
                lines.append(f"  {str(change['new_value'])[:60]} ({timestamp})")
            return "\n".join(lines)

    def debug_diff(self, old_state: Dict[str, Any]) -> str:
        current = self.get_state()
        changed = [key for key in current.keys() if current[key] != old_state.get(key)]
        unchanged = [key for key in current.keys() if current[key] == old_state.get(key)]
        return "\n".join(
            [
                "State Comparison:",
                f"Changed: {', '.join(changed) if changed else 'None'}",
                f"Unchanged: {', '.join(unchanged) if unchanged else 'None'}",
            ]
        )

    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "created_at": self._created_at.isoformat(),
                "uptime_seconds": (datetime.now() - self._created_at).total_seconds(),
                "change_log_size": len(self._change_log),
                "subscribers": {k: len(v) for k, v in self._subscribers.items() if v},
                "state_size_bytes": len(str(self._state).encode()),
                "metrics": deepcopy(self._state["metrics"]),
                "recent_history_size": len(self._state["recent_history"]),
                "pinned_memories": len(self._state["pinned_memories"]),
                "context_token_limit": self.DEFAULT_CONTEXT_TOKEN_LIMIT,
            }

    # =====================================================================
    # SUBSCRIBERS / HOUSEKEEPING
    # =====================================================================

    def on_change(self, field: str, callback: Callable) -> None:
        if field not in self._state:
            raise KeyError(f"Unknown field: {field}")
        self._subscribers.setdefault(field, []).append(callback)

    def clear(self) -> None:
        """Reset runtime state while keeping persistent memory on disk."""
        with self._lock:
            session_id = self._state.get("session_id")
            self._state = self._build_initial_state()
            self._state["session_id"] = session_id
            self._change_log.clear()
            self._created_at = datetime.now()
            self._hydrate_from_disk()
            self._persist_runtime_state()

    # =====================================================================
    # INTERNALS
    # =====================================================================

    def _build_initial_state(self) -> Dict[str, Any]:
        return {
            "session_id": uuid.uuid4().hex,
            "current_task": None,
            "last_action": None,
            "current_status": "idle",
            "context": {},
            "user_preferences": {},
            "pinned_memories": [],
            "recent_history": [],
            "compiled_context": {},
            "last_memory_event": None,
            "metrics": {
                "memory_events": 0,
                "context_builds": 0,
                "pinned_memories": 0,
            },
        }

    def _hydrate_from_disk(self) -> None:
        self._state["user_preferences"] = MemoryReader.load_user_preferences()
        self._state["pinned_memories"] = MemoryReader.load_important_memory().get("items", [])
        self._state["metrics"]["pinned_memories"] = len(self._state["pinned_memories"])
        self._state["recent_history"] = MemoryReader.load_14_day_memory()[:200]

    def _append_recent_history(self, entry_type: str, payload: Any) -> None:
        self._state["recent_history"].insert(
            0,
            {
                "timestamp": datetime.now().isoformat(),
                "type": entry_type,
                "payload": deepcopy(payload),
            },
        )
        self._state["recent_history"] = self._state["recent_history"][:500]

    def _persist_runtime_state(self) -> None:
        MemoryWriter.save_state_snapshot(
            {
                "state": {
                    "session_id": self._state["session_id"],
                    "current_task": self._state["current_task"],
                    "last_action": self._state["last_action"],
                    "current_status": self._state["current_status"],
                    "context": self._state["context"],
                    "metrics": self._state["metrics"],
                }
            }
        )

    def _record_change(self, field: str, old_value: Any, new_value: Any) -> None:
        self._change_log.append(
            {
                "field": field,
                "old_value": deepcopy(old_value),
                "new_value": deepcopy(new_value),
                "timestamp": datetime.now().isoformat(),
            }
        )
        if len(self._change_log) > 10:
            self._change_log.pop(0)

    def _notify_subscribers(self, field: str, value: Any) -> None:
        for callback in self._subscribers.get(field, []):
            try:
                callback(value)
            except Exception:
                pass

    @staticmethod
    def _filter_entries_by_terms(entries: List[Dict[str, Any]], query: str, limit: int) -> List[Dict[str, Any]]:
        terms = [term.lower() for term in query.split() if term.strip()]
        if not terms:
            return entries[:limit]

        matches = []
        for entry in entries:
            haystack = str(entry).lower()
            if all(term in haystack for term in terms):
                matches.append(entry)
            if len(matches) >= limit:
                break
        return matches


MEMORY = Memory()
