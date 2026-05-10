#!/usr/bin/env python3
"""
Integration entry point for the modular AI assistant system.
Demonstrates complete flow: user input → brain decision → execution → state tracking.
"""

import sys
import json
from datetime import datetime
from typing import Dict, Any, Tuple

# Core modules
from router import route
from router.message import Message, Response
from brain import analyze_intent, check_safety, generate_action
from executor import execute
from state import get_state as get_system_state, clear_state as clear_system_state
from memory import MEMORY


def print_header(text: str) -> None:
    """Print formatted header."""
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")


def print_section(title: str, content: str = "") -> None:
    """Print formatted section."""
    print(f"\n→ {title}")
    if content:
        print(f"  {content}")


def format_result(data: Dict[str, Any]) -> str:
    """Format result for display."""
    return json.dumps(data, indent=2)


def get_user_approval(action: Dict[str, Any]) -> bool:
    """Ask user for approval of action."""
    print_section("⚠ APPROVAL REQUIRED", f"Action: {action.get('action', 'unknown')}")

    if action.get("steps"):
        print("  Steps:")
        for i, step in enumerate(action["steps"], 1):
            print(f"    {i}. {step.get('tool', 'unknown')} - {step.get('data', {})}")

    response = input("\n  Approve? [y/n]: ").strip().lower()
    return response == "y"


def display_state_summary() -> None:
    """Display current system state summary."""
    state = get_system_state()

    if isinstance(state, dict):
        if state.get("current_action"):
            print_section(
                "Current Action",
                f"{state.get('current_action', 'N/A')}"
            )

        if state.get("execution_history"):
            print_section("Recent Execution History")
            for item in state["execution_history"][-3:]:  # Last 3 items
                action = item.get('action', 'N/A')
                result = item.get('result', {})
                print(f"  → {action}: {result}")

        if state.get("status") != "idle":
            print_section("System Status", f"Current: {state.get('status', 'N/A')}")


def display_memory_info() -> None:
    """Display memory system info."""
    memory_state = MEMORY.get_state()

    if memory_state.get("current_task"):
        task = memory_state["current_task"]
        print_section("Task Memory", f"{task.get('name', 'N/A')} ({task.get('status', 'N/A')})")

    if memory_state.get("current_status") != "idle":
        print_section("Memory Status", memory_state.get("current_status", "N/A"))

    if memory_state.get("context"):
        print_section("Context Keys", str(list(memory_state["context"].keys())))


def main_interactive() -> None:
    """Interactive mode: loop until user quits."""
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
                display_state_summary()
                display_memory_info()
                continue

            if user_input.lower() == "memory":
                print(MEMORY.debug_view())
                continue

            # Process user input through system
            process_user_input(user_input)

        except KeyboardInterrupt:
            print("\n\nGoodbye")
            break
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()


