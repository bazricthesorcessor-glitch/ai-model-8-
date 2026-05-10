# 🎯 Hyprland & Caelestia Configuration Analysis

## System Overview

**Actual Configuration Structure (NOT what we created, but what EXISTS):**

```
User System:
├── ~/.config/hypr/                    # User-editable Hyprland config
│   ├── hyprland.conf                  # MAIN entry point (sources everything)
│   ├── variables.conf                 # User variables (gaps, colors, keybinds)
│   ├── monitors.conf                  # (empty - auto-detected)
│   ├── workspaces.conf                # (empty - dynamic)
│   ├── hyprland/                      # Modular configs
│   │   ├── animations.conf
│   │   ├── decoration.conf
│   │   ├── env.conf
│   │   ├── execs.conf
│   │   ├── general.conf
│   │   ├── gestures.conf              # Gesture mappings
│   │   ├── group.conf                 # Window grouping
│   │   ├── input.conf
│   │   ├── keybinds.conf              # User keybinds (8700+ lines!)
│   │   ├── misc.conf
│   │   └── rules.conf
│   ├── scripts/                       # Custom scripts
│   │   └── change-wallpaper.fish
│   └── scheme/                        # Color schemes
│
├── ~/.config/caelestia/               # Caelestia shell config
│   ├── shell.json                     # MAIN shell config (1985 lines!)
│   ├── hypr-user.conf                 # NVIDIA + stability fixes
│   ├── hypr-vars.conf                 # Generated user vars
│   └── hypr-user.conf.save            # Backup
│
└── ~/.local/share/caelestia/hypr/     # Core Caelestia Hyprland configs
    ├── variables.conf                 # Base variables
    ├── hyprland/
    │   ├── animations.conf
    │   ├── decoration.conf
    │   ├── env.conf
    │   ├── execs.conf
    │   ├── general.conf
    │   ├── gestures.conf
    │   ├── group.conf
    │   ├── input.conf
    │   ├── keybinds.conf              # Core keybinds
    │   ├── misc.conf
    │   └── rules.conf
    ├── scheme/
    │   └── default.conf               # Copied to ~/.config/hypr/scheme/current.conf
```

---

## 📋 Configuration Layer Stack

### Layer 1: Core Caelestia (Immutable)
**Location**: `~/.local/share/caelestia/hypr/`
- Foundation configs provided by Caelestia
- Not meant to be edited directly
- Sourced first by hyprland.conf
- Provides: animations, decoration, general behavior, keybinds, gestures

### Layer 2: User Variables
**Location**: `~/.config/hypr/variables.conf`
- **Modifiable by user**
- Controls visual/functional behavior
- Example variables:
  ```conf
  $terminal = foot
  $browser = firefox
  $editor = code
  
  # Window styling
  $windowOpacity = 0.8
  $windowRounding = 10
  $windowBorderSize = 3
  $activeWindowBorderColour = 0xffbd93f9    # Neon Purple
  $inactiveWindowBorderColour = 0xff44475a  # Dark Grey
  
  # Gaps
  $workspaceGaps = 20
  $windowGapsIn = 10
  $windowGapsOut = 40
  
  # Keybind definitions
  $kbMoveWinToWs = Super+Alt
  $kbGoToWs = Super
  $kbCloseWindow = Super, Q
  $kbTerminal = Super, T
  ```

### Layer 3: User Overrides (Last sourced = highest priority)
**Location**: `~/.config/hypr/hyprland/keybinds.conf` and `~/.config/hypr-user.conf`
- **Modifiable by user**
- Overrides core Caelestia configs
- NVIDIA-specific fixes in hypr-user.conf:
  ```conf
  env = GBM_BACKEND,nvidia-drm
  env = __GLX_VENDOR_LIBRARY_NAME,nvidia
  env = LIBVA_DRIVER_NAME,nvidia
  env = WLR_NO_HARDWARE_CURSORS,1
  ```

---

## 🎛️ Key Configuration Files

### 1. Main Entry Point: `hyprland.conf`
**What it does:**
- Sources core paths ($hypr, $conf, $caelestia)
- Copies color scheme: Caelestia → current config
- Sources all sub-configs in order:
  1. Caelestia core configs
  2. Scheme/colors
  3. User variables
  4. Caelestia modular configs
  5. Monitor detection
  6. User overrides (LAST = highest priority)

**Flow:**
```
hyprland.conf
  ├─ sources $caelestia/variables.conf
  ├─ copies scheme to current.conf
  ├─ sources current.conf (colors)
  ├─ sources hypr-vars.conf (user vars)
  ├─ sources $caelestia/hyprland/*.conf (core)
  ├─ sources hyprland/keybinds.conf (user overrides)
  └─ sources hypr-user.conf (nvidia fixes + last overrides)
```

