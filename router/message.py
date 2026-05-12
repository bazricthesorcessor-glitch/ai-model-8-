"""
Router packet schema - source/target/action/payload.
Strict structure for all inter-module communication.
"""

from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Message:
    """
    Router packet schema - strictly defined for all inter-module communication.
    Every message MUST know source, target, and action.

    Routes: target determines where message goes
    - source: "scout", "executor", "coder", "query_maker1", etc.
    - target: "executor", "query_maker1", "coder", "thinker", etc.
    - action: "dispatch_model", "dispatch_tool", "run_query_maker", etc.
    """

    source: str  # Who sent this: "scout", "executor", etc.
    target: str  # Who receives this: "executor", "coder", "query_maker1", etc.
    action: str  # What to do: "dispatch_model", "dispatch_tool", "run_query_maker", etc.
    payload: Dict[str, Any] = field(default_factory=dict)  # Data for the target
    context: Dict[str, Any] = field(default_factory=dict)  # Execution context
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self):
        """Validate schema after creation."""
        valid_actions = {
            "dispatch_model",
            "dispatch_tool",
            "run_query_maker",
            "restart_service",
            "health_check",
            "queue_task",
            "abort_task",
            "record_state",
            "get_state",
            "verify_result",
        }

        if self.action not in valid_actions:
            raise ValueError(f"action must be one of {valid_actions}, got {self.action}")
        if not self.source:
            raise ValueError("source cannot be empty")
        if not self.target:
            raise ValueError("target cannot be empty")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict for logging."""
        return {
            "source": self.source,
            "target": self.target,
            "action": self.action,
            "payload": self.payload,
            "context": self.context,
            "timestamp": self.timestamp,
        }


@dataclass
class Response:
    """Response from router action execution - same source/target pattern."""
    source: str  # Who generated this response (the service that processed it)
    success: bool
    result: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "timestamp": self.timestamp,
        }
