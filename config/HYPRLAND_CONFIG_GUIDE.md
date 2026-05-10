# Hyprland & Caelestia Configuration Guide

## 🎯 Overview

All Hyprland and Caelestia shell configuration is centralized in two main locations:
- **Hyprland configs**: `/home/.config/hypr/` - Core window manager configuration
- **Caelestia shell**: `/home/.config/.caelestia/shell.json` - Shell and gesture configuration

These are the "goldmines" for OS manipulation and desktop automation.

## 📁 Configuration Structure

### Hyprland Configuration Directory
```
~/.config/hypr/
├── hyprland.conf          # Main Hyprland configuration
├── binds.conf            # Keyboard bindings
├── monitors.conf         # Monitor/display setup
├── workspaces.conf       # Workspace configuration
├── animations.conf       # Animation settings
├── keybinds.conf        # Keybinding definitions
└── [other configs]      # Additional configs
```

### Caelestia Shell Configuration
```
~/.config/.caelestia/
└── shell.json            # Caelestia shell configuration
                          # Contains:
                          # - Gesture mappings
                          # - Keyboard shortcuts
                          # - Window management settings
                          # - Workspace configuration
```

## 🔑 Key Configuration Files

### 1. Hyprland Configuration (`~/.config/hypr/hyprland.conf`)

Main window manager configuration. Controls:
- Monitor setup and resolution
- Workspace layout
- Default applications
- Visual settings (gaps, borders, animations)
- Input devices
- General behavior

Example:
```conf
# Monitor configuration
monitor=HDMI-1,1920x1200@60,0x0,1

# Workspace setup
workspace=1,monitor:HDMI-1
workspace=2,monitor:HDMI-1

# General settings
general {
    gaps_in = 10
    gaps_out = 20
    border_size = 2
}

# Decoration/visual
decoration {
    rounding = 10
    shadow_ignore_window = true
}
```

### 2. Keyboard Bindings (`~/.config/hypr/binds.conf` or `keybinds.conf`)

Custom keyboard shortcuts:
```conf
$mainMod = SUPER

bind = $mainMod, Q, killactive
bind = $mainMod, F, fullscreen, 0
bind = $mainMod, Space, togglefloating
bind = $mainMod, 1, workspace, 1
bind = $mainMod, H, splitratio, -0.1
```

### 3. Caelestia Shell Configuration (`~/.config/.caelestia/shell.json`)

Shell-level automation and gesture configuration:
```json
{
  "gestures": {
    "swipe_up": "maximize_window",
    "swipe_down": "minimize_window",
    "swipe_left": "prev_workspace",
    "swipe_right": "next_workspace"
  },
  "keyboard": {
    "super+q": "close_window",
    "super+f": "toggle_fullscreen"
  },
  "window_management": {
    "layout": "master-slave",
    "gaps": 10
  }
}
```

## 🔗 Integration with OS Module

The OS module reads and manipulates these configurations:

### HyprlandManager
```python
from os import HyprlandManager

hyprland = HyprlandManager()

# Executes commands via hyprctl
# Reads from ~/.config/hypr/
# Manages workspaces, windows, monitors
```

### KeyboardShortcutHandler
```python
from os import KeyboardShortcutHandler

shortcuts = KeyboardShortcutHandler()

# Generates Hyprland config bindings
# Reads from shell.json
# Creates hyprland.conf entries
```

### MouseGestureRecognizer
```python
from os import MouseGestureRecognizer

recognizer = MouseGestureRecognizer()

# Recognizes Celestial dot patterns
# Maps to actions in shell.json
# Celestial dot patterns: swipe/circle gestures
```

### WindowManager & SplitManager
```python
from os import WindowManager, SplitManager

windows = WindowManager(hyprland)
splits = SplitManager(hyprland)

# Uses Hyprland config for layout settings
# Applies gap and ratio settings
# Manages splits based on ~/.config/hypr/ settings
```

## 📝 Configuration Priority

1. **shell.json** - High-level Caelestia configuration
2. **hyprland.conf** - Core window manager config
3. **Specific conf files** - monitors.conf, binds.conf, etc.
4. **Runtime changes** - Via hyprctl commands

Changes to config files take effect on Hyprland reload:
```bash
hyprctl reload
```

Or programmatically:
```python
hyprland.reload_config()
```

## 🚀 Common Configuration Tasks

### Add Custom Keyboard Shortcut

1. Edit `~/.config/hypr/keybinds.conf`:
```conf
bind = $mainMod SHIFT, V, exec, vim
```

2. Or update via KeyboardShortcutHandler:
```python
shortcuts.register_shortcut("super+shift+v", "open_vim", "Open Vim")
```

3. Reload Hyprland:
```bash
hyprctl reload
```

### Configure Gesture Mapping

1. Edit `~/.config/.caelestia/shell.json`:
```json
{
  "gestures": {
    "swipe_up": "my_custom_action"
  }
}
```

2. Or programmatically:
```python
recognizer.register_gesture_handler(
    GestureType.SWIPE_UP,
    lambda gesture: hyprland.dispatch("workspace 1")
)
```

### Adjust Window Layout

1. Edit `~/.config/hypr/hyprland.conf`:
```conf
general {
    gaps_in = 15
    gaps_out = 25
    border_size = 3
}
```

2. Or programmatically:
```python
splits.increase_gaps(5)
splits.set_master_ratio(0.65)
```

## 🔍 Configuration Discovery

List current Hyprland config:
```bash
# View active Hyprland configuration
hyprctl instances

# View workspace layout
hyprctl workspaces

# View monitor setup
hyprctl monitors

# View all bindings
hyprctl binds
```

Programmatically:
```python
status = hyprland.get_status()
monitors = hyprland.get_monitors()
workspaces = hyprland.get_workspaces()
```

## 💾 Backup Configurations

Always backup before major changes:
```bash
cp -r ~/.config/hypr ~/.config/hypr.backup
cp ~/.config/.caelestia/shell.json ~/.config/.caelestia/shell.json.backup
```

## 🔐 Best Practices

1. **Edit via files first** - More reliable than runtime commands
2. **Always backup** - Before making changes
3. **Reload after changes** - `hyprctl reload`
4. **Test changes** - Verify before deploying
5. **Document custom configs** - Note what you changed and why
6. **Keep configs in sync** - shell.json matches hyprland.conf

## 📚 References

- **Hyprland Wiki**: https://wiki.hyprland.org
- **Hyprland Config**: https://wiki.hyprland.org/Configuring/
- **Binds Documentation**: https://wiki.hyprland.org/Configuring/Binds/
- **Window Management**: https://wiki.hyprland.org/Configuring/Window-Rules/

---

**These configuration locations are critical for all OS manipulation and desktop automation.**
