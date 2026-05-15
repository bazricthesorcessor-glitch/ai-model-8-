# Scout Memory System Architecture
## Complete Persistent Memory Implementation

**Date**: May 12, 2026  
**Status**: Foundation Complete (paths, writer, reader, compiler)  
**Next Steps**: Integration with query makers and agent routing

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│ Scout Memory System - 4 Critical Components                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 1. PATHS (memory/paths.py)                                 │
│    - Define all file structure & storage locations         │
│    - Directories for: active, archive, identity, state,    │
│      agents, temporary, tools, semantic, indexes           │
│                                                             │
│ 2. WRITER (memory/writer.py)                               │
│    - Persistent write operations                           │
│    - Daily logging, archive saves, state snapshots         │
│    - Expiry list management, tool registry updates         │
│                                                             │
│ 3. READER (memory/reader.py)                               │
│    - Persistent read operations                            │
│    - Load 14-day memory, search archives, filter logs      │
│    - Get upcoming deadlines, tool usage patterns           │
│                                                             │
│ 4. COMPILER (memory/compiler.py) [MOST CRITICAL]           │
│    - Builds Scout's complete context prompt               │
│    - 9 sections: Identity, Time/Date, State, Agents,       │
│      Important Memory, Recent 14 Days, Archive,            │
│      Tools, Current Query                                  │
│    - 1M token window with smart allocation                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
memory/data/
├── active/
│   └── daily_logs/              # 14-day rolling JSONL files (YYYY-MM-DD.jsonl)
│
├── archive/                      # Long-term searchable storage
│   ├── conversations/            # Conversation summaries
│   ├── failures/                 # Errors and bugs
│   ├── projects/                 # Project info and status
│   ├── sessions/                 # Session summaries
│   └── semantic/                 # Semantic relationships
│
├── identity/
│   ├── important_memory.json     # Explicitly saved important items
│   ├── user_preferences.json     # User configuration
│   └── identity.json             # Scout's identity data
│
├── state/
│   ├── current_state.json        # Current system state snapshot
│   ├── execution_history.jsonl   # Execution event log
│   ├── agents_state.json         # All agents' status
│   ├── browser_state.json        # Browser context
│   └── workspace_state.json      # Workspace context
│
├── agents/
│   ├── executor/                 # Executor-specific memory
│   │   ├── recent.json           # Recent context
│   │   ├── archive.json          # Archived learnings
│   │   ├── learned.json          # Learned patterns
│   │   └── context.json          # Working context
│   └── [other agents]/
│
├── temporary/
│   ├── exams.json                # Exams list (with expiry dates)
│   ├── deadlines.json            # Deadlines (with expiry)
│   ├── events.json               # Events (with expiry)
│   └── expiry_log.jsonl          # Log of expired items
│
├── tools/
│   ├── registry.json             # Available tools & capabilities
│   ├── capabilities.json         # Tool capability matrix
│   └── usage_log.jsonl           # Tool usage history
│
├── semantic/
│   ├── graph.json                # Semantic relationship graph
│   ├── search_index.json         # Search index
│   └── keyword_index.json        # Keyword lookup
│
└── indexes/
    ├── metadata.json             # System metadata
    ├── search_cache.json         # Search result cache
    └── expiry_index.json         # Track expiring items
