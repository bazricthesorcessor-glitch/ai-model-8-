"""
Memory system data schemas.
Defines data structures for all memory types with validation.

Provides Pydantic models and type hints for:
- Daily log entries
- Archive items
- Important memories
- State snapshots
- Agent memory
- Expiry items
"""

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Literal
from datetime import datetime
from enum import Enum


# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class LogType(str, Enum):
    """Types of daily log entries."""
    ACTION = "action"
    DECISION = "decision"
    ERROR = "error"
    STATE_CHANGE = "state_change"
    TASK_ASSIGNED = "task_assigned"
    TASK_COMPLETED = "task_completed"
    ROUTING = "routing"
    CONTEXT_COMPILATION = "context_compilation"
    AGENT_CONTEXT = "agent_context"
    EXECUTION = "execution"
    SCOUT_DECISION = "scout_decision"
    MILESTONE = "milestone"


class Severity(str, Enum):
    """Severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ArchiveType(str, Enum):
    """Types of archive categories."""
    CONVERSATIONS = "conversations"
    FAILURES = "failures"
    PROJECTS = "projects"
    SESSIONS = "sessions"
    SEMANTIC = "semantic"


class MemoryType(str, Enum):
    """Types of agent memory."""
    RECENT = "recent"
    ARCHIVE = "archive"
    LEARNED = "learned"
    CONTEXT = "context"


# ============================================================================
# DAILY LOG ENTRY
# ============================================================================

@dataclass
class DailyLogEntry:
    """A single entry in the daily log."""
    timestamp: str
    type: str
    message: str
    severity: str = "info"
    category: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            k: v for k, v in asdict(self).items()
            if v is not None
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "DailyLogEntry":
        """Create from dictionary."""
        return DailyLogEntry(
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            type=data.get("type", "unknown"),
            message=data.get("message", ""),
            severity=data.get("severity", "info"),
            category=data.get("category"),
            data=data.get("data")
        )


# ============================================================================
# ARCHIVE ITEMS
# ============================================================================

@dataclass
class ConversationItem:
    """Archived conversation."""
    archive_id: str
    title: str
    participants: List[str]
    summary: str
    created_at: str
    archived_at: str
    messages_count: int = 0
    duration_seconds: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FailureItem:
    """Archived failure/error."""
    archive_id: str
    title: str
    description: str
    severity: str
    root_cause: str
    solution: str
    created_at: str
    archived_at: str
    resolved: bool = True
    prevention_measures: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ProjectItem:
    """Archived project."""
    archive_id: str
    name: str
    description: str
    status: str  # planning, in_progress, completed, on_hold
    created_at: str
    archived_at: str
    goals: List[str] = field(default_factory=list)
    learnings: List[str] = field(default_factory=list)
    metrics: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SessionItem:
    """Archived session summary."""
    archive_id: str
    date: str
    duration_minutes: int
    focus_area: str
    archived_at: str
    completed_tasks: List[str] = field(default_factory=list)
    issues_encountered: List[str] = field(default_factory=list)
    learnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================================
# IDENTITY & IMPORTANT MEMORY
# ============================================================================

@dataclass
class ImportantMemoryItem:
    """User-explicit important memory."""
    content: str
    category: str
    saved_at: str
    tags: List[str] = field(default_factory=list)
    priority: str = "normal"  # low, normal, high, critical
    expires_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class UserPreferences:
    """User preferences and configuration."""
    language: str = "en"
    timezone: str = "UTC"
    focus_areas: List[str] = field(default_factory=list)
    work_hours_start: str = "09:00"
    work_hours_end: str = "17:00"
    notification_level: str = "normal"
    context_depth: str = "full"  # minimal, normal, full
    theme: str = "light"
    custom_settings: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================================
# STATE SNAPSHOTS
# ============================================================================

@dataclass
class AgentState:
    """State of a single agent."""
    name: str
    status: str  # idle, busy, waiting, error
    last_task: Optional[str] = None
    last_result: Optional[str] = None
    updated_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BrowserState:
    """Browser state snapshot."""
    current_url: Optional[str] = None
    tabs_count: int = 0
    tabs: List[str] = field(default_factory=list)
    active_tab: Optional[str] = None
    updated_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class WorkspaceState:
    """Workspace state snapshot."""
    focused_window: Optional[str] = None
    active_workspace: Optional[str] = None
    open_files: List[str] = field(default_factory=list)
    terminal_open: bool = False
    updated_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SystemState:
    """Overall system state snapshot."""
    current_focus: Optional[str] = None
    active_task: Optional[str] = None
    agents: Dict[str, AgentState] = field(default_factory=dict)
    browser: Optional[BrowserState] = None
    workspace: Optional[WorkspaceState] = None
    snapshot_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        # Convert nested dataclasses
        if self.agents:
            data["agents"] = {
                name: agent.to_dict() if isinstance(agent, AgentState) else agent
                for name, agent in self.agents.items()
            }
        if self.browser:
            data["browser"] = self.browser.to_dict() if isinstance(self.browser, BrowserState) else self.browser
        if self.workspace:
            data["workspace"] = self.workspace.to_dict() if isinstance(self.workspace, WorkspaceState) else self.workspace
        return data


# ============================================================================
# EXECUTION HISTORY
# ============================================================================

@dataclass
class ExecutionRecord:
    """Single execution record."""
    timestamp: str
    agent: str
    action: str
    target: Optional[str] = None
    result: str = "success"  # success, failure, partial
    duration_ms: int = 0
    error_message: Optional[str] = None
    context_type: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            k: v for k, v in asdict(self).items()
            if v is not None
        }


# ============================================================================
# AGENT MEMORY
# ============================================================================

@dataclass
class AgentMemoryRecord:
    """Memory record for a specific agent."""
    agent_name: str
    memory_type: str  # recent, archive, learned, context
    updated_at: str
    content: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================================
# TOOLS & REGISTRY
# ============================================================================

@dataclass
class ToolInfo:
    """Information about a tool."""
    name: str
    description: str
    capabilities: List[str] = field(default_factory=list)
    status: str = "available"  # available, unavailable, error
    last_used: Optional[str] = None
    usage_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ToolRegistry:
    """Registry of available tools."""
    tools: Dict[str, ToolInfo] = field(default_factory=dict)
    updated_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["tools"] = {
            name: tool.to_dict() if isinstance(tool, ToolInfo) else tool
            for name, tool in self.tools.items()
        }
        return data


# ============================================================================
# TEMPORARY/EXPIRING ITEMS
# ============================================================================

@dataclass
class ExamItem:
    """Exam entry."""
    name: str
    date: str  # ISO format
    subject: Optional[str] = None
    location: Optional[str] = None
    duration_minutes: Optional[int] = None
    added_at: Optional[str] = None
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            k: v for k, v in asdict(self).items()
            if v is not None
        }


@dataclass
class DeadlineItem:
    """Deadline entry."""
    title: str
    date: str  # ISO format
    priority: str = "normal"  # low, normal, high, critical
    project: Optional[str] = None
    added_at: Optional[str] = None
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            k: v for k, v in asdict(self).items()
            if v is not None
        }


@dataclass
class EventItem:
    """Event entry."""
    title: str
    date: str  # ISO format
    time: Optional[str] = None
    location: Optional[str] = None
    added_at: Optional[str] = None
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            k: v for k, v in asdict(self).items()
            if v is not None
        }


# ============================================================================
# SEARCH & SEMANTIC
# ============================================================================

@dataclass
class SearchResult:
    """Result from a search query."""
    item_id: str
    item_type: str
    title: str
    relevance_score: float  # 0.0 to 1.0
    source: str  # logs, archive, important, etc
    preview: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SemanticRelation:
    """Relationship between two items."""
    source_id: str
    target_id: str
    relation_type: str  # related_to, causes, resolves, etc
    strength: float  # 0.0 to 1.0
    bidirectional: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================================
# VALIDATION HELPERS
# ============================================================================

class SchemaValidator:
    """Validation utilities for memory schemas."""

    @staticmethod
    def validate_daily_log_entry(data: Dict[str, Any]) -> bool:
        """Validate daily log entry structure."""
        required = {"timestamp", "type", "message"}
        return all(key in data for key in required)

    @staticmethod
    def validate_archive_item(data: Dict[str, Any], archive_type: str) -> bool:
        """Validate archive item structure."""
        if archive_type == "conversations":
            required = {"title", "participants", "summary"}
        elif archive_type == "failures":
            required = {"title", "description", "root_cause"}
        elif archive_type == "projects":
            required = {"name", "status"}
        elif archive_type == "sessions":
            required = {"date", "focus_area"}
        else:
            return False

        return all(key in data for key in required)

    @staticmethod
    def validate_important_memory(data: Dict[str, Any]) -> bool:
        """Validate important memory structure."""
        required = {"content", "category"}
        return all(key in data for key in required)

    @staticmethod
    def validate_exam_item(data: Dict[str, Any]) -> bool:
        """Validate exam entry."""
        required = {"name", "date"}
        return all(key in data for key in required)

    @staticmethod
    def validate_deadline_item(data: Dict[str, Any]) -> bool:
        """Validate deadline entry."""
        required = {"title", "date"}
        return all(key in data for key in required)


# ============================================================================
# TYPE CONVERSION UTILITIES
# ============================================================================

def dict_to_daily_log_entry(data: Dict[str, Any]) -> DailyLogEntry:
    """Convert dict to DailyLogEntry."""
    return DailyLogEntry.from_dict(data)


def dict_to_conversation_item(data: Dict[str, Any]) -> ConversationItem:
    """Convert dict to ConversationItem."""
    return ConversationItem(
        archive_id=data.get("archive_id", ""),
        title=data.get("title", ""),
        participants=data.get("participants", []),
        summary=data.get("summary", ""),
        created_at=data.get("created_at", datetime.now().isoformat()),
        archived_at=data.get("archived_at", datetime.now().isoformat()),
        messages_count=data.get("messages_count", 0),
        duration_seconds=data.get("duration_seconds", 0)
    )


def dict_to_important_memory(data: Dict[str, Any]) -> ImportantMemoryItem:
    """Convert dict to ImportantMemoryItem."""
    return ImportantMemoryItem(
        content=data.get("content", ""),
        category=data.get("category", "general"),
        saved_at=data.get("saved_at", datetime.now().isoformat()),
        tags=data.get("tags", []),
        priority=data.get("priority", "normal"),
        expires_at=data.get("expires_at")
    )


if __name__ == "__main__":
    print("Memory Schemas Initialized")
    print("=" * 50)

    # Test creating some records
    log_entry = DailyLogEntry(
        timestamp=datetime.now().isoformat(),
        type="test",
        message="Testing schema",
        severity="info",
        category="testing"
    )
    print(f"✓ Created DailyLogEntry: {log_entry.message}")

    important = ImportantMemoryItem(
        content="Test important memory",
        category="testing",
        saved_at=datetime.now().isoformat()
    )
    print(f"✓ Created ImportantMemoryItem: {important.content}")

    tool = ToolInfo(
        name="test_tool",
        description="A test tool",
        capabilities=["action1", "action2"]
    )
    print(f"✓ Created ToolInfo: {tool.name}")

    print("\n✓ All schemas working correctly")
