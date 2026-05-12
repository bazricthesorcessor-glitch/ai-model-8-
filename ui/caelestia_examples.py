"""
Caelestia Controller - Complete Usage Guide

This file demonstrates all features of the Caelestia UI controller system.
Every control has a toggle. The executor just says what to do, and the system handles it.
"""

from ui.caelestia_controller import CaelestiaController, ExecutorAdapter, BrowserAutomation
from executor.caelestia_integration import ExecutorCaelestiaInterface
import json


def demo_brightness_control():
    """Demo: Brightness control with toggle."""
    print("\n" + "=" * 60)
    print("BRIGHTNESS CONTROL DEMO")
    print("=" * 60)

    controller = CaelestiaController()

    print(f"\nCurrent brightness: {controller.brightness.current_level:.1%}")
    print(f"Enabled: {controller.brightness.enabled}")

    # Increase brightness
    result = controller.increase_brightness()
    print(f"\nIncrease brightness: {result}")
    print(f"New level: {controller.brightness.current_level:.1%}")

    # Decrease brightness
    result = controller.decrease_brightness()
    print(f"\nDecrease brightness: {result}")
    print(f"New level: {controller.brightness.current_level:.1%}")

    # Set brightness to specific level
    result = controller.set_brightness(0.75)
    print(f"\nSet brightness to 75%: {result}")

    # Toggle brightness on/off
    result = controller.toggle_brightness()
    print(f"\nToggle brightness: {result}")
    print(f"Brightness now {'enabled' if controller.brightness.enabled else 'disabled'}")


def demo_volume_control():
    """Demo: Volume control with toggle."""
    print("\n" + "=" * 60)
    print("VOLUME CONTROL DEMO")
    print("=" * 60)

    controller = CaelestiaController()

    print(f"\nCurrent volume: {controller.volume.current_level:.1%}")
    print(f"Muted: {controller.volume.muted}")
    print(f"Enabled: {controller.volume.enabled}")

    # Increase volume
    result = controller.increase_volume()
    print(f"\nIncrease volume: {result}")

    # Decrease volume
    result = controller.decrease_volume()
    print(f"\nDecrease volume: {result}")

    # Set volume
    result = controller.set_volume(0.6)
    print(f"\nSet volume to 60%: {result}")

    # Toggle mute
    result = controller.toggle_mute()
    print(f"\nToggle mute: {result}")

    # Toggle volume control
    result = controller.toggle_volume()
    print(f"\nToggle volume control: {result}")


def demo_window_management():
    """Demo: Window management controls."""
    print("\n" + "=" * 60)
    print("WINDOW MANAGEMENT DEMO")
    print("=" * 60)

    controller = CaelestiaController()

    print(f"\nLayout: {controller.window_layout.layout}")
    print(f"Master ratio: {controller.window_layout.master_ratio}")
    print(f"Gaps: {controller.window_layout.gaps}")
    print(f"Enabled: {controller.window_layout.enabled}")

    # Change layout
    print("\nChanging layout to 'tile'...")
    result = controller.set_layout("tile")
    print(f"Result: {result}")

    # Change master ratio
    print("\nSetting master ratio to 0.5...")
    result = controller.set_master_ratio(0.5)
    print(f"Result: {result}")

    # Increase gaps
    print("\nIncreasing gaps...")
    result = controller.increase_gaps(5)
    print(f"Result: {result}")

    # Toggle window management
    result = controller.toggle_window_management()
    print(f"Window management now {'enabled' if controller.window_layout.enabled else 'disabled'}")


def demo_split_management():
    """Demo: Split window management."""
    print("\n" + "=" * 60)
    print("SPLIT MANAGEMENT DEMO")
    print("=" * 60)

    controller = CaelestiaController()

    print(f"\nSplits enabled: {controller.splits.enabled}")
    print(f"Resize step: {controller.splits.resize_step}")
    print(f"Gap step: {controller.splits.gap_step}")

    # Split operations (simulated)
    print("\nCreating splits...")
    print(f"Split left: {controller.split_left()}")
    print(f"Split right: {controller.split_right()}")
    print(f"Split up: {controller.split_up()}")
    print(f"Split down: {controller.split_down()}")

    # Resize split
    print("\nResizing split...")
    result = controller.resize_split("left", 100)
    print(f"Result: {result}")

    # Toggle splits
    result = controller.toggle_splits()
    print(f"Splits now {'enabled' if controller.splits.enabled else 'disabled'}")


def demo_workspace_management():
    """Demo: Workspace control."""
    print("\n" + "=" * 60)
    print("WORKSPACE MANAGEMENT DEMO")
    print("=" * 60)

    controller = CaelestiaController()

    print(f"\nWorkspaces: {controller.workspaces.count}")
    print(f"Current: {controller.workspaces.current_workspace}")
    print(f"Enabled: {controller.workspaces.enabled}")

    # Switch workspaces
    print("\nSwitching workspaces...")
    for ws in [1, 2, 3, 4, 1]:
        result = controller.switch_workspace(ws)
        print(f"Switch to {ws}: {result['workspace'] if result['success'] else result['error']}")

    # Next/prev workspace
    print("\nNext workspace:")
    print(controller.next_workspace())

    print("\nPrevious workspace:")
    print(controller.prev_workspace())

    # Toggle workspace management
    result = controller.toggle_workspaces()
    print(f"Workspaces now {'enabled' if controller.workspaces.enabled else 'disabled'}")