```

---

## Key Components

### 1. Runtime Memory (`memory/core.py`)
**Purpose**: Volatile, in-memory task state  
**Responsibility**: Track current task, last action, status  
**Lifecycle**: Exists for session duration  
**Thread-Safe**: Yes (with RLock)

```python
# Example usage
from memory import Memory
mem = Memory()
mem.set_task({"name": "example", "priority": "high"})
current_task = mem.get_task()
```

### 2. Persistent Paths (`memory/paths.py`)
**Purpose**: Define all file locations  
**Responsibility**: Centralized path management  
**Key Features**:
- `get_daily_log_path(date)` - Get log file for any date
- `get_agent_memory_file(agent_name, memory_type)` - Agent-specific paths
- `ensure_all_directories()` - Create all needed directories

```python
from memory import paths
paths.ensure_all_directories()
log_file = paths.get_daily_log_path()
```

### 3. Memory Writer (`memory/writer.py`)
**Purpose**: Save all types of memory data  
**Responsibility**: Persistent writes with proper serialization  
**Key Methods**:

| Method | Purpose |
|--------|---------|
| `save_json(filepath, data)` | Save structured JSON |
| `append_jsonl(filepath, data)` | Append to JSONL log |
| `log_to_daily(entry)` | Log to today's daily log |
| `save_to_archive(type, id, data)` | Archive important items |
| `save_important_memory(item)` | User-explicit memories |
| `save_state_snapshot(data)` | Snapshot current state |
| `add_exam/deadline/event()` | Add expiring items |
| `save_agent_memory()` | Agent-specific memory |
| `initialize_memory_system()` | Create all files |

```python
from memory import MemoryWriter

# Log a decision
entry = MemoryWriter.create_daily_log_entry(
    log_type="decision",
    message="Chose to prioritize UI work",
    category="prioritization",
    severity="info"
)
MemoryWriter.log_to_daily(entry)

# Save important memory
MemoryWriter.save_important_memory({
    "content": "Always backup before migrations",
    "category": "best_practices",
    "tags": ["safety", "databases"]
})

# Archive a conversation
MemoryWriter.save_to_archive(
    "conversations",
    "conv_123",
    {"title": "Project Planning", "notes": "..."}
)
```

### 4. Memory Reader (`memory/reader.py`)
**Purpose**: Load and retrieve all types of memory data  
**Responsibility**: Read operations with filtering and search  
**Key Methods**:

| Method | Purpose |
|--------|---------|
| `load_daily_log(date)` | Load entries from specific day |
| `load_14_day_memory()` | Load past 14 days, newest first |
| `stream_daily_log(date)` | Memory-efficient streaming |
| `filter_daily_log(type/category/severity)` | Filtered queries |
| `load_archive_item(type, id)` | Get specific archive item |
| `load_all_archive(type)` | Load entire archive category |
| `load_important_memory()` | Get important memories |
| `load_current_state()` | Get last state snapshot |
| `search_daily_logs(query, days)` | Full-text search in logs |
| `search_archives(query, type)` | Search archive items |
| `get_upcoming_deadlines(days)` | Get near-future deadlines |
| `load_agent_memory(agent, type)` | Agent-specific memory |

```python
from memory import MemoryReader

# Get 14-day history
history = MemoryReader.load_14_day_memory()

# Search for related information
failures = MemoryReader.search_archives("authentication", "failures")

# Get upcoming tasks
deadlines = MemoryReader.get_upcoming_deadlines(days=7)

# Load agent's specific memory
executor_recent = MemoryReader.load_agent_memory("executor", "recent")
```

### 5. Context Compiler (`memory/compiler.py`) [MOST CRITICAL]
**Purpose**: Build Scout's complete decision-making context  
**Responsibility**: Compile 9-section prompt for 1M token window  
**Token Allocation**: Smart distribution across sections

#### Scout Context Sections:
```
[IDENTITY] - Scout's role, personality, preferences
  - Who Scout is
  - Core responsibilities
  - Configured preferences

[TIME_DATE] - Temporal context
  - Current time/date
  - Day of week
  - Upcoming deadlines and exams

[STATE] - Current system state
  - General system state
  - Agents status
  - Browser state
  - Workspace state

[AGENTS] - Other agents' capabilities
  - Executor: UI control, browser automation
  - Query Makers: Context compilation
  - Status and capabilities

[IMPORTANT MEMORY] - Explicit important memories
  - User-saved important items
  - Categories and tags
  - Highest priority information

[RECENT 14 DAYS] - Recent history
  - Grouped by date (newest first)
  - Actions, decisions, errors
  - Categories and severity

[RELEVANT ARCHIVE] - Contextual archive items
  - Related conversations
  - Related failures/errors
  - Related projects
  - Related sessions

[TOOLS] - Available capabilities
  - Tool registry
  - Capabilities list
  - Usage information

[CURRENT QUERY] - Immediate task
  - Query text
  - Type analysis
  - Priority determination
  - Related agents
