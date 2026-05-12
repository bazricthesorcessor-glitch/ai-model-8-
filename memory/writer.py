"""
Persistent memory write operations.
Handles saving, updating, and appending to memory files.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import asdict, is_dataclass

from . import paths


class MemoryWriter:
    """Handles all persistent write operations for Scout's memory system."""

    @staticmethod
    def ensure_parent_dir(filepath: Path) -> None:
        """Ensure parent directory exists."""
        filepath.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def save_json(filepath: Path, data: Any, pretty: bool = True) -> None:
        """Save data as JSON file.

        Args:
            filepath: Path to save to
            data: Data to serialize (dict, list, or dataclass)
            pretty: Whether to pretty-print JSON
        """
        MemoryWriter.ensure_parent_dir(filepath)

        # Convert dataclass to dict if needed
        if is_dataclass(data) and not isinstance(data, type):
            data = asdict(data)

        with open(filepath, 'w') as f:
            if pretty:
                json.dump(data, f, indent=2, default=str)
            else:
                json.dump(data, f, default=str)

    @staticmethod
    def append_jsonl(filepath: Path, data: Dict[str, Any]) -> None:
        """Append a JSON line to a JSONL file.

        Args:
            filepath: Path to append to
            data: Data to append (will be serialized as one line)
        """
        MemoryWriter.ensure_parent_dir(filepath)

        # Convert dataclass to dict if needed
        if is_dataclass(data) and not isinstance(data, type):
            data = asdict(data)

        with open(filepath, 'a') as f:
            json.dump(data, f, default=str)
            f.write('\n')

    @staticmethod
    def update_json(filepath: Path, updates: Dict[str, Any]) -> None:
        """Load JSON, update specific keys, and save back.

        Args:
            filepath: Path to update
            updates: Dictionary of key-value pairs to update
        """
        MemoryWriter.ensure_parent_dir(filepath)

        # Load existing data
        if filepath.exists():
            with open(filepath, 'r') as f:
                data = json.load(f)
        else:
            data = {}

        # Update
        data.update(updates)

        # Save back
        MemoryWriter.save_json(filepath, data)

    # ========================================================================
    # DAILY LOG OPERATIONS
    # ========================================================================

    @staticmethod
    def log_to_daily(entry: Dict[str, Any], date: Optional[datetime] = None) -> None:
        """Append entry to today's daily log.

        Args:
            entry: Log entry (will auto-add timestamp if missing)
            date: Date for the log (default: today)
        """
        if date is None:
            date = datetime.now()

        # Add timestamp if missing
        if 'timestamp' not in entry:
            entry['timestamp'] = datetime.now().isoformat()

        filepath = paths.get_daily_log_path(date)
        MemoryWriter.append_jsonl(filepath, entry)

    @staticmethod
    def create_daily_log_entry(
        log_type: str,
        message: str,
        category: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        severity: str = "info"
    ) -> Dict[str, Any]:
        """Create a structured daily log entry.

        Args:
            log_type: Type of log (decision, action, error, state_change, etc.)
            message: Human-readable message
            category: Category for filtering (optional)
            data: Additional structured data
            severity: Severity level (info, warning, error, critical)
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": log_type,
            "message": message,
            "severity": severity,
        }
        if category:
            entry["category"] = category
        if data:
            entry["data"] = data

        return entry

    # ========================================================================
    # ARCHIVE OPERATIONS
    # ========================================================================

    @staticmethod
    def save_to_archive(
        archive_type: str,
        archive_id: str,
        data: Dict[str, Any]
    ) -> Path:
        """Save item to appropriate archive category.

        Args:
            archive_type: Type of archive (conversations, failures, projects, sessions)
            archive_id: Unique identifier for the item
            data: Data to save (will auto-add metadata)

        Returns:
            Path to saved file
        """
        # Auto-add metadata
        if 'archived_at' not in data:
            data['archived_at'] = datetime.now().isoformat()
        if 'archive_id' not in data:
            data['archive_id'] = archive_id

        # Determine archive path
        if archive_type == "conversations":
            filepath = paths.ARCHIVE_CONVERSATIONS / f"{archive_id}.json"
        elif archive_type == "failures":
            filepath = paths.ARCHIVE_FAILURES / f"{archive_id}.json"
        elif archive_type == "projects":
            filepath = paths.ARCHIVE_PROJECTS / f"{archive_id}.json"
        elif archive_type == "sessions":
            filepath = paths.ARCHIVE_SESSIONS / f"{archive_id}.json"
        elif archive_type == "semantic":
            filepath = paths.ARCHIVE_SEMANTIC / f"{archive_id}.json"
        else:
            raise ValueError(f"Unknown archive type: {archive_type}")

        # Save
        MemoryWriter.save_json(filepath, data)

        # Update index
        MemoryWriter._update_archive_index(archive_type, archive_id, filepath)

        return filepath

    @staticmethod
    def _update_archive_index(archive_type: str, archive_id: str, filepath: Path) -> None:
        """Update archive index for faster lookups."""
        if archive_type == "conversations":
            index_file = paths.ARCHIVE_CONVERSATIONS_INDEX
        elif archive_type == "failures":
            index_file = paths.ARCHIVE_FAILURES_INDEX
        elif archive_type == "projects":
            index_file = paths.ARCHIVE_PROJECTS_INDEX
        elif archive_type == "sessions":
            index_file = paths.ARCHIVE_SESSIONS_INDEX
        else:
            return

        # Load existing index
        if index_file.exists():
            with open(index_file, 'r') as f:
                index = json.load(f)
        else:
            index = {}

        # Add entry
        index[archive_id] = {
            "path": str(filepath.relative_to(paths.MEMORY_ROOT)),
            "updated_at": datetime.now().isoformat(),
        }

        # Save index
        MemoryWriter.save_json(index_file, index)

    # ========================================================================
    # IDENTITY & IMPORTANT MEMORY
    # ========================================================================

    @staticmethod
    def save_important_memory(memory_item: Dict[str, Any]) -> None:
        """Save user-explicit important memory.

        Args:
            memory_item: Should have 'content', optionally 'category', 'tags'
        """
        # Ensure metadata
        if 'saved_at' not in memory_item:
            memory_item['saved_at'] = datetime.now().isoformat()

        # Load existing
        if paths.IMPORTANT_MEMORY_FILE.exists():
            with open(paths.IMPORTANT_MEMORY_FILE, 'r') as f:
                data = json.load(f)
        else:
            data = {"items": []}

        # Append
        data["items"].append(memory_item)

        # Save
        MemoryWriter.save_json(paths.IMPORTANT_MEMORY_FILE, data)

    @staticmethod
    def save_user_preferences(preferences: Dict[str, Any]) -> None:
        """Save or update user preferences."""
        data = {
            "preferences": preferences,
            "updated_at": datetime.now().isoformat(),
        }
        MemoryWriter.save_json(paths.USER_PREFERENCES_FILE, data)

    # ========================================================================
    # STATE SNAPSHOTS
    # ========================================================================

    @staticmethod
    def save_state_snapshot(state_data: Dict[str, Any]) -> None:
        """Save current state snapshot."""
        state_data['snapshot_at'] = datetime.now().isoformat()
        MemoryWriter.save_json(paths.STATE_SNAPSHOT_FILE, state_data)

    @staticmethod
    def log_execution_history(execution: Dict[str, Any]) -> None:
        """Log execution event to history."""
        if 'timestamp' not in execution:
            execution['timestamp'] = datetime.now().isoformat()
        MemoryWriter.append_jsonl(paths.EXECUTION_HISTORY_FILE, execution)

    @staticmethod
    def save_agents_state(agents_state: Dict[str, Any]) -> None:
        """Save state of all agents."""
        agents_state['updated_at'] = datetime.now().isoformat()
        MemoryWriter.save_json(paths.AGENTS_STATE_FILE, agents_state)

    @staticmethod
    def save_browser_state(browser_state: Dict[str, Any]) -> None:
        """Save browser state."""
        browser_state['updated_at'] = datetime.now().isoformat()
        MemoryWriter.save_json(paths.BROWSER_STATE_FILE, browser_state)

    @staticmethod
    def save_workspace_state(workspace_state: Dict[str, Any]) -> None:
        """Save workspace state."""
        workspace_state['updated_at'] = datetime.now().isoformat()
        MemoryWriter.save_json(paths.WORKSPACE_STATE_FILE, workspace_state)

    # ========================================================================
    # TEMPORARY MEMORY (Expiring items)
    # ========================================================================

    @staticmethod
    def add_exam(exam_data: Dict[str, Any]) -> None:
        """Add exam to temporary exams list."""
        MemoryWriter._add_to_expiry_list(
            paths.EXAMS_FILE,
            exam_data,
            required_fields=['name', 'date']
        )

    @staticmethod
    def add_deadline(deadline_data: Dict[str, Any]) -> None:
        """Add deadline to temporary deadlines list."""
        MemoryWriter._add_to_expiry_list(
            paths.DEADLINES_FILE,
            deadline_data,
            required_fields=['title', 'date']
        )

    @staticmethod
    def add_event(event_data: Dict[str, Any]) -> None:
        """Add event to temporary events list."""
        MemoryWriter._add_to_expiry_list(
            paths.EVENTS_FILE,
            event_data,
            required_fields=['title', 'date']
        )

    @staticmethod
    def _add_to_expiry_list(filepath: Path, item: Dict[str, Any], required_fields: List[str]) -> None:
        """Add item to an expiry list file."""
        # Validate required fields
        for field in required_fields:
            if field not in item:
                raise ValueError(f"Missing required field: {field}")

        # Add metadata
        item['added_at'] = datetime.now().isoformat()

        # Load existing
        MemoryWriter.ensure_parent_dir(filepath)
        if filepath.exists():
            with open(filepath, 'r') as f:
                data = json.load(f)
        else:
            data = {"items": []}

        # Append
        data["items"].append(item)

        # Save
        MemoryWriter.save_json(filepath, data)

    # ========================================================================
    # TOOLS & REGISTRY
    # ========================================================================

    @staticmethod
    def save_tool_registry(registry: Dict[str, Any]) -> None:
        """Save tool registry."""
        registry['updated_at'] = datetime.now().isoformat()
        MemoryWriter.save_json(paths.TOOL_REGISTRY_FILE, registry)

    @staticmethod
    def log_tool_usage(tool_name: str, usage_data: Dict[str, Any]) -> None:
        """Log tool usage event."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            **usage_data
        }
        MemoryWriter.append_jsonl(paths.TOOL_USAGE_LOG, entry)

    # ========================================================================
    # AGENT-SPECIFIC MEMORY
    # ========================================================================

    @staticmethod
    def save_agent_memory(agent_name: str, memory_type: str, data: Dict[str, Any]) -> None:
        """Save memory for a specific agent.

        Args:
            agent_name: Name of the agent (e.g., 'executor', 'scout')
            memory_type: Type of memory (recent, archive, learned, context)
            data: Memory data
        """
        filepath = paths.get_agent_memory_file(agent_name, memory_type)
        data['updated_at'] = datetime.now().isoformat()
        MemoryWriter.save_json(filepath, data)


def initialize_memory_system() -> None:
    """Initialize all memory directories and create default files."""
    paths.ensure_all_directories()

    # Create default empty files/structures
    default_files = {
        paths.IMPORTANT_MEMORY_FILE: {"items": []},
        paths.STATE_SNAPSHOT_FILE: {"state": None, "initialized_at": datetime.now().isoformat()},
        paths.AGENTS_STATE_FILE: {"agents": {}},
        paths.TOOL_REGISTRY_FILE: {"tools": {}},
        paths.EXAMS_FILE: {"items": []},
        paths.DEADLINES_FILE: {"items": []},
        paths.EVENTS_FILE: {"items": []},
    }

    for filepath, default_data in default_files.items():
        if not filepath.exists():
            MemoryWriter.save_json(filepath, default_data)


if __name__ == "__main__":
    # Initialize memory system
    initialize_memory_system()
    print("Memory writer initialized")

    # Test logging
    entry = MemoryWriter.create_daily_log_entry(
        log_type="test",
        message="Testing daily log",
        category="initialization",
        severity="info"
    )
    MemoryWriter.log_to_daily(entry)
    print(f"Test entry logged to {paths.get_daily_log_path()}")
