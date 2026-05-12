"""
Persistent memory read operations.
Handles loading, querying, and retrieving from memory files.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Generator

from . import paths


class MemoryReader:
    """Handles all persistent read operations for Scout's memory system."""

    # ========================================================================
    # DAILY LOG OPERATIONS
    # ========================================================================

    @staticmethod
    def load_daily_log(date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Load entries from a specific day's log.

        Args:
            date: Date to load (default: today)

        Returns:
            List of log entries
        """
        if date is None:
            date = datetime.now()

        filepath = paths.get_daily_log_path(date)

        if not filepath.exists():
            return []

        entries = []
        with open(filepath, 'r') as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))

        return entries

    @staticmethod
    def load_14_day_memory() -> List[Dict[str, Any]]:
        """Load all entries from the last 14 days.

        Returns:
            List of all entries from past 14 days, newest first
        """
        all_entries = []
        today = datetime.now()

        for days_back in range(14):
            date = today - timedelta(days=days_back)
            entries = MemoryReader.load_daily_log(date)
            all_entries.extend(entries)

        # Sort by timestamp, newest first
        all_entries.sort(
            key=lambda x: x.get('timestamp', ''),
            reverse=True
        )

        return all_entries

    @staticmethod
    def stream_daily_log(date: Optional[datetime] = None) -> Generator[Dict[str, Any], None, None]:
        """Stream entries from a daily log (memory efficient).

        Args:
            date: Date to stream (default: today)

        Yields:
            Log entries one at a time
        """
        if date is None:
            date = datetime.now()

        filepath = paths.get_daily_log_path(date)

        if not filepath.exists():
            return

        with open(filepath, 'r') as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)

    @staticmethod
    def filter_daily_log(
        date: Optional[datetime] = None,
        log_type: Optional[str] = None,
        category: Optional[str] = None,
        severity: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Load and filter entries from a daily log.

        Args:
            date: Date to load (default: today)
            log_type: Filter by type (decision, action, error, etc.)
            category: Filter by category
            severity: Filter by severity (info, warning, error, critical)

        Returns:
            Filtered list of entries
        """
        entries = MemoryReader.load_daily_log(date)

        if log_type:
            entries = [e for e in entries if e.get('type') == log_type]
        if category:
            entries = [e for e in entries if e.get('category') == category]
        if severity:
            entries = [e for e in entries if e.get('severity') == severity]

        return entries

    # ========================================================================
    # ARCHIVE OPERATIONS
    # ========================================================================

    @staticmethod
    def load_archive_item(archive_type: str, item_id: str) -> Optional[Dict[str, Any]]:
        """Load a specific item from archive.

        Args:
            archive_type: Type of archive (conversations, failures, projects, sessions)
            item_id: ID of the item

        Returns:
            Item data or None if not found
        """
        if archive_type == "conversations":
            filepath = paths.ARCHIVE_CONVERSATIONS / f"{item_id}.json"
        elif archive_type == "failures":
            filepath = paths.ARCHIVE_FAILURES / f"{item_id}.json"
        elif archive_type == "projects":
            filepath = paths.ARCHIVE_PROJECTS / f"{item_id}.json"
        elif archive_type == "sessions":
            filepath = paths.ARCHIVE_SESSIONS / f"{item_id}.json"
        elif archive_type == "semantic":
            filepath = paths.ARCHIVE_SEMANTIC / f"{item_id}.json"
        else:
            return None

        if not filepath.exists():
            return None

        with open(filepath, 'r') as f:
            return json.load(f)

    @staticmethod
    def list_archive(archive_type: str) -> List[str]:
        """List all IDs in an archive category.

        Args:
            archive_type: Type of archive (conversations, failures, projects, sessions)

        Returns:
            List of item IDs
        """
        if archive_type == "conversations":
            directory = paths.ARCHIVE_CONVERSATIONS
        elif archive_type == "failures":
            directory = paths.ARCHIVE_FAILURES
        elif archive_type == "projects":
            directory = paths.ARCHIVE_PROJECTS
        elif archive_type == "sessions":
            directory = paths.ARCHIVE_SESSIONS
        elif archive_type == "semantic":
            directory = paths.ARCHIVE_SEMANTIC
        else:
            return []

        if not directory.exists():
            return []

        return [f.stem for f in directory.glob("*.json")]

    @staticmethod
    def load_all_archive(archive_type: str) -> List[Dict[str, Any]]:
        """Load all items from an archive category.

        Args:
            archive_type: Type of archive

        Returns:
            List of all items in that category
        """
        item_ids = MemoryReader.list_archive(archive_type)
        items = []

        for item_id in item_ids:
            item = MemoryReader.load_archive_item(archive_type, item_id)
            if item:
                items.append(item)

        return items

    # ========================================================================
    # IDENTITY & IMPORTANT MEMORY
    # ========================================================================

    @staticmethod
    def load_important_memory() -> Dict[str, Any]:
        """Load all important memories.

        Returns:
            Dictionary with 'items' list
        """
        if not paths.IMPORTANT_MEMORY_FILE.exists():
            return {"items": []}

        with open(paths.IMPORTANT_MEMORY_FILE, 'r') as f:
            return json.load(f)

    @staticmethod
    def get_important_memory_by_category(category: str) -> List[Dict[str, Any]]:
        """Get important memories filtered by category."""
        data = MemoryReader.load_important_memory()
        return [
            item for item in data.get("items", [])
            if item.get("category") == category
        ]

    @staticmethod
    def load_user_preferences() -> Dict[str, Any]:
        """Load user preferences."""
        if not paths.USER_PREFERENCES_FILE.exists():
            return {}

        with open(paths.USER_PREFERENCES_FILE, 'r') as f:
            data = json.load(f)

        return data.get("preferences", {})

    @staticmethod
    def load_identity() -> Dict[str, Any]:
        """Load identity information."""
        if not paths.IDENTITY_FILE.exists():
            return {}

        with open(paths.IDENTITY_FILE, 'r') as f:
            return json.load(f)

    # ========================================================================
    # STATE SNAPSHOTS
    # ========================================================================

    @staticmethod
    def load_current_state() -> Dict[str, Any]:
        """Load last saved state snapshot."""
        if not paths.STATE_SNAPSHOT_FILE.exists():
            return {}

        with open(paths.STATE_SNAPSHOT_FILE, 'r') as f:
            return json.load(f)

    @staticmethod
    def load_agents_state() -> Dict[str, Any]:
        """Load state of all agents."""
        if not paths.AGENTS_STATE_FILE.exists():
            return {"agents": {}}

        with open(paths.AGENTS_STATE_FILE, 'r') as f:
            return json.load(f)

    @staticmethod
    def load_browser_state() -> Dict[str, Any]:
        """Load browser state."""
        if not paths.BROWSER_STATE_FILE.exists():
            return {}

        with open(paths.BROWSER_STATE_FILE, 'r') as f:
            return json.load(f)

    @staticmethod
    def load_workspace_state() -> Dict[str, Any]:
        """Load workspace state."""
        if not paths.WORKSPACE_STATE_FILE.exists():
            return {}

        with open(paths.WORKSPACE_STATE_FILE, 'r') as f:
            return json.load(f)

    @staticmethod
    def load_execution_history(limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load execution history.

        Args:
            limit: Maximum number of recent entries to load

        Returns:
            List of execution entries
        """
        if not paths.EXECUTION_HISTORY_FILE.exists():
            return []

        entries = []
        with open(paths.EXECUTION_HISTORY_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))

        # Return most recent entries first
        entries.reverse()

        if limit:
            return entries[:limit]

        return entries

    # ========================================================================
    # TEMPORARY MEMORY (Expiring items)
    # ========================================================================

    @staticmethod
    def load_exams() -> List[Dict[str, Any]]:
        """Load all exams."""
        if not paths.EXAMS_FILE.exists():
            return []

        with open(paths.EXAMS_FILE, 'r') as f:
            data = json.load(f)

        return data.get("items", [])

    @staticmethod
    def load_deadlines() -> List[Dict[str, Any]]:
        """Load all deadlines."""
        if not paths.DEADLINES_FILE.exists():
            return []

        with open(paths.DEADLINES_FILE, 'r') as f:
            data = json.load(f)

        return data.get("items", [])

    @staticmethod
    def load_events() -> List[Dict[str, Any]]:
        """Load all events."""
        if not paths.EVENTS_FILE.exists():
            return []

        with open(paths.EVENTS_FILE, 'r') as f:
            data = json.load(f)

        return data.get("items", [])

    @staticmethod
    def get_upcoming_deadlines(days: int = 7) -> List[Dict[str, Any]]:
        """Get deadlines within the next N days.

        Args:
            days: Number of days to look ahead

        Returns:
            List of upcoming deadlines
        """
        deadlines = MemoryReader.load_deadlines()
        now = datetime.now()
        cutoff = now + timedelta(days=days)

        upcoming = []
        for deadline in deadlines:
            try:
                deadline_date = datetime.fromisoformat(deadline['date'])
                if now <= deadline_date <= cutoff:
                    upcoming.append(deadline)
            except (ValueError, KeyError):
                pass

        # Sort by date
        upcoming.sort(key=lambda x: x['date'])

        return upcoming

    @staticmethod
    def get_upcoming_exams(days: int = 7) -> List[Dict[str, Any]]:
        """Get exams within the next N days."""
        exams = MemoryReader.load_exams()
        now = datetime.now()
        cutoff = now + timedelta(days=days)

        upcoming = []
        for exam in exams:
            try:
                exam_date = datetime.fromisoformat(exam['date'])
                if now <= exam_date <= cutoff:
                    upcoming.append(exam)
            except (ValueError, KeyError):
                pass

        # Sort by date
        upcoming.sort(key=lambda x: x['date'])

        return upcoming

    # ========================================================================
    # TOOLS & REGISTRY
    # ========================================================================

    @staticmethod
    def load_tool_registry() -> Dict[str, Any]:
        """Load tool registry."""
        if not paths.TOOL_REGISTRY_FILE.exists():
            return {"tools": {}}

        with open(paths.TOOL_REGISTRY_FILE, 'r') as f:
            return json.load(f)

    @staticmethod
    def get_tool_info(tool_name: str) -> Optional[Dict[str, Any]]:
        """Get info about a specific tool."""
        registry = MemoryReader.load_tool_registry()
        return registry.get("tools", {}).get(tool_name)

    @staticmethod
    def load_tool_usage_log(limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load tool usage log."""
        if not paths.TOOL_USAGE_LOG.exists():
            return []

        entries = []
        with open(paths.TOOL_USAGE_LOG, 'r') as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))

        # Return most recent first
        entries.reverse()

        if limit:
            return entries[:limit]

        return entries

    # ========================================================================
    # AGENT-SPECIFIC MEMORY
    # ========================================================================

    @staticmethod
    def load_agent_memory(agent_name: str, memory_type: str) -> Optional[Dict[str, Any]]:
        """Load memory for a specific agent.

        Args:
            agent_name: Name of the agent
            memory_type: Type of memory (recent, archive, learned, context)

        Returns:
            Memory data or None if not found
        """
        filepath = paths.get_agent_memory_file(agent_name, memory_type)

        if not filepath.exists():
            return None

        with open(filepath, 'r') as f:
            return json.load(f)

    @staticmethod
    def list_agent_memories(agent_name: str) -> List[str]:
        """List all memory types for an agent."""
        agent_dir = paths.get_agent_memory_dir(agent_name)

        if not agent_dir.exists():
            return []

        return [f.stem for f in agent_dir.glob("*.json")]

    # ========================================================================
    # SEARCH & QUERY
    # ========================================================================

    @staticmethod
    def search_daily_logs(query: str, days: int = 14) -> List[Dict[str, Any]]:
        """Search daily logs for entries containing query text.

        Args:
            query: Search query (case-insensitive substring match)
            days: Number of days to search back

        Returns:
            List of matching entries
        """
        results = []
        today = datetime.now()
        query_lower = query.lower()

        for days_back in range(days):
            date = today - timedelta(days=days_back)
            entries = MemoryReader.load_daily_log(date)

            for entry in entries:
                # Check message and other string fields
                message = entry.get('message', '').lower()
                if query_lower in message:
                    results.append(entry)

        return results

    @staticmethod
    def search_archives(query: str, archive_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search archive items for query text.

        Args:
            query: Search query (case-insensitive substring match)
            archive_type: Specific archive to search, or None for all

        Returns:
            List of matching items
        """
        results = []
        query_lower = query.lower()

        # Determine which archives to search
        archives = [archive_type] if archive_type else [
            "conversations",
            "failures",
            "projects",
            "sessions",
            "semantic"
        ]

        for archive in archives:
            items = MemoryReader.load_all_archive(archive)

            for item in items:
                # Search in title, content, message, description fields
                searchable = str(item).lower()
                if query_lower in searchable:
                    results.append(item)

        return results


def get_memory_status() -> Dict[str, Any]:
    """Get current memory system status."""
    return {
        "today_log_entries": len(MemoryReader.load_daily_log()),
        "14day_entries": len(MemoryReader.load_14_day_memory()),
        "important_memories": len(MemoryReader.load_important_memory().get("items", [])),
        "archive_conversations": len(MemoryReader.list_archive("conversations")),
        "archive_failures": len(MemoryReader.list_archive("failures")),
        "archive_projects": len(MemoryReader.list_archive("projects")),
        "archive_sessions": len(MemoryReader.list_archive("sessions")),
        "upcoming_deadlines": len(MemoryReader.get_upcoming_deadlines()),
        "upcoming_exams": len(MemoryReader.get_upcoming_exams()),
    }


if __name__ == "__main__":
    print("Memory Reader Test")
    print("=" * 50)

    status = get_memory_status()
    for key, value in status.items():
        print(f"{key}: {value}")

    print("\n14-day entries (last 5):")
    entries = MemoryReader.load_14_day_memory()[:5]
    for entry in entries:
        print(f"  {entry.get('timestamp')} - {entry.get('message', '')[:50]}")
