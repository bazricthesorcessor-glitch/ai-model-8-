# Tools Module - Tool Registry & Definitions

Centralized tool registry and definitions. Defines WHAT tools are available and HOW they work, but contains no execution logic.

## 🎯 Purpose

- **Tool catalog** - All available tools defined here
- **No execution logic** - Only schema and metadata
- **Tool registry** - Central lookup for executor
- **Handler mapping** - Which module executes each tool
- **Documentation** - Descriptions and parameters

## 📁 Structure

```
tools/
├── __init__.py           # Main exports
├── registry.py           # Tool registry loader
├── definitions.py        # Tool definitions
└── README.md            # This file
```

## 📋 Tool Registry Schema

Tools defined in `definitions.py`:

```python
TOOL_REGISTRY = {
    "tool_name": {
        "name": "tool_name",
        "description": "What this tool does",
        "platform": "cli",              # "cli", "gui", "web", "system"
        "requires_approval": True,      # Ask user first?
        "params": {
            "param_name": {
                "type": "string",
                "required": True,
                "description": "What this param does",
                "default": "default_value"
            }
        },
        "returns": {
            "type": "dict",
            "description": "What tool returns"
        },
        "examples": [
            {
                "description": "Example 1",
                "params": {"param": "value"},
                "result": "expected output"
            }
        ],
        "handler": "executor.cli",      # String reference, no imports
        "timeout": 30
    }
}
```

## 🛠️ Available Tools (Planned)

### CLI Tools

**run_command**
```python
{
    "name": "run_command",
    "description": "Execute shell command",
    "platform": "cli",
    "params": {
        "command": {"type": "string", "required": True},
        "shell": {"type": "string", "default": "bash"}
    },
    "handler": "executor.cli"
}
```

**find_files**
```python
{
    "name": "find_files",
    "description": "Find files matching pattern",
    "platform": "cli",
    "params": {
        "pattern": {"type": "string", "required": True},
        "path": {"type": "string", "default": "."}
    },
    "handler": "executor.cli"
}
```

### GUI Tools

**click_button**
```python
{
    "name": "click_button",
    "description": "Click UI element",
    "platform": "gui",
    "params": {
        "selector": {"type": "string", "required": True},
        "x": {"type": "int"},
        "y": {"type": "int"}
    },
    "handler": "executor.ui"
}
```

**type_text**
```python
{
    "name": "type_text",
    "description": "Type text into focused element",
    "platform": "gui",
    "params": {
        "text": {"type": "string", "required": True},
        "delay": {"type": "float", "default": 0.05}
    },
    "handler": "executor.ui"
}
```

### Web Tools

**search_web**
```python
{
    "name": "search_web",
    "description": "Search the web",
    "platform": "web",
    "params": {
        "query": {"type": "string", "required": True},
        "provider": {"type": "string", "default": "google"}
    },
    "handler": "executor.web"
}
```

**get_page_content**
```python
{
    "name": "get_page_content",
    "description": "Get content from web page",
    "platform": "web",
    "params": {
        "url": {"type": "string", "required": True},
        "extract": {"type": "string", "default": "text"}
    },
    "handler": "executor.web"
}
```

### OS Tools

**switch_workspace**
```python
{
    "name": "switch_workspace",
    "description": "Switch Hyprland workspace",
    "platform": "os",
    "params": {
        "workspace_id": {"type": "int", "required": True}
    },
    "handler": "executor.os"
}
```

**window_split**
```python
{
    "name": "window_split",
    "description": "Split window in direction",
    "platform": "os",
    "params": {
        "direction": {"type": "string", "enum": ["left", "right", "up", "down"]}
    },
    "handler": "executor.os"
}
```

## 📖 Using the Registry

### Load Registry
```python
from tools import get_tool_definition, list_tools, search_tools

# Get specific tool
tool = get_tool_definition("run_command")

# List all tools
all_tools = list_tools()

# Search tools by platform
cli_tools = search_tools(platform="cli")
```

### Validate Parameters
```python
tool = get_tool_definition("run_command")

# Check if params valid
params = {"command": "ls", "shell": "bash"}
valid = validate_params(tool, params)

# Get missing required params
required = get_required_params(tool)
```