### 2. Shell Configuration: `~/.config/caelestia/shell.json`

**What it does:**
- Configures the Caelestia shell UI (NOT Hyprland directly)
- 1985 lines of JSON controlling:
  - **appearance**: Fonts, rounding, spacing, animations
  - **general**: Default apps, idle/battery settings
  - **bar**: Taskbar/panel configuration
  - **dashboard**: System info display
  - **launcher**: Application launcher settings
  - **gestures**: Gesture recognition mappings
  - **services**: Weather, audio, media players

**Example:**
```json
{
  "appearance": {
    "rounding": {"scale": 1.011679914277939},
    "transparency": {
      "enabled": true,
      "base": 0.5997511112119013,
      "layers": 0.3990016101233671
    }
  },
  "general": {
    "apps": {
      "terminal": ["foot"],
      "audio": ["pavucontrol"],
      "explorer": ["dolphin"]
    },
    "idle": {
      "lockBeforeSleep": true,
      "timeouts": [
        {"idleAction": "lock", "timeout": 180},
        {"idleAction": "dpms off", "timeout": 300},
        {"idleAction": ["systemctl", "suspend-then-hibernate"], "timeout": 600}
      ]
    }
  },
  "bar": {
    "persistent": false,
    "showOnHover": true,
    "workspaces": {"shown": 5, "perMonitorWorkspaces": true}
  },
  "paths": {
    "wallpaperDir": "/home/dmannu/Pictures/Wallpapers",
    "sessionGif": "/home/dmannu/shell/assets/7.gif"
  }
}
```

### 3. Keybinds: `~/.config/hypr/hyprland/keybinds.conf`

**What it does:**
- Defines ALL keyboard shortcuts for Hyprland
- 8700+ lines of keybindings
- Uses variables from variables.conf:
  ```conf
  $kbGoToWs = Super        # Go to workspace
  $kbMoveWinToWs = Super+Alt  # Move window to workspace
  $kbCloseWindow = Super, Q
  $kbToggleGroup = Super, Comma
  $kbWindowPip = Super+Alt, Backslash
  ```

**Keybind Examples:**
```conf
# Workspace navigation (using variables)
bind = $kbGoToWs, 1, exec, $wsaction workspace 1
bind = $kbGoToWs, 2, exec, $wsaction workspace 2
bind = $kbGoToWs, 3, exec, $wsaction workspace 3

# Window operations
bind = $kbCloseWindow, global, killactive
bind = $kbToggleGroup, global, togglegroup
bind = $kbWindowFullscreen, global, fullscreen, 0

# Special workspaces
bind = $kbToggleSpecialWs, exec, caelestia toggle specialws

# Shell integration
bindi = Super, Super_L, global, caelestia:launcher
bind = $kbSession, global, caelestia:session
bind = $kbLock, global, caelestia:lock
```

### 4. Gestures: `~/.config/hypr/hyprland/gestures.conf`

**What it does:**
- Defines multitouch gesture recognition
- Maps gestures to Hyprland actions

**Gesture Configuration:**
```conf
gestures {
    workspace_swipe_distance = 700
    workspace_swipe_cancel_ratio = 0.15
    workspace_swipe_min_speed_to_force = 5
    workspace_swipe_direction_lock = true
}

# Gesture mappings
gesture = 4, horizontal, workspace       # 4 fingers horizontal = switch workspace
gesture = 3, up, special, special        # 3 fingers up = toggle special workspace
gesture = 3, down, dispatcher, exec, caelestia toggle specialws
gesture = 4, down, dispatcher, exec, systemctl suspend-then-hibernate
```

### 5. Variables: `~/.config/hypr/variables.conf`

**What it does:**
- Central place for all configuration variables
- Visual settings: colors, gaps, borders, opacity
- Application defaults: terminal, browser, editor
- Keybind variable definitions
- Gesture finger configuration

**Variables:**
```conf
# Apps
$terminal = foot
$browser = firefox
$editor = code
$fileExplorer = dolphin

# Window styling
$windowOpacity = 0.8
$windowRounding = 10
$windowBorderSize = 3
$activeWindowBorderColour = 0xffbd93f9
$inactiveWindowBorderColour = 0xff44475a

# Gaps
$workspaceGaps = 20
$windowGapsIn = 10
$windowGapsOut = 40
$singleWindowGapsOut = 1

# Keybinds
$kbMoveWinToWs = Super+Alt
$kbGoToWs = Super
$kbNextWs = Ctrl+Super, right
$kbPrevWs = Ctrl+Super, left
```

---

## 🔄 Configuration Flow & Priority

