# Executor Module - Execution Orchestration & Step Running

Orchestrates execution of steps, handles different execution modes (visible, headless, hybrid), manages approval workflow, and retries. Central execution engine.

## 🎯 Purpose

- **Step execution** - Run action steps in sequence
- **Mode handling** - Support visible, headless, and hybrid modes
- **Approval workflow** - Ask user for confirmation
- **Error handling** - Retry failed steps
- **Progress tracking** - Monitor execution status
- **Tool dispatching** - Call tools via router

## 📁 Structure

```
executor/
├── __init__.py           # Main exports
├── executor.py           # Core execution logic
├── modes.py              # Execution mode handlers
└── README.md            # This file
```

## 🚀 Core Functions

### execute(message: Message) → Response
Main execution entry point.

```python
message = Message(
    action="execute",
    platform="cli",
    mode="visible",
    steps=[
        {"tool": "run_command", "params": {"command": "ls /tmp"}}
    ]
)
response = executor.execute(message)
# Returns Response with results
```

### execute_step(step: dict, context: dict) → dict
Execute a single step.

```python
step = {"tool": "run_command", "params": {"command": "echo hello"}}
result = executor.execute_step(step, context={})
# Returns {"success": True, "output": "hello"}
```

### execute_step_with_approval(step: dict) → dict
Execute step with user approval.

```python
step = {"tool": "run_command", "params": {"command": "sudo apt update"}}
result = executor.execute_step_with_approval(step)
# Asks user: "Execute: sudo apt update? (yes/no)"
# Returns result if approved
```

### handle_visible_mode(steps: list) → Response
Execute steps with user interaction visible.

```python
# User sees each step
# Can pause/cancel
# Gets real-time output
response = executor.handle_visible_mode(steps)
```

### handle_headless_mode(steps: list) → Response
Execute steps in background.

```python
# No user interaction
# No output displayed
# Fast execution
response = executor.handle_headless_mode(steps)
```

### handle_hybrid_mode(steps: list) → Response
Mix of visible and headless execution.

```python
# First steps visible, later steps headless
# Or approval steps interactive, others background
response = executor.handle_hybrid_mode(steps)
```

## 🔄 Execution Flow

```
Message(action="execute", steps=[...])
    ↓
executor.execute(message)
    ↓
Validate steps
    ↓
Choose mode handler:
    - visible: show to user, get approvals
    - headless: run silently
    - hybrid: mix
    ↓
For each step:
    - execute_step(step)
    - If error: retry_failed_step()
    - Track result
    ↓
Return Response with all results
```

## 🎯 Execution Modes

### Visible Mode
User sees and approves each action.

```python
Step 1: run_command "find /tmp -name '*.py'"
→ Display: "Finding Python files in /tmp..."
→ Show result to user
→ Ask: "Continue to next step?"

Step 2: count_results
→ Display: "Found 42 Python files"
```

### Headless Mode
Silent background execution.

```python
Step 1: run_command "find /tmp -name '*.py'"
→ Execute silently
→ Don't show output
→ Continue to next step

Step 2: count_results
→ Execute silently
→ Return results only
```

### Hybrid Mode
Mix of both approaches.

```python
Step 1: run_command (visible)
→ Display and approve

Step 2: count_results (headless)
→ Execute silently

Step 3: dangerous_operation (visible)
→ Display and ask for confirmation
```

## ✅ Approval Workflow

From original `ai-exec.py`:

```python
def execute_step_with_approval(step: dict) -> dict:
    """
    Execute step with user approval.
    
    1. Display what will be executed
    2. Ask for confirmation
    3. Execute if approved
    4. Record result
    """
    
    # Step 1: Show the action
    print(f"About to execute: {step['tool']}")
    if step['params']:
        print(f"Parameters: {step['params']}")
    
    # Step 2: Ask user
    approval = input("Execute? (yes/no/cancel): ")
    
    if approval.lower() in ['yes', 'y']:
        # Step 3: Execute
        return executor_step(step)
    elif approval.lower() == 'cancel':
        return {"success": False, "error": "Cancelled by user"}
    else:
        return {"success": False, "error": "Rejected by user"}
```