def demo_gestures():
    """Demo: Gesture control."""
    print("\n" + "=" * 60)
    print("GESTURE CONTROL DEMO")
    print("=" * 60)

    controller = CaelestiaController()

    print(f"\nGestures enabled: {controller.gestures.enabled}")
    print(f"Available gestures:")
    for gesture, action in controller.gestures.mappings.items():
        print(f"  {gesture:15} -> {action}")

    # Map gesture to action
    print("\nMapping 'swipe_up' to 'custom_action'...")
    result = controller.set_gesture_mapping("swipe_up", "custom_action")
    print(f"Result: {result}")

    # Toggle gestures
    result = controller.toggle_gestures()
    print(f"Gestures now {'enabled' if controller.gestures.enabled else 'disabled'}")


def demo_state_toggles():
    """Demo: State toggles."""
    print("\n" + "=" * 60)
    print("STATE TOGGLES DEMO")
    print("=" * 60)

    controller = CaelestiaController()

    print(f"\nCurrent state: {json.dumps(controller.state, indent=2)}")

    # Toggle game mode
    print("\nToggling game mode...")
    result = controller.toggle_game_mode()
    print(f"Result: {result}")

    # Toggle DND mode
    print("\nToggling DND mode...")
    result = controller.toggle_dnd_mode()
    print(f"Result: {result}")

    # Toggle WiFi
    print("\nToggling WiFi...")
    result = controller.toggle_wifi()
    print(f"Result: {result}")

    # Toggle Bluetooth
    print("\nToggling Bluetooth...")
    result = controller.toggle_bluetooth()
    print(f"Result: {result}")

    # Toggle microphone
    print("\nToggling microphone...")
    result = controller.toggle_microphone()
    print(f"Result: {result}")


def demo_executor_integration():
    """Demo: Executor integration."""
    print("\n" + "=" * 60)
    print("EXECUTOR INTEGRATION DEMO")
    print("=" * 60)

    interface = ExecutorCaelestiaInterface()

    # Example commands from executor
    commands = [
        ("increase_brightness", {}),
        ("decrease_volume", {}),
        ("set_volume", {"level": 0.5}),
        ("switch_workspace", {"number": 2}),
        ("toggle_game_mode", {}),
        ("toggle_wifi", {}),
        ("split_left", {}),
    ]

    print("\nExecutor sending commands...\n")
    for command, params in commands:
        print(f"[Executor] {command} {params if params else ''}")
        result = interface.execute_command(command, params)
        print(f"[Result] {result}")
        print()


def demo_browser_automation():
    """Demo: Browser automation."""
    print("\n" + "=" * 60)
    print("BROWSER AUTOMATION DEMO")
    print("=" * 60)

    controller = CaelestiaController()
    browser = controller.get_browser()

    print("\nBrowser automation capabilities:")
    print("  - navigate(url): Navigate to URL")
    print("  - click(x, y): Click at coordinates")
    print("  - type_text(text): Type text")
    print("  - scroll(direction, amount): Scroll page")
    print("  - search(term): Search (Ctrl+F)")
    print("  - press_key(key): Press key")
    print("  - refresh(): Refresh page (F5)")
    print("  - go_back(): Go back (Alt+Left)")
    print("  - go_forward(): Go forward (Alt+Right)")
    print("  - new_tab(): New tab (Ctrl+T)")
    print("  - close_tab(): Close tab (Ctrl+W)")

    print("\nExample browser actions (simulated):")
    print(browser.type_text("example search"))
    print(browser.press_key("Return"))
    print(browser.scroll("down", 3))


def demo_config_persistence():
    """Demo: Save and load configuration."""
    print("\n" + "=" * 60)
    print("CONFIG PERSISTENCE DEMO")
    print("=" * 60)

    controller = CaelestiaController()

    # Get current state
    state = controller.get_state()
    print(f"\nCurrent state:")
    print(json.dumps(state, indent=2))

    # Make changes
    print("\nMaking changes...")
    controller.set_brightness(0.9)
    controller.set_volume(0.3)
    controller.switch_workspace(5)

    # Save config
    print("\nSaving configuration...")
    result = controller.save_config()
    print(f"Result: {result}")

    # Get updated state
    new_state = controller.get_state()
    print(f"\nUpdated state:")
    print(json.dumps(new_state, indent=2))


def demo_all_features():
    """Demo: All features in sequence."""
    print("\n" + "=" * 80)
    print("COMPLETE CAELESTIA CONTROLLER FEATURE DEMONSTRATION")
    print("=" * 80)

    controller = CaelestiaController()

    # Create a comprehensive action sequence
    actions = [
        ("Increase brightness", lambda: controller.increase_brightness()),
        ("Set volume to 50%", lambda: controller.set_volume(0.5)),
        ("Toggle fullscreen", lambda: controller.toggle_fullscreen()),
        ("Switch to workspace 2", lambda: controller.switch_workspace(2)),
        ("Toggle game mode", lambda: controller.toggle_game_mode()),
        ("Decrease gaps", lambda: controller.decrease_gaps(5)),
        ("Next workspace", lambda: controller.next_workspace()),
    ]

    print("\nExecuting action sequence:\n")
    for description, action in actions:
        try:
            result = action()
            status = "✓" if result.get("success", False) else "✗"
            print(f"{status} {description}: {result.get('success', False)}")
        except Exception as e:
            print(f"✗ {description}: Error - {e}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    print("\n" + "█" * 80)
    print("CAELESTIA CONTROLLER - COMPREHENSIVE USAGE EXAMPLES")
    print("█" * 80)

    # Run all demos
    try:
        demo_brightness_control()
        demo_volume_control()
        demo_window_management()
        demo_split_management()
        demo_workspace_management()
        demo_gestures()
        demo_state_toggles()
        demo_executor_integration()
        demo_browser_automation()
        demo_config_persistence()
        demo_all_features()

    except Exception as e:
        print(f"\n✗ Demo error: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "█" * 80)
    print("ALL DEMONSTRATIONS COMPLETE")
    print("█" * 80 + "\n")
