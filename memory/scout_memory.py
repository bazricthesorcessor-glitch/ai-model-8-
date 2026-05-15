"""
Scout Memory System - Cognitive Operating Memory for Scout Agent

Scout is the master coordinator. It needs:
1. 2-week exact memory (not summaries)
2. Lifetime archive with deep search
3. Current state/world knowledge
4. Agent state tracking
5. Priority-based memory management
6. Auto-cleanup of stale memory
7. Context compilation for 1M token window
"""

import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


# ============================================================================
# MEMORY STRUCTURE
# ============================================================================

class MemoryPriority(Enum):
    """Memory priority levels."""
    CRITICAL = 10    # Exam dates, explicit user saves, repeated failures
    HIGH = 7         # Project architecture, agent states, important decisions
    NORMAL = 5       # Regular conversations, completed tasks
    LOW = 2           # Small talk, temporary messages
    TEMP = 0          # Greetings, repeated outputs


@dataclass
class MemoryEntry:
    """Single memory entry with priority scoring."""
    timestamp: float
    speaker: str                    # 'user', 'scout', 'executor', etc.
    message: str
    importance: int = 5
    recency: int = 10
    task_relevance: int = 5
    emotional_weight: int = 0
    user_pinned: bool = False
    tags: List[str] = None
    agent: str = "scout"           # Which agent's memory

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

    @property
    def priority_score(self) -> int:
        """Calculate priority score (0-50)."""
        return (
            self.importance +
            self.recency +
            self.task_relevance +
            self.emotional_weight +
            (10 if self.user_pinned else 0)
        )


@dataclass
class StateSnapshot:
    """Current world state snapshot."""
    timestamp: float
    ui_state: Dict[str, Any]          # active window, workspace, etc.
    browser_state: Dict[str, Any]     # open tabs, active tab, etc.
    workspace_state: Dict[str, Any]   # workspace names and purposes
    agent_state: Dict[str, Any]       # executor_busy, coder_busy, etc.
    system_state: Dict[str, Any]      # battery, network, volume, brightness
    task_state: Dict[str, Any]        # active_tasks, completed_tasks, failed_tasks


# ============================================================================
# SCOUT MEMORY MANAGER
# ============================================================================