## 🔄 Retry Logic

Automatic retry for transient failures:

```python
def retry_failed_step(step: dict, attempt: int = 1) -> dict:
    """
    Retry failed step with exponential backoff.
    
    Max 3 retries (from config.EXECUTION_CONFIG)
    Delay increases: 1s, 2s, 4s
    """
    
    MAX_RETRIES = 3
    RETRY_DELAYS = [1, 2, 4]  # seconds
    
    if attempt > MAX_RETRIES:
        return {"success": False, "error": "Max retries exceeded"}
    
    delay = RETRY_DELAYS[attempt - 1]
    time.sleep(delay)
    
    result = execute_step(step)
    
    if not result.get("success") and attempt < MAX_RETRIES:
        return retry_failed_step(step, attempt + 1)
    
    return result
```

## 🔧 Tool Execution

Steps reference tools from the tool registry:

```python
step = {
    "tool": "run_command",
    "params": {
        "command": "ls /tmp",
        "shell": "bash"
    }
}

# Executor looks up tool in registry
tool_def = TOOL_REGISTRY["run_command"]

# Calls via router to avoid direct imports
message = Message(
    action="execute_tool",
    data={
        "tool": "run_command",
        "params": step["params"]
    }
)
result = router.route(message)
```

## 📊 Step Schema

Each step in the steps list:

```python
{
    "tool": "run_command",           # Tool name (from registry)
    "description": "Find .py files", # Human-readable
    "platform": "cli",               # Required platform
    "params": {                       # Tool-specific parameters
        "command": "find . -name '*.py'",
        "shell": "bash"
    },
    "requires_approval": False,      # Ask user first?
    "retry_on_failure": True,        # Retry if fails?
    "timeout": 30                    # Max seconds
}
```

## 🧪 Testing Executor

```python
def test_execute_simple():
    message = Message(
        action="execute",
        steps=[{"tool": "echo", "params": {"text": "hello"}}]
    )
    response = executor.execute(message)
    assert response.success

def test_execute_visible_mode():
    response = executor.handle_visible_mode(steps)
    assert response.success

def test_execute_headless_mode():
    response = executor.handle_headless_mode(steps)
    assert response.success

def test_approval_workflow():
    # Mock user saying "yes"
    result = executor.execute_step_with_approval(step)
    assert result["success"]

def test_retry_on_failure():
    # Mock failing step, test retry logic
    result = executor.retry_failed_step(failing_step)
    # Should retry up to 3 times
```

## 📝 Key Features

### Step Execution
- ✅ Sequential step execution
- ✅ Tool registry lookup
- ✅ Parameter validation
- ✅ Timeout protection
- ✅ Error handling

### Mode Handling
- ✅ Visible mode with user interaction
- ✅ Headless mode for background execution
- ✅ Hybrid mode mixing both
- ✅ Mode selection from message

### Approval Workflow
- ✅ Display actions to user
- ✅ Request confirmation
- ✅ Support yes/no/cancel
- ✅ Log approvals

### Error Handling
- ✅ Catch step failures
- ✅ Automatic retry with exponential backoff
- ✅ Max retry limit from config
- ✅ Clear error messages

### Progress Tracking
- ✅ Track current step
- ✅ Maintain results list
- ✅ Calculate completion percentage
- ✅ Send to state module

## 🚫 What Executor NEVER Does

```python
# ❌ Never imports tools directly
from os import run_command

# ❌ Never makes LLM decisions
brain.generate_action()

# ❌ Never directly calls check_safety
brain.check_safety(command)

# ❌ Never imports state
state.update(result)

# ✅ Always routes through router
router.route(message)
```

## ✨ Highlights

- **Orchestration** - Runs steps in order
- **Mode flexible** - Visible/headless/hybrid
- **Approval flow** - User can control execution
- **Error resilient** - Retries transient failures
- **Progress aware** - Tracks completion
- **Type-safe** - Full type hints
- **Extensible** - Easy to add new modes

---

**Status: 🚀 Ready for integration with router, tools, and state modules**
