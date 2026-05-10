# 🎭 Caelestia Shell Integration Guide

How to integrate Caelestia shell commands into the AI system for comprehensive OS control.

---

## 📚 Files Created

1. **CAELESTIA_COMMAND_REFERENCE.md** - Complete command reference
2. **caelestia.py** - Python API wrapper
3. **caelestia_examples.py** - Usage examples
4. **CAELESTIA_INTEGRATION_GUIDE.md** - This file

---

## 🚀 Quick Start

### Basic Usage

```python
from tools.caelestia import CaelestiaShell

shell = CaelestiaShell()

# Clear notifications
shell.clear_notifications()

# Set wallpaper
shell.set_wallpaper("/path/to/image.jpg")

# Send notification
shell.send_toast("Title", "Message", icon="emblem-ok")

# Control media
shell.pause_media()
shell.next_track()

# Manage system
shell.enable_game_mode()
shell.lock_screen()
```

---

## 🔧 Integration Points

### 1. **executor/ Module**

Use for executing system control actions:

```python
# executor/executor.py

from tools.caelestia import CaelestiaShell, ToastType

class SystemActionExecutor:
    def __init__(self):
        self.shell = CaelestiaShell()

    def execute_action(self, action: str, params: dict) -> Response:
        """Execute system control actions"""
        
        if action == "clear_notifications":
            return self._clear_notifications()
        elif action == "set_wallpaper":
            return self._set_wallpaper(params)
        elif action == "lock_screen":
            return self._lock_screen()
        elif action == "game_mode":
            return self._manage_game_mode(params)
```

### 2. **brain/ Module**

Use for decision-making about system state:

```python
# brain/brain.py

from tools.caelestia import CaelestiaShell

class IntentAnalyzer:
    def __init__(self):
        self.shell = CaelestiaShell()

    def analyze_user_intent(self, user_input: str) -> dict:
        """Analyze intent and recommend actions"""
        
        # Use system status to inform decisions
        if "focus" in user_input:
            dnd_enabled = self.shell.is_dnd_enabled()
            brightness = self.shell.get_brightness()
            
            return {
                "intent": "focus",
                "current_state": {
                    "dnd": dnd_enabled,
                    "brightness": brightness
                },
                "recommended_actions": [
                    "clear_notifications",
                    "enable_dnd",
                    "adjust_brightness"
                ]
            }
```

### 3. **memory/ Module**

Track system state changes:

```python
# memory/memory.py

from tools.caelestia import CaelestiaShell
import json

class StateLogger:
    def __init__(self):
        self.shell = CaelestiaShell()

    def log_system_state(self) -> None:
        """Log current system state"""
        
        state = {
            "timestamp": datetime.now().isoformat(),
            "notifications": {
                "dnd_enabled": self.shell.is_dnd_enabled(),
            },
            "display": {
                "brightness": self.shell.get_brightness(),
                "wallpaper": self.shell.get_wallpaper(),
            },
            "media": {
                "active_player": self.shell.get_active_player(),
            },
            "system": {
                "game_mode": self.shell.is_game_mode_enabled(),
                "screen_locked": self.shell.is_screen_locked(),
            }
        }
        
        # Save to memory
        self.save_state_log(state)
```

### 4. **tools/ Module**

Create tool definitions for AI use:

```python
# tools/definitions.py

CAELESTIA_TOOLS = {
    "clear_notifications": {
        "description": "Clear all system notifications",
        "function": "tools.caelestia.clear_notifications",
        "params": {}
    },
    "set_wallpaper": {
        "description": "Set desktop wallpaper",
        "function": "tools.caelestia.set_wallpaper",
        "params": {
            "path": {"type": "string", "description": "Path to image file"},
            "smart_scheme": {"type": "boolean", "description": "Auto-adjust colors"}
        }
    },
    "lock_screen": {
        "description": "Lock the screen",
        "function": "tools.caelestia.lock_screen",
        "params": {}
    },
    "enable_focus_mode": {
        "description": "Enable focus mode (DND, clear notifs)",
        "function": "tools.caelestia.enable_focus_mode",
        "params": {}
    },
    # ... more tools
}
```

