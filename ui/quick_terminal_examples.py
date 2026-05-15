#!/usr/bin/env python3
"""
Quick Terminal - Usage Examples

Demonstrates quick terminal utilities for common tasks:
- YouTube
- Screenshots (with clipboard copy)
- ChatGPT integration
- Brightness control
"""

from ui.quick_terminal import QuickTerminal
import json


def example_youtube():
    """Example: Open YouTube."""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Open YouTube")
    print("=" * 60)

    qt = QuickTerminal()
    result = qt.open_youtube()

    print(f"\nResult:")
    print(json.dumps(result, indent=2))


def example_screenshot():
    """Example: Take screenshot and copy."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Screenshot & Copy")
    print("=" * 60)

    qt = QuickTerminal()

    print("\nTaking screenshot...")
    result = qt.screenshot_and_copy()

    if result["success"]:
        print(f"\n✓ Screenshot taken and copied!")
        print(f"  Path: {result['path']}")
    else:
        print(f"\n✗ Error: {result['error']}")


def example_chatgpt_screenshot():
    """Example: Send screenshot to ChatGPT."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Screenshot to ChatGPT (Full Workflow)")
    print("=" * 60)

    print("""
This example demonstrates the complete workflow:
  1. Takes a screenshot
  2. Copies it to clipboard
  3. Opens ChatGPT (reuses existing tab if open)
  4. Pastes the screenshot
  5. Prompts to send

Usage:
    qt = QuickTerminal()
    qt.paste_screenshot_into_chatgpt()

The workflow handles:
  - Auto-detection of Brave
  - Reusing existing ChatGPT tabs
  - Image copying to clipboard
  - Automatic pasting
  - Optional auto-send
""")

    # Uncomment to actually run (requires browser interaction)
    # qt = QuickTerminal()
    # result = qt.paste_screenshot_into_chatgpt()


def example_brightness():
    """Example: Brightness control."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Brightness Control")
    print("=" * 60)

    qt = QuickTerminal()

    # Get current brightness
    print("\nGetting current brightness...")
    brightness = qt.get_brightness()

    if brightness["success"]:
        print(f"  Current: {brightness['percent']}%")
        print(f"  ({brightness['current']} / {brightness['max']})")
    else:
        print(f"  Error: {brightness['error']}")
        return

    # Increase brightness
    print("\nIncreasing brightness by 10%...")
    result = qt.brightness_up()
    print(f"  Result: {result}")

    # Check new brightness
    brightness_new = qt.get_brightness()
    if brightness_new["success"]:
        print(f"  New brightness: {brightness_new['percent']}%")

    # Decrease brightness
    print("\nDecreasing brightness by 10%...")
    result = qt.brightness_down()
    print(f"  Result: {result}")

    # Set brightness to specific level
    print("\nSetting brightness to 60%...")
    result = qt.set_brightness(60)
    print(f"  Result: {result}")

    # Check final brightness
    brightness_final = qt.get_brightness()
    if brightness_final["success"]:
        print(f"  Final brightness: {brightness_final['percent']}%")


def example_cli_commands():
    """Example: Command-line usage."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: CLI Command Usage")
    print("=" * 60)

    print("""
Command-line usage examples:

1. YouTube:
   python ui/quick_terminal.py youtube

2. Screenshot:
   python ui/quick_terminal.py screenshot

3. Screenshot to ChatGPT:
   python ui/quick_terminal.py screenshot-to-chatgpt

4. Brightness:
   python ui/quick_terminal.py brightness-up
   python ui/quick_terminal.py brightness-down
   python ui/quick_terminal.py brightness 75      # Set to 75%
   python ui/quick_terminal.py brightness-info

5. ChatGPT:
   python ui/quick_terminal.py chatgpt

With aliases (for speed):
   yt              # YouTube
   ss              # Screenshot
   ss-chat         # Screenshot to ChatGPT
   bright-up       # Increase brightness
   bright-down     # Decrease brightness
   bright-info     # Show brightness
   bright 50       # Set to 50%
""")