```

#### Token Allocation Strategy:
```
Total Budget: 1,000,000 tokens
Reserved for Response: 100,000 tokens
Available: 900,000 tokens

Allocation:
  - Identity:           2%  (18,000 tokens)
  - Time/Date:          0.5% (4,500 tokens)
  - State:              10%  (90,000 tokens)
  - Agents:             5%   (45,000 tokens)
  - Important Memory:   8%   (72,000 tokens)
  - Recent 14 Days:     20%  (180,000 tokens)
  - Relevant Archive:   25%  (225,000 tokens)
  - Tools:              10%  (90,000 tokens)
  - Current Query:      15%  (135,000 tokens)
  - Reserved:           5%   (45,000 tokens - buffer)
```

```python
from memory import ContextCompiler

# Compile full Scout context for decision-making
context = ContextCompiler.compile_scout_context(
    query="Help me plan my week",
    include_sections=None,  # All sections
    custom_token_allocation=None  # Use defaults
)

# Get summary of available context
summary = ContextCompiler.get_context_summary()
# → {identity: True, preferences: True, 14day_entries: 50, ...}

# Compile agent-specific context (agent's type only)
agent_context = ContextCompiler.compile_agent_context(
    agent_name="executor",
    query="Open Brave and navigate to example.com",
    memory_type="recent"
)
```

---

## Integration Points

### Scout Memory System Flow

```
Query to Scout
      ↓
ContextCompiler.compile_scout_context(query)
      ├─ MemoryReader.load_identity()
      ├─ MemoryReader.load_14_day_memory()
      ├─ MemoryReader.load_important_memory()
      ├─ MemoryReader.search_archives(query)
      ├─ MemoryReader.load_current_state()
      ├─ MemoryReader.load_tool_registry()
      └─ Returns formatted 1M-token prompt
      ↓
Scout (LLM) Reasoning
      ├─ Analyzes context
      ├─ Makes decision
      └─ Determines action
      ↓
Log Decision
      ↓
MemoryWriter.log_to_daily(decision_entry)
MemoryWriter.save_state_snapshot(new_state)
```

### Agent Memory System Flow

```
Query to Agent (via Query Maker 2)
      ↓
ContextCompiler.compile_agent_context(agent_name, query, memory_type)
      ├─ Gets agent's SPECIFIC memory type only
      ├─ Load agent_name/memory_type.json
      ├─ Fetch tool registry
      └─ Returns focused prompt
      ↓
Agent Execution
      ↓
Log Action
      ↓
MemoryWriter.save_agent_memory(agent_name, memory_type, results)
```

### Query Maker Routing

```
LLM Query
  └─ Query Maker 1
      ├─ ContextCompiler.compile_scout_context()
      ├─ Full 9-section context
      ├─ 1M token budget
      └─ → Scout complete reasoning

Agent Query
  └─ Query Maker 2
      ├─ ContextCompiler.compile_agent_context()
      ├─ Agent's memory type ONLY
      ├─ Focused task context
      └─ → Agent focused execution
```

---

## Data Examples

### Daily Log Entry
```json
{
  "timestamp": "2026-05-12T21:13:31.875847",
  "type": "decision",
  "message": "Prioritized async refactor over new feature",
  "category": "prioritization",
  "severity": "info",
  "data": {
    "reasoning": "Performance impact higher",
    "impact": "high"
  }
}
```

### Archive Item
```json
{
  "archive_id": "proj_ml_001",
  "type": "project",
  "name": "ML Model Optimization",
  "status": "in_progress",
  "created_at": "2026-04-15T10:00:00",
  "archived_at": "2026-05-12T21:00:00",
  "description": "..."
}
```

### Important Memory
```json
{
  "items": [
    {
      "content": "Always test migrations on 1% of users first",
      "category": "best_practices",
      "tags": ["deployment", "safety"],
      "saved_at": "2026-05-10T15:30:00"
    }
  ]
}
```

### Agent Memory
```json
{
  "agent_name": "executor",
  "memory_type": "recent",
  "updated_at": "2026-05-12T21:15:00",
  "recent_actions": [
    {"tool": "browser", "action": "navigate", "url": "example.com"},
    {"tool": "keyboard", "action": "type", "text": "hello"}
  ]
}
```

---

## Operational Procedures

### Initialize Memory System
```python
from memory import initialize_memory_system
initialize_memory_system()
# Creates all directories and default files
```

### Log a Daily Entry
```python
from memory import MemoryWriter

