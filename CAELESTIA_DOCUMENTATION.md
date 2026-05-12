"""
CAELESTIA UI CONTROL SYSTEM - COMPLETE DOCUMENTATION

This is a comprehensive, modular system for controlling the Caelestia shell from the executor model.
The executor issues simple commands and this system handles all the complexity.

=== ARCHITECTURE ===

1. CaelestiaController (ui/caelestia_controller.py)
   - Master controller for all UI operations
   - Reads shell.json configuration
   - Every feature has a corresponding toggle
   - Returns standardized success/error responses

2. BrowserAutomation (ui/caelestia_controller.py)
   - Keyboard/mouse control via InputController
   - Navigation, clicking, typing, scrolling
   - Form submission, search, page refresh
   - Tab management

3. ExecutorAdapter (ui/caelestia_controller.py)
   - Maps simple commands to controller methods
   - Translates executor requests to actions
   - Command and parameter handling

4. ExecutorCaelestiaInterface (executor/caelestia_integration.py)
   - Direct integration point with executor
   - execute_command() - simple command execution
   - execute_browser_command() - browser automation
   - get_controller_state() - read current state

=== FEATURES ===

BRIGHTNESS CONTROL:
  - increase_brightness() - Increase by increment
  - decrease_brightness() - Decrease by increment
  - set_brightness(level) - Set to specific level (0.0-1.0)
  - toggle_brightness() - Enable/disable control

VOLUME CONTROL:
  - increase_volume() - Increase by increment
  - decrease_volume() - Decrease by increment
  - set_volume(level) - Set to specific level (0.0-1.0)
  - toggle_mute() - Mute/unmute
  - toggle_volume() - Enable/disable control

WINDOW MANAGEMENT:
  - toggle_fullscreen() - Fullscreen toggle
  - toggle_floating() - Floating window toggle
  - close_window() - Close active window
  - maximize_window() - Maximize window
  - minimize_window() - Minimize window
  - set_layout(layout) - Change layout (master-slave, tile, floating)
  - set_master_ratio(ratio) - Set master window ratio
  - increase_gaps() - Increase window gaps
  - decrease_gaps() - Decrease window gaps
  - toggle_window_management() - Enable/disable

SPLIT MANAGEMENT:
  - split_left() - Create left split
  - split_right() - Create right split
  - split_up() - Create up split
  - split_down() - Create down split
  - resize_split(direction, amount) - Resize split
  - toggle_splits() - Enable/disable

WORKSPACE MANAGEMENT:
  - switch_workspace(number) - Switch to workspace N
  - next_workspace() - Next workspace
  - prev_workspace() - Previous workspace
  - toggle_workspaces() - Enable/disable

GESTURE CONTROL:
  - enable_gestures() - Enable gesture recognition
  - disable_gestures() - Disable gesture recognition
  - toggle_gestures() - Toggle on/off
  - set_gesture_mapping(gesture, action) - Map gesture to action

KEYBOARD SHORTCUTS:
  - enable_keyboard() - Enable keyboard shortcuts
  - disable_keyboard() - Disable keyboard shortcuts
  - toggle_keyboard() - Toggle on/off

STATE TOGGLES:
  - toggle_game_mode() - Game mode on/off
  - toggle_dnd_mode() - Do Not Disturb on/off
  - toggle_wifi() - WiFi on/off
  - toggle_bluetooth() - Bluetooth on/off
  - toggle_microphone() - Microphone on/off

BROWSER AUTOMATION:
  - navigate(url) - Open URL
  - click(x, y) - Click at coordinates
  - type_text(text) - Type text
  - scroll(direction, amount) - Scroll page
  - search(term) - Search (Ctrl+F)
  - press_key(key) - Press key
  - submit_form() - Submit form
  - refresh() - Refresh page (F5)
  - go_back() - Go back (Alt+Left)
  - go_forward() - Go forward (Alt+Right)
  - new_tab() - New tab (Ctrl+T)
  - close_tab() - Close tab (Ctrl+W)
  - open_devtools() - Open dev tools (F12)

CONFIGURATION:
  - get_state() - Get current state
  - save_config(path) - Save configuration to file

=== EXECUTOR INTEGRATION EXAMPLES ===

Example 1: Simple brightness command
  interface = ExecutorCaelestiaInterface()
  result = interface.execute_command("increase_brightness")
  # Returns: {"success": True, "action": "set_brightness", "level": 0.9, "percent": 90}

Example 2: Command with parameters
  result = interface.execute_command("set_volume", {"level": 0.5})
  # Returns: {"success": True, "action": "set_volume", "level": 0.5, "percent": 50}

Example 3: Workspace switching
  result = interface.execute_command("switch_workspace", {"number": 2})
  # Returns: {"success": True, "workspace": 2}

Example 4: Browser automation
  result = interface.execute_browser_command("navigate", url="https://example.com")
  # Returns: {"success": True, "url": "https://example.com"}

Example 5: State toggle
  result = interface.execute_command("toggle_game_mode")
  # Returns: {"success": True, "game_mode": True}

Example 6: Get current state
  state = interface.get_controller_state()
  # Returns full state dictionary

=== EXECUTOR STEP FORMAT ===

Standard executor step using Caelestia:

{
    "tool": "caelestia",
    "action": "increase_brightness"
}

With parameters:

{
    "tool": "caelestia",
    "action": "set_volume",
    "params": {"level": 0.5}
}

Browser automation:

{
    "tool": "caelestia_browser",
    "action": "navigate",
    "params": {"url": "https://example.com"}
}

=== CONFIGURATION FILE ===

shell.json automatically loaded and applied:
  - window_management settings
  - split_management settings
  - gestures settings
  - keyboard shortcuts
  - workspace configuration
  - system settings (shell, timeout, max_retries)

Location: ~/.config/shell.json (default)

=== TOGGLE PATTERN ===

Every major feature has a toggle to enable/disable it:

Feature                   Toggle Method
-------------------       ----------------------
Brightness control        toggle_brightness()
Volume control            toggle_volume()
Window management         toggle_window_management()
Split management          toggle_splits()
Workspace management      toggle_workspaces()
Gesture recognition       toggle_gestures()
Keyboard shortcuts        toggle_keyboard()

Each toggle returns: {"success": True, "feature_enabled": True/False}

State can be checked via: controller.feature.enabled

=== RETURN VALUE FORMAT ===

All commands return standardized dictionaries:

Success:
{
    "success": True,
    "action": "action_name",
    "specific_key": "specific_value",
    ...
}

Error:
{
    "success": False,
    "error": "Error message"
}

=== CONFIGURATION AND STATE PERSISTENCE ===

Save configuration:
  result = controller.save_config()
  # Saves to: ~/.config/shell.json (or custom path)

Get current state:
  state = controller.get_state()
  # Returns all settings, volumes, workspaces, etc.

State includes:
  - brightness: level, enabled
  - volume: level, muted, enabled
  - window_layout: layout, master_ratio, gaps, enabled
  - splits: enabled, resize_step
  - workspaces: current, count, enabled
  - gestures_enabled: bool
  - keyboard_enabled: bool
  - state: game_mode, dnd_mode, wifi_enabled, etc.

=== INPUT CONTROLLER INTEGRATION ===

BrowserAutomation uses InputController (executor/input_controller.py):
  - Mouse movement (absolute/relative)
  - Click operations (left/right/middle)
  - Keyboard typing
  - Key combinations
  - Wheel scrolling

All via ydotool, which is non-blocking and smooth.

=== COMMON EXECUTOR WORKFLOWS ===

Workflow 1: Adjust brightness and volume
  execute_command("increase_brightness")
  execute_command("set_volume", {"level": 0.7})

Workflow 2: Navigate to website and search
  execute_browser_command("navigate", url="https://google.com")
  execute_browser_command("type_text", text="python tutorial")
  execute_browser_command("press_key", key="Return")

Workflow 3: Window layout customization
  execute_command("set_layout", {"layout": "tile"})
  execute_command("set_master_ratio", {"ratio": 0.5})
  execute_command("increase_gaps", {"amount": 10})

Workflow 4: Gaming setup
  execute_command("toggle_game_mode")
  execute_command("set_brightness", {"level": 1.0})
  execute_command("toggle_dnd_mode")

Workflow 5: Multi-workspace management
  execute_command("next_workspace")
  execute_command("split_left")
  execute_command("switch_workspace", {"number": 1})

=== FILES ===

ui/caelestia_controller.py
  - CaelestiaController: Main control class
  - BrowserAutomation: Browser control
  - ExecutorAdapter: Command mapping
  - Data classes: Configuration structures

ui/__init__.py
  - Module exports

ui/caelestia_examples.py
  - Comprehensive usage examples
  - Demo functions for each feature
  - Executor integration examples

executor/caelestia_integration.py
  - ExecutorCaelestiaInterface: Direct executor integration
  - execute_command(): Simple command execution
  - execute_browser_command(): Browser automation
  - Example executor steps

=== TESTING ===

Test brightness:
  python -m ui.caelestia_controller
  # Runs demo with brightness, volume, state tests

Test full system:
  python -m ui.caelestia_examples
  # Runs all feature demos

Test executor integration:
  python -m executor.caelestia_integration
  # Shows executor integration examples

=== DEPENDENCIES ===

Runtime:
  - hyprctl: Window manager control
  - brightnessctl: Brightness control
  - pactl: Volume control
  - nmcli: Network control (WiFi, Bluetooth)
  - ydotool: Input control (keyboard/mouse)
  - firefox/chromium: Browser automation

Python:
  - json: Configuration
  - subprocess: Shell commands
  - time: Timing operations
  - typing: Type hints
  - dataclasses: Configuration structures
  - enum: Enumerations
  - pathlib: Path handling

=== USAGE IN EXECUTOR ===

In executor.py, add to tool handlers:

from executor.caelestia_integration import ExecutorCaelestiaInterface

def _handle_caelestia(
    data: Dict[str, Any],
    step_num: int,
    total_steps: int,
    attempt: int,
    max_retries: int,
    mode: str
) -> Dict[str, Any]:
    interface = ExecutorCaelestiaInterface()
    action = data.get("action")
    params = data.get("params", {})

    if action.startswith("browser_"):
        browser_action = action.replace("browser_", "")
        return interface.execute_browser_command(browser_action, **params)
    else:
        return interface.execute_command(action, params)

register_tool_handler("caelestia", _handle_caelestia)

Then executor steps can use:
{
    "tool": "caelestia",
    "action": "increase_brightness",
    "data": {}
}

=== EXTENDING THE SYSTEM ===

Add new control:
1. Add method to CaelestiaController
2. Add to ExecutorAdapter.command_map
3. Test with execute_command()
4. Document in this file

Example:
def set_gamma(self, gamma: float) -> Dict[str, Any]:
    try:
        subprocess.run(["redshift", "-g", str(gamma)])
        return {"success": True, "gamma": gamma}
    except Exception as e:
        return {"success": False, "error": str(e)}

=== NOTES ===

- All operations are non-blocking
- Brightness/volume use system tools (brightnessctl, pactl)
- Window management uses Hyprland dispatches
- Input control uses ydotool for smooth automation
- Browser automation is keyboard/mouse based
- Every feature can be toggled on/off
- Configuration persists to shell.json
- Executor integration is seamless
"""

# To use this documentation:
# 1. Read the ARCHITECTURE section
# 2. Look at FEATURES for available commands
# 3. Check EXECUTOR INTEGRATION EXAMPLES for your use case
# 4. Run the example file to see it in action
# 5. Integrate with your executor model

# Quick start example:
if __name__ == "__main__":
    from executor.caelestia_integration import ExecutorCaelestiaInterface

    interface = ExecutorCaelestiaInterface()

    # Executor says: "increase brightness"
    print(interface.execute_command("increase_brightness"))

    # Executor says: "set volume to 50%"
    print(interface.execute_command("set_volume", {"level": 0.5}))

    # Executor says: "switch to workspace 2"
    print(interface.execute_command("switch_workspace", {"number": 2}))

    # Get current state
    print(interface.get_controller_state())