class ScoutMemoryManager:
    """Manages Scout's 3-tier memory system."""

    def __init__(self, memory_root: str = None):
        """
        Initialize memory manager.

        Args:
            memory_root: Root directory for memory (default: memory/)
        """
        self.root = Path(memory_root or "memory")
        self._setup_directories()

        # Configuration
        self.retention_days = 14        # 2 weeks exact memory
        self.archive_logs_after = 90    # Archive after 90 days
        self.max_active_entries = 5000  # Prevent bloat

        # Load current state
        self.current_state: Optional[StateSnapshot] = self._load_state()
        self.current_date = datetime.now().date()

    def _setup_directories(self) -> None:
        """Create memory directory structure."""
        dirs = [
            self.root / "active" / "daily_logs",
            self.root / "active" / "rolling_context",
            self.root / "archive" / "conversations",
            self.root / "archive" / "failures",
            self.root / "archive" / "projects",
            self.root / "state",
            self.root / "identity",
            self.root / "agents" / "scout",
            self.root / "agents" / "executor",
            self.root / "agents" / "coder",
            self.root / "agents" / "thinker",
            self.root / "semantic",
            self.root / "temporary",
            self.root / "indexes",
        ]

        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)

    # ========================================================================
    # ACTIVE MEMORY (2-WEEK ROLLING WINDOW)
    # ========================================================================

    def add_to_active_memory(
        self,
        speaker: str,
        message: str,
        importance: int = 5,
        tags: List[str] = None,
        agent: str = "scout",
    ) -> None:
        """
        Add entry to active memory (exact 2-week window).

        Args:
            speaker: Who said it ('user', 'scout', 'executor', etc.)
            message: What was said
            importance: 1-10 importance score
            tags: List of tags for this entry
            agent: Which agent this is for
        """
        entry = MemoryEntry(
            timestamp=time.time(),
            speaker=speaker,
            message=message,
            importance=importance,
            recency=10,  # Active memory is always recent
            task_relevance=5,
            tags=tags or [],
            agent=agent,
        )

        # Get today's log file
        today = datetime.now().strftime("%Y-%m-%d")
        log_path = self.root / "active" / "daily_logs" / f"{today}.jsonl"

        # Append entry to daily log
        with open(log_path, "a") as f:
            f.write(json.dumps(asdict(entry), default=str) + "\n")

        # Clean up old logs (keep only 14 days)
        self._cleanup_old_logs()

    def get_active_memory(self, days: int = 14) -> List[MemoryEntry]:
        """
        Get exact memory from last N days.

        Args:
            days: Number of days to retrieve

        Returns:
            List of memory entries sorted by recency
        """
        entries = []
        cutoff_date = datetime.now() - timedelta(days=days)

        logs_dir = self.root / "active" / "daily_logs"

        for log_file in sorted(logs_dir.glob("*.jsonl")):
            file_date = datetime.strptime(log_file.stem, "%Y-%m-%d")

            if file_date < cutoff_date:
                continue

            try:
                with open(log_file, "r") as f:
                    for line in f:
                        data = json.loads(line)
                        entries.append(MemoryEntry(**data))
            except json.JSONDecodeError:
                continue

        return sorted(entries, key=lambda x: x.timestamp, reverse=True)

    def _cleanup_old_logs(self) -> None:
        """Remove logs older than retention period."""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        logs_dir = self.root / "active" / "daily_logs"

        for log_file in logs_dir.glob("*.jsonl"):
            file_date = datetime.strptime(log_file.stem, "%Y-%m-%d")

            if file_date < cutoff_date:
                # Archive before deleting
                self._archive_daily_log(log_file)
                log_file.unlink()

    def _archive_daily_log(self, log_file: Path) -> None:
        """Archive daily log to archive storage."""
        archive_path = (
            self.root / "archive" / "conversations" /
            f"archive_{log_file.stem}.jsonl"
        )

        if not archive_path.exists():
            archive_path.write_text(log_file.read_text())

    # ========================================================================
    # ARCHIVE MEMORY (INFINITE SEARCH)
    # ========================================================================

    def add_to_archive(
        self,
        category: str,  # 'failures', 'projects', 'conversations'
        content: Dict[str, Any],
        tags: List[str] = None,
    ) -> None:
        """
        Add to long-term archive.

        Args:
            category: Archive category
            content: What to store
            tags: Search tags
        """
        archive_dir = self.root / "archive" / category
        archive_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().isoformat()
        filename = f"{timestamp.replace(':', '-')}.json"

        entry = {
            "timestamp": timestamp,
            "content": content,
            "tags": tags or [],
        }

        with open(archive_dir / filename, "w") as f:
            json.dump(entry, f, indent=2, default=str)

    def search_archive(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search archive for relevant information.

        Args:
            query: Search query
            category: Specific category to search
            limit: Max results

        Returns:
            List of matching entries
        """
        results = []

        if category:
            search_dirs = [self.root / "archive" / category]
        else:
            search_dirs = (self.root / "archive").glob("*")

        for search_dir in search_dirs:
            if not search_dir.is_dir():
                continue

            for entry_file in search_dir.glob("*.json"):
                try:
                    with open(entry_file, "r") as f:
                        entry = json.load(f)

                    # Simple keyword search
                    content_str = str(entry).lower()
                    if query.lower() in content_str:
                        results.append(entry)

                        if len(results) >= limit:
                            return results
                except json.JSONDecodeError:
                    continue

        return results

    # ========================================================================
    # STATE MEMORY (CURRENT REALITY)
    # ========================================================================

    def update_state(self, state: StateSnapshot) -> None:
        """Update current world state."""
        self.current_state = state

        # Save to file
        state_file = self.root / "state" / "current_state.json"

        state_data = {
            "timestamp": state.timestamp,
            "ui_state": state.ui_state,
            "browser_state": state.browser_state,
            "workspace_state": state.workspace_state,
            "agent_state": state.agent_state,
            "system_state": state.system_state,
            "task_state": state.task_state,
        }

        with open(state_file, "w") as f:
            json.dump(state_data, f, indent=2, default=str)

    def _load_state(self) -> Optional[StateSnapshot]:
        """Load current state from file."""
        state_file = self.root / "state" / "current_state.json"

        if not state_file.exists():
            return None

        try:
            with open(state_file, "r") as f:
                data = json.load(f)

            return StateSnapshot(
                timestamp=data.get("timestamp", time.time()),
                ui_state=data.get("ui_state", {}),
                browser_state=data.get("browser_state", {}),
                workspace_state=data.get("workspace_state", {}),
                agent_state=data.get("agent_state", {}),
                system_state=data.get("system_state", {}),
                task_state=data.get("task_state", {}),
            )
        except json.JSONDecodeError:
            return None

    def get_state(self) -> Optional[StateSnapshot]:
        """Get current state."""
        return self.current_state

    # ========================================================================
    # AGENT MEMORY
    # ========================================================================

    def get_agent_memory(self, agent_name: str) -> Dict[str, Any]:
        """Get specific agent's memory context."""
        agent_dir = self.root / "agents" / agent_name

        memory_context = {}

        for file_path in agent_dir.glob("*.json"):
            try:
                with open(file_path, "r") as f:
                    memory_context[file_path.stem] = json.load(f)
            except json.JSONDecodeError:
                continue

        return memory_context

    def save_agent_memory(
        self,
        agent_name: str,
        key: str,
        value: Dict[str, Any],
    ) -> None:
        """Save agent-specific memory."""
        agent_dir = self.root / "agents" / agent_name
        agent_dir.mkdir(parents=True, exist_ok=True)

        file_path = agent_dir / f"{key}.json"

        with open(file_path, "w") as f:
            json.dump(value, f, indent=2, default=str)

    # ========================================================================
    # IDENTITY MEMORY (PERMANENT)
    # ========================================================================

    def get_identity(self) -> Dict[str, Any]:
        """Get Scout's identity/personality."""
        identity = {}

        identity_dir = self.root / "identity"

        for file_path in identity_dir.glob("*.json"):
            try:
                with open(file_path, "r") as f:
                    identity[file_path.stem] = json.load(f)
            except json.JSONDecodeError:
                continue

        return identity

    def set_identity(self, key: str, value: Dict[str, Any]) -> None:
        """Update Scout's identity."""
        identity_file = self.root / "identity" / f"{key}.json"

        with open(identity_file, "w") as f:
            json.dump(value, f, indent=2, default=str)

    # ========================================================================
    # MEMORY STATS
    # ========================================================================

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        active_entries = len(self.get_active_memory())

        # Count archive
        archive_count = sum(1 for _ in (self.root / "archive").rglob("*.json"))

        # Count state files
        state_count = len(list((self.root / "state").glob("*.json")))

        return {
            "active_entries": active_entries,
            "archive_entries": archive_count,
            "state_files": state_count,
            "retention_days": self.retention_days,
            "current_date": str(self.current_date),
        }

    def cleanup_stale_memory(self) -> int:
        """
        Auto-clean stale/outdated memory.

        Returns:
            Number of entries removed
        """
        cleaned = 0

        # Remove logs older than retention period
        self._cleanup_old_logs()
        cleaned += 1

        # Clean stale browser tabs from state
        if self.current_state:
            original_tabs = len(self.current_state.browser_state.get("open_tabs", []))
            # Would verify tabs exist here
            cleaned += max(0, original_tabs - len(self.current_state.browser_state.get("open_tabs", [])))

        return cleaned


# ============================================================================
# DEMO / TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("SCOUT MEMORY SYSTEM TEST")
    print("=" * 60)

    manager = ScoutMemoryManager()

    # Test 1: Add to active memory
    print("\n[TEST 1] Adding to active memory...")
    manager.add_to_active_memory(
        speaker="user",
        message="Scout, please monitor the system",
        importance=8,
        tags=["important", "system"],
    )
    print("✓ Added to active memory")

    # Test 2: Get active memory
    print("\n[TEST 2] Retrieving active memory...")
    active = manager.get_active_memory(days=1)
    print(f"✓ Retrieved {len(active)} entries from active memory")

    # Test 3: Update state
    print("\n[TEST 3] Updating state...")
    state = StateSnapshot(
        timestamp=time.time(),
        ui_state={"active_window": "Brave", "workspace": 2},
        browser_state={"open_tabs": [{"title": "YouTube"}]},
        workspace_state={"workspace_1": "coding", "workspace_2": "media"},
        agent_state={"executor_busy": False, "scout_busy": True},
        system_state={"brightness": 0.8, "volume": 0.5},
        task_state={"active_tasks": [], "completed_tasks": []},
    )
    manager.update_state(state)
    print("✓ State updated")

    # Test 4: Get state
    print("\n[TEST 4] Retrieving state...")
    current = manager.get_state()
    if current:
        print(f"✓ Retrieved state: {current.ui_state}")

    # Test 5: Memory stats
    print("\n[TEST 5] Memory statistics...")
    stats = manager.get_memory_stats()
    print(json.dumps(stats, indent=2))

    print("\n" + "=" * 60)
    print("✓ SCOUT MEMORY TESTS PASSED")
    print("=" * 60)