def example_aliases_setup():
    """Example: How to set up aliases."""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Setting Up Shell Aliases")
    print("=" * 60)

    setup_fish = """
Fish shell (~/.config/fish/config.fish):
=========================================

# YouTube
alias yt='python /home/dmannu/ai-model-8/ui/quick_terminal.py youtube'

# Screenshots
alias ss='python /home/dmannu/ai-model-8/ui/quick_terminal.py screenshot'
alias ss-chat='python /home/dmannu/ai-model-8/ui/quick_terminal.py screenshot-to-chatgpt'

# Brightness
alias bright-up='python /home/dmannu/ai-model-8/ui/quick_terminal.py brightness-up'
alias bright-down='python /home/dmannu/ai-model-8/ui/quick_terminal.py brightness-down'
function bright
    python /home/dmannu/ai-model-8/ui/quick_terminal.py brightness $argv[1]
end
alias bright-info='python /home/dmannu/ai-model-8/ui/quick_terminal.py brightness-info'

# Reload:
source ~/.config/fish/config.fish
"""

    setup_bash = """
Bash shell (~/.bashrc):
=======================

# YouTube
alias yt='python /home/dmannu/ai-model-8/ui/quick_terminal.py youtube'

# Screenshots
alias ss='python /home/dmannu/ai-model-8/ui/quick_terminal.py screenshot'
alias ss-chat='python /home/dmannu/ai-model-8/ui/quick_terminal.py screenshot-to-chatgpt'

# Brightness
alias bright-up='python /home/dmannu/ai-model-8/ui/quick_terminal.py brightness-up'
alias bright-down='python /home/dmannu/ai-model-8/ui/quick_terminal.py brightness-down'
bright() {
    python /home/dmannu/ai-model-8/ui/quick_terminal.py brightness "$1"
}
alias bright-info='python /home/dmannu/ai-model-8/ui/quick_terminal.py brightness-info'

# Reload:
source ~/.bashrc
"""

    print(setup_fish)
    print("\n" + "=" * 30)
    print(setup_bash)


def example_workflows():
    """Example: Common workflows."""
    print("\n" + "=" * 60)
    print("EXAMPLE 7: Common Workflows")
    print("=" * 60)

    workflows = """
WORKFLOW 1: Share screenshot on ChatGPT
----------------------------------------
Terminal: ss-chat
Automated steps:
  1. Takes screenshot of entire screen
  2. Copies image to clipboard automatically
  3. Detects Brave (opens if needed)
  4. Finds ChatGPT tab (opens new if needed)
  5. Pastes screenshot (Ctrl+V)
  6. Asks if you want to auto-send
Time: 8-10 seconds vs 13+ seconds manual

WORKFLOW 2: Quick brightness adjustment
----------------------------------------
Terminal: bright-up      # Increase by 10%
Terminal: bright-down    # Decrease by 10%
Terminal: bright 75      # Set to exact 75%
Time: 1-2 seconds per command

WORKFLOW 3: YouTube + ChatGPT setup
----------------------------------------
Terminal: yt             # Opens YouTube
Terminal: ss-chat        # Send screenshot to ChatGPT
Result: Both windows ready for comparison/discussion

WORKFLOW 4: Monitor brightness
----------------------------------------
Terminal: bright-info
Output:
  Current brightness: 75%
  Current: 75 / Max: 100
Time: <1 second
"""
    print(workflows)


def example_error_handling():
    """Example: Error handling."""
    print("\n" + "=" * 60)
    print("EXAMPLE 8: Error Handling")
    print("=" * 60)

    code = """
from ui.quick_terminal import QuickTerminal
import json

qt = QuickTerminal()

# Check if command succeeds
result = qt.screenshot_and_copy()

if result['success']:
    print(f"✓ Screenshot saved: {result['path']}")
else:
    print(f"✗ Error: {result['error']}")

# All methods return standardized format:
# {
#     "success": True/False,
#     "action": "action_name",
#     "error": "error message (if success=False)",
#     ...other fields...
# }

# Example: Set brightness with error handling
result = qt.set_brightness(75)
if result['success']:
    print(f"✓ Brightness set to {result['percent']}%")
else:
    print(f"✗ Error: {result['error']}")
    # Could be: brightnessctl not installed, etc.
"""
    print(code)


def example_dependencies():
    """Example: Dependencies setup."""
    print("\n" + "=" * 60)
    print("EXAMPLE 9: Installing Dependencies")
    print("=" * 60)

    deps = """
All dependencies (Arch Linux):
==============================
sudo pacman -S brightnessctl xclip gnome-screenshot xdotool brave

Individual packages:
====================
# Brightness control
sudo pacman -S brightnessctl

# Clipboard tools (choose one)
sudo pacman -S xclip          # For X11
sudo pacman -S wl-clipboard   # For Wayland

# Screenshot tools (choose at least one)
sudo pacman -S gnome-screenshot
sudo pacman -S scrot
sudo pacman -S imagemagick

# Window detection
sudo pacman -S xdotool

# Browser
sudo pacman -S brave

Verification:
=============
which brightnessctl    # Should show path
which xclip            # Should show path
which gnome-screenshot # Should show path
which brave          # Should show path
"""
    print(deps)


if __name__ == "__main__":
    print("\n" + "█" * 60)
    print("QUICK TERMINAL - COMPREHENSIVE EXAMPLES")
    print("█" * 60)

    # Run examples
    try:
        example_youtube()
        example_screenshot()
        example_chatgpt_screenshot()
        example_brightness()
        example_cli_commands()
        example_aliases_setup()
        example_workflows()
        example_error_handling()
        example_dependencies()

    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "█" * 60)
    print("EXAMPLES COMPLETE")
    print("█" * 60)
    print("\nFor more information, see: ui/QUICK_TERMINAL_GUIDE.md")
    print("For CLI help: python ui/quick_terminal.py help\n")
