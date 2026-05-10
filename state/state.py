"""
State tracking - maintains current system status.
NOT conversation history - only actionable state.
In-memory for now, will be persisted to memory module later.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SystemState:
    """Current system execution state."""

    current_action: Optional[str] = None  # What's being executed
    status: str = "idle"  # idle, executing, waiting_approval
    execution_history: List[Dict[str, Any]] = field(
        default_factory=list
    )  # [{"action": ..., "result": ..., "timestamp": ...}]
    tool_results: Dict[str, Any] = field(default_factory=dict)  # Latest tool outputs
    errors: List[Dict[str, Any]] = field(default_factory=list)  # Error log


# Global state instance (in-memory)
_global_state = SystemState()


def update_state(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update system state with action result.

    Args:
        data: Dict with 'action', 'result', optional 'error'

    Returns:
        Updated state dict
    """
    global _global_state

    action = data.get("action", "unknown")
    result = data.get("result", {})
    error = data.get("error")
    status = data.get("status", _global_state.status)

    # Add to execution history
    history_entry = {
        "action": action,
        "result": result,
        "timestamp": datetime.now().isoformat(),
    }
    _global_state.execution_history.append(history_entry)

    # Keep only last 50 actions to avoid memory bloat
    if len(_global_state.execution_history) > 50:
        _global_state.execution_history = _global_state.execution_history[-50:]

    # Update tool results
    if result:
        _global_state.tool_results = result

    # Update status
    _global_state.current_action = action
    _global_state.status = status

    # Log errors
    if error:
        _global_state.errors.append(
            {"action": action, "error": error, "timestamp": datetime.now().isoformat()}
        )
        if len(_global_state.errors) > 20:
            _global_state.errors = _global_state.errors[-20:]

    return {"success": True, "state": get_state()}


def get_state() -> Dict[str, Any]:
    """Get current system state."""
    global _global_state

    return {
        "current_action": _global_state.current_action,
        "status": _global_state.status,
        "execution_history": _global_state.execution_history,
        "tool_results": _global_state.tool_results,
        "errors": _global_state.errors,
        "timestamp": datetime.now().isoformat(),
    }


def get_last_actions(n: int = 5) -> List[Dict[str, Any]]:
    """
    Get last N actions for context in brain.
    Used to provide context to LLM for decision making.
    """
    global _global_state
    return _global_state.execution_history[-n:]


def clear_state() -> Dict[str, Any]:
    """Clear all state between sessions."""
    global _global_state
    _global_state = SystemState()
    return {"success": True, "message": "State cleared"}
