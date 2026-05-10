"""
Message schema for router - strict, immutable structure.
All inter-module communication uses this schema.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Message:
    """
    Strict message schema for all module communication.

    Routes: action determines where message goes
    - "decide" → brain module
    - "execute" → executor module
    - "record_state" → state module
    - "get_state" → state module
    """

    action: str  # "decide", "execute", "record_state", "get_state"
    platform: str  # "cli", "gui", "web", "system", "vision"
    mode: str  # "visible", "headless", "hybrid"
    data: Dict[str, Any] = field(default_factory=dict)
    steps: List[Dict[str, Any]] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self):
        """Validate schema after creation."""
        valid_actions = {"decide", "execute", "record_state", "get_state"}
        valid_platforms = {"cli", "gui", "web", "system", "vision"}
        valid_modes = {"visible", "headless", "hybrid"}

        if self.action not in valid_actions:
            raise ValueError(f"action must be one of {valid_actions}, got {self.action}")
        if self.platform not in valid_platforms:
            raise ValueError(f"platform must be one of {valid_platforms}, got {self.platform}")
        if self.mode not in valid_modes:
            raise ValueError(f"mode must be one of {valid_modes}, got {self.mode}")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict for logging."""
        return {
            "action": self.action,
            "platform": self.platform,
            "mode": self.mode,
            "data": self.data,
            "steps": self.steps,
            "context": self.context,
            "timestamp": self.timestamp,
        }


@dataclass
class Response:
    """Response from router action execution."""
    success: bool
    action: str  # which action was processed
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "action": self.action,
            "data": self.data,
            "error": self.error,
            "timestamp": self.timestamp,
        }
