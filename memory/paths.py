"""
Memory file paths and directory structure.
Defines all persistent storage locations for Scout's memory system.

Directory structure:
memory/data/
├── active/daily_logs/           # 14-day rolling logs (YYYY-MM-DD.jsonl)
├── archive/                      # Long-term searchable storage
│   ├── conversations/            # Conversation summaries & context
│   ├── failures/                 # Errors, bugs, failed attempts
│   ├── projects/                 # Project goals, status, learnings
│   ├── sessions/                 # Session summaries
│   └── semantic/                 # Semantic graph relationships
├── identity/                     # Core identity & preferences
├── state/                        # Current runtime state snapshots
├── agents/                       # Agent-specific persistent memory
├── tools/                        # Tool registry & capabilities
├── temporary/                    # Expiring memories (exams, deadlines)
├── indexes/                      # Search indexes & metadata
└── important/                    # Explicitly saved important memories
"""

import os
from datetime import datetime
from pathlib import Path

# Root memory directory
MEMORY_ROOT = Path(__file__).parent / "data"

# ============================================================================
# ACTIVE MEMORY (14-day rolling window)
# ============================================================================
ACTIVE_DIR = MEMORY_ROOT / "active"
ACTIVE_DAILY_LOGS = ACTIVE_DIR / "daily_logs"

def get_daily_log_path(date: datetime = None) -> Path:
    """Get path to daily log for a specific date (default: today)."""
    if date is None:
        date = datetime.now()
    filename = date.strftime("%Y-%m-%d.jsonl")
    return ACTIVE_DAILY_LOGS / filename


# ============================================================================
# ARCHIVE MEMORY (long-term searchable)
# ============================================================================
ARCHIVE_DIR = MEMORY_ROOT / "archive"
ARCHIVE_CONVERSATIONS = ARCHIVE_DIR / "conversations"
ARCHIVE_FAILURES = ARCHIVE_DIR / "failures"
ARCHIVE_PROJECTS = ARCHIVE_DIR / "projects"
ARCHIVE_SESSIONS = ARCHIVE_DIR / "sessions"
ARCHIVE_SEMANTIC = ARCHIVE_DIR / "semantic"

# Archive index files
ARCHIVE_CONVERSATIONS_INDEX = ARCHIVE_CONVERSATIONS / "index.json"
ARCHIVE_FAILURES_INDEX = ARCHIVE_FAILURES / "index.json"
ARCHIVE_PROJECTS_INDEX = ARCHIVE_PROJECTS / "index.json"
ARCHIVE_SESSIONS_INDEX = ARCHIVE_SESSIONS / "index.json"


# ============================================================================
# IDENTITY MEMORY (core preferences & important memories)
# ============================================================================
IDENTITY_DIR = MEMORY_ROOT / "identity"
IMPORTANT_MEMORY_FILE = IDENTITY_DIR / "important_memory.json"
USER_PREFERENCES_FILE = IDENTITY_DIR / "user_preferences.json"
IDENTITY_FILE = IDENTITY_DIR / "identity.json"


# ============================================================================
# STATE MEMORY (current runtime snapshots)
# ============================================================================
STATE_DIR = MEMORY_ROOT / "state"
STATE_SNAPSHOT_FILE = STATE_DIR / "current_state.json"
EXECUTION_HISTORY_FILE = STATE_DIR / "execution_history.jsonl"
AGENTS_STATE_FILE = STATE_DIR / "agents_state.json"
BROWSER_STATE_FILE = STATE_DIR / "browser_state.json"
WORKSPACE_STATE_FILE = STATE_DIR / "workspace_state.json"


# ============================================================================
# AGENT-SPECIFIC MEMORY (per-agent persistent data)
# ============================================================================
AGENTS_DIR = MEMORY_ROOT / "agents"

def get_agent_memory_dir(agent_name: str) -> Path:
    """Get directory for an agent's memory."""
    return AGENTS_DIR / agent_name


def get_agent_memory_file(agent_name: str, memory_type: str) -> Path:
    """Get path to specific memory type for an agent.

    Args:
        agent_name: Name of the agent (e.g., 'executor', 'scout')
        memory_type: Type of memory ('recent', 'archive', 'learned', 'context')
    """
    return AGENTS_DIR / agent_name / f"{memory_type}.json"


