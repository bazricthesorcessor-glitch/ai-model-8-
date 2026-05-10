# Memory Module - Persistent Storage & Logging

Long-term persistent storage for action logs and execution history. Survives process restarts. Enables debugging and action replay.

## 🎯 Purpose

- **Action logging** - Permanent record of all actions
- **Persistence** - Survives restarts
- **Debugging** - Historical trace for troubleshooting
- **Replay** - Can replay actions from log
- **Analytics** - Tool usage statistics

## 📁 Structure

```
memory/
├── __init__.py           # Main exports
├── memory.py             # Core memory management
└── README.md            # This file
```

## 📝 Persistent Storage

### Action Log
JSON file with complete action history:

```json
[
    {
        "timestamp": 1234567890.123,
        "action_id": "action_001",
        "action": "run_command",
        "params": {
            "command": "ls /tmp",
            "shell": "bash"
        },
        "result": {
            "success": true,
            "output": "file1.txt\nfile2.txt",
            "exit_code": 0
        },
        "duration": 0.234,
        "approved_by": "user",
        "session_id": "sess_123"
    },
    {
        "timestamp": 1234567891.234,
        "action_id": "action_002",
        ...
    }
]
```

### State Snapshots
Periodic snapshots of full state:

```json
{
    "timestamp": 1234567890,
    "session_id": "sess_123",
    "state": {
        "status": "idle",
        "execution_history": [...],
        "tool_results": {...}
    }
}
```

### Tool Results Cache
Caching for deduplication:

```json
{
    "hash": "abc123def",
    "tool": "search_web",
    "params": {"query": "python"},
    "result": {...},
    "timestamp": 1234567890,
    "hits": 5
}
```

## 🔧 Core Functions

### log_action(action: str, params: dict, result: dict) → str
Log an action to persistent storage.

```python
action_id = memory.log_action(
    action="run_command",
    params={"command": "ls /tmp"},
    result={"success": True, "output": "files"}
)
# Returns action_id for tracking
```

### get_action_log(limit: int = 100) → list
Retrieve action log.

```python
log = memory.get_action_log(limit=50)
# Returns last 50 actions from disk
```

### save_state_snapshot(state: dict) → bool
Save state snapshot.

```python
memory.save_state_snapshot(current_state)
# Saves to timestamped file
```

### get_session_history(session_id: str) → list
Get all actions from a session.

```python
session_actions = memory.get_session_history("sess_123")
# Returns all actions in session
```

### cache_tool_result(tool: str, params: dict, result: dict) → str
Cache tool result for deduplication.

```python
result_id = memory.cache_tool_result(
    tool="search_web",
    params={"query": "python"},
    result={...}
)
```

### get_cached_result(tool: str, params: dict) -> dict
Check if result cached.

```python
cached = memory.get_cached_result(
    tool="search_web",
    params={"query": "python"}
)
if cached:
    return cached  # Use cache instead of calling tool
```

## 📂 Storage Location

All persistent data stored in:
```
~/.ai_assistant/
├── logs/
│   ├── action_log.jsonl
│   └── state_snapshots/
│       ├── snapshot_001.json
│       ├── snapshot_002.json
├── cache/
│   ├── tool_results.json
└── sessions/
    ├── sess_001.json
    ├── sess_002.json
```

## 🔄 Action Logging Format (JSONL)

Each action is one line (JSON Lines format):

```jsonl
{"timestamp": 1234567890.123, "action_id": "a001", "action": "run_command", "params": {...}, "result": {...}}
{"timestamp": 1234567891.234, "action_id": "a002", "action": "search_web", "params": {...}, "result": {...}}
{"timestamp": 1234567892.345, "action_id": "a003", "action": "run_command", "params": {...}, "result": {...}}
```

Benefits:
- Streaming reads/writes
- No memory overhead for large logs
- Natural append-only format
- Can process one action at a time

## 🧪 Testing Memory

```python
def test_log_action():
    memory.clear()
    action_id = memory.log_action("test", {"param": "value"}, {"ok": True})
    assert action_id is not None

def test_get_action_log():
    memory.clear()
    for i in range(5):
        memory.log_action(f"action_{i}", {}, {})
    log = memory.get_action_log()
    assert len(log) == 5

def test_cache_hit():
    memory.clear()
    result_id = memory.cache_tool_result("search", {"q": "test"}, {"data": [...]})
    cached = memory.get_cached_result("search", {"q": "test"})
    assert cached is not None

def test_session_history():
    memory.clear()
    session_id = "test_session"
    memory.log_action("a1", {}, {}, session_id)
    memory.log_action("a2", {}, {}, session_id)
    history = memory.get_session_history(session_id)
    assert len(history) == 2
```

## 📊 Statistics

Get memory statistics:

```python
def get_memory_stats() -> dict:
    return {
        "total_actions": memory.count_actions(),
        "total_cache_hits": memory.count_cache_hits(),
        "storage_size_mb": memory.get_storage_size(),
        "sessions_count": memory.count_sessions(),
        "oldest_action": memory.get_oldest_action(),
        "newest_action": memory.get_newest_action()
    }

stats = memory.get_memory_stats()
print(f"Total actions: {stats['total_actions']}")
print(f"Cache hit rate: {stats['total_cache_hits'] / stats['total_actions'] * 100:.1f}%")
```

## 🗑️ Cleanup

Management functions:

```python
# Archive old logs (>30 days)
memory.archive_old_logs(days=30)

# Clear cache
memory.clear_cache()

# Delete session
memory.delete_session("sess_old")

# Get storage usage
usage = memory.get_storage_usage()
print(f"Using {usage['total_mb']:.1f} MB")

if usage['total_mb'] > 1000:  # > 1GB
    memory.archive_old_logs(days=7)  # Archive aggressively
```

## 🚀 Integration with State

Memory stores what State tracks:

```
State (in-memory)
    ↓
Router receives record_state message
    ↓
State.update() - update in-memory state
    ↓
State.record_in_memory() - keep recent history
    ↓
Memory.log_action() - write to persistent log

Result: Recent history in memory (fast), all history on disk (persistent)
```

## 🔍 Querying History

Search action logs:

```python
# Get all "run_command" actions
commands = memory.filter_actions(action="run_command")

# Get all successful actions
successful = memory.filter_actions(success=True)

# Get actions in time range
recent = memory.filter_actions(
    start_time=datetime.now() - timedelta(hours=1),
    end_time=datetime.now()
)

# Get actions by tool
web_searches = memory.filter_actions(action="search_web")
```

## 💾 Backup & Restore

```python
# Backup all logs
memory.backup("/backup/ai_assistant_backup.tar.gz")

# Restore from backup
memory.restore("/backup/ai_assistant_backup.tar.gz")

# Export to CSV for analysis
memory.export_to_csv("/tmp/actions.csv")

# Import from external log
memory.import_actions_from_file("/tmp/external_actions.jsonl")
```

## ✨ Highlights

- **Persistent** - Survives restarts
- **JSONL format** - Efficient append-only logging
- **Session aware** - Track actions per session
- **Caching** - Avoid duplicate tool calls
- **Searchable** - Query historical data
- **Manageable** - Archive and cleanup tools
- **Auditable** - Complete action trail

---

**Status: 🚀 Ready for Phase 5 integration (deferred, optional)**