entry = MemoryWriter.create_daily_log_entry(
    log_type="action",
    message="Executed task successfully",
    category="execution",
    severity="info",
    data={"duration_seconds": 45}
)
MemoryWriter.log_to_daily(entry)
```

### Retrieve 14-Day History
```python
from memory import MemoryReader

history = MemoryReader.load_14_day_memory()
for entry in history[:10]:  # Last 10 entries
    print(f"{entry['timestamp']} - {entry['message']}")
```

### Save Important Information
```python
MemoryWriter.save_important_memory({
    "content": "Database migration takes ~2 hours",
    "category": "operations",
    "tags": ["database", "timing"]
})
```

### Archive a Conversation
```python
MemoryWriter.save_to_archive(
    archive_type="conversations",
    archive_id=f"conv_{datetime.now().timestamp()}",
    data={
        "title": "Discussion on Architecture",
        "participants": ["scout", "user"],
        "summary": "..."
    }
)
```

### Compile Scout Context
```python
from memory import ContextCompiler

context = ContextCompiler.compile_scout_context(
    query="What should I focus on today?"
)
# Use context with LLM for Scout reasoning
```

---

## File Sizes (Current)

| File | Size | Purpose |
|------|------|---------|
| paths.py | 8.1 KB | Path definitions and utilities |
| writer.py | 14.1 KB | Write operations |
| reader.py | 17.5 KB | Read operations |
| compiler.py | 17.1 KB | Context compilation (CRITICAL) |
| **Total** | **56.8 KB** | Foundation complete |

---

## Next Implementation Steps

### Phase 2: Agent Integration
- [ ] Create `memory/schemas.py` - Data models for all memory types
- [ ] Create `memory/search.py` - Advanced search with keyword/semantic search
- [ ] Integrate with agent routing (connect to `scout/scout_context_router.py`)
- [ ] Create integration tests

### Phase 3: Advanced Features
- [ ] Create `memory/cleaner.py` - Auto-cleanup of expired items
- [ ] Add semantic relationship graph for smarter context selection
- [ ] Implement memory compression for very old logs
- [ ] Add privacy/security considerations for sensitive data

### Phase 4: Optimization
- [ ] Context caching for repeated queries
- [ ] Search index optimization
- [ ] Memory size monitoring and archival
- [ ] Performance benchmarking

---

## Testing the System

```bash
# Test paths initialization
python -m memory.paths

# Test writer operations
python -m memory.writer

# Test reader operations  
python -m memory.reader

# Test context compilation
python3 -c "from memory import ContextCompiler; ctx = ContextCompiler.compile_scout_context('test'); print(f'Context: {len(ctx)} chars')"
```

---

## Current Status

✅ **Foundation Complete**
- memory/paths.py - File structure defined
- memory/writer.py - Write operations working
- memory/reader.py - Read operations working
- memory/compiler.py - Context compilation functional
- Directory structure created and tested
- Integration with __init__.py complete

⏳ **Next Priority**
- Integration with query makers
- Agent routing implementation
- Advanced search capabilities
- Memory schemas definition

---

## References

- **Architecture**: See `/home/dmannu/ai-model-8/memory/` structure
- **Runtime Memory**: `memory/core.py`
- **Persistent Memory**: `memory/paths.py`, `memory/writer.py`, `memory/reader.py`, `memory/compiler.py`
- **Agent Integration**: See `scout/scout_context_router.py` (to be updated)
- **Query Makers**: `tools/query_maker1.py` and `tools/query_maker2.py` (need updates for integration)

---

**Created**: May 12, 2026  
**Last Updated**: May 12, 2026  
**Architect**: Claude Code AI Assistant  
**Status**: Foundation Phase Complete ✓
