"""
Executor core - runs steps, handles modes, manages retries, dispatches tools.
Extracted approval workflow from ai-exec.py.
Enhanced with: retry logic, tool registry dispatch, state integration, performance tracking.
"""

import subprocess
import time
from typing import Dict, List, Any, Optional, Callable
from config import EXECUTION_CONFIG
from brain import check_safety
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from state import update_state
from tools import REGISTRY


# Tool handler registry - maps tool names to handler functions
_TOOL_HANDLERS: Dict[str, Callable] = {}


def register_tool_handler(tool_name: str, handler: Callable) -> None:
    """Register a tool handler function."""
    _TOOL_HANDLERS[tool_name] = handler


def get_tool_handler(tool_name: str) -> Optional[Callable]:
    """Get handler for a tool, or None if not found."""
    return _TOOL_HANDLERS.get(tool_name)


def execute(message) -> Dict[str, Any]:
    """
    Execute a message with steps.

    Args:
        message: Message object with action, platform, mode, steps

    Returns:
        Dict with execution results including timing and retry info
    """
    mode = message.mode  # visible, headless, hybrid
    steps = message.steps
    platform = message.platform
    start_time = time.perf_counter()

    results = []

    for step_idx, step in enumerate(steps):
        # Retry loop
        max_retries = step.get("max_retries", EXECUTION_CONFIG.get("max_retries", 1))
        retryable = step.get("retryable", True)
        attempt = 0
        result = None

        while attempt < max_retries:
            step_start = time.perf_counter()
            try:
                if mode == "visible":
                    result = _execute_visible(step, step_idx, len(steps), attempt, max_retries)
                elif mode == "headless":
                    result = _execute_headless(step, step_idx, len(steps), attempt, max_retries)
                elif mode == "hybrid":
                    if step.get("visible", False):
                        result = _execute_visible(step, step_idx, len(steps), attempt, max_retries)
                    else:
                        result = _execute_headless(step, step_idx, len(steps), attempt, max_retries)
                else:
                    result = {"success": False, "error": f"Unknown mode: {mode}"}

                # Add timing info
                result["duration_ms"] = (time.perf_counter() - step_start) * 1000
                result["step_index"] = step_idx
                result["attempt"] = attempt

                # If successful, break retry loop
                if result.get("success", False):
                    break

                # If failed but retryable, prepare for retry
                if retryable and attempt < max_retries - 1:
                    attempt += 1
                    wait_time = 2 ** attempt  # Exponential backoff: 2s, 4s, 8s
                    print(f"\n[Retry {attempt}/{max_retries - 1}] Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    break

            except Exception as e:
                step_duration = (time.perf_counter() - step_start) * 1000
                result = {
                    "success": False,
                    "error": str(e),
                    "step_index": step_idx,
                    "attempt": attempt,
                    "duration_ms": step_duration,
                }
                if retryable and attempt < max_retries - 1:
                    attempt += 1
                    wait_time = 2 ** attempt
                    print(f"\n[Retry {attempt}/{max_retries - 1}] Exception, waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    break

        # Record result and update state
        if result:
            results.append(result)
            _update_execution_state(step_idx, result, len(steps))

        # Check stop_on_error
        if not result.get("success", False) and step.get("stop_on_error", True):
            break

    # Final execution summary
    total_duration = (time.perf_counter() - start_time) * 1000
    all_successful = all(r.get("success", False) for r in results)

    # Final state update
    update_state(
        {
            "action": "execute_complete",
            "result": {
                "steps_executed": len(results),
                "steps_total": len(steps),
                "all_successful": all_successful,
                "duration_ms": total_duration,
            },
            "status": "idle",
        }
    )

    return {
        "success": all_successful,
        "results": results,
        "total_steps": len(steps),
        "executed_steps": len(results),
        "total_duration_ms": total_duration,
    }


def _update_execution_state(step_idx: int, result: Dict[str, Any], total_steps: int) -> None:
    """Update system state after each step execution."""
    update_state(
        {
            "action": f"execute_step_{step_idx}",
            "result": result,
            "status": "idle" if result.get("success") else "executing",
        }
    )


def _execute_visible(
    step: Dict[str, Any], step_num: int, total_steps: int, attempt: int = 0, max_retries: int = 1
) -> Dict[str, Any]:
    """Execute in visible mode - user sees actions, gets approvals."""
    tool_name = step.get("tool", "unknown")
    params = step.get("params", step.get("data", {}))

    # Try registered handler first (backward compatibility)
    handler = get_tool_handler(tool_name)
    if handler:
        # Convert to old-style data parameter for backward compatibility
        data = step.get("data", {})
        return handler(data, step_num, total_steps, attempt, max_retries, mode="visible")

    # Fallback: Try REGISTRY lookup for direct tool execution
    return _execute_tool_from_registry(
        tool_name, params, step_num, total_steps, attempt, max_retries, mode="visible"
    )


def _execute_headless(
    step: Dict[str, Any], step_num: int, total_steps: int, attempt: int = 0, max_retries: int = 1
) -> Dict[str, Any]:
    """Execute in headless mode - background execution, no UI."""
    tool_name = step.get("tool", "unknown")
    params = step.get("params", step.get("data", {}))

    # Try registered handler first (backward compatibility)
    handler = get_tool_handler(tool_name)
    if handler:
        # Convert to old-style data parameter for backward compatibility
        data = step.get("data", {})
        return handler(data, step_num, total_steps, attempt, max_retries, mode="headless")

    # Fallback: Try REGISTRY lookup for direct tool execution
    return _execute_tool_from_registry(
        tool_name, params, step_num, total_steps, attempt, max_retries, mode="headless"
    )


def _execute_tool_from_registry(
    tool_name: str, params: Dict[str, Any], step_num: int, total_steps: int,
    attempt: int, max_retries: int, mode: str
) -> Dict[str, Any]:
    """
    Execute a tool by looking it up in the REGISTRY.
    Fallback mechanism for tools not in the handler registry.

    Args:
        tool_name: Name of the tool to execute
        params: Parameters for the tool
        step_num, total_steps: Step numbering for display
        attempt, max_retries: Retry information
        mode: Execution mode (visible, headless)

    Returns:
        Standardized result dict
    """
    tool = REGISTRY.get(tool_name)
    if not tool:
        return {"success": False, "error": f"Unknown tool: {tool_name}"}

    # In visible mode, show what we're about to do
    if mode == "visible":
        print(f"\n[Step {step_num}/{total_steps}] Tool: {tool_name}")
        print(f"Description: {tool.description}")
        if attempt > 0:
            print(f"[Attempt {attempt + 1}/{max_retries}]")

        if EXECUTION_CONFIG.get("require_approval", True):
            completer = WordCompleter(["y", "n"], ignore_case=True)
            answer = prompt("Execute? [y/N]: ", completer=completer).lower()
            if answer != "y":
                return {"success": False, "error": "User cancelled"}

    # Execute the tool
    try:
        result = tool.run(params, context={"step_num": step_num, "total_steps": total_steps})
        return result
    except Exception as e:
        return {
            "success": False,
            "error": f"Tool execution failed: {str(e)}",
            "tool": tool_name,
        }




def _handle_run_command(
    data: Dict[str, Any], step_num: int, total_steps: int, attempt: int, max_retries: int, mode: str
) -> Dict[str, Any]:
    """Handle run_command tool execution."""
    command = data.get("command", "")

    if not command:
        return {"success": False, "error": "No command provided"}

    is_safe, severity, reason = check_safety(command)

    if mode == "visible":
        print(f"\n[Step {step_num}/{total_steps}] Command: {command}")
        if attempt > 0:
            print(f"[Attempt {attempt + 1}/{max_retries}]")
        print(f"Safety: {severity} - {reason}")

        if severity == "blocked":
            print("[BLOCKED] Command not allowed")
            return {"success": False, "error": f"Blocked: {reason}"}

        if severity == "warning":
            print(f"[WARNING] {reason}")

        if EXECUTION_CONFIG.get("require_approval", True):
            completer = WordCompleter(["y", "n", "e", "d"], ignore_case=True)
            answer = prompt("Execute? [y/N/e(dit)/d(ry-run)]: ", completer=completer).lower()

            if answer == "y":
                return _run_command(command)
            elif answer == "e":
                edited = prompt("Edit command: ", default=command)
                return _handle_run_command(
                    {"command": edited}, step_num, total_steps, attempt, max_retries, mode
                )
            elif answer == "d":
                print(f"[DRY RUN] Would execute: {command}")
                return {"success": True, "dry_run": True, "command": command}
            else:
                print("[CANCELLED]")
                return {"success": False, "error": "User cancelled"}
        else:
            return _run_command(command)

    elif mode == "headless":
        if severity == "blocked":
            return {"success": False, "error": f"Blocked: {reason}"}

        return _run_command(command)

    return {"success": False, "error": f"Unknown mode: {mode}"}


def _handle_click_button(
    data: Dict[str, Any], step_num: int, total_steps: int, attempt: int, max_retries: int, mode: str
) -> Dict[str, Any]:
    """Handle click_button tool execution (UI automation)."""
    selector = data.get("selector")
    x = data.get("x")
    y = data.get("y")

    if not selector and not (x and y):
        return {"success": False, "error": "Need selector or x,y coordinates"}

    if mode == "visible":
        action_str = f"selector={selector}" if selector else f"x={x}, y={y}"
        print(f"\n[Step {step_num}/{total_steps}] Click: {action_str}")

        if EXECUTION_CONFIG.get("require_approval", True):
            completer = WordCompleter(["y", "n"], ignore_case=True)
            answer = prompt("Execute? [y/N]: ", completer=completer).lower()
            if answer != "y":
                return {"success": False, "error": "User cancelled"}

    # Placeholder: actual UI automation would go here
    return {
        "success": True,
        "action": "click_button",
        "selector": selector,
        "coordinates": (x, y) if x and y else None,
        "note": "UI automation not yet implemented",
    }


def _handle_type_text(
    data: Dict[str, Any], step_num: int, total_steps: int, attempt: int, max_retries: int, mode: str
) -> Dict[str, Any]:
    """Handle type_text tool execution (UI automation)."""
    text = data.get("text")
    selector = data.get("selector")

    if not text:
        return {"success": False, "error": "No text provided"}

    if mode == "visible":
        print(f"\n[Step {step_num}/{total_steps}] Type text into: {selector or 'focused element'}")

        if EXECUTION_CONFIG.get("require_approval", True):
            completer = WordCompleter(["y", "n"], ignore_case=True)
            answer = prompt("Execute? [y/N]: ", completer=completer).lower()
            if answer != "y":
                return {"success": False, "error": "User cancelled"}

    # Placeholder: actual UI automation would go here
    return {
        "success": True,
        "action": "type_text",
        "text_length": len(text),
        "selector": selector,
        "note": "UI automation not yet implemented",
    }


def _handle_read_screen(
    data: Dict[str, Any], step_num: int, total_steps: int, attempt: int, max_retries: int, mode: str
) -> Dict[str, Any]:
    """Handle read_screen tool execution (vision/OCR)."""
    region = data.get("region")  # Optional: (x, y, width, height)

    if mode == "visible":
        print(f"\n[Step {step_num}/{total_steps}] Reading screen{f' region {region}' if region else ''}")

    # Placeholder: actual vision/OCR would go here
    return {
        "success": True,
        "action": "read_screen",
        "region": region,
        "text": "[Vision/OCR not yet implemented - would return screen text here]",
        "note": "Vision capability not yet implemented",
    }


def _run_command(command: str) -> Dict[str, Any]:
    """Actually run a shell command and capture output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            executable=EXECUTION_CONFIG.get("shell", "/bin/bash"),
            timeout=EXECUTION_CONFIG.get("timeout", 300),
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "command": command,
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Command timed out after {EXECUTION_CONFIG['timeout']}s",
            "command": command,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "command": command,
        }


# ============================================================================
# INITIALIZE TOOL HANDLERS
# ============================================================================

register_tool_handler("run_command", _handle_run_command)
register_tool_handler("click_button", _handle_click_button)
register_tool_handler("type_text", _handle_type_text)
register_tool_handler("read_screen", _handle_read_screen)

