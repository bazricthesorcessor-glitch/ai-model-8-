# OS Module

The `os` package contains desktop and Hyprland integration code. It wraps window management, split operations, keyboard shortcuts, mouse gestures, and environment checks.

## Main files

- `hyprland.py`: Hyprland command wrappers.
- `window_manager.py`: higher-level window actions.
- `split_manager.py`: tiling and split behavior.
- `keyboard_shortcuts.py`, `mouse_gestures.py`: input mapping helpers.
- `os_check.py`, `hyprland_config.sh`, `hyprland_ai_agent.py`: environment and legacy integration scripts.

## Use cases

- move or resize windows
- switch workspaces
- bind desktop actions to shortcuts or gestures
- inspect Hyprland availability and configuration
