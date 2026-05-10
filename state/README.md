# State Module - System Status & Memory

Tracks current system execution state and recent action history. Stores status, NOT chat history. In-memory with optional persistence.

## 🎯 Purpose

- **Current status** - What's happening now
- **Execution history** - Recent actions and results
- **Tool results** - Latest output from tools
- **Context preservation** - For decision making
- **Progress tracking** - Execution status

## 📁 Structure

```
state/
├── __init__.py           # Main exports
├── state.py              # Core state management
└── README.md            # This file
```

## 📊 State Schema

Current system state:

```python
{
    "status": "idle",  # "idle", "executing", "waiting_approval", "error"
    "current_action": None,
    "current_step": 0,
    "total_steps": 0,
    "completion_percent": 0,
    
    "execution_history": [
        {
            "timestamp": 1234567890.123,
            "action": "run_command",
            "params": {"command": "ls"},
            "success": True,
            "result": "file1.txt\nfile2.txt",
            "error": None
        }
    ],
    
    "tool_results": {
        "last_command": {
            "output": "...",
            "success": True
        }
    },
    
    "approvals": [
        {
            "timestamp": 1234567890.0,
            "action": "run_command",
            "params": {"command": "sudo apt update"},
            "user_response": "approved"
        }
    ]
}
```

## 🔧 Core Functions

### update(action: str, result: dict, error: str = None) → bool
Record an action result.

```python
state.update(
    action="run_command",
    result={"output": "hello world", "exit_code": 0},
    error=None
)
```

### get_status() → dict
Get current system status.

```python
status = state.get_status()
# Returns current status dict
print(f"Status: {status['status']}")  # "idle", "executing", etc.
print(f"Current: {status['current_action']}")
```

### get_last_N_actions(n: int = 5) → list
Get recent actions for context.

```python
recent = state.get_last_N_actions(3)
# Returns last 3 actions for context in brain
```

### record_approval(action: str, params: dict, response: str) → bool
Record user approval/denial.

```python
state.record_approval(
    action="run_command",
    params={"command": "sudo apt update"},
    response="approved"  # or "denied", "cancelled"
)
```

### set_execution_status(status: str, current_step: int, total_steps: int) → bool
Update execution progress.

```python
state.set_execution_status("executing", 1, 5)
# Now status shows: "Step 1 of 5"
```

### clear() → bool
Reset state between sessions.

```python
state.clear()
# All state cleared, ready for new session
```

## 🔄 State Flow

```
Executor starts execution
    ↓
state.set_execution_status("executing", 0, 3)
    
For each step:
    ↓
    state.set_execution_status("executing", current, total)
    
    Step executes
    ↓
    state.update(action, result)
    
    If approval needed:
    ↓
    state.record_approval(action, params, response)
    
Execution complete
    ↓
state.set_execution_status("idle", 0, 0)
```

## 📝 State Types

### Status Values
- `idle` - No execution happening
- `executing` - Steps running
- `waiting_approval` - Awaiting user confirmation
- `error` - Execution failed
- `paused` - Paused by user
- `complete` - Execution finished

### Action Result
```python
{
    "timestamp": time.time(),
    "action": "tool_name",
    "params": {...},
    "success": True/False,
    "result": {...},
    "error": "error message" or None
}
```

### Approval Record
```python
{
    "timestamp": time.time(),
    "action": "tool_name",
    "params": {...},
    "user_response": "approved|denied|cancelled"
}
```

## 🧪 Testing State

```python
def test_update_action():
    state.clear()
    state.update("test_action", {"result": "ok"})
    status = state.get_status()
    assert len(status["execution_history"]) == 1

def test_get_status():
    state.clear()
    status = state.get_status()
    assert status["status"] == "idle"

def test_execution_progress():
    state.clear()
    state.set_execution_status("executing", 1, 5)
    status = state.get_status()
    assert status["completion_percent"] == 20  # 1/5

def test_approval_recording():
    state.clear()
    state.record_approval("test", {}, "approved")
    status = state.get_status()
    assert len(status["approvals"]) == 1

def test_get_recent_actions():
    state.clear()
    for i in range(5):
        state.update(f"action_{i}", {"data": i})
    recent = state.get_last_N_actions(2)
    assert len(recent) == 2
```

## 🔐 Safety

- ✅ Read-only status access
- ✅ Timestamped records
- ✅ Complete action logging
- ✅ Approval tracking
- ✅ Error recording

## 📡 Integration with Router

State is only updated via router messages:

```python
# Executor doesn't call state directly
from router import Message, route

# Instead sends message
message = Message(
    action="record_state",
    data={
        "action": "run_command",
        "result": {"output": "..."},
        "success": True
    }
)

# Router dispatches to state
response = route(message)
```

## 🚫 What State NEVER Stores

```python
# ❌ Never stores chat history
conversation = ["user said X", "bot said Y"]

# ❌ Never stores full execution logs
every_single_keystroke = [...]

# ❌ Never stores sensitive data
passwords = [...]

# ❌ Never makes decisions
if status == "idle":
    brain.decide()

# ✅ Only stores:
# - Current execution status
# - Recent action results (last N)
# - Tool outputs for context
# - Approval records for audit
```

## 💾 Optional Persistence

State can be persisted to disk (Phase 5):

```python
# Save state to JSON file
state.save("/tmp/state.json")

# Load state from file
state.load("/tmp/state.json")

# State file format
{
    "timestamp": 1234567890,
    "status": "idle",
    "execution_history": [...],
    "tool_results": {...}
}
```

## 📊 State Statistics

```python
def get_state_stats() -> dict:
    """Get state statistics"""
    status = get_status()
    return {
        "total_actions": len(status["execution_history"]),
        "successful_actions": sum(1 for a in status["execution_history"] if a["success"]),
        "total_approvals": len(status["approvals"]),
        "current_status": status["status"]
    }

stats = state.get_state_stats()
print(f"Executed {stats['successful_actions']}/{stats['total_actions']} actions")
```

## ✨ Highlights

- **Status tracking** - Current execution state
- **Recent history** - Last N actions for context
- **Approval logging** - User decisions recorded
- **Tool results** - Latest outputs available
- **Progress aware** - Execution step tracking
- **Clean API** - Simple state access
- **Optional persistence** - Save to disk if needed

---

**Status: 🚀 Ready for integration with router and executor**
