#!/usr/bin/env python3
"""
Integration tests - verify all modules work together correctly.
Tests the complete flow: input → brain → router → executor → state.
"""

import sys
import os
from datetime import datetime

# Import all modules
from router import route
from router.message import Message, Response
from brain import analyze_intent, check_safety, generate_action
from executor import execute
from state import get_state, clear_state
from memory import MEMORY


def test_integration_basic():
    """Test 1: Basic integration flow."""
    print("\n" + "=" * 70)
    print("TEST 1: Basic Integration Flow")
    print("=" * 70)

    clear_state()
    MEMORY.clear()

    # User input
    user_input = "hello"
    print(f"\nUser input: {user_input}")

    # Step 1: Intent analysis
    intent = analyze_intent(user_input)
    assert intent["intent"] in ["conversational", "command"], f"Invalid intent: {intent['intent']}"
    print(f"✓ Intent: {intent['intent']}")

    # Step 2: Safety check
    is_safe, severity, reason = check_safety(user_input)
    assert is_safe, f"Safety check failed: {reason}"
    print(f"✓ Safety check passed")

    # Step 3: Action generation
    action = generate_action(user_input, MEMORY.get_context())
    assert action.get("action"), "No action generated"
    print(f"✓ Action generated: {action['action']}")

    # Step 4: Create message and route
    message = Message(
        action=action.get("action", "execute"),
        platform=action.get("platform", "cli"),
        mode=action.get("mode", "visible"),
        data=action.get("data", {}),
        steps=action.get("steps", []),
        context=action.get("context", {})
    )
    assert isinstance(message, Message), "Message creation failed"
    print(f"✓ Message created: {message.action}")

    # Step 5: Route message
    result = route(message)
    assert isinstance(result, Response), f"Expected Response, got {type(result)}"
    print(f"✓ Message routed successfully")

    print("\n✓ TEST 1 PASSED")


def test_integration_safety_blocking():
    """Test 2: Safety blocking prevents execution."""
    print("\n" + "=" * 70)
    print("TEST 2: Safety Blocking")
    print("=" * 70)

    clear_state()
    MEMORY.clear()

    user_input = "rm -rf /"
    print(f"\nUser input: {user_input}")

    is_safe, severity, reason = check_safety(user_input)
    assert not is_safe, "Dangerous command was not blocked"
    assert severity == "blocked", f"Expected 'blocked' severity, got '{severity}'"
    print(f"✓ Blocked: {reason}")

    print("\n✓ TEST 2 PASSED")


def test_integration_conversational():
    """Test 3: Conversational intent detection."""
    print("\n" + "=" * 70)
    print("TEST 3: Conversational Intent")
    print("=" * 70)

    clear_state()
    MEMORY.clear()

    conversational_inputs = [
        "hello",
        "hi",
        "how are you?",
        "what's the weather?",
    ]

    for user_input in conversational_inputs:
        intent = analyze_intent(user_input)
        assert intent["intent"] == "conversational", f"Failed to detect conversational intent for: {user_input}"
        print(f"✓ {user_input} → conversational")

    print("\n✓ TEST 3 PASSED")


def test_integration_command():
    """Test 4: Command intent detection."""
    print("\n" + "=" * 70)
    print("TEST 4: Command Intent")
    print("=" * 70)

    clear_state()
    MEMORY.clear()

    command_inputs = [
        "list files",
        "create a backup",
        "check the system",
    ]

    for user_input in command_inputs:
        intent = analyze_intent(user_input)
        assert intent["intent"] == "command", f"Failed to detect command intent for: {user_input}"
        print(f"✓ {user_input} → command")

    print("\n✓ TEST 4 PASSED")


def test_integration_memory_tracking():
    """Test 5: Memory system tracks current state."""
    print("\n" + "=" * 70)
    print("TEST 5: Memory Tracking")
    print("=" * 70)

    clear_state()
    MEMORY.clear()

    # Update memory with task
    task = {
        "id": "task-001",
        "name": "Test task",
        "status": "in_progress"
    }
    MEMORY.update_task(task)
    retrieved = MEMORY.get_task()
    assert retrieved == task, "Task not tracked correctly"
    print(f"✓ Task stored: {task['name']}")

    # Update context
    MEMORY.update_context({"step": 1, "username": "testuser"})
    context = MEMORY.get_context()
    assert context["step"] == 1, "Context not updated"
    assert context["username"] == "testuser", "Context merge failed"
    print(f"✓ Context updated with merge")

    # Update status
    MEMORY.set_status("executing")
    status = MEMORY.get_status()
    assert status == "executing", "Status not updated"
    print(f"✓ Status set: {status}")

    print("\n✓ TEST 5 PASSED")


def test_integration_full_pipeline():
    """Test 6: Full pipeline with action generation and execution."""
    print("\n" + "=" * 70)
    print("TEST 6: Full Pipeline")
    print("=" * 70)

    clear_state()
    MEMORY.clear()

    user_input = "list files"
    print(f"\nUser input: {user_input}")

    # Complete pipeline
    intent = analyze_intent(user_input)
    print(f"1. Intent: {intent['intent']}")

    is_safe, severity, reason = check_safety(user_input)
    print(f"2. Safety: {severity}")
    assert is_safe, "Safety check failed"

    action = generate_action(user_input, MEMORY.get_context())
    print(f"3. Action: {action['action']}")

    message = Message(
        action=action.get("action", "execute"),
        platform=action.get("platform", "cli"),
        mode=action.get("mode", "visible"),
        data=action.get("data", {}),
        steps=action.get("steps", []),
        context=action.get("context", {})
    )
    print(f"4. Message created")

    result = route(message)
    print(f"5. Routed: {result.action}")

    state = get_state()
    print(f"6. State updated: {state['current_action']}")

    assert result.success, "Execution failed"
    print(f"\n✓ Full pipeline completed successfully")

    print("\n✓ TEST 6 PASSED")


def test_integration_state_tracking():
    """Test 7: State module tracks execution history."""
    print("\n" + "=" * 70)
    print("TEST 7: State Tracking")
    print("=" * 70)

    clear_state()
    MEMORY.clear()

    # Execute message
    message = Message(
        action="execute",
        platform="cli",
        mode="visible",
        data={},
        steps=[]
    )

    result = route(message)

    # Check state
    state = get_state()
    assert state["current_action"], "Current action not set"
    assert state["status"] in ["idle", "executing"], f"Invalid status: {state['status']}"
    print(f"✓ State tracked: {state['current_action']}")

    print("\n✓ TEST 7 PASSED")


def run_all_tests():
    """Run all integration tests."""
    print("\n" + "=" * 70)
    print("INTEGRATION TEST SUITE")
    print("=" * 70)

    tests = [
        test_integration_basic,
        test_integration_safety_blocking,
        test_integration_conversational,
        test_integration_command,
        test_integration_memory_tracking,
        test_integration_full_pipeline,
        test_integration_state_tracking,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n✗ TEST FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
