#!/usr/bin/env python3
"""
Test tool service bridge - verify router can dispatch to tools.
Tier 0 checkpoint: does the bridge actually work?
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from router.message import Message
from router import dispatch
import json

# Import tools to trigger service registration
import tools


def test_tool_dispatch_execute_command():
    """Test: execute_command tool via router."""
    print("\n" + "=" * 70)
    print("TEST: dispatch execute_command via router")
    print("=" * 70)

    message = Message(
        source="test",
        target="tools",
        action="dispatch_tool",
        payload={
            "tool": "execute_command",
            "data": {
                "command": "echo 'Hello from Elzyra tool service'",
                "shell": "/bin/bash",
                "timeout": 5,
            }
        }
    )

    print(f"\nSending message to: {message.target}")
    print(f"Tool: {message.payload.get('tool')}")
    print(f"Command: {message.payload.get('data', {}).get('command')}")

    result = dispatch(message)

    print(f"\nResponse:")
    print(f"  Success: {result.success}")
    print(f"  Error: {result.error}")

    if result.success:
        tool_result = result.result
        print(f"\nTool execution result:")
        print(f"  Tool: {tool_result.get('tool')}")
        print(f"  Return code: {tool_result.get('result', {}).get('returncode')}")
        print(f"  Stdout: {tool_result.get('result', {}).get('stdout')[:100]}")
        print(f"\n✓ PASS: execute_command executed via router")
        return True
    else:
        print(f"\n✗ FAIL: {result.error}")
        return False


def test_tool_dispatch_not_implemented():
    """Test: fake-success tool now returns error."""
    print("\n" + "=" * 70)
    print("TEST: fake-success tool now returns error (mouse_click)")
    print("=" * 70)

    message = Message(
        source="test",
        target="tools",
        action="dispatch_tool",
        payload={
            "tool": "mouse_click",
            "data": {
                "x": 100,
                "y": 100,
                "button": "left",
            }
        }
    )

    print(f"\nSending message to: {message.target}")
    print(f"Tool: {message.payload.get('tool')}")

    result = dispatch(message)

    print(f"\nResponse:")
    print(f"  Success: {result.success}")
    print(f"  Error: {result.error}")

    if not result.success and "not implemented" in result.error.lower():
        print(f"\n✓ PASS: fake-success tool correctly returns error")
        return True
    else:
        print(f"\n✗ FAIL: expected not-implemented error")
        return False


def test_tool_not_found():
    """Test: unknown tool returns error."""
    print("\n" + "=" * 70)
    print("TEST: unknown tool returns error")
    print("=" * 70)

    message = Message(
        source="test",
        target="tools",
        action="dispatch_tool",
        payload={
            "tool": "nonexistent_tool",
            "data": {},
        }
    )

    print(f"\nSending message to: {message.target}")
    print(f"Tool: {message.payload.get('tool')}")

    result = dispatch(message)

    print(f"\nResponse:")
    print(f"  Success: {result.success}")
    print(f"  Error: {result.error}")

    if not result.success and "not found" in result.error.lower():
        print(f"\n✓ PASS: unknown tool returns proper error")
        return True
    else:
        print(f"\n✗ FAIL: expected not-found error")
        return False


def main():
    """Run all tests."""
    print("\n" + "╔" + "=" * 68 + "╗")
    print("║" + " TIER 0: TOOL SERVICE BRIDGE TESTS ".center(68) + "║")
    print("╚" + "=" * 68 + "╝")

    tests = [
        ("Execute Command", test_tool_dispatch_execute_command),
        ("Not Implemented Error", test_tool_dispatch_not_implemented),
        ("Tool Not Found", test_tool_not_found),
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
    import sys
    success = main()
    sys.exit(0 if success else 1)
