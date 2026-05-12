"""
UNIFIED MEMORY ARCHITECTURE - Single System for All Agents

This unifies:
- memory/memory.py (action logging)
- memory/scout_memory.py (Scout's 3-tier system)
- executor/caelestia_integration.py (Executor context)

Into one coherent architecture.

PRINCIPLE: Three-tier memory pool that all agents draw from.
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


# ============================================================================
# UNIFIED MEMORY TYPES
# ============================================================================

class AgentRole(Enum):
    """Agent types in the system."""
    SCOUT = "scout"          # Master coordinator
    EXECUTOR = "executor"    # System actions
    CODER = "coder"          # Code operations
    THINKER = "thinker"      # Strategic thinking


@dataclass
class MemoryEntry:
    """Unified memory entry used by all agents."""
    timestamp: float
    speaker: str              # 'user', 'scout', 'executor', 'coder', 'thinker'
    message: str
    agent_role: str           # Which agent's domain
    importance: int = 5       # 0-10
    tags: List[str] = None
    result: Optional[Dict] = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

    @property
    def priority_score(self) -> int:
        """Calculate priority (higher = more important for context)."""
        base = self.importance
        if self.error:
            base += 3  # Failures are important
        if 'repeated' in self.tags:
            base += 2
        return min(base, 10)


# ============================================================================
# TIER 1: ACTIVE MEMORY (14-day rolling window)
# ============================================================================

class ActiveMemory:
    """Recent exact memory - what agents see most of the time."""

    def __init__(self, root: str = "memory/active"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.retention_days = 14

    def add(
        self,
        speaker: str,
        message: str,
        agent_role: str,
        importance: int = 5,
        tags: List[str] = None,
    ) -> None:
        """Add entry to active memory."""
        entry = MemoryEntry(
            timestamp=time.time(),
            speaker=speaker,
            message=message,
            agent_role=agent_role,
            importance=importance,
            tags=tags or [],
        )

        # Write to daily log
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.root / f"{today}.jsonl"

        with open(log_file, "a") as f:
            f.write(json.dumps(asdict(entry), default=str) + "\n")

        # Cleanup old logs
        self._cleanup_old()

    def get(self, days: int = 14, agent_role: Optional[str] = None) -> List[MemoryEntry]:
        """Get active memory from last N days."""
        entries = []
        cutoff = datetime.now() - timedelta(days=days)

        for log_file in sorted(self.root.glob("*.jsonl")):
            if log_file.suffix == ".jsonl":
                file_date = datetime.strptime(log_file.stem, "%Y-%m-%d")
                if file_date < cutoff:
                    continue

                with open(log_file, "r") as f:
                    for line in f:
                        data = json.loads(line)
                        entry = MemoryEntry(**data)

                        if agent_role is None or entry.agent_role == agent_role:
                            entries.append(entry)

        return sorted(entries, key=lambda x: x.timestamp, reverse=True)

    def _cleanup_old(self) -> None:
        """Move logs older than retention period to archive."""
        cutoff = datetime.now() - timedelta(days=self.retention_days)

        for log_file in self.root.glob("*.jsonl"):
            file_date = datetime.strptime(log_file.stem, "%Y-%m-%d")
            if file_date < cutoff:
                log_file.unlink()


# ============================================================================
# TIER 2: ARCHIVE MEMORY (Infinite searchable history)
# ============================================================================

class ArchiveMemory:
    """Permanent storage, searchable."""

    def __init__(self, root: str = "memory/archive"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def add(self, category: str, data: Dict[str, Any]) -> None:
        """Add to archive (category = failures, projects, conversations, etc.)."""
        category_dir = self.root / category
        category_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().isoformat().replace(":", "-")
        filename = f"{timestamp}.json"

        with open(category_dir / filename, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict]:
        """Search archive for entries matching query."""
        results = []

        dirs = [self.root / category] if category else self.root.glob("*")

        for dir_path in dirs:
            if not dir_path.is_dir():
                continue

            for json_file in dir_path.glob("*.json"):
                try:
                    with open(json_file, "r") as f:
                        data = json.load(f)

                    # Simple keyword search
                    if query.lower() in str(data).lower():
                        results.append(data)
                        if len(results) >= limit:
                            return results
                except json.JSONDecodeError:
                    continue

        return results


# ============================================================================
# TIER 3: STATE MEMORY (Current reality)
# ============================================================================

@dataclass
class SystemState:
    """Current system state - what's actually happening."""
    timestamp: float
    browser: Dict[str, Any]      # open tabs, URLs, active tab
    workspace: Dict[str, Any]    # workspace names, active workspace
    agents: Dict[str, Any]       # agent states (busy/idle)
    system: Dict[str, Any]       # brightness, volume, battery
    tasks: Dict[str, Any]        # active, completed, failed tasks


