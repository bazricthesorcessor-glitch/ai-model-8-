# Scout Memory System - Developer Quick Start
## Essential Operations and Code Examples

---

## Installation & Initialization

```python
# Initialize the entire memory system
from memory import initialize_memory_system
initialize_memory_system()
# This creates all directories and default files
```

---

## Common Operations

### 1. Log Daily Entries (Most Common)

```python
from memory import MemoryWriter
from datetime import datetime

# Simple log entry
MemoryWriter.log_to_daily({
    "type": "action",
    "message": "Completed task processing",
    "severity": "info"
})

# Structured log entry with metadata
entry = MemoryWriter.create_daily_log_entry(
    log_type="decision",
    message="Chose async processing approach",
    category="architecture",
    data={"reasoning": "Better for scalability"},
    severity="info"
)
MemoryWriter.log_to_daily(entry)
```

### 2. Save Important Information

```python
from memory import MemoryWriter

MemoryWriter.save_important_memory({
    "content": "Always migrate database in off-peak hours",
    "category": "operations",
    "tags": ["database", "safety", "critical"]
})
```

### 3. Retrieve 14-Day History

```python
from memory import MemoryReader

# Get all entries from past 14 days (newest first)
history = MemoryReader.load_14_day_memory()

# Filter by type or category
errors = MemoryReader.filter_daily_log(
    log_type="error",
    severity="critical"
)

# Search for something specific
results = MemoryReader.search_daily_logs(
    query="database migration",
    days=14
)
```

### 4. Compile Context for Scout

```python
from memory import ContextCompiler

# Full context for LLM reasoning
context = ContextCompiler.compile_scout_context(
    query="What should I prioritize today?",
    include_sections=None,  # All sections
    custom_token_allocation=None  # Default allocation
)

# Print first section for debugging
print(context[:1000])
```

### 5. Get Context for Specific Agent

```python
from memory import ContextCompiler

# Agent-focused context (their memory type only)
executor_context = ContextCompiler.compile_agent_context(
    agent_name="executor",
    query="Open Brave and navigate to example.com",
    memory_type="recent"
)
```

### 6. Archive Important Items

```python
from memory import MemoryWriter

MemoryWriter.save_to_archive(
    archive_type="failures",
    archive_id="bug_auth_001",
    data={
        "title": "Authentication timeout issue",
        "description": "Login endpoint returns 504 after 30s",
        "root_cause": "Database query missing index",
        "solution": "Added index on user_email column",
        "severity": "critical"
    }
)
```

### 7. Save Agent-Specific Memory

```python
from memory import MemoryWriter

# Save what the executor agent learned
MemoryWriter.save_agent_memory(
    agent_name="executor",
    memory_type="learned",
    data={
        "patterns": [
            "Always check if browser is open before navigating",
            "Wait for page load before interacting"
        ],
        "errors_avoided": 5,
        "updated_at": "2026-05-12T21:00:00"
    }
)
```

### 8. Log Execution Events

```python
from memory import MemoryWriter

MemoryWriter.log_execution_history({
    "agent": "executor",
    "action": "clicked",
    "target": "submit_button",
    "result": "success",
    "duration_ms": 245
})
```

### 9. Get System Status

```python
from memory import get_memory_status

status = get_memory_status()
# → {
#     "today_log_entries": 42,
#     "14day_entries": 350,
#     "important_memories": 12,
#     "archive_conversations": 8,
#     ...
# }
```

---

## Pattern: Daily Workflow Logging

```python
from memory import MemoryWriter

# 1. Log start of work session
MemoryWriter.log_to_daily({
    "type": "session_start",
    "message": "Started work session",
    "data": {"focus_area": "backend_optimization"}
})

# 2. Log decisions during work
MemoryWriter.log_to_daily({
    "type": "decision",
    "message": "Refactored database queries for performance",
    "data": {"improvement_percent": 40}
})

# 3. Log any errors/issues
MemoryWriter.log_to_daily({
    "type": "error",
    "message": "Database timeout during migration",
    "severity": "critical",
    "data": {"error_code": "500", "duration_minutes": 5}
})

# 4. Log important findings
MemoryWriter.save_important_memory({
    "content": "Query N+1 problem found in reports module",
    "category": "performance",
    "tags": ["database", "optimization"]
})

# 5. Archive session summary
MemoryWriter.save_to_archive(
    archive_type="sessions",
    archive_id=f"session_{date.today()}",
    data={
        "date": date.today().isoformat(),
        "focus": "backend_optimization",
        "completed_tasks": ["query refactor", "index optimization"],
        "issues": ["timeout during testing"],
        "learnings": ["always test with realistic data volumes"]
    }
)
```

