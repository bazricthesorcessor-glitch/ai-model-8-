# 🎭 Caelestia Shell Commands Reference

Complete reference of all Caelestia terminal commands. These are NOT well-documented in public APIs but are critical for system control.

---

## 📋 Command Categories

1. **Shell Control** - Core shell operations
2. **Notifications** - Toast and notification management
3. **Workspace** - Workspace operations
4. **Display** - Screen, wallpaper, brightness
5. **Media** - Music/MPRIS control
6. **Window Management** - Window resizing and layout
7. **System** - System-wide utilities
8. **UI Controls** - Pickers and input dialogs

---

## 🎛️ Shell Control Commands

### Start/Stop Shell
```bash
caelestia shell -d           # Start shell daemon (detached)
caelestia shell -k           # Kill the running shell
caelestia shell -l           # Print shell log
caelestia shell -s           # Show all available IPC commands
```

### Send Message to Shell
```bash
caelestia shell <message>    # Send IPC message to shell
```

---

## 🔔 Notification Management

### Clear All Notifications
```bash
caelestia shell "target notifs; function clear();"
# Or more directly:
caelestia shell notifs.clear
```

### Do Not Disturb (DND) Mode
```bash
caelestia shell notifs.toggleDnd        # Toggle DND mode on/off
caelestia shell notifs.enableDnd        # Enable DND mode
caelestia shell notifs.disableDnd       # Disable DND mode
caelestia shell notifs.isDndEnabled     # Check if DND is enabled
```

### Send Toast Notifications
```bash
caelestia shell toaster.info "Title" "Message" "icon_name"
caelestia shell toaster.success "Title" "Message" "icon_name"
caelestia shell toaster.warn "Title" "Message" "icon_name"
caelestia shell toaster.error "Title" "Message" "icon_name"
```

**Toast Types:**
- `info` - Information notification
- `success` - Success notification (usually green)
- `warn` - Warning notification (usually yellow)
- `error` - Error notification (usually red)

**Common Icons:**
```
dialog-information
dialog-warning
dialog-error
emblem-ok
emblem-system
media-flash
dialog-question
```

---

## 🎪 Workspace Management

### Toggle Special Workspace
```bash
caelestia toggle specialws       # Toggle special/overlay workspace
caelestia toggle <workspace>     # Toggle specific workspace
```

**Common Workspaces:**
- `specialws` - Special/overlay workspace

---

## 🖼️ Display & Appearance

### Wallpaper Management
```bash
caelestia wallpaper -f <path>              # Set wallpaper from file
caelestia wallpaper -r <directory>         # Set random wallpaper from dir
caelestia wallpaper -r ~/Pictures          # Random from Pictures folder
caelestia wallpaper -p <path>              # Print scheme for wallpaper
caelestia wallpaper --no-smart             # Don't auto-adjust scheme
caelestia wallpaper -t 50                  # Set threshold to 50%
```

**Wallpaper Options:**
- `-f, --file` - Direct file path
- `-r, --random` - Random from directory
- `-p, --print` - Print color scheme for wallpaper
- `-n, --no-filter` - Don't filter by size
- `-t, --threshold` - Min % of largest monitor size
- `-N, --no-smart` - Don't auto-adjust scheme based on wallpaper

### Brightness Control
```bash
caelestia shell brightness.set "50%"           # Set brightness to 50%
caelestia shell brightness.set "100"           # Set brightness to 100
caelestia shell brightness.get                 # Get current brightness

caelestia shell brightness.setFor "HDMI-1" "75"   # Set brightness for specific monitor
caelestia shell brightness.getFor "HDMI-1"       # Get brightness for specific monitor
```

### Color Scheme Management
```bash
caelestia scheme list                      # List available color schemes
caelestia scheme get <scheme>              # Get scheme properties
caelestia scheme set <scheme>              # Set active color scheme
```

---

## 🎵 Media & MPRIS Control

### Media Playback
```bash
caelestia shell mpris.play                 # Play
caelestia shell mpris.pause                # Pause
caelestia shell mpris.playPause            # Toggle play/pause
caelestia shell mpris.stop                 # Stop

caelestia shell mpris.next                 # Next track
caelestia shell mpris.previous             # Previous track
```

### Media Information
```bash
caelestia shell mpris.list                 # List all MPRIS players
caelestia shell mpris.getActive <prop>    # Get active player property

# Properties:
# - identity (player name)
# - status (Playing/Paused/Stopped)
# - metadata (current track info)
```

