# Config Module - Application Configuration & Constants

Centralized configuration management for the entire AI assistant system. All settings, constants, and configuration parameters are defined here without requiring module imports elsewhere.

## 🎯 Purpose

- **Single source of truth** for all application settings
- **No hardcoded values** in other modules
- **Easy configuration** without code changes
- **Environment-aware** settings (development, testing, production)

## 📁 Structure

```
config/
├── __init__.py           # Main exports
├── settings.py           # Configuration definitions
├── paths.py              # Semantic path resolver
└── README.md            # This file
```

## 🗂️ Path Resolver System

The `paths.py` module provides semantic access to configuration file paths:

```python
from config import Paths, path_of

# Access paths via Paths class
shell_path = Paths.shell
hyprland_path = Paths.hyprland

# Or use semantic path_of() function
shell = path_of("shell")
hyprland = path_of("hyprland")
```

### Why path_of() exists

- **Models understand semantics better than raw paths**: `path_of("shell")` is more meaningful to an LLM than `/home/user/.config/caelestia/shell.json`
- **Single source of truth**: Path definitions centralized in one place (easier to maintain and refactor)
- **Runtime path resolution**: No need to parse config files to find paths
- **Type-safe access**: Models can introspect available paths and error messages list all available options

**Available paths**:
- `path_of("shell")` → `~/.config/caelestia/shell.json`
- `path_of("hyprland")` → `~/.config/hypr/hyprland.conf`
- `path_of("hyprland_dir")` → `~/.config/hypr/`
- `path_of("hyprland_keybinds")` → `~/.config/hypr/hyprland/keybinds.conf`
- `path_of("caelestia_dir")` → `~/.config/caelestia/`

## ⚙️ Configuration Categories

### OS/Hyprland Configuration (Goldmine for Desktop Automation)
```python
OS_CONFIG = {
    "hyprland_config_dir": "~/.config/hypr",
    "shell_config_file": "~/.config/caelestia/shell.json",
    "hyprland_config_file": "~/.config/hypr/hyprland.conf",
    "hyprland_configs": {
        "binds": "~/.config/hypr/binds.conf",
        "monitors": "~/.config/hypr/monitors.conf",
        "workspaces": "~/.config/hypr/workspaces.conf",
        "animations": "~/.config/hypr/animations.conf",
    }
}
```

**Critical paths for OS manipulation**:
- `~/.config/hypr/` - Core Hyprland window manager configuration
- `~/.config/caelestia/shell.json` - Caelestia shell configuration with gestures and shortcuts
- All window management, splits, gestures, and keyboard controls configured here

See `HYPRLAND_CONFIG_GUIDE.md` for detailed documentation.

### LLM Configuration
```python
LLM_CONFIG = {
    "general_model": "llama3.2",        # General purpose LLM
    "code_model": "qwen2.5-coder",      # Code generation LLM
    "ollama_url": "http://127.0.0.1:11434"  # Ollama server URL
}
```

### Safety Rules
```python
SAFETY_RULES = {
    "forbidden": [
        "rm -rf",
        "dd if=/dev/zero",
        "format c:",
        # ... dangerous patterns
    ],
    "requires_confirmation": [
        "sudo",
        "kill",
        "reboot",
        # ... requires user approval
    ]
}
```

### Execution Parameters
```python
EXECUTION_CONFIG = {
    "approval_required": True,
    "timeout_seconds": 30,
    "max_retries": 3,
    "retry_delay": 2
}
```

### Tool Registry
```python
TOOL_REGISTRY = {
    "run_command": {
        "platform": "cli",
        "handler": "executor.cli"
    },
    "click_button": {
        "platform": "gui",
        "handler": "executor.ui"
    },
    # ... all available tools defined here
}
```

## 🔑 Key Features

- ✅ Centralized settings management
- ✅ No module dependencies
- ✅ Safe defaults for all parameters

## 📚 Usage

### Import Configuration
```python
from config import LLM_CONFIG, SAFETY_RULES, TOOL_REGISTRY

# Access settings
ollama_url = LLM_CONFIG["ollama_url"]
general_model = LLM_CONFIG["general_model"]
forbidden_patterns = SAFETY_RULES["forbidden"]
```

### Access Tool Registry
```python
from config import TOOL_REGISTRY

# Get tool definition
tool = TOOL_REGISTRY.get("run_command")
if tool:
    platform = tool["platform"]
    handler = tool["handler"]
```

### Check Safety Rules
```python
from config import SAFETY_RULES

def is_dangerous(command: str) -> bool:
    for pattern in SAFETY_RULES["forbidden"]:
        if pattern in command:
            return True
    return False
```

## 🔧 Configuration Files

All configuration is defined directly in `settings.py` as Python dictionaries.

## 🚀 Best Practices

1. **Never hardcode values** - Always use config module
2. **No module imports** - Config never imports other modules
3. **Documentation** - Each setting documented with purpose
4. **Safe defaults** - Sensible defaults for all parameters

## 📋 Settings Validation

All configuration is validated when the module loads:
- Required keys are present
- Values have correct types
- URLs are properly formatted
- Numeric values are in valid ranges

Invalid configuration will raise `ValueError` with clear error messages.

## 🔐 Security

- No sensitive data (passwords, tokens) hardcoded
- Safety patterns defined for dangerous operations
- Approval workflow configuration available
- Timeout protection configured

## 📝 Adding New Settings

To add new configuration:

1. Add to `settings.py` dictionary
2. Document purpose and valid values
3. Add type hints
4. Add validation logic
5. Export in `__init__.py`
6. Update this README

Example:
```python
NEW_CONFIG = {
    "setting_name": value,
    "another_setting": value,
    # ...
}
```

## ✨ Highlights

- **Centralized** - Single configuration source
- **Flexible** - Environment variable overrides
- **Safe** - Built-in validation
- **Clear** - Well-documented settings
- **Type-safe** - Full type hints
- **No dependencies** - Config module imports nothing else

---

**Status: 🚀 Ready for integration with other modules**