```
hyprland.conf (sourced first)
    ↓
$caelestia/variables.conf (base)
    ↓
$caelestia/scheme/current.conf (colors)
    ↓
~/.config/hypr/hypr-vars.conf (system generated)
    ↓
$caelestia/hyprland/*.conf (core Caelestia configs)
    ↓
~/.config/hypr/variables.conf (USER EDITS HERE! overrides base)
    ↓
~/.config/hypr/hyprland/keybinds.conf (USER KEYBINDS)
    ↓
~/.config/hypr/hyprland/*.conf (other modular configs)
    ↓
~/.config/hypr/hypr-user.conf (FINAL overrides - NVIDIA fixes)
    ↓
hyprctl reload (apply changes)
```

**Key**: Files sourced LATER override earlier ones!

---

## 🎮 How to Make Changes

### Change Keybinds
**Edit**: `~/.config/hypr/hyprland/keybinds.conf`
```conf
# Add custom keybind
bind = Super+Shift, V, exec, vim

# Override existing
bind = Super, Q, exec, your_custom_close_command
```

### Change Variables (Colors, Gaps, etc)
**Edit**: `~/.config/hypr/variables.conf`
```conf
$windowRounding = 15              # Increase rounding
$windowGapsIn = 15                # Increase inner gaps
$activeWindowBorderColour = 0xff00ff00  # Green border
```

### Change Shell Appearance
**Edit**: `~/.config/caelestia/shell.json`
```json
{
  "appearance": {
    "rounding": {"scale": 1.2},
    "transparency": {"enabled": true, "base": 0.7}
  }
}
```

### Apply Changes
```bash
# Reload Hyprland
hyprctl reload

# Or via OS module
from os import HyprlandManager
hyprland = HyprlandManager()
hyprland.reload_config()
```

---

## 🎯 Important Paths for OS Module Integration

### Configuration Access Points:
```python
OS_CONFIG = {
    # User-editable configs
    "user_hyprland_config": "~/.config/hypr/hyprland.conf",
    "user_variables": "~/.config/hypr/variables.conf",
    "user_keybinds": "~/.config/hypr/hyprland/keybinds.conf",
    "user_overrides": "~/.config/hypr/hypr-user.conf",
    
    # Shell config
    "shell_config": "~/.config/caelestia/shell.json",
    
    # Core Caelestia (read-only reference)
    "caelestia_base": "~/.local/share/caelestia/hypr/",
}
```

### What the OS Module Should Do:

1. **Read** variables.conf → understand current settings
2. **Modify** variables.conf → change colors, gaps, keybinds
3. **Add** to keybinds.conf → register custom shortcuts
4. **Read** shell.json → understand gestures
5. **Modify** shell.json → change gesture mappings
6. **Execute** `hyprctl reload` → apply changes
7. **Query** `hyprctl` → get current state

---

## 📊 Configuration Statistics

| Aspect | File | Lines | Modifiable |
|--------|------|-------|------------|
| Main Config | hyprland.conf | 76 | No (sources others) |
| Variables | variables.conf | 96 | ✅ YES |
| Keybinds | keybinds.conf | 8700+ | ✅ YES |
| Gestures | gestures.conf | 14 | ✅ YES |
| Shell | shell.json | 1985 | ✅ YES |
| Core Caelestia | ~/.local/share/caelestia/ | N/A | NO (system files) |

---

## 🎓 Key Insights

1. **Two separate systems**:
   - **Hyprland**: Window manager (keybinds, workspaces, windows)
   - **Caelestia**: Shell/UI (bar, launcher, gestures, appearance)

2. **Two config locations**:
   - `~/.config/hypr/` - User-editable Hyprland configs
   - `~/.config/caelestia/` - User-editable Caelestia shell config

3. **Configuration layers**:
   - Immutable: Caelestia base (`~/.local/share/`)
   - User overrideable: Everything in `~/.config/`

4. **Hot reload**:
   - Changes applied via `hyprctl reload`
   - No restart needed

5. **Priority order**:
   - Last sourced file wins
   - User configs override Caelestia base

---

## 🔗 Integration Points for AI Module

```python
# Read current config
variables = parse_config("~/.config/hypr/variables.conf")
keybinds = parse_config("~/.config/hypr/hyprland/keybinds.conf")
shell_config = load_json("~/.config/caelestia/shell.json")

# Modify config
variables["$windowGapsIn"] = 15
add_keybind("Super+Shift+V", "exec, vim")
shell_config["appearance"]["rounding"]["scale"] = 1.2

# Apply changes
write_config("~/.config/hypr/variables.conf", variables)
write_config("~/.config/hypr/hyprland/keybinds.conf", keybinds)
save_json("~/.config/caelestia/shell.json", shell_config)
execute("hyprctl reload")
```

---

**This is the actual goldmine for OS manipulation! 🎯**
