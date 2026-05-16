#!/usr/bin/env python3
"""
Integration entry point for the modular AI assistant system.

This file now includes a dedicated memory self-test path so the runtime memory
system can be validated independently of the rest of the stack.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from typing import Any, Dict, Tuple

from memory import MEMORY, initialize_memory_system


def print_header(text: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")


def print_section(title: str, content: str = "") -> None:
    print(f"\n→ {title}")
    if content:
        print(f"  {content}")


def format_result(data: Dict[str, Any]) -> str:
    return json.dumps(data, indent=2, default=str)


def _load_runtime_modules():
    from brain import analyze_intent, check_safety, generate_action_legacy
    from router import dispatch
    from router.message import Message, Response
    from state import get_state as get_system_state, clear_state as clear_system_state

    return {
        "analyze_intent": analyze_intent,
        "check_safety": check_safety,
        "generate_action_legacy": generate_action_legacy,
        "dispatch": dispatch,
        "Message": Message,
        "Response": Response,
        "get_system_state": get_system_state,
        "clear_system_state": clear_system_state,
    }


def get_user_approval(action: Dict[str, Any]) -> bool:
    print_section("Approval Required", f"Action: {action.get('action', 'unknown')}")
    if action.get("steps"):
        print("  Steps:")
        for i, step in enumerate(action["steps"], 1):
            print(f"    {i}. {step.get('tool', 'unknown')} - {step.get('data', {})}")
    response = input("\n  Approve? [y/n]: ").strip().lower()
    return response == "y"


def display_state_summary(runtime_modules: Dict[str, Any]) -> None:
    state = runtime_modules["get_system_state"]()
    if isinstance(state, dict):
        if state.get("current_action"):
            print_section("Current Action", f"{state.get('current_action', 'N/A')}")
        if state.get("execution_history"):
            print_section("Recent Execution History")
            for item in state["execution_history"][-3:]:
                print(f"  → {item.get('action', 'N/A')}: {item.get('result', {})}")
        if state.get("status") != "idle":
            print_section("System Status", f"Current: {state.get('status', 'N/A')}")


def display_memory_info() -> None:
    memory_state = MEMORY.get_state()
    if memory_state.get("current_task"):
        task = memory_state["current_task"]
        print_section("Task Memory", f"{task.get('name', 'N/A')} ({task.get('status', 'N/A')})")
    if memory_state.get("current_status") != "idle":
        print_section("Memory Status", memory_state.get("current_status", "N/A"))
    if memory_state.get("context"):
        print_section("Context Keys", str(list(memory_state["context"].keys())))
    print_section("Memory Stats", format_result(MEMORY.get_stats()))


def process_user_input(user_input: str) -> Tuple[bool, Dict[str, Any]]:
    runtime = _load_runtime_modules()

    print_section("Input", user_input)
    MEMORY.record_user_message(user_input, tags=["interactive_input"], importance=7)

    print_section("Step 1: Intent Analysis")
    intent_result = runtime["analyze_intent"](user_input)
    print(f"  Intent: {intent_result.get('intent', 'unknown')}")
    print(f"  Is Question: {intent_result.get('is_question', False)}")
    MEMORY.update_context({"last_intent": intent_result})

    print_section("Step 2: Safety Check")
    is_safe, severity, reason = runtime["check_safety"](user_input)
    print(f"  Safe: {is_safe}")
    if not is_safe:
        print(f"  Severity: {severity}")
        print(f"  Reason: {reason}")
        if severity == "blocked":
            MEMORY.record_execution_result("safety_check", {"reason": reason}, success=False)
            return False, {"error": reason}
        if severity in ["warning", "confirmation"]:
            response = input(f"  Continue anyway? [y/n]: ").strip().lower()
            if response != "y":
                MEMORY.record_execution_result("safety_check", {"reason": "user_cancelled"}, success=False)
                return False, {"cancelled": True}

    print_section("Step 3: Action Generation")
    try:
        action = runtime["generate_action_legacy"](user_input, MEMORY.get_context())
        print(f"  Action Type: {action.get('action', 'N/A')}")
        print(f"  Platform: {action.get('platform', 'N/A')}")
        print(f"  Mode: {action.get('mode', 'N/A')}")
        MEMORY.update_task({"name": user_input, "status": "planned", "action": action.get("action")})
    except Exception as exc:
        MEMORY.record_execution_result("generate_action", {"error": str(exc)}, success=False)
        return False, {"error": str(exc)}

    print_section("Step 4: Message Routing")
    try:
        message = runtime["Message"](
            source="main",
            target=action.get("target", "tools"),
            action="dispatch_tool",
            payload=action.get("payload", {}),
            context=action.get("context", {}),
        )
        print(f"  Message ID: {message.timestamp}")
        print(f"  Routes to: {message.target}")
    except Exception as exc:
        MEMORY.record_execution_result("build_message", {"error": str(exc)}, success=False)
        return False, {"error": str(exc)}

    print_section("Step 5: Execution")
    try:
        from config import EXECUTION_CONFIG

        approval_required = EXECUTION_CONFIG.get("require_approval", True)
        if approval_required and action.get("mode") == "visible":
            if not get_user_approval(action):
                MEMORY.record_execution_result("approval", {"status": "denied"}, success=False)
                return False, {"denied": True}

        result = runtime["dispatch"](message)
        if isinstance(result, runtime["Response"]):
            MEMORY.record_execution_result(message.target, result.to_dict(), success=result.success)
            if result.success:
                return True, result.to_dict()
            return False, result.to_dict()

        MEMORY.record_execution_result(message.target, result, success=bool(result.get("success")))
        return bool(result.get("success")), result
    except Exception as exc:
        MEMORY.record_execution_result("dispatch", {"error": str(exc)}, success=False)
        return False, {"error": str(exc)}


def main_interactive() -> None:
    print_header("AI Assistant - Interactive Mode")
    print("Type your command or ask a question. Type 'exit' to quit, 'status' to see state.\n")

    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            if user_input.lower() == "exit":
                print_header("Goodbye")
                break
            if user_input.lower() == "status":
                runtime = _load_runtime_modules()
                display_state_summary(runtime)
                display_memory_info()
                continue
            if user_input.lower() == "memory":
                print(MEMORY.debug_view())
                continue
            process_user_input(user_input)
        except KeyboardInterrupt:
            print("\n\nGoodbye")
            break
        except Exception as exc:
            print(f"\n✗ Error: {exc}")


def main_test_command(command: str) -> None:
    print_header("AI Assistant - Test Mode")
    print(f"Command: {command}\n")

    runtime = _load_runtime_modules()
    runtime["clear_system_state"]()
    MEMORY.clear()

    success, result = process_user_input(command)
    print_header("Results")
    print(f"Success: {success}")
    print(f"Result: {format_result(result)}")
    print_header("Final State")
    display_state_summary(runtime)
    display_memory_info()


def main_memory_test() -> None:
    """Deterministic memory-system smoke test."""
    print_header("Perfect Memory - Self Test")
    initialize_memory_system()
    MEMORY.clear()
    session_id = MEMORY.start_session(
        session_name="main_memory_test",
        metadata={"entrypoint": "main.py", "mode": "memory-test"},
    )

    print_section("Session", session_id)

    MEMORY.set_preferences(
        {
            "context_depth": "full",
            "memory_token_budget": 10_000_000,
            "preferred_browser": "firefox",
            "assistant_browser": "brave",
        }
    )
    MEMORY.update_task({"id": "memory-001", "name": "Validate perfect memory", "status": "in_progress"})
    MEMORY.set_status("executing")
    MEMORY.record_user_message("Remember that Elzyrra uses Brave and the user uses Firefox.")
    MEMORY.record_agent_message("scout", "Confirmed browser split and stored it.")
    MEMORY.pin_memory(
        "Elzyrra uses Brave. The human user uses Firefox. Keep browser responsibilities separate.",
        category="browser_policy",
        tags=["browser", "policy", "important"],
        priority="critical",
    )
    MEMORY.update_context(
        {
            "token_budget": 10_000_000,
            "architecture": "persistent_runtime_memory",
            "test_mode": True,
        }
    )
    MEMORY.record_execution_result(
        "memory_self_test",
        {"step": "setup", "status": "complete"},
        success=True,
    )

    search_result = MEMORY.search_memory("Brave Firefox")
    context_window = MEMORY.build_context_window("What browser policy should Elzyrra follow?")
    snapshot = MEMORY.save_snapshot()
    MEMORY.set_status("complete")

    print_section("Memory View")
    print(MEMORY.debug_view())
    print_section("Search Result")
    print(format_result(search_result))
    print_section("Context Window")
    print(format_result(context_window))
    print_section("Snapshot Saved")
    print(format_result({"snapshot_keys": list(snapshot.keys())}))

    assert MEMORY.get_status() == "complete"
    assert MEMORY.get_preferences()["memory_token_budget"] == 10_000_000
    assert search_result["total_matches"] >= 1
    assert context_window["max_tokens"] == 10_000_000
    assert context_window["payload"]["important_memory"], "Important memory should not be empty"

    print_header("Memory Test Passed")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Modular AI Assistant - Execute tasks via natural language")
    parser.add_argument(
        "--mode",
        choices=["interactive", "test", "demo", "memory-test"],
        default="interactive",
        help="Execution mode",
    )
    parser.add_argument("--command", type=str, help="Command to execute (for test mode)")
    parser.add_argument("--no-memory-init", action="store_true", help="Don't initialize memory on startup")
    args = parser.parse_args()

    if not args.no_memory_init:
        initialize_memory_system()
        MEMORY.start_session(session_name=f"main_{args.mode}", metadata={"started_at": datetime.now().isoformat()})
        MEMORY.update_context({"session_start": datetime.now().isoformat()})

    try:
        if args.mode == "test":
            if not args.command:
                print("Error: --command required for test mode")
                sys.exit(1)
            main_test_command(args.command)
        elif args.mode == "demo":
            print_header("Demo Mode Not Updated")
            print("Use --mode memory-test to validate the new memory system.")
        elif args.mode == "memory-test":
            main_memory_test()
        else:
            main_interactive()
    except AssertionError as exc:
        print(f"Memory self-test failed: {exc}")
        sys.exit(1)