# ============================================================================
# TEMPORARY MEMORY (expiring items)
# ============================================================================
TEMPORARY_DIR = MEMORY_ROOT / "temporary"
EXAMS_FILE = TEMPORARY_DIR / "exams.json"
DEADLINES_FILE = TEMPORARY_DIR / "deadlines.json"
EVENTS_FILE = TEMPORARY_DIR / "events.json"
EXPIRY_LOG_FILE = TEMPORARY_DIR / "expiry_log.jsonl"


# ============================================================================
# TOOLS & CAPABILITIES
# ============================================================================
TOOLS_DIR = MEMORY_ROOT / "tools"
TOOL_REGISTRY_FILE = TOOLS_DIR / "registry.json"
TOOL_CAPABILITIES_FILE = TOOLS_DIR / "capabilities.json"
TOOL_USAGE_LOG = TOOLS_DIR / "usage_log.jsonl"


# ============================================================================
# SEMANTIC & SEARCH
# ============================================================================
SEMANTIC_DIR = MEMORY_ROOT / "semantic"
SEMANTIC_GRAPH_FILE = SEMANTIC_DIR / "graph.json"
SEARCH_INDEX_FILE = SEMANTIC_DIR / "search_index.json"
KEYWORD_INDEX_FILE = SEMANTIC_DIR / "keyword_index.json"


# ============================================================================
# INDEXES & METADATA
# ============================================================================
INDEXES_DIR = MEMORY_ROOT / "indexes"
MEMORY_METADATA_FILE = INDEXES_DIR / "metadata.json"
SEARCH_CACHE_FILE = INDEXES_DIR / "search_cache.json"
EXPIRY_INDEX_FILE = INDEXES_DIR / "expiry_index.json"


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def ensure_all_directories() -> None:
    """Create all memory directories if they don't exist."""
    directories = [
        MEMORY_ROOT,
        ACTIVE_DIR,
        ACTIVE_DAILY_LOGS,
        ARCHIVE_DIR,
        ARCHIVE_CONVERSATIONS,
        ARCHIVE_FAILURES,
        ARCHIVE_PROJECTS,
        ARCHIVE_SESSIONS,
        ARCHIVE_SEMANTIC,
        IDENTITY_DIR,
        STATE_DIR,
        AGENTS_DIR,
        TEMPORARY_DIR,
        TOOLS_DIR,
        SEMANTIC_DIR,
        INDEXES_DIR,
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def get_memory_stats() -> dict:
    """Get current memory system statistics."""
    stats = {
        "memory_root": str(MEMORY_ROOT),
        "exists": MEMORY_ROOT.exists(),
        "directories": {
            "active": ACTIVE_DIR.exists(),
            "archive": ARCHIVE_DIR.exists(),
            "identity": IDENTITY_DIR.exists(),
            "state": STATE_DIR.exists(),
            "agents": AGENTS_DIR.exists(),
            "temporary": TEMPORARY_DIR.exists(),
            "tools": TOOLS_DIR.exists(),
            "semantic": SEMANTIC_DIR.exists(),
            "indexes": INDEXES_DIR.exists(),
        }
    }
    return stats


if __name__ == "__main__":
    # Initialize all directories
    ensure_all_directories()

    # Print directory structure
    print("Memory System Initialized")
    print("=" * 50)
    print(f"Root: {MEMORY_ROOT}")
    print("\nDirectories:")
    print(f"  Active:     {ACTIVE_DIR}")
    print(f"  Archive:    {ARCHIVE_DIR}")
    print(f"  Identity:   {IDENTITY_DIR}")
    print(f"  State:      {STATE_DIR}")
    print(f"  Agents:     {AGENTS_DIR}")
    print(f"  Temporary:  {TEMPORARY_DIR}")
    print(f"  Tools:      {TOOLS_DIR}")
    print(f"  Semantic:   {SEMANTIC_DIR}")
    print(f"  Indexes:    {INDEXES_DIR}")

    # Show stats
    stats = get_memory_stats()
    print("\nStatus:")
    for dir_name, exists in stats["directories"].items():
        status = "✓" if exists else "✗"
        print(f"  {status} {dir_name}")
