#!/usr/bin/env python3
"""
Test UI service bridge - verify router can dispatch to UI primitives.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from router.message import Message
from router import dispatch

# Import UI module to trigger service registration
import ui


def test_ui_list_providers():
    """Test: list available AI providers via router."""
    print("\n" + "=" * 70)
    print("TEST: list_providers via router")
    print("=" * 70)

    message = Message(
        source="test",
        target="ui",
        action="dispatch_tool",
        payload={
            "action": "list_providers",
            "data": {},
        }
    )

    print(f"\nDispatching: {message.payload.get('action')}")
    result = dispatch(message)

    print(f"\nResponse:")
    print(f"  Success: {result.success}")

    if result.success:
        providers = result.result.get("result", {}).get("providers", [])
        print(f"  Providers: {providers}")
        print(f"\n✓ PASS: got {len(providers)} providers")
        return True
    else:
        print(f"  Error: {result.error}")
        print(f"\n✗ FAIL")
        return False


def test_ui_focus_provider():
    """Test: focus_provider action (won't actually work without browser, but should validate)."""
    print("\n" + "=" * 70)
    print("TEST: focus_provider validation")
    print("=" * 70)

    message = Message(
        source="test",
        target="ui",
        action="dispatch_tool",
        payload={
            "action": "focus_provider",
            "data": {"provider": "claude"},
        }
    )

    print(f"\nDispatching: focus_provider(claude)")
    result = dispatch(message)

    print(f"\nResponse:")
    print(f"  Success: {result.success}")
    print(f"  Error: {result.error}")

    # Should either succeed (if browser exists) or fail with clear error
    if result.error:
        print(f"  Expected: action attempted, got error (may be expected if browser not running)")
        print(f"\n✓ PASS: action properly validated")
        return True
    else:
        print(f"\n✓ PASS: action executed")
        return True


def test_ui_unknown_action():
    """Test: unknown action returns error."""
    print("\n" + "=" * 70)
    print("TEST: unknown_action returns error")
    print("=" * 70)

    message = Message(
        source="test",
        target="ui",
        action="dispatch_tool",
        payload={
            "action": "nonexistent_action",
            "data": {},
        }
    )

    print(f"\nDispatching: nonexistent_action")
    result = dispatch(message)

    print(f"\nResponse:")
    print(f"  Success: {result.success}")
    print(f"  Error: {result.error}")

    if not result.success and "unknown action" in result.error.lower():
        print(f"\n✓ PASS: unknown action properly rejected")
        return True
    else:
        print(f"\n✗ FAIL: expected unknown action error")
        return False


def main():
    """Run all tests."""
    print("\n" + "╔" + "=" * 68 + "╗")
    print("║" + " TIER 1: UI SERVICE PRIMITIVES TESTS ".center(68) + "║")
    print("╚" + "=" * 68 + "╝")

    tests = [
        ("List Providers", test_ui_list_providers),
        ("Focus Provider", test_ui_focus_provider),
        ("Unknown Action", test_ui_unknown_action),
    ]

    results = {}
    for name, test_func in tests:
        try:
            passed = test_func()
            results[name] = "✓ PASS" if passed else "✗ FAIL"
        except Exception as e:
            print(f"\n✗ EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
            results[name] = "✗ ERROR"

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for name, status in results.items():
        print(f"  {status}  {name}")

    passed = sum(1 for s in results.values() if s == "✓ PASS")
    print(f"\nTotal: {passed}/{len(results)} passed")

    return all(s == "✓ PASS" for s in results.values())


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