---

## Pattern: Agent Task Execution

```python
from memory import MemoryReader, MemoryWriter, ContextCompiler

def execute_agent_task(agent_name: str, task: str):
    """Execute a task with an agent and log everything."""
    
    # 1. Compile agent context
    context = ContextCompiler.compile_agent_context(
        agent_name=agent_name,
        query=task,
        memory_type="recent"
    )
    
    # 2. Log task assignment
    MemoryWriter.log_to_daily({
        "type": "task_assigned",
        "message": f"Assigned task to {agent_name}",
        "data": {"task": task[:100]}
    })
    
    # 3. Execute task (placeholder)
    result = agent_execute(agent_name, context)
    
    # 4. Log execution result
    MemoryWriter.log_execution_history({
        "agent": agent_name,
        "task": task,
        "status": result.get("status"),
        "duration_ms": result.get("duration")
    })
    
    # 5. Update agent's memory
    MemoryWriter.save_agent_memory(
        agent_name=agent_name,
        memory_type="recent",
        data={"last_task": task, "last_result": result}
    )
    
    # 6. Log any new learnings
    if result.get("learning"):
        MemoryWriter.save_important_memory({
            "content": result["learning"],
            "category": f"agent_{agent_name}",
            "tags": ["learning", agent_name]
        })
    
    return result
```

---

## Pattern: Scout Decision Making

```python
from memory import ContextCompiler, MemoryWriter

def scout_decide(query: str, llm_callable):
    """Scout makes a decision and logs it."""
    
    # 1. Compile full context
    context = ContextCompiler.compile_scout_context(query)
    
    # 2. Get Scout's reasoning (from LLM)
    prompt = f"{context}\n\nTask: {query}"
    decision = llm_callable(prompt)
    
    # 3. Log the decision
    MemoryWriter.log_to_daily({
        "type": "scout_decision",
        "message": f"Decision made: {decision[:100]}...",
        "category": "coordination",
        "data": {"full_decision": decision}
    })
    
    # 4. Save state after decision
    MemoryWriter.save_state_snapshot({
        "last_decision": decision,
        "decision_time": datetime.now().isoformat(),
        "query": query
    })
    
    return decision
```

---

## Pattern: Search and Retrieve

```python
from memory import MemoryReader

def find_related_context(topic: str):
    """Find all related information about a topic."""
    
    # Search daily logs
    recent_mentions = MemoryReader.search_daily_logs(
        query=topic,
        days=14
    )
    
    # Search archives
    failures = MemoryReader.search_archives(topic, "failures")
    projects = MemoryReader.search_archives(topic, "projects")
    conversations = MemoryReader.search_archives(topic, "conversations")
    
    # Get important memories about topic
    important = MemoryReader.load_important_memory()
    relevant_important = [
        item for item in important.get("items", [])
        if topic.lower() in item.get("content", "").lower()
    ]
    
    return {
        "recent": recent_mentions,
        "failures": failures,
        "projects": projects,
        "conversations": conversations,
        "important": relevant_important
    }
```

---

## File Locations Reference

| Data Type | Location | Reader Method |
|-----------|----------|----------------|
| Today's Log | `memory/data/active/daily_logs/YYYY-MM-DD.jsonl` | `load_daily_log()` |
| 14-Day History | All daily logs | `load_14_day_memory()` |
| Important Memory | `memory/data/identity/important_memory.json` | `load_important_memory()` |
| User Preferences | `memory/data/identity/user_preferences.json` | `load_user_preferences()` |
| Current State | `memory/data/state/current_state.json` | `load_current_state()` |
| Agent Memory | `memory/data/agents/{agent_name}/{type}.json` | `load_agent_memory()` |
| Conversations | `memory/data/archive/conversations/` | `load_archive_item()` |
| Failures | `memory/data/archive/failures/` | `search_archives()` |
| Projects | `memory/data/archive/projects/` | `load_all_archive()` |

