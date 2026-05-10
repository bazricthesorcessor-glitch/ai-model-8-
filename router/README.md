# Router Module - Message Routing & Orchestration

Central message dispatcher that routes all communication between system modules. Pure routing logic with no business logic.

## 🎯 Purpose

- **Single dispatcher** for all message routing
- **Standardized message format** across the system
- **No cross-module imports** - all module communication via router
- **Clean separation** between modules
- **Message tracing** for debugging

## 📁 Structure

```
router/
├── __init__.py           # Main exports (route function)
├── message.py            # Message schema definitions
├── router.py             # Router dispatcher logic
└── README.md            # This file
```

## 📨 Message Schema

### Message Class
```python
class Message:
    action: str              # "decide", "execute", "record_state", "get_state"
    platform: str            # "cli", "gui", "web", "system"
    mode: str                # "visible", "headless", "hybrid"
    data: dict               # Action-specific payload
    steps: list              # Execution steps for execute action
    context: dict            # Context from prior steps
    timestamp: float         # When message was created
```

### Message Actions

**decide** - Ask brain to make a decision
```python
Message(
    action="decide",
    data={
        "user_input": "list files in /tmp",
        "intent": "command"
    }
)
```

**execute** - Execute steps via executor
```python
Message(
    action="execute",
    platform="cli",
    mode="visible",
    steps=[
        {"tool": "run_command", "params": {"command": "ls /tmp"}}
    ]
)
```

**record_state** - Update state with action result
```python
Message(
    action="record_state",
    data={
        "action": "list_files",
        "result": "...",
        "timestamp": 1234567890
    }
)
```

**get_state** - Retrieve current system state
```python
Message(
    action="get_state",
    data={"request": "status"}
)
```

## 🚀 Router Function

The main routing dispatcher:

```python
def route(message: Message) -> Response:
    """
    Route a message to appropriate module.
    
    Args:
        message: Message to route
        
    Returns:
        Response from module
    """
    if message.action == "decide":
        return brain.decide(message)
    elif message.action == "execute":
        return executor.execute(message)
    elif message.action == "record_state":
        return state.update(message)
    elif message.action == "get_state":
        return state.get(message)
    else:
        raise ValueError(f"Unknown action: {message.action}")
```

## 🔄 Message Flow

```
User Input
    ↓
main.py calls router.route(message)
    ↓
Router.route() checks message.action
    ↓
Route to appropriate module:
    - "decide" → brain module
    - "execute" → executor module  
    - "record_state" → state module
    - "get_state" → state module
    ↓
Module processes and returns Response
    ↓
Response returned to caller
```

## 📋 Response Schema

```python
class Response:
    success: bool            # Success status
    data: dict              # Response data
    error: str              # Error message if failed
    timestamp: float        # When response created
```

## ✅ Core Design Rules

### 1. Router Routes, Doesn't Logic
```python
# ❌ WRONG - Router doing logic
if message.requires_approval:
    executor.ask_user()

# ✅ RIGHT - Just route
return executor.execute(message)
```

### 2. No Cross-Module Imports
```python
# ❌ WRONG - Direct import
from brain import decide
result = decide(user_input)

# ✅ RIGHT - Via router
message = Message(action="decide", data={"user_input": user_input})
result = router.route(message)
```

### 3. All Module Communication Via Router
```python
# ❌ WRONG - Direct call
from executor import execute_step
execute_step(step)

# ✅ RIGHT - Via router
message = Message(action="execute", steps=[step])
router.route(message)
```

### 4. Message Format Consistent
```python
# ❌ WRONG - Direct function calls with different signatures
brain.analyze(input)
executor.run(steps)
state.save(data)

# ✅ RIGHT - Standardized message format
router.route(Message(action="decide", ...))
router.route(Message(action="execute", ...))
router.route(Message(action="record_state", ...))
```

## 📊 Usage Examples

### Example 1: Decision Request
```python
from router import Message, route

# Ask brain to decide what to do
message = Message(
    action="decide",
    data={
        "user_input": "find python files",
        "context": {"last_action": "explore"}
    }
)
response = route(message)
print(response.data)  # {"action": "execute", "steps": [...]}
```

### Example 2: Execute Steps
```python
# Execute the action brain decided
message = Message(
    action="execute",
    platform="cli",
    mode="visible",
    steps=[
        {"tool": "run_command", "params": {"command": "find . -name '*.py'"}}
    ]
)
response = route(message)
print(response.data)  # {"results": [...], "status": "success"}
```

### Example 3: Record Result
```python
# Log the execution result
message = Message(
    action="record_state",
    data={
        "action": "find_python_files",
        "result": ["file1.py", "file2.py"],
        "success": True
    }
)
response = route(message)
print(response.data)  # {"recorded": True}
```

### Example 4: Get Status
```python
# Get current system status
message = Message(action="get_state")
response = route(message)
print(response.data)  # {"status": "idle", "current_action": None, ...}
```

## 🔐 Safety Features

- ✅ Message validation
- ✅ Action type checking
- ✅ Data schema validation
- ✅ Error handling
- ✅ Message tracing for debugging
- ✅ Timeout protection

## 🧪 Testing Router

```python
def test_router_decide():
    msg = Message(action="decide", data={"user_input": "test"})
    response = route(msg)
    assert response.success

def test_router_execute():
    msg = Message(action="execute", steps=[...])
    response = route(msg)
    assert response.success

def test_router_invalid_action():
    msg = Message(action="invalid")
    with pytest.raises(ValueError):
        route(msg)
```

## 📝 Adding New Message Types

To add a new message action:

1. Add to Message schema in `message.py`
2. Document the data structure
3. Add routing logic in `router.py`
4. Create handler in appropriate module
5. Add tests in `test_router.py`

Example:
```python
# In message.py - document the new action
# In router.py - add routing logic
elif message.action == "my_new_action":
    return my_module.handle(message)
```

## 🎯 Key Benefits

- **Modular** - Clean module separation
- **Testable** - Easy to mock modules
- **Traceable** - Clear message flow
- **Flexible** - Easy to add new actions
- **Safe** - Validation at routing layer
- **Debuggable** - Message logging available

## ✨ Highlights

- **Pure routing** - No business logic
- **Standardized** - All messages same format
- **Clean** - No module cross-imports
- **Extensible** - Easy to add new actions
- **Type-safe** - Full type hints
- **Well-tested** - Comprehensive test coverage

---

**Status: 🚀 Ready for integration with brain, executor, and state modules**