### 5. **router/ Module**

Route Caelestia actions through message system:

```python
# router/router.py

from tools.caelestia import CaelestiaShell
from router.message import Message, Response

def route_caelestia_action(message: Message) -> Response:
    """Route Caelestia control messages"""
    
    shell = CaelestiaShell()
    action = message.data.get("action")
    params = message.data.get("params", {})
    
    actions = {
        "clear_notifications": lambda: shell.clear_notifications(),
        "toggle_dnd": lambda: shell.toggle_dnd(),
        "set_wallpaper": lambda: shell.set_wallpaper(params["path"]),
        "set_brightness": lambda: shell.set_brightness(params["level"]),
        "lock_screen": lambda: shell.lock_screen(),
        "enable_game_mode": lambda: shell.enable_game_mode(),
        "send_toast": lambda: shell.send_toast(
            params["title"],
            params["message"],
            icon=params.get("icon")
        ),
    }
    
    if action in actions:
        try:
            result = actions[action]()
            return Response(success=True, data={"result": result})
        except Exception as e:
            return Response(success=False, error=str(e))
    
    return Response(success=False, error=f"Unknown action: {action}")
```

---

## 🎯 Common Workflows

### Workflow 1: Focus Mode
```python
def enable_focus_mode():
    shell = CaelestiaShell()
    
    # Clear notifications
    shell.clear_notifications()
    
    # Enable DND
    shell.enable_dnd()
    
    # Reduce distractions
    shell.send_toast(
        "Focus Mode Activated",
        "All notifications disabled",
        icon="emblem-ok"
    )
```

### Workflow 2: Night Mode
```python
def enable_night_mode():
    shell = CaelestiaShell()
    
    # Set dark wallpaper
    shell.set_random_wallpaper(
        "~/Pictures/Wallpapers/Dark",
        smart_scheme=True
    )
    
    # Reduce brightness
    shell.set_brightness(20)
    
    # Enable DND
    shell.enable_dnd()
    
    # Notify user
    shell.send_toast(
        "Night Mode",
        "Wallpaper changed, brightness reduced",
        icon="weather-clear-night"
    )
```

### Workflow 3: Gaming Mode
```python
def enable_gaming_mode():
    shell = CaelestiaShell()
    
    # Enable game mode (auto-disables notifs)
    shell.enable_game_mode()
    
    # Prevent sleep
    shell.enable_idle_inhibitor()
    
    # Max brightness
    shell.set_brightness(100)
    
    # Pause background music
    shell.pause_media()
    
    # Notify
    shell.send_toast(
        "Gaming Mode",
        "System optimized",
        icon="application-games"
    )
```

### Workflow 4: Status Check
```python
def get_system_status():
    shell = CaelestiaShell()
    
    return {
        "notifications": {
            "dnd": shell.is_dnd_enabled(),
        },
        "display": {
            "brightness": shell.get_brightness(),
            "wallpaper": shell.get_wallpaper(),
        },
        "media": {
            "active_player": shell.get_active_player(),
            "players": shell.list_players(),
        },
        "system": {
            "game_mode": shell.is_game_mode_enabled(),
            "idle_inhibitor": shell.is_idle_inhibitor_enabled(),
            "screen_locked": shell.is_screen_locked(),
        }
    }
```

---

## 📊 Command Categories

| Category | Commands | Purpose |
|----------|----------|---------|
| **Notifications** | clear, toggle_dnd, send_toast | Notification management |
| **Display** | wallpaper, brightness, scheme | Screen control |
| **Media** | play, pause, next, previous | Media playback |
| **System** | game_mode, idle_inhibitor, lock | System modes |
| **Capture** | screenshot, record | Screen capture |
| **Window** | resize, toggle_workspace | Window management |
| **Utility** | clipboard, emoji_picker, color_picker | Utilities |

---

## 🔌 API Reference

### CaelestiaShell Class

#### Initialization
```python
shell = CaelestiaShell(timeout=5)
```

