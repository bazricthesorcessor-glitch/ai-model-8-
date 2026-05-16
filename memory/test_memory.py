"""
Memory system tests - verify lightweight task state tracking.
"""

import sys
import os
import time
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory import Memory, MEMORY


def test_basic_read_write():
    """Test 1: Basic read/write operations."""
    print("\n" + "=" * 70)
    print("TEST 1: Basic Read/Write Operations")
    print("=" * 70)

    mem = Memory()

    # Write task
    task = {"id": "task-001", "name": "Login form", "status": "in_progress"}
    mem.update_task(task)

    # Read task
    retrieved = mem.get_task()
    assert retrieved == task, "Task mismatch"
    print(f"✓ Task stored and retrieved: {retrieved['name']}")

    # Write action
    action = {"tool": "click_element", "result": {"success": True, "duration_ms": 45.23}}
    mem.update_action(action)

    # Read action
    retrieved = mem.get_action()
    assert retrieved == action, "Action mismatch"
    print(f"✓ Action stored and retrieved: {retrieved['tool']}")

    # Set status
    mem.set_status("executing")
    assert mem.get_status() == "executing", "Status mismatch"
    print(f"✓ Status: {mem.get_status()}")

    print("\n✓ TEST 1 PASSED")


def test_context_merge():
    """Test 2: Context merging (not overwriting)."""
    print("\n" + "=" * 70)
    print("TEST 2: Context Merging")
    print("=" * 70)

    mem = Memory()

    # Set initial context
    mem.update_context({"step": 1, "username": "john"})
    context = mem.get_context()
    assert context == {"step": 1, "username": "john"}
    print(f"✓ Initial context: {context}")

    # Merge new values (shouldn't overwrite)
    mem.update_context({"step": 2, "password_entered": True})
    context = mem.get_context()
    assert context["step"] == 2, "Step should be updated"
    assert context["username"] == "john", "Username should remain"
    assert context["password_entered"] == True, "New field should be added"
    print(f"✓ Merged context: {context}")

    print("\n✓ TEST 2 PASSED")


def test_preferences():
    """Test 3: User preferences."""
    print("\n" + "=" * 70)
    print("TEST 3: User Preferences")
    print("=" * 70)

    mem = Memory()

    prefs = {
        "approval_required": True,
        "auto_retry": True,
        "default_timeout": 10,
    }
    mem.set_preferences(prefs)

    retrieved = mem.get_preferences()
    assert retrieved == prefs, "Preferences mismatch"
    print(f"✓ Preferences: {retrieved}")

    # Add preference
    mem.set_preference("screenshot_on_error", True)
    prefs = mem.get_preferences()
    assert len(prefs) == 4, "Should have 4 preferences"
    print(f"✓ Added preference: {prefs}")

    print("\n✓ TEST 3 PASSED")


def test_status_validation():
    """Test 4: Status validation."""
    print("\n" + "=" * 70)
    print("TEST 4: Status Validation")
    print("=" * 70)

    mem = Memory()

    # Valid statuses
    valid_statuses = ["idle", "executing", "waiting_approval", "error"]
    for status in valid_statuses:
        mem.set_status(status)
        assert mem.get_status() == status
        print(f"✓ Valid status: {status}")

    # Invalid status
    try:
        mem.set_status("invalid_status")
        assert False, "Should raise ValueError"
    except ValueError as e:
        print(f"✓ Rejected invalid status: {e}")

    print("\n✓ TEST 4 PASSED")


def test_change_log():
    """Test 5: Change log for debugging."""
    print("\n" + "=" * 70)
    print("TEST 5: Change Log")
    print("=" * 70)

    mem = Memory()

    # Make changes
    mem.set_status("executing")
    mem.update_context({"step": 1})
    mem.set_status("error")
    mem.update_context({"error": "timeout"})

    # Check change log
    changes = mem.get_change_log()
    assert len(changes) == 4, "Should have 4 changes"
    print(f"✓ Change log has {len(changes)} entries")

    for i, change in enumerate(changes, 1):
        print(f"  {i}. {change['field']}: {change['old_value']} → {change['new_value']}")

    # Test max 10 changes
    for i in range(10):
        mem.set_status("idle" if i % 2 == 0 else "executing")

    changes = mem.get_change_log()
    assert len(changes) <= 10, "Should keep max 10 changes"
    print(f"✓ Change log capped at {len(changes)} entries")

    print("\n✓ TEST 5 PASSED")


def test_subscribers():
    """Test 6: Subscriber notifications."""
    print("\n" + "=" * 70)
    print("TEST 6: Subscriber Notifications")
    print("=" * 70)

    mem = Memory()
    results = []

    # Subscribe to status changes
    def on_status_change(new_status):
        results.append(f"Status: {new_status}")

    mem.on_change("current_status", on_status_change)

    # Trigger changes
    mem.set_status("executing")
    mem.set_status("error")
    mem.set_status("idle")

    assert len(results) == 3, "Should have 3 notifications"
    print(f"✓ Received {len(results)} notifications:")
    for result in results:
        print(f"  - {result}")

    print("\n✓ TEST 6 PASSED")