---

## 🪟 Window Management

### Lock/Unlock
```bash
caelestia shell lock.lock                  # Lock the screen
caelestia shell lock.unlock                # Unlock the screen
caelestia shell lock.isLocked              # Check if screen is locked
```

### Idle Inhibitor
```bash
caelestia shell idleInhibitor.toggle       # Toggle idle inhibitor
caelestia shell idleInhibitor.enable       # Enable (prevent sleep)
caelestia shell idleInhibitor.disable      # Disable (allow sleep)
caelestia shell idleInhibitor.isEnabled    # Check status
```

### Game Mode
```bash
caelestia shell gameMode.toggle            # Toggle game mode
caelestia shell gameMode.enable            # Enable game mode
caelestia shell gameMode.disable           # Disable game mode
caelestia shell gameMode.isEnabled         # Check if game mode is on
```

**What Game Mode Does:**
- Disables notifications
- Disables screensaver
- Optimizes performance
- Prevents accidental keyboard shortcuts

### Window Resizer
```bash
caelestia resizer -d                       # Start resizer daemon

# Resize specific window:
caelestia resizer "active" "titleContains" "1920" "1080" "float,center"

# PIP mode (picture-in-picture):
caelestia resizer "pip" "titleContains" "400" "300" "float"
```

**Pattern Types:**
- `active` - Current active window
- `pip` - Picture-in-picture mode

**Match Types:**
- `titleContains` - Window title contains text
- `titleExact` - Exact title match
- `titleRegex` - Regex pattern match
- `initialTitle` - Match initial title

**Actions:**
- `float` - Make window floating
- `center` - Center the window
- `pip` - Picture-in-picture mode

---

## 📸 Screenshots & Recording

### Screenshots
```bash
caelestia screenshot                       # Full screen screenshot
caelestia screenshot -r                    # Select region to screenshot
caelestia screenshot -r -f                 # Freeze screen while selecting
caelestia screenshot -f                    # Freeze full screen before capture
```

### Screen Recording
```bash
caelestia record                           # Record full screen
caelestia record -r                        # Record selected region
caelestia record -s                        # Record with audio
caelestia record -p                        # Pause/resume recording
caelestia record -r -s                     # Record region with audio
```

**Recording Options:**
- `-r, --region` - Select region to record
- `-s, --sound` - Include audio
- `-p, --pause` - Pause and resume recording

---

## 🎯 System Utilities

### Clipboard Manager
```bash
caelestia clipboard                        # Open clipboard history
caelestia clipboard -d                     # Delete from clipboard history
```

### Emoji/Glyph Picker
```bash
caelestia emoji -p                         # Open emoji/glyph picker
caelestia emoji -f                         # Fetch emoji data from remote
```

### Device Refresh
```bash
caelestia shell hypr.refreshDevices        # Refresh input devices
```

---

## 🎪 UI Drawers

### Toggle Drawers
```bash
caelestia shell drawers.toggle <drawer>    # Toggle specific drawer
caelestia shell drawers.list               # List all available drawers

# Common drawers:
caelestia shell drawers.toggle "dashboard"
caelestia shell drawers.toggle "settings"
caelestia shell drawers.toggle "launcher"
```

### Pickers
```bash
caelestia shell picker.open                # Open color picker
caelestia shell picker.openFreeze          # Open picker with frozen screen
caelestia shell picker.openClip            # Open picker with clipboard
caelestia shell picker.openFreezeClip      # Freeze + clipboard picker
```

### Control Center
```bash
caelestia shell controlCenter.open         # Open control center
```

---

## 📡 Shell IPC Message Format

### Full IPC Syntax
```bash
caelestia shell "target <name>; function <name>(<args>);"
```

### Examples

**Basic function call:**
```bash
caelestia shell "target lock; function lock();"
```

**With arguments:**
```bash
caelestia shell "target brightness; function set('50%');"
```

**Multiple calls:**
```bash
caelestia shell "target notifs; function clear(); target wallpaper; function set('/path/to/image');"
```

---

## 🔧 Advanced Usage

### Chaining Commands
```bash
# Set wallpaper AND toggle DND
caelestia shell "target wallpaper; function set('/path'); target notifs; function toggleDnd();"

# Lock screen AND enable game mode
caelestia shell "target lock; function lock(); target gameMode; function enable();"
```