---

## Debugging & Troubleshooting

### Check Memory System Status
```python
from memory import get_memory_status

status = get_memory_status()
for key, value in status.items():
    print(f"{key}: {value}")
```

### Verify Directories Exist
```python
from memory import paths
paths.ensure_all_directories()
print("Memory directories verified")
```

### View Today's Logs
```python
from memory import MemoryReader

entries = MemoryReader.load_daily_log()
for entry in entries:
    print(f"{entry['timestamp']} - {entry['message']}")
```

### Check Last Executions
```python
from memory import MemoryReader

history = MemoryReader.load_execution_history(limit=10)
for execution in history:
    print(f"{execution['agent']}: {execution['action']} → {execution['result']}")
```

### Search for Issues
```python
from memory import MemoryReader

errors = MemoryReader.search_daily_logs("error", days=14)
failures = MemoryReader.search_archives("bug", "failures")

print(f"Found {len(errors)} errors in logs")
print(f"Found {len(failures)} related failures in archive")
```

---

## Common Mistakes to Avoid

❌ **Don't**: Forget to initialize memory system
```python
# Wrong
from memory import MemoryWriter
MemoryWriter.log_to_daily({...})  # Might fail if dirs don't exist
```

✅ **Do**: Initialize first
```python
from memory import initialize_memory_system, MemoryWriter
initialize_memory_system()
MemoryWriter.log_to_daily({...})  # Safe
```

❌ **Don't**: Use same archive_id twice
```python
# Wrong - overwrites previous
MemoryWriter.save_to_archive("projects", "proj_001", data1)
MemoryWriter.save_to_archive("projects", "proj_001", data2)  # Overwrites!
```

✅ **Do**: Use unique IDs with timestamp
```python
from datetime import datetime
timestamp = int(datetime.now().timestamp() * 1000)
MemoryWriter.save_to_archive("projects", f"proj_{timestamp}", data)
```

❌ **Don't**: Load all data without limit
```python
# Wrong - might be huge
all_history = MemoryReader.load_14_day_memory()
for entry in all_history:  # Could be thousands
    process(entry)
```

✅ **Do**: Use pagination or limits
```python
# Better
history = MemoryReader.load_14_day_memory()[:100]  # First 100
# Or stream for memory efficiency
for entry in MemoryReader.stream_daily_log():
    if should_process(entry):
        process(entry)
```

---

## Performance Tips

1. **Use stream_daily_log() for large files**
   ```python
   for entry in MemoryReader.stream_daily_log():
       # Process one at a time
   ```

2. **Use filter_daily_log() to reduce data**
   ```python
   errors = MemoryReader.filter_daily_log(severity="critical")
   ```

3. **Cache frequently accessed data**
   ```python
   identity = MemoryReader.load_identity()
   # Use identity multiple times without reloading
   ```

4. **Limit archive searches to specific type**
   ```python
   # Better - specific type
   failures = MemoryReader.search_archives(query, "failures")
   # vs worse - all types
   all_results = MemoryReader.search_archives(query, None)
   ```

---

## Testing Memory Operations

```python
# Quick integration test
from memory import (
    initialize_memory_system,
    MemoryWriter,
    MemoryReader,
    ContextCompiler
)

# 1. Initialize
initialize_memory_system()

# 2. Write test entry
MemoryWriter.log_to_daily({
    "type": "test",
    "message": "Testing memory system"
})

# 3. Read it back
entries = MemoryReader.load_daily_log()
assert len(entries) > 0, "Failed to read entries"

# 4. Compile context
context = ContextCompiler.compile_scout_context("test query")
assert len(context) > 100, "Context too short"

print("✓ All memory operations working!")
```

---

## Next: Integration Steps

After familiarizing yourself with this quick start:

1. Check `SCOUT_MEMORY_SYSTEM.md` for architecture details
2. Check `QUERY_MAKER_INTEGRATION.md` for integration procedures
3. Look at `memory/compiler.py` for advanced context compilation
4. Integrate with your query makers and agent systems
5. Add comprehensive logging to your workflow

---

Created: May 12, 2026  
Purpose: Quick reference for Scout memory system usage  
Status: Ready to use ✓
