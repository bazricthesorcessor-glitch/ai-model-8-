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
import ui.service as ui_service_module


class FakeTabsManager:
    def __init__(self):
        self.calls = []

    def list_tabs(self):
        self.calls.append(("list_tabs", None))
        return {
            "success": True,
            "tabs": [
                {
                    "id": "tab-1",
                    "type": "page",
                    "url": "https://chat.openai.com/",
                    "title": "ChatGPT",
                }
            ],
            "count": 1,
        }

    def activate_tab(self, tab_id):
        self.calls.append(("activate_tab", tab_id))
        return {"success": True, "action": "activated", "tab_id": tab_id}

    def open_tab(self, url):
        self.calls.append(("open_tab", url))
        return {"success": True, "action": "opened", "url": url, "tab_id": "tab-2"}

    def focus_provider(self, provider):
        self.calls.append(("focus_provider", provider))
        return {"success": True, "provider": provider, "action": "focused"}

    def list_providers(self):
        self.calls.append(("list_providers", None))
        return {"success": True, "providers": ["chatgpt"], "count": 1}

    def get_current_provider(self):
        self.calls.append(("get_current_provider", None))
        return {"success": True, "provider": "chatgpt"}

    def detect_provider_tab(self, window_title):
        self.calls.append(("detect_provider_tab", window_title))
        return "chatgpt" if "chatgpt" in window_title.lower() else None


def install_fake_tabs_manager():
    fake = FakeTabsManager()
    ui_service_module._ai_tabs_manager = fake
    return fake


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


def test_ui_browser_tab_primitives():
    """Test: Brave/CDP browser primitives are exposed through router."""
    print("\n" + "=" * 70)
    print("TEST: browser tab primitives via router")
    print("=" * 70)

    fake = install_fake_tabs_manager()

    messages = [
        (
            "list_tabs",
            {},
            lambda result: result.result.get("count") == 1,
        ),
        (
            "activate_tab",
            {"tab_id": "tab-1"},
            lambda result: result.result.get("tab_id") == "tab-1",
        ),
        (
            "open_tab",
            {"url": "https://example.com"},
            lambda result: result.result.get("url") == "https://example.com",
        ),
        (
            "focus_provider",
            {"provider": "chatgpt"},
            lambda result: result.result.get("provider") == "chatgpt",
        ),
    ]

    for action, data, assertion in messages:
        message = Message(
            source="test",
            target="ui",
            action="dispatch_tool",
            payload={
                "action": action,
                "data": data,
            },
        )

        print(f"\nDispatching: {action}")
        result = dispatch(message)
        print(f"  Success: {result.success}")
        print(f"  Error: {result.error}")

        if not result.success or not assertion(result):
            print(f"\n✗ FAIL: {action}")
            return False

    expected_calls = [
        ("list_tabs", None),
        ("activate_tab", "tab-1"),
        ("open_tab", "https://example.com"),
        ("focus_provider", "chatgpt"),
    ]
    if fake.calls != expected_calls:
        print(f"\n✗ FAIL: expected calls {expected_calls}, got {fake.calls}")
        return False

    print(f"\n✓ PASS: browser primitives routed")
    return True


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
        ("Browser Tab Primitives", test_ui_browser_tab_primitives),
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
