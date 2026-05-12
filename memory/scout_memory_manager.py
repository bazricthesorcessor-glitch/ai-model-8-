"""
Scout Memory Manager - Scout has ALL memory types (Active, Archive, State)

ARCHITECTURE:
  Scout: ├─ Active Memory (14-day exact logs)
         ├─ Archive Memory (searchable history)
         ├─ State Memory (current reality)
         └─ Agent-specific subdirectories

  Agents (Executor, Coder, Thinker):
         Get ONLY their context from query_maker via Scout
"""

import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class MemoryEntry:
    """Entry in Scout's memory."""
    timestamp: float
    speaker: str
    message: str
    agent: str           # Which agent domain (scout, executor, coder, thinker)
    importance: int = 5
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class ScoutMemoryManager:
    """Scout's complete 3-tier memory system."""

    def __init__(self, memory_root: str = "memory/scout"):
        self.root = Path(memory_root)
        self.root.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (self.root / "active").mkdir(exist_ok=True)
        (self.root / "archive").mkdir(exist_ok=True)
        (self.root / "state").mkdir(exist_ok=True)

        self.retention_days = 14
        self.current_state = None

    # ========================================================================
    # TIER 1: ACTIVE MEMORY (14-day rolling window)
    # ========================================================================

    def add_to_active(
        self,
        speaker: str,
        message: str,
        agent: str,
        importance: int = 5,
        tags: List[str] = None,
    ) -> None:
        """Add to Scout's active memory."""
        entry = MemoryEntry(
            timestamp=time.time(),
            speaker=speaker,
            message=message,
            agent=agent,
            importance=importance,
            tags=tags or [],
        )

        # Daily log file
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.root / "active" / f"{today}.jsonl"

        with open(log_file, "a") as f:
            f.write(json.dumps(asdict(entry), default=str) + "\n")

        # Cleanup old logs
        self._cleanup_active()

    def get_active(self, days: int = 14, agent: Optional[str] = None) -> List[MemoryEntry]:
        """Get active memory from Scout."""
        entries = []
        cutoff = datetime.now() - timedelta(days=days)

        for log_file in sorted((self.root / "active").glob("*.jsonl")):
            file_date = datetime.strptime(log_file.stem, "%Y-%m-%d")
            if file_date < cutoff:
                continue

            with open(log_file, "r") as f:
                for line in f:
                    data = json.loads(line)
                    entry = MemoryEntry(**data)
                    if agent is None or entry.agent == agent:
                        entries.append(entry)

        return sorted(entries, key=lambda x: x.timestamp, reverse=True)

    def _cleanup_active(self) -> None:
        """Move old logs to archive."""
        cutoff = datetime.now() - timedelta(days=self.retention_days)

        for log_file in (self.root / "active").glob("*.jsonl"):
            file_date = datetime.strptime(log_file.stem, "%Y-%m-%d")
            if file_date < cutoff:
                log_file.unlink()

    # ========================================================================
    # TIER 2: ARCHIVE MEMORY (Infinite searchable)
    # ========================================================================

    def add_to_archive(
        self,
        category: str,  # 'failures', 'projects', 'conversations'
        data: Dict[str, Any],
    ) -> None:
        """Archive important information."""
        archive_dir = self.root / "archive" / category
        archive_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().isoformat().replace(":", "-")
        with open(archive_dir / f"{timestamp}.json", "w") as f:
            json.dump(data, f, indent=2, default=str)

    def search_archive(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict]:
        """Search Scout's archive."""
        results = []
        dirs = [(self.root / "archive" / category)] if category else (self.root / "archive").glob("*")

        for dir_path in dirs:
            if not dir_path.is_dir():
                continue

            for json_file in dir_path.glob("*.json"):
                try:
                    with open(json_file, "r") as f:
                        data = json.load(f)
                    if query.lower() in str(data).lower():
                        results.append(data)
                        if len(results) >= limit:
                            return results
                except json.JSONDecodeError:
                    continue

        return results

    # ========================================================================
    # TIER 3: STATE MEMORY (Current reality)
    # ========================================================================

    def update_state(self, state: Dict[str, Any]) -> None:
        """Update current system state."""
        self.current_state = state

        state_file = self.root / "state" / "current.json"
        with open(state_file, "w") as f:
            json.dump(state, f, indent=2, default=str)

    def get_state(self) -> Optional[Dict[str, Any]]:
        """Get current state."""
        if self.current_state:
            return self.current_state

        state_file = self.root / "state" / "current.json"
        if state_file.exists():
            try:
                with open(state_file, "r") as f:
                    self.current_state = json.load(f)
                    return self.current_state
            except json.JSONDecodeError:
                pass

        return None

    # ========================================================================
    # SESSION CONTINUITY
    # ========================================================================

    def save_last_session(self, messages: List[Dict]) -> None:
        """Save last conversation."""
        session_file = self.root / "state" / "last_session.json"
        with open(session_file, "w") as f:
            json.dump({
                "timestamp": time.time(),
                "messages": messages,
            }, f, indent=2, default=str)

    def load_last_session(self) -> Optional[Dict]:
        """Load last conversation."""
        session_file = self.root / "state" / "last_session.json"
        if not session_file.exists():
            return None

        try:
            with open(session_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return None

    # ========================================================================
    # CONVENIENCE METHODS
    # ========================================================================

    def log_action(self, agent: str, action: str, result: Dict) -> None:
        """Log agent action."""
        self.add_to_active(
            speaker=agent,
            message=f"Action: {action}",
            agent=agent,
            importance=6,
            tags=["action"],
        )

    def log_error(self, agent: str, action: str, error: str) -> None:
        """Log error."""
        self.add_to_active(
            speaker=agent,
            message=f"Error in {action}: {error}",
            agent=agent,
            importance=8,
            tags=["error"],
        )

        # Archive for learning
        self.add_to_archive("failures", {
            "agent": agent,
            "action": action,
            "error": error,
            "timestamp": datetime.now().isoformat(),
        })


if __name__ == "__main__":
    print("=" * 60)
    print("SCOUT MEMORY MANAGER TEST")
    print("=" * 60)

    scout = ScoutMemoryManager()

    # Test: Add to active
    print("\n[TEST 1] Adding to active memory...")
    scout.add_to_active("user", "Take screenshot", "scout", importance=8)
    print("✓ Added")

    # Test: Get active
    print("\n[TEST 2] Getting active memory...")
    recent = scout.get_active()
    print(f"✓ Found {len(recent)} entries")

    # Test: Log error
    print("\n[TEST 3] Logging error...")
    scout.log_error("executor", "screenshot", "tool not found")
    print("✓ Logged")

    # Test: State
    print("\n[TEST 4] Updating state...")
    scout.update_state({"browser": {"tabs": []}, "workspace": 1})
    state = scout.get_state()
    print(f"✓ State: {state}")

    # Test: Session
    print("\n[TEST 5] Saving session...")
    scout.save_last_session([{"speaker": "user", "message": "test"}])
    session = scout.load_last_session()
    print(f"✓ Loaded {len(session['messages'])} messages")

    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED")
    print("=" * 60)