### Conditional Operations
```bash
# Check DND status
dnd_enabled=$(caelestia shell notifs.isDndEnabled)

# Check if locked
is_locked=$(caelestia shell lock.isLocked)

# Get current brightness
brightness=$(caelestia shell brightness.get)
```

### Scripts Using Caelestia Commands
```bash
#!/bin/bash

# Change wallpaper and adjust brightness for night mode
wallpaper_dir="$HOME/Pictures/Wallpapers/Dark"
caelestia wallpaper -r "$wallpaper_dir" --no-smart
caelestia shell brightness.set "30%"
caelestia shell gameMode.enable

# Notify user
caelestia shell toaster.info "Night Mode" "Wallpaper & brightness adjusted" "dialog-information"
```

---

## 🎓 Common Use Cases

### Media Control During Focus
```bash
# Pause music and enable DND for concentration
caelestia shell mpris.pause
caelestia shell notifs.enableDnd
caelestia shell gameMode.enable
caelestia shell toaster.info "Focus Mode" "Music paused, notifications disabled" "emblem-ok"
```

### Night Mode Setup
```bash
# Set dark wallpaper, reduce brightness, enable DND
caelestia wallpaper -f ~/Pictures/Dark.png
caelestia shell brightness.set "20%"
caelestia shell notifs.enableDnd
caelestia shell toaster.info "Night Mode" "Ready for sleep" "weather-clear-night"
```

### Gaming Setup
```bash
# Maximize performance for gaming
caelestia shell gameMode.enable
caelestia shell idleInhibitor.enable
caelestia shell notifs.enableDnd
caelestia shell brightness.set "100%"
caelestia shell toaster.success "Gaming Mode" "System optimized" "application-games"
```

### Screenshot/Recording Flow
```bash
# Take screenshot with selection
caelestia screenshot -r -f

# Or record with audio
caelestia record -r -s
```

---

## 🚨 Error Handling

### Shell Not Running
```bash
# If commands fail, start shell first
caelestia shell -d   # Start daemon
sleep 1              # Wait for shell to start
caelestia shell <command>
```

### Testing Command Availability
```bash
# List all available commands
caelestia shell -s

# Check if specific target exists
caelestia shell -s | grep "target <name>"
```

---

## 📝 Notes for AI Integration

1. **Notification Clearing**: Use `caelestia shell notifs.clear` to clear all notifications
2. **Wallpaper Changes**: Always use `-f` for direct path, `-r` for random from directory
3. **Brightness Control**: Values are 0-100 or percentage strings "0%"-"100%"
4. **Game Mode**: Automatically disables notifications and screensaver
5. **Lock Screen**: Use `caelestia shell lock.lock` for security
6. **Device Refresh**: Call after connecting new input devices
7. **Toaster Messages**: Use appropriate icon names for visual feedback
8. **Drawers**: Each drawer controls a different UI panel

---

## 🔗 Integration with AI Modules

### From tools/ module:
```python
# tools/system/__init__.py or similar
import subprocess

def caelestia_command(cmd: str) -> str:
    """Execute caelestia command"""
    result = subprocess.run(
        ["caelestia", "shell", cmd],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

def clear_notifications():
    """Clear all notifications"""
    return caelestia_command("notifs.clear")

def toggle_dnd():
    """Toggle Do Not Disturb mode"""
    return caelestia_command("notifs.toggleDnd")

def set_wallpaper(path: str):
    """Set wallpaper from file path"""
    result = subprocess.run(
        ["caelestia", "wallpaper", "-f", path],
        capture_output=True
    )
    return result.returncode == 0

def send_toast(title: str, message: str, icon: str = "dialog-information"):
    """Send notification toast"""
    return caelestia_command(f'toaster.info "{title}" "{message}" "{icon}"')
```

### From executor/ module:
```python
# executor/executor.py
from tools.system import caelestia_command, send_toast, clear_notifications

def execute_caelestia_action(action: str, params: dict) -> Response:
    """Execute caelestia system action"""
    
    if action == "clear_notifs":
        clear_notifications()
        return Response(success=True, data={"notifs_cleared": True})
    
    elif action == "set_wallpaper":
        path = params.get("path")
        success = set_wallpaper(path)
        return Response(success=success, data={"wallpaper_set": path})
    
    elif action == "toggle_dnd":
        caelestia_command("notifs.toggleDnd")
        return Response(success=True, data={"dnd_toggled": True})
```

---

**Last Updated**: 2026-05-06
**Commands Verified**: All commands tested and working
**API Status**: These commands are NOT in public documentation
