#!/usr/bin/env python3
"""
COMPLETE WORKFLOW: Send screenshot to any AI provider using primitives.

This shows how Scout/Brain can orchestrate micro-primitives
without any hardcoded workflows.

Workflow:
1. capture_screenshot() → take screenshot, copy to clipboard
2. focus_provider("claude") → focus Claude tab (works for any provider)
3. paste_clipboard() → paste image into input area
4. type_text(message) → optionally type a message
5. press_enter() → send the message

All steps are observable, retryable, and composable.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from router.message import Message
from router import dispatch

# Import to trigger service registration
import ui
import tools


def send_screenshot_workflow(provider: str = "claude", message: str = ""):
    """
    Send screenshot to AI provider using composable primitives.

    Args:
        provider: Target provider (claude, chatgpt, gemini, grok, deepseek)
        message: Optional message to include with screenshot

    Returns:
        bool: True if all steps succeeded
    """

    print(f"\n{'=' * 70}")
    print(f"WORKFLOW: Send screenshot to {provider.upper()}")
    print(f"{'=' * 70}\n")

    steps = []

    # ========================================================================
    # STEP 1: CAPTURE SCREENSHOT
    # ========================================================================

    print("[1/5] Capturing screenshot...")
    message_obj = Message(
        source="scout",
        target="ui",
        action="dispatch_tool",
        payload={"action": "capture_screenshot", "data": {}},
    )

    response = dispatch(message_obj)

    if not response.success:
        print(f"  ✗ FAILED: {response.error}")
        return False

    screenshot_path = response.result.get("result", {}).get("path")
    print(f"  ✓ Screenshot: {screenshot_path}")
    steps.append(("capture_screenshot", response.success))

    # ========================================================================
    # STEP 2: FOCUS PROVIDER
    # ========================================================================

    print(f"\n[2/5] Focusing {provider}...")
    message_obj = Message(
        source="scout",
        target="ui",
        action="dispatch_tool",
        payload={"action": "focus_provider", "data": {"provider": provider}},
    )

    response = dispatch(message_obj)

    if not response.success:
        print(f"  ✗ FAILED: {response.error}")
        print(f"  (Note: Expected if browser/provider not running)")
        return False

    action = response.result.get("result", {}).get("action")
    print(f"  ✓ Provider focused (action: {action})")
    steps.append(("focus_provider", response.success))

    # ========================================================================
    # STEP 3: PASTE SCREENSHOT
    # ========================================================================

    print(f"\n[3/5] Pasting screenshot...")
    message_obj = Message(
        source="scout",
        target="ui",
        action="dispatch_tool",
        payload={"action": "paste_clipboard", "data": {}},
    )

    response = dispatch(message_obj)

    if not response.success:
        print(f"  ✗ FAILED: {response.error}")
        return False

    print(f"  ✓ Image pasted (Ctrl+V)")
    steps.append(("paste_clipboard", response.success))

    # ========================================================================
    # STEP 4: TYPE MESSAGE (optional)
    # ========================================================================

    if message:
        print(f"\n[4/5] Typing message...")
        message_obj = Message(
            source="scout",
            target="ui",
            action="dispatch_tool",
            payload={"action": "type_text", "data": {"text": message}},
        )

        response = dispatch(message_obj)

        if not response.success:
            print(f"  ✗ FAILED: {response.error}")
            return False

        print(f"  ✓ Message typed ({len(message)} chars)")
        steps.append(("type_text", response.success))
        step_num = 5
    else:
        step_num = 4
        print(f"\n[4/5] (Skipping message - none provided)")

    # ========================================================================
    # STEP 5: SEND MESSAGE
    # ========================================================================

    print(f"\n[{step_num}/5] Sending message...")
    message_obj = Message(
        source="scout",
        target="ui",
        action="dispatch_tool",
        payload={"action": "press_enter", "data": {}},
    )

    response = dispatch(message_obj)

    if not response.success:
        print(f"  ✗ FAILED: {response.error}")
        return False

    print(f"  ✓ Message sent (pressed Enter)")
    steps.append(("press_enter", response.success))

    # ========================================================================
    # SUMMARY
    # ========================================================================

    print(f"\n{'=' * 70}")
    print("✓ WORKFLOW COMPLETE")
    print(f"{'=' * 70}\n")

    print("Steps executed:")
    for step_name, success in steps:
        status = "✓" if success else "✗"
        print(f"  {status} {step_name}")

    print(f"\nKey achievements:")
    print(f"  • Same primitives work for ALL providers (Claude, ChatGPT, Gemini, etc.)")
    print(f"  • Each step observable and independently retryable")
    print(f"  • No hardcoded workflows - fully composable")
    print(f"  • Scout/Brain controls orchestration, not functions")
    print(f"  • No blocking input() - fully autonomous")

    return True


def main():
    """Run workflow examples."""
    print("\n" + "╔" + "=" * 68 + "╗")
    print("║" + " COMPLETE WORKFLOW: SEND SCREENSHOT ".center(68) + "║")
    print("╚" + "=" * 68 + "╝")

    # Try Claude with message
    send_screenshot_workflow("claude", "Analyze this screenshot for me")


if __name__ == "__main__":
    main()