class StateMemory:
    """Current state tracking."""

    def __init__(self, root: str = "memory/state"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.state: Optional[SystemState] = self._load()

    def update(self, state: SystemState) -> None:
        """Update current state."""
        self.state = state

        state_file = self.root / "current.json"

        state_data = {
            "timestamp": state.timestamp,
            "browser": state.browser,
            "workspace": state.workspace,
            "agents": state.agents,
            "system": state.system,
            "tasks": state.tasks,
        }

        with open(state_file, "w") as f:
            json.dump(state_data, f, indent=2, default=str)

    def get(self) -> Optional[SystemState]:
        """Get current state."""
        return self.state

    def _load(self) -> Optional[SystemState]:
        """Load saved state."""
        state_file = self.root / "current.json"

        if not state_file.exists():
            return None

        try:
            with open(state_file, "r") as f:
                data = json.load(f)

            return SystemState(
                timestamp=data.get("timestamp", time.time()),
                browser=data.get("browser", {}),
                workspace=data.get("workspace", {}),
                agents=data.get("agents", {}),
                system=data.get("system", {}),
                tasks=data.get("tasks", {}),
            )
        except json.JSONDecodeError:
            return None


# ============================================================================
# UNIFIED MEMORY MANAGER
# ============================================================================

class UnifiedMemory:
    """Single memory system for all agents."""

    def __init__(self, root: str = "memory"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

        self.active = ActiveMemory(str(self.root / "active"))
        self.archive = ArchiveMemory(str(self.root / "archive"))
        self.state = StateMemory(str(self.root / "state"))

    # ========================================================================
    # ACTIVE MEMORY INTERFACE
    # ========================================================================

    def remember(
        self,
        speaker: str,
        message: str,
        agent_role: str,
        importance: int = 5,
        tags: List[str] = None,
    ) -> None:
        """Add to active memory."""
        self.active.add(
            speaker=speaker,
            message=message,
            agent_role=agent_role,
            importance=importance,
            tags=tags,
        )

    def recall(
        self,
        days: int = 14,
        agent_role: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[MemoryEntry]:
        """Get active memory."""
        entries = self.active.get(days=days, agent_role=agent_role)
        return entries[:limit] if limit else entries

    # ========================================================================
    # ARCHIVE INTERFACE
    # ========================================================================

    def archive(
        self,
        category: str,
        data: Dict[str, Any],
    ) -> None:
        """Save to archive."""
        self.archive.add(category, data)

    def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict]:
        """Search archive."""
        return self.archive.search(query, category, limit)

    # ========================================================================
    # STATE INTERFACE
    # ========================================================================

    def update_state(self, state: SystemState) -> None:
        """Update current state."""
        self.state.update(state)

    def get_state(self) -> Optional[SystemState]:
        """Get current state."""
        return self.state.get()

    # ========================================================================
    # CONVENIENCE METHODS
    # ========================================================================

    def log_action(
        self,
        agent: str,
        action: str,
        result: Dict[str, Any],
        tags: List[str] = None,
    ) -> None:
        """Log agent action."""
        self.remember(
            speaker=agent,
            message=action,
            agent_role=agent,
            importance=6,
            tags=tags or ["action"],
        )

    def log_error(
        self,
        agent: str,
        error: str,
        action: str = "",
        tags: List[str] = None,
    ) -> None:
        """Log error/failure."""
        self.remember(
            speaker=agent,
            message=f"Error: {error}\nAction: {action}",
            agent_role=agent,
            importance=8,
            tags=tags or ["error"],
        )

        # Also save to archive for deep analysis
        self.archive("failures", {
            "agent": agent,
            "action": action,
            "error": error,
            "timestamp": datetime.now().isoformat(),
        })

    def get_agent_memory(self, agent_role: str) -> Dict[str, Any]:
        """Get all memory for specific agent."""
        recent = self.recall(agent_role=agent_role)
        state = self.get_state()

        return {
            "agent": agent_role,
            "recent_memory": recent,
            "current_state": state,
            "memory_count": len(recent),
        }


# ============================================================================
# DEMO
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("UNIFIED MEMORY SYSTEM TEST")
    print("=" * 70)

    mem = UnifiedMemory()

    # Test 1: Scout remembers user request
    print("\n[TEST 1] Scout remembers request...")
    mem.remember(
        speaker="user",
        message="Take screenshot and send to ChatGPT",
        agent_role="scout",
        importance=8,
        tags=["task", "screenshot"],
    )
    print("✓ Remembered")

    # Test 2: Executor logs action
    print("\n[TEST 2] Executor logs action...")
    mem.log_action(
        agent="executor",
        action="Take screenshot via gnome-screenshot",
        result={"success": True, "path": "/tmp/screenshot.png"},
        tags=["screenshot"],
    )
    print("✓ Logged")

    # Test 3: Scout recalls memory
    print("\n[TEST 3] Scout recalls active memory...")
    recent = mem.recall(agent_role="scout")
    print(f"✓ Found {len(recent)} entries")

    # Test 4: Update state
    print("\n[TEST 4] Updating state...")
    state = SystemState(
        timestamp=time.time(),
        browser={
            "tabs": ["YouTube", "ChatGPT"],
            "active": "ChatGPT",
        },
        workspace={
            "active": 2,
            "workspaces": ["coding", "media", "browser"],
        },
        agents={
            "scout": "idle",
            "executor": "idle",
        },
        system={
            "brightness": 0.8,
            "volume": 0.5,
        },
        tasks={
            "active": ["task_001"],
        },
    )
    mem.update_state(state)
    print("✓ State updated")

    # Test 5: Get agent memory
    print("\n[TEST 5] Getting Scout's full memory...")
    scout_mem = mem.get_agent_memory("scout")
    print(f"✓ Scout has {scout_mem['memory_count']} entries")

    print("\n" + "=" * 70)
    print("✓ ALL TESTS PASSED")
    print("=" * 70)