def process_user_input(user_input: str) -> Tuple[bool, Dict[str, Any]]:
    """
    Process user input through the full system pipeline.

    Returns:
        (success: bool, result: Dict[str, Any])
    """
    print_section("Input", user_input)

    # Step 1: Analyze intent
    print_section("Step 1: Intent Analysis")
    intent_result = analyze_intent(user_input)
    print(f"  Intent: {intent_result.get('intent', 'unknown')}")
    print(f"  Is Question: {intent_result.get('is_question', False)}")

    # Step 2: Check safety
    print_section("Step 2: Safety Check")
    is_safe, severity, reason = check_safety(user_input)
    print(f"  Safe: {is_safe}")
    if not is_safe:
        print(f"  Severity: {severity}")
        print(f"  Reason: {reason}")
        if severity == "blocked":
            print_section("Action", "Command blocked by safety filter")
            return False, {"error": reason}

        # For warning/confirmation, ask user
        if severity in ["warning", "confirmation"]:
            response = input(f"  Continue anyway? [y/n]: ").strip().lower()
            if response != "y":
                print_section("Action", "User cancelled")
                return False, {"cancelled": True}

    # Step 3: Generate action
    print_section("Step 3: Action Generation")
    try:
        action = generate_action(user_input, MEMORY.get_context())
        print(f"  Action Type: {action.get('action', 'N/A')}")
        print(f"  Platform: {action.get('platform', 'N/A')}")
        print(f"  Mode: {action.get('mode', 'N/A')}")

        if action.get("steps"):
            print(f"  Steps: {len(action['steps'])}")
            for i, step in enumerate(action["steps"], 1):
                print(f"    {i}. {step.get('tool', 'N/A')}")
    except Exception as e:
        print(f"  ✗ Failed to generate action: {e}")
        return False, {"error": str(e)}

    # Step 4: Create message and route
    print_section("Step 4: Message Routing")
    try:
        message = Message(
            action=action.get("action", "execute"),
            platform=action.get("platform", "cli"),
            mode=action.get("mode", "visible"),
            data=action.get("data", {}),
            steps=action.get("steps", []),
            context=action.get("context", {})
        )
        print(f"  Message ID: {message.timestamp}")
        print(f"  Routes to: {message.action} ({message.platform})")
    except Exception as e:
        print(f"  ✗ Failed to create message: {e}")
        return False, {"error": str(e)}

    # Step 5: Execute (with approval if needed)
    print_section("Step 5: Execution")
    try:
        # Check if approval needed
        from config import EXECUTION_CONFIG
        if EXECUTION_CONFIG.get("approval_required") and message.mode == "visible":
            if not get_user_approval(action):
                print_section("Action", "User denied approval")
                return False, {"denied": True}

        # Execute via router
        result = route(message)

        # Display result
        if isinstance(result, Response):
            if result.success:
                print("  ✓ Execution successful")
                if result.data:
                    print(f"  Result: {format_result(result.data)}")
            else:
                print(f"  ✗ Execution failed: {result.error or 'unknown error'}")

            return result.success, result.to_dict()
        else:
            # Handle dict response (fallback)
            if result.get("success"):
                print("  ✓ Execution successful")
                if result.get("data"):
                    print(f"  Result: {result['data']}")
            else:
                print(f"  ✗ Execution failed: {result.get('error', 'unknown error')}")

            return result.get("success", False), result

    except Exception as e:
        print(f"  ✗ Execution error: {e}")
        import traceback
        traceback.print_exc()
        return False, {"error": str(e)}


def main_test_command(command: str) -> None:
    """Test mode: execute single command."""
    print_header("AI Assistant - Test Mode")
    print(f"Command: {command}\n")

    clear_system_state()
    MEMORY.clear()

    success, result = process_user_input(command)

    print_header("Results")
    print(f"Success: {success}")
    print(f"Result: {format_result(result)}")

    print_header("Final State")
    display_state_summary()
    display_memory_info()


def main_demo() -> None:
    """Demo mode: run through example scenarios."""
    print_header("AI Assistant - Demo Mode")

    scenarios = [
        "list files in /tmp",
        "create a backup of my documents",
        "show me the time",
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'─' * 60}")
        print(f"Scenario {i}: {scenario}")
        print(f"{'─' * 60}")

        clear_system_state()
        MEMORY.clear()

        success, result = process_user_input(scenario)

        print(f"\n→ Scenario {i} Result: {'✓ Success' if success else '✗ Failed'}")

        if i < len(scenarios):
            print(f"\n[Continuing to next scenario...]")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Modular AI Assistant - Execute tasks via natural language"
    )
    parser.add_argument(
        "--mode",
        choices=["interactive", "test", "demo"],
        default="interactive",
        help="Execution mode"
    )
    parser.add_argument(
        "--command",
        type=str,
        help="Command to execute (for test mode)"
    )
    parser.add_argument(
        "--no-memory-init",
        action="store_true",
        help="Don't initialize memory on startup"
    )

    args = parser.parse_args()

    # Initialize memory if not disabled
    if not args.no_memory_init:
        MEMORY.update_context({"session_start": datetime.now().isoformat()})

    try:
        if args.mode == "test":
            if not args.command:
                print("Error: --command required for test mode")
                sys.exit(1)
            main_test_command(args.command)

        elif args.mode == "demo":
            main_demo()

        else:  # interactive
            main_interactive()

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