#### Notification Methods
```python
shell.clear_notifications() -> bool
shell.toggle_dnd() -> bool
shell.enable_dnd() -> bool
shell.disable_dnd() -> bool
shell.is_dnd_enabled() -> bool
shell.send_toast(title, message, toast_type, icon) -> bool
```

#### Display Methods
```python
shell.set_wallpaper(path, smart_scheme=True) -> bool
shell.set_random_wallpaper(directory, smart_scheme=True, threshold=0) -> bool
shell.get_wallpaper() -> Optional[str]
shell.set_brightness(value: int) -> bool
shell.get_brightness() -> Optional[float]
```

#### Media Methods
```python
shell.play_media() -> bool
shell.pause_media() -> bool
shell.toggle_media() -> bool
shell.next_track() -> bool
shell.previous_track() -> bool
shell.get_active_player() -> Optional[str]
shell.list_players() -> List[str]
```

#### System Methods
```python
shell.enable_game_mode() -> bool
shell.disable_game_mode() -> bool
shell.is_game_mode_enabled() -> bool
shell.lock_screen() -> bool
shell.unlock_screen() -> bool
shell.is_screen_locked() -> bool
```

#### Utility Methods
```python
shell.screenshot(region=False, freeze=False) -> bool
shell.start_recording(region=False, audio=False) -> bool
shell.open_clipboard_manager() -> bool
shell.open_emoji_picker() -> bool
shell.toggle_special_workspace() -> bool
```

---

## ⚙️ Configuration

### Shell Timeout
```python
# Custom timeout
shell = CaelestiaShell(timeout=10)
```

### Error Handling
```python
try:
    shell.set_wallpaper("/path/to/image.jpg")
except RuntimeError as e:
    print(f"Failed to set wallpaper: {e}")
```

### Graceful Degradation
```python
# All methods return bool or None on failure
brightness = shell.get_brightness()
if brightness is None:
    # Handle failure gracefully
    brightness = 50  # Default
```

---

## 🧪 Testing

### Unit Tests
```python
# tests/test_caelestia.py

import pytest
from tools.caelestia import CaelestiaShell

def test_clear_notifications():
    shell = CaelestiaShell()
    assert shell.clear_notifications() == True

def test_dnd_toggle():
    shell = CaelestiaShell()
    initial = shell.is_dnd_enabled()
    shell.toggle_dnd()
    assert shell.is_dnd_enabled() != initial

def test_brightness_control():
    shell = CaelestiaShell()
    shell.set_brightness(50)
    brightness = shell.get_brightness()
    assert brightness is not None
    assert 40 <= brightness <= 60
```

---

## 📝 Best Practices

1. **Always use try-except** for error handling
2. **Check return values** before proceeding
3. **Use appropriate icons** for toast notifications
4. **Batch operations** when possible
5. **Respect user settings** (don't force changes)
6. **Log important actions** to memory module
7. **Test on actual system** before deploying

---

## 🔐 Security Notes

1. **Lock screen** on sensitive operations
2. **Respect DND mode** user preferences
3. **Don't enable game mode** without user consent
4. **Validate file paths** before setting wallpaper
5. **Log all system control** actions
6. **Gracefully handle** missing Caelestia installation

---

## 📞 Troubleshooting

### Shell Not Responding
```python
try:
    shell = CaelestiaShell()
except RuntimeError:
    # Start shell manually
    subprocess.run(["caelestia", "shell", "-d"])
```

### Command Timeout
```python
# Increase timeout for slow systems
shell = CaelestiaShell(timeout=10)
```

### Permission Denied
```bash
# Ensure caelestia is in PATH
which caelestia

# Or add to system PATH
export PATH="$PATH:/usr/bin"
```

---

## 🚀 Future Enhancements

1. **Event callbacks** for state changes
2. **Gesture integration** with mouse gestures
3. **Schedule-based** automation (time-based modes)
4. **Workspace groups** management
5. **Custom notifications** with actions
6. **Performance profiling** for slow operations
7. **Batch command** execution for efficiency

---

**Created**: 2026-05-06
**Status**: Complete and tested
**Integration**: Ready for production use
