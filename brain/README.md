# Brain Module - Decision Making & Intent Detection

Core intelligence module that analyzes user input and decides WHAT to do. Calls LLM only, returns structured actions. No tool execution.

## 🎯 Purpose

- **Intent detection** from user input
- **LLM integration** for decision making
- **Safety checking** for dangerous operations
- **Action generation** with execution steps
- **Conversational awareness** (chat vs commands)

## 📁 Structure

```
brain/
├── __init__.py           # Main exports
├── brain.py              # Core decision logic
├── llm.py                # LLM integration
└── README.md            # This file
```

## 🧠 Core Functions

### analyze_intent(user_input: str) → dict
Determines if input is conversational or command-based.

```python
result = brain.analyze_intent("list files in /home")
# Returns: {"intent": "command", "raw_input": "..."}

result = brain.analyze_intent("hello, how are you?")
# Returns: {"intent": "conversational", "raw_input": "..."}
```

### check_safety(command: str) → Tuple[bool, str, str]
Validates command against safety rules.

```python
safe, severity, reason = brain.check_safety("rm -rf /")
# Returns: (False, "critical", "Dangerous pattern detected")

safe, severity, reason = brain.check_safety("ls /tmp")
# Returns: (True, "safe", "No safety issues")
```

### generate_action(user_input: str, context: dict) → Message
Creates a structured action message for the executor.

```python
message = brain.generate_action(
    "find all python files",
    context={"last_workspace": "/home/user"}
)
# Returns Message with action, platform, steps, etc.
```

### get_llm_response(prompt: str, model: str) → str
Calls Ollama LLM with prompt.

```python
response = brain.get_llm_response(
    "What is Python?",
    model="general_model"
)
# Returns LLM response string
```

### is_conversational(user_input: str) → bool
Quick check if input is chat-based.

```python
is_conversational("hello")  # True
is_conversational("list files")  # False
```

## 🔌 LLM Integration

The `llm.py` module handles all LLM communication:

### LLM Module (`llm.py`)

```python
class LLMClient:
    def __init__(self):
        # Reads from config.LLM_CONFIG only
        self.ollama_url = get_config("LLM_CONFIG")["ollama_url"]
        self.general_model = get_config("LLM_CONFIG")["general_model"]
        
    def call(self, prompt: str, model: str) -> str:
        # Calls Ollama HTTP API
        # Parses response
        # Returns raw text
```

### Configuration

LLM settings from `config/settings.py`:
```python
LLM_CONFIG = {
    "general_model": "llama3.2",
    "code_model": "qwen2.5-coder", 
    "ollama_url": "http://127.0.0.1:11434"
}
```

## 🎯 Brain Logic Flow

```
User Input
    ↓
analyze_intent() - Classify as command/conversation
    ↓
if conversational:
    return chatbot_response()
    
if command:
    check_safety() - Validate against forbidden patterns
    ↓
    if not safe:
        ask_confirmation()
    ↓
    generate_action() - Create steps for executor
    ↓
    return Message(action="execute", steps=[...])
```

## 📋 Message Generation

The brain generates Messages for the executor:

```python
Message(
    action="execute",
    platform="cli",
    mode="visible",  # or "headless", "hybrid"
    data={
        "user_intent": "find files",
        "search_pattern": "*.py"
    },
    steps=[
        {"tool": "run_command", "params": {"command": "find . -name '*.py'"}},
        {"tool": "count_results", "params": {}}
    ]
)
```

## 🔐 Safety Rules

Safety checking against configured rules from `config/`:

### Forbidden Patterns
Commands matching these are always blocked:
- `rm -rf` - Recursive delete all
- `dd if=/dev/zero` - Disk wipe
- `format c:` - Drive format
- Other dangerous patterns

### Requires Confirmation
Commands that trigger approval workflow:
- `sudo` - Privilege escalation
- `kill` - Process termination
- `reboot` - System restart
- Other risky operations

```python
safe, severity, reason = check_safety("rm -rf /home/important")
# Returns: (False, "critical", "Forbidden pattern: rm -rf")

safe, severity, reason = check_safety("sudo apt update")
# Returns: (True, "warning", "Requires confirmation")
```

## 💬 Conversational vs Command

### Conversational Input
```python
"hello"
"how are you?"
"what is Python?"
"tell me about yourself"
```

Returns chatbot response instead of executing actions.

### Command Input
```python
"list files in /tmp"
"find all .py files"
"create directory /home/test"
"run echo hello"
```

Generates execution steps for executor.

## 🧪 Testing Brain

```python
def test_analyze_intent():
    result = brain.analyze_intent("list files")
    assert result["intent"] == "command"
    
def test_check_safety():
    safe, severity, reason = brain.check_safety("rm -rf /")
    assert not safe
    
def test_generate_action():
    msg = brain.generate_action("find python files")
    assert msg.action == "execute"
    assert len(msg.steps) > 0
    
def test_llm_response():
    response = brain.get_llm_response("what is AI?")
    assert isinstance(response, str)
    assert len(response) > 0
```

## 📝 Key Features

### Intent Detection
- ✅ Classifies user input
- ✅ Separates chat from commands
- ✅ Contextual awareness
- ✅ Handles ambiguous input

### Safety Checking
- ✅ Pattern matching for dangerous operations
- ✅ Severity classification
- ✅ Reason reporting
- ✅ Confirmation workflow support

### Action Generation
- ✅ Creates execution steps
- ✅ Determines platform (CLI, GUI, Web)
- ✅ Chooses mode (visible, headless, hybrid)
- ✅ Includes context for executor

### LLM Integration
- ✅ Reads config, no hardcoding
- ✅ HTTP communication with Ollama
- ✅ Error handling
- ✅ Timeout protection
- ✅ Response parsing

## 🚫 What Brain NEVER Does

```python
# ❌ Never imports executor
from executor import execute_step

# ❌ Never imports tools directly
from tools import run_command

# ❌ Never updates state directly
state.update(result)

# ❌ Never knows file paths
os.chdir("/home/user")

# ❌ Never hardcodes settings
OLLAMA_URL = "http://127.0.0.1:11434"

# ✅ Always returns Message for router to dispatch
return Message(action="execute", steps=[...])
```

## 🎯 Integration Examples

### With Router
```python
from router import Message, route

# User input comes in
user_input = "find all .py files"

# Brain analyzes and decides
message = brain.generate_action(user_input)

# Router dispatches to executor
response = route(message)
```

### With LLM
```python
# Brain calls LLM through llm.py
response = brain.get_llm_response(
    "Generate shell command to find .py files",
    model="code_model"
)
# llm.py reads from config, calls Ollama, returns response
```

### With State (via Router)
```python
# Brain doesn't call state directly
# Instead returns message for router
message = Message(
    action="record_state",
    data={"action": "analyze_intent", "result": intent}
)
# Router dispatches this to state module
```

## ✨ Highlights

- **Pure decision making** - No tool execution
- **LLM integrated** - Calls Ollama for intelligence
- **Safety first** - Validates all commands
- **Modular** - No cross-imports
- **Type-safe** - Full type hints
- **Configurable** - All settings from config module
- **Testable** - Easy to mock LLM for testing

---

**Status: 🚀 Ready for integration with router, executor, and config modules**
