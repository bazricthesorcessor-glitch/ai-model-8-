"""
Scout Cognitive History Logger - Event-based memory for Scout agent.

Captures Scout's:
- Decisions and reasoning
- Agent delegations
- Task completions
- Errors and failures
- State changes
- Important outcomes

Creates structured event logs for memory retrieval and analysis.
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from config import LOCAL_SHARE_DIR


@dataclass
class ScoutEvent:
    """Single Scout event."""
    timestamp: float
    event_type: str  # 'decision', 'delegation', 'completion', 'error', 'state_change'
    description: str
    agent_involved: Optional[str] = None
    task_id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class ScoutHistoryLogger:
    """Enhanced Scout history logger with event tracking."""

    # Text log (for human reading)
    DEFAULT_TEXT_LOG = str(LOCAL_SHARE_DIR / "scout_history.txt")

    # Event log (for memory system)
    DEFAULT_EVENT_LOG_DIR = Path("memory/archive/scout_events")

    def __init__(
        self,
        text_log: Optional[str] = None,
        event_log_dir: Optional[str] = None,
    ):
        """Initialize Scout history logger."""
        # Text log for readability
        self.text_log = text_log or self.DEFAULT_TEXT_LOG
        os.makedirs(os.path.dirname(self.text_log), exist_ok=True)
        Path(self.text_log).touch()

        # Event log for memory system
        self.event_log_dir = Path(event_log_dir or self.DEFAULT_EVENT_LOG_DIR)
        self.event_log_dir.mkdir(parents=True, exist_ok=True)

        self.current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_event_log = (
            self.event_log_dir / f"session_{self.current_session_id}.jsonl"
        )

    # ========================================================================
    # TEXT LOG (HUMAN READABLE)
    # ========================================================================

    def append_user(self, message: str) -> None:
        """Append user message to history."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"\n{'='*80}\n[{timestamp}] USER:\n{message}\n"
        self._write_text(entry)

    def append_scout(self, message: str) -> None:
        """Append Scout message to history."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"\n[{timestamp}] SCOUT:\n{message}\n"
        self._write_text(entry)

    def append_section(self, title: str) -> None:
        """Append a section header."""
        entry = f"\n{'-'*80}\n{title}\n{'-'*80}\n"
        self._write_text(entry)

    def append_raw(self, text: str) -> None:
        """Append raw text (no formatting)."""
        self._write_text(text + "\n")

    def _write_text(self, text: str) -> None:
        """Write to text log file (append)."""
        try:
            with open(self.text_log, 'a', encoding='utf-8') as f:
                f.write(text)
                f.flush()
        except IOError as e:
            print(f"Error writing to text log: {e}")

    def read_all(self) -> str:
        """Read entire text history."""
        try:
            with open(self.text_log, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return ""

    def read_recent(self, lines: int = 100) -> str:
        """Read last N lines of text history."""
        try:
            with open(self.text_log, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                return ''.join(all_lines[-lines:])
        except FileNotFoundError:
            return ""

    def clear(self) -> None:
        """Clear text history (DESTRUCTIVE)."""
        Path(self.text_log).write_text("")
        print(f"✓ History cleared: {self.text_log}")

    def get_text_log_path(self) -> str:
        """Get text log file path."""
        return self.text_log

    def get_text_log_size(self) -> str:
        """Get text log file size in human readable format."""
        try:
            size = os.path.getsize(self.text_log)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024:
                    return f"{size:.1f} {unit}"
                size /= 1024
            return f"{size:.1f} TB"
        except FileNotFoundError:
            return "0 B"

    def get_line_count(self) -> int:
        """Get total lines in text history."""
        try:
            with open(self.text_log, 'r', encoding='utf-8') as f:
                return len(f.readlines())
        except FileNotFoundError:
            return 0

    # ========================================================================
    # EVENT LOG (FOR MEMORY SYSTEM)
    # ========================================================================

    def log_decision(
        self,
        description: str,
        task_id: Optional[str] = None,
        tags: List[str] = None,
    ) -> None:
        """Log Scout's decision."""
        event = ScoutEvent(
            timestamp=time.time(),
            event_type="decision",
            description=description,
            task_id=task_id,
            tags=tags or [],
        )
        self._write_event(event)

    def log_delegation(
        self,
        agent: str,
        description: str,
        task_id: Optional[str] = None,
        tags: List[str] = None,
    ) -> None:
        """Log delegation to agent."""
        event = ScoutEvent(
            timestamp=time.time(),
            event_type="delegation",
            description=description,
            agent_involved=agent,
            task_id=task_id,
            tags=tags or ["delegation", agent],
        )
        self._write_event(event)

    def log_completion(
        self,
        description: str,
        result: Dict[str, Any],
        task_id: Optional[str] = None,
        tags: List[str] = None,
    ) -> None:
        """Log task completion."""
        event = ScoutEvent(
            timestamp=time.time(),
            event_type="completion",
            description=description,
            result=result,
            task_id=task_id,
            tags=tags or ["completion"],
        )
        self._write_event(event)

    def log_error(
        self,
        description: str,
        error: str,
        task_id: Optional[str] = None,
        tags: List[str] = None,
    ) -> None:
        """Log error or failure."""
        event = ScoutEvent(
            timestamp=time.time(),
            event_type="error",
            description=description,
            result={"error": error},
            task_id=task_id,
            tags=tags or ["error"],
        )
        self._write_event(event)

    def log_state_change(
        self,
        description: str,
        old_state: Dict[str, Any],
        new_state: Dict[str, Any],
        tags: List[str] = None,
    ) -> None:
        """Log state change."""
        event = ScoutEvent(
            timestamp=time.time(),
            event_type="state_change",
            description=description,
            result={"old_state": old_state, "new_state": new_state},
            tags=tags or ["state_change"],
        )
        self._write_event(event)

    def _write_event(self, event: ScoutEvent) -> None:
        """Write event to structured log."""
        try:
            with open(self.session_event_log, 'a') as f:
                f.write(json.dumps(asdict(event), default=str) + "\n")
        except IOError as e:
            print(f"Error writing to event log: {e}")

    def get_session_events(self) -> List[ScoutEvent]:
        """Get all events from current session."""
        events = []

        try:
            with open(self.session_event_log, 'r') as f:
                for line in f:
                    data = json.loads(line)
                    events.append(ScoutEvent(**data))
        except FileNotFoundError:
            pass

        return events

    def get_events_by_type(self, event_type: str) -> List[ScoutEvent]:
        """Get events of specific type."""
        return [e for e in self.get_session_events() if e.event_type == event_type]

    def get_events_by_agent(self, agent: str) -> List[ScoutEvent]:
        """Get events involving specific agent."""
        return [
            e for e in self.get_session_events()
            if e.agent_involved == agent
        ]

    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session."""
        events = self.get_session_events()

        return {
            "session_id": self.current_session_id,
            "total_events": len(events),
            "decisions": len(self.get_events_by_type("decision")),
            "delegations": len(self.get_events_by_type("delegation")),
            "completions": len(self.get_events_by_type("completion")),
            "errors": len(self.get_events_by_type("error")),
            "state_changes": len(self.get_events_by_type("state_change")),
            "start_time": events[0].timestamp if events else None,
            "end_time": events[-1].timestamp if events else None,
        }


# ============================================================================
# SIMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    logger = ScoutHistoryLogger()

    print("📝 SCOUT CONVERSATION HISTORY LOGGER\n")

    # Demo conversation
    logger.append_section("SESSION START - Test Demo")

    logger.append_user("Can you optimize my function?")
    logger.append_scout("Sure, I'll analyze it. Using minimal context for quick fix.\nRecommendations:\n1. Cache results\n2. Use vectorization\n3. Remove nested loops")

    logger.append_user("This is still broken. Same error as before!")
    logger.append_scout("Detected repeated failure. Now using DEEP context to analyze.\nFound pattern: timeout in retry loop.\nFix: Use cancellation token instead of retry recursion.")

    logger.append_section("SESSION END - Summary: 2 issues resolved")

    # Display what was written
    print("✓ Messages appended to history\n")
    print("File:", logger.get_file_path())
    print("Size:", logger.get_file_size())
    print("Lines:", logger.get_line_count())
    print("\n" + "="*80)
    print("COMPLETE HISTORY:")
    print("="*80)
    print(logger.read_all())