def test_thread_safety():
    """Test 7: Thread safety."""
    print("\n" + "=" * 70)
    print("TEST 7: Thread Safety")
    print("=" * 70)

    mem = Memory()
    results = {"updates": 0, "reads": 0}

    def writer(thread_id, iterations):
        for i in range(iterations):
            mem.set_status("executing" if i % 2 == 0 else "idle")
            mem.update_context({"thread": thread_id, "iteration": i})
            results["updates"] += 1

    def reader(iterations):
        for _ in range(iterations):
            mem.get_state()
            results["reads"] += 1

    # Start multiple threads
    threads = []
    for i in range(3):
        t = threading.Thread(target=writer, args=(i, 10))
        threads.append(t)
        t.start()

    for _ in range(3):
        t = threading.Thread(target=reader, args=(20,))
        threads.append(t)
        t.start()

    # Wait for all threads
    for t in threads:
        t.join()

    print(f"✓ Completed {results['updates']} writes and {results['reads']} reads")
    print(f"✓ Final state: {mem.get_state()}")

    print("\n✓ TEST 7 PASSED")


def test_snapshots_and_diffs():
    """Test 8: Snapshots and diffs."""
    print("\n" + "=" * 70)
    print("TEST 8: Snapshots and Diffs")
    print("=" * 70)

    mem = Memory()

    # Take snapshot
    snapshot1 = mem.get_snapshot()
    print(f"✓ Snapshot 1 taken")

    # Make changes
    mem.update_task({"id": "task-001", "name": "Login"})
    mem.set_status("executing")
    mem.update_context({"step": 1})

    # Take another snapshot
    snapshot2 = mem.get_snapshot()
    print(f"✓ Snapshot 2 taken after changes")

    # Compare
    current = mem.get_state()
    assert snapshot1 != snapshot2, "Snapshots should differ"
    assert current == snapshot2, "Current should match snapshot 2"
    print(f"✓ Snapshots differ as expected")

    print("\n✓ TEST 8 PASSED")


def test_clear():
    """Test 9: Memory clear."""
    print("\n" + "=" * 70)
    print("TEST 9: Memory Clear")
    print("=" * 70)

    mem = Memory()

    # Add data
    mem.update_task({"id": "task-001"})
    mem.set_status("executing")
    mem.update_context({"step": 1})

    assert mem.get_task() is not None, "Task should exist"
    print(f"✓ Memory has data before clear")

    # Clear
    mem.clear()

    assert mem.get_task() is None, "Task should be cleared"
    assert mem.get_status() == "idle", "Status should reset"
    assert mem.get_context() == {}, "Context should be empty"
    print(f"✓ Memory cleared")

    print("\n✓ TEST 9 PASSED")


def test_global_memory():
    """Test 10: Global MEMORY instance."""
    print("\n" + "=" * 70)
    print("TEST 10: Global MEMORY Instance")
    print("=" * 70)

    # Use global instance
    MEMORY.clear()
    MEMORY.update_task({"id": "global-task"})
    MEMORY.set_status("executing")

    # Access from "different" location
    task = MEMORY.get_task()
    status = MEMORY.get_status()

    assert task["id"] == "global-task", "Global task access"
    assert status == "executing", "Global status access"
    print(f"✓ Global MEMORY instance works: task={task['id']}, status={status}")

    print("\n✓ TEST 10 PASSED")


def test_persistent_pin_and_search():
    """Test 11: Pinned memory persists into search results."""
    print("\n" + "=" * 70)
    print("TEST 11: Pinned Memory And Search")
    print("=" * 70)

    mem = Memory()
    mem.clear()
    mem.start_session("test_persistent_pin_and_search")
    mem.pin_memory(
        "Elzyrra uses Brave and the user uses Firefox.",
        category="browser_policy",
        tags=["browser", "policy"],
        priority="critical",
    )

    result = mem.search_memory("Brave Firefox")
    assert result["total_matches"] >= 1, "Pinned memory should be searchable"
    print(f"✓ Search found {result['total_matches']} matches")

    print("\n✓ TEST 11 PASSED")


def test_large_context_window():
    """Test 12: Context window builder supports 10M-token budgets."""
    print("\n" + "=" * 70)
    print("TEST 12: Large Context Window")
    print("=" * 70)

    mem = Memory()
    mem.clear()
    mem.start_session("test_large_context_window")
    mem.record_user_message("Remember the browser policy and long-term task priorities.")
    mem.pin_memory("Browser policy: Elzyrra uses Brave; user uses Firefox.")

    context = mem.build_context_window("What browser policy applies?")
    assert context["max_tokens"] == 10_000_000
    assert context["fits_budget"] is True
    assert context["payload"]["important_memory"], "Important memory should be present"
    print(f"✓ Built context window with approx {context['approx_tokens']} tokens")

    print("\n✓ TEST 12 PASSED")


def run_all_tests():
    """Run all Memory tests."""
    print("\n" + "=" * 70)
    print("MEMORY SYSTEM TEST SUITE")
    print("=" * 70)
    print("\nTesting:")
    print("  1. Basic read/write")
    print("  2. Context merging")
    print("  3. User preferences")
    print("  4. Status validation")
    print("  5. Change log")
    print("  6. Subscriber notifications")
    print("  7. Thread safety")
    print("  8. Snapshots and diffs")
    print("  9. Memory clear")
    print("  10. Global instance")
    print("  11. Pinned memory search")
    print("  12. Large context window")

    try:
        test_basic_read_write()
        test_context_merge()
        test_preferences()
        test_status_validation()
        test_change_log()
        test_subscribers()
        test_thread_safety()
        test_snapshots_and_diffs()
        test_clear()
        test_global_memory()
        test_persistent_pin_and_search()
        test_large_context_window()

        print("\n" + "=" * 70)
        print("✓ ALL MEMORY TESTS PASSED")
        print("=" * 70)
        return True

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