### Generate Tool Help
```python
tool = get_tool_definition("click_button")

# Get description
print(tool["description"])

# Get example usage
for example in tool["examples"]:
    print(f"Example: {example['description']}")
    print(f"Params: {example['params']}")
```

## 🔗 Integration with Executor

Executor looks up tools by name:

```python
# Step references a tool
step = {
    "tool": "run_command",
    "params": {"command": "ls /tmp"}
}

# Executor gets tool definition
tool_def = TOOL_REGISTRY["run_command"]

# Validates parameters
assert validate_params(tool_def, step["params"])

# Calls handler (no direct execution)
# Just dispatches via router
handler_path = tool_def["handler"]  # "executor.cli"
# Router routes to actual executor
```

## 🚫 What Tools NEVER Contains

```python
# ❌ Never imports other modules
from executor import execute_cli_command

# ❌ Never contains execution logic
def run_command(command):
    subprocess.run(command)

# ❌ Never modifies state
state.update({"tool": "run_command"})

# ❌ Never calls tools directly
run_command("ls")

# ✅ Only definitions
TOOL_REGISTRY = {
    "run_command": {
        "description": "...",
        "params": {...},
        "handler": "executor.cli"
    }
}
```

## 📝 Adding New Tools

To add a new tool:

1. Add to `TOOL_REGISTRY` in `definitions.py`
2. Include complete schema
3. Add examples
4. Document parameters
5. Update this README

Example:
```python
TOOL_REGISTRY["my_tool"] = {
    "name": "my_tool",
    "description": "Does something useful",
    "platform": "cli",
    "params": {
        "param1": {
            "type": "string",
            "required": True,
            "description": "..."
        }
    },
    "handler": "executor.cli",
    "examples": [
        {
            "description": "Example usage",
            "params": {"param1": "value"},
            "result": "result"
        }
    ]
}
```

## 🔍 Tool Discovery

List tools by category:

```python
# All CLI tools
cli_tools = [t for t in TOOL_REGISTRY.values() if t["platform"] == "cli"]

# All tools requiring approval
approval_tools = [t for t in TOOL_REGISTRY.values() if t["requires_approval"]]

# All GUI tools
gui_tools = [t for t in TOOL_REGISTRY.values() if t["platform"] == "gui"]
```

## ✅ Tool Schema Validation

All tools validated on load:

```python
required_keys = ["name", "description", "platform", "handler", "params"]
for tool_name, tool_def in TOOL_REGISTRY.items():
    for key in required_keys:
        assert key in tool_def, f"Tool {tool_name} missing {key}"
    
    # Validate parameters schema
    for param_name, param_def in tool_def["params"].items():
        assert "type" in param_def
        assert param_def["type"] in valid_types
```

## 📊 Tool Statistics

```python
# Get tool counts
total_tools = len(TOOL_REGISTRY)
cli_count = len([t for t in TOOL_REGISTRY.values() if t["platform"] == "cli"])
gui_count = len([t for t in TOOL_REGISTRY.values() if t["platform"] == "gui"])
web_count = len([t for t in TOOL_REGISTRY.values() if t["platform"] == "web"])

print(f"Total tools: {total_tools}")
print(f"CLI tools: {cli_count}")
print(f"GUI tools: {gui_count}")
print(f"Web tools: {web_count}")
```

## 🧪 Testing Tools

```python
def test_tool_registry_loaded():
    from tools import TOOL_REGISTRY
    assert len(TOOL_REGISTRY) > 0

def test_tool_schema_valid():
    from tools import TOOL_REGISTRY
    for tool_name, tool_def in TOOL_REGISTRY.items():
        assert "handler" in tool_def
        assert "params" in tool_def

def test_get_tool_definition():
    from tools import get_tool_definition
    tool = get_tool_definition("run_command")
    assert tool is not None
    assert tool["platform"] == "cli"

def test_search_tools():
    from tools import search_tools
    cli_tools = search_tools(platform="cli")
    assert len(cli_tools) > 0
```

## ✨ Highlights

- **Catalog** - All tools in one place
- **Schema-based** - Clear parameter definitions
- **No logic** - Definitions only
- **Discoverable** - Easy tool lookup
- **Examples** - Usage examples included
- **Validated** - Schema checked on load
- **Extensible** - Easy to add new tools

---

**Status: 🚀 Ready for integration with executor and router**
