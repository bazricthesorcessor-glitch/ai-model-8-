#!/usr/bin/env python3
"""
EXAMPLE: Composing UI primitives to solve real workflows.

Shows how Scout/Brain decomposes high-level goals into composable primitives,
instead of calling hardcoded functions like send_screenshot_to_chatgpt().

KEY INSIGHT:
- OLD (macro workflow): send_screenshot_to_chatgpt()
- NEW (primitives): capture_screenshot() → focus_provider("chatgpt") → paste_image()

Primitives are:
- Small: one responsibility each
- Composable: can be combined in any order
- Observable: each step succeeds/fails independently
- Reusable: paste_image() works for Claude, Gemini, Grok, etc.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from router.message import Message
from router import dispatch, send_to_service

# Import UI and tools to trigger service registration
import ui
import tools


def example_send_screenshot_to_provider(provider: str = "claude"):
    """
    Example: Send screenshot to AI provider using composable primitives.

    Instead of calling:
        send_screenshot_to_chatgpt()
        send_screenshot_to_claude()
        send_screenshot_to_gemini()

    Brain composes primitives:
        1. Capture screenshot
        2. Focus provider tab
        3. Paste image to clipboard
        4. Send message

    Args:
        provider: Target provider ("claude", "chatgpt", "gemini", etc.)
    """

    print(f"\n{'=' * 70}")
    print(f"WORKFLOW: Send screenshot to {provider.upper()}")
    print(f"{'=' * 70}")

    # ========================================================================
    # STEP 1: CAPTURE SCREENSHOT
    # ========================================================================

    print(f"\n[1/4] Capturing screenshot...")
    message = Message(
        source="scout",
        target="ui",
        action="dispatch_tool",
        payload={
            "action": "capture_screenshot",
            "data": {
                "region": None,  # Full screen
                "persistent": False,  # Temporary buffer
            },
        },
    )

    response = dispatch(message)

    if not response.success:
        print(f"  ✗ Failed: {response.error}")
        return False

    screenshot_path = response.result.get("result", {}).get("path")
    print(f"  ✓ Screenshot captured: {screenshot_path}")

    # ========================================================================
    # STEP 2: FOCUS PROVIDER TAB
    # ========================================================================

    print(f"\n[2/4] Focusing {provider} tab...")
    message = Message(
        source="scout",
        target="ui",
        action="dispatch_tool",
        payload={
            "action": "focus_provider",
            "data": {
                "provider": provider,
            },
        },
    )

    response = dispatch(message)

    if not response.success:
        print(f"  ✗ Failed: {response.error}")
        print(f"  Note: This is expected if browser/provider not running")
        return False

    action = response.result.get("result", {}).get("action")
    print(f"  ✓ Provider tab focused (action: {action})")

    # ========================================================================
    # STEP 3: PASTE SCREENSHOT
    # ========================================================================

    print(f"\n[3/4] Pasting screenshot to {provider}...")
    message = Message(
        source="scout",
        target="ui",
        action="dispatch_tool",
        payload={
            "action": "copy_screenshot_to_clipboard",
            "data": {},
        },
    )

    response = dispatch(message)

    if not response.success:
        print(f"  ✗ Failed: {response.error}")
        return False

    print(f"  ✓ Screenshot pasted to clipboard")

    # ========================================================================
    # STEP 4: SEND MESSAGE (auto-send or manual)
    # ========================================================================

    print(f"\n[4/4] Message ready to send...")
    print(f"  [Option A] Scout can execute keyboard primitive: press_key('ctrl+Return')")
    print(f"  [Option B] Scout waits for user to press Enter manually")
    print(f"  [Option C] Scout observes for response, then continues")

    print(f"\n✓ WORKFLOW COMPLETE")
    print(f"\nKey advantages of primitive composition:")
    print(f"  • Same primitives work for Claude, ChatGPT, Gemini, Grok, DeepSeek")
    print(f"  • Each step is observable (can retry, skip, or modify)")
    print(f"  • Can be reordered (focus first, then capture; or capture, then focus)")
    print(f"  • No duplicate code for each provider")
    print(f"  • Scout controls the flow, not hardcoded functions")

    return True


def example_list_available_providers():
    """Example: List available AI providers."""
    print(f"\n{'=' * 70}")
    print("AVAILABLE PROVIDERS")
    print(f"{'=' * 70}\n")

    message = Message(
        source="scout",
        target="ui",
        action="dispatch_tool",
        payload={
            "action": "list_providers",
            "data": {},
        },
    )

    response = dispatch(message)

    if response.success:
        providers = response.result.get("result", {}).get("providers", [])
        print(f"Available providers ({len(providers)}):\n")
        for provider in providers:
            print(f"  • {provider}")
    else:
        print(f"Error: {response.error}")


def main():
    """Run examples."""
    print("\n" + "╔" + "=" * 68 + "╗")
    print("║" + " EXAMPLE: COMPOSING UI PRIMITIVES ".center(68) + "║")
    print("╚" + "=" * 68 + "╝")

    # Show available providers
    example_list_available_providers()

    # Show how to compose primitives for a workflow
    # (May fail gracefully if browser not running, that's OK)
    example_send_screenshot_to_provider("claude")


if __name__ == "__main__":
    main()
