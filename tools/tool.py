"""
Tool base class and common interfaces.
All tools inherit from this and follow the same contract.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
import time
from datetime import datetime


class Tool(ABC):
    """Base class for all tools. Enforces consistent interface."""

    def __init__(self, name: str, platform: str, description: str):
        """
        Initialize tool.

        Args:
            name: Tool name (used for lookup)
            platform: Platform (web, keyboard, mouse, vision, system)
            description: Human-readable description
        """
        self.name = name
        self.platform = platform
        self.description = description

    @abstractmethod
    def validate_input(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate input data before execution.

        Args:
            data: Input data dict

        Returns:
            (is_valid: bool, error_message: str)
        """
        pass

    @abstractmethod
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool action.

        Args:
            data: Validated input data

        Returns:
            Result dict with 'result' key containing tool output
        """
        pass

    def run(
        self, data: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute tool with validation, timing, and result wrapping.

        Args:
            data: Input data
            context: Optional execution context

        Returns:
            Standardized result dict
        """
        start_time = time.perf_counter()

        # Validate input
        is_valid, error_msg = self.validate_input(data)
        if not is_valid:
            return self._error_result(error_msg, start_time)

        # Execute tool
        try:
            result = self.execute(data)
            if not isinstance(result, dict):
                return self._error_result("Tool must return dict", start_time)

            # Ensure success field is set
            if "success" not in result:
                result["success"] = True

        except Exception as e:
            return self._error_result(str(e), start_time)

        # Wrap result
        return self._wrap_result(result, start_time)

    def _error_result(self, error: str, start_time: float) -> Dict[str, Any]:
        """Create standardized error result."""
        duration_ms = (time.perf_counter() - start_time) * 1000
        return {
            "success": False,
            "tool": self.name,
            "duration_ms": duration_ms,
            "result": None,
            "error": error,
            "metadata": {
                "platform": self.platform,
                "timestamp": datetime.now().isoformat(),
            },
        }

    def _wrap_result(self, result: Dict[str, Any], start_time: float) -> Dict[str, Any]:
        """Wrap result with metadata."""
        duration_ms = (time.perf_counter() - start_time) * 1000
        return {
            "success": result.get("success", True),
            "tool": self.name,
            "duration_ms": duration_ms,
            "result": result.get("result"),
            "error": result.get("error"),
            "metadata": {
                "platform": self.platform,
                "timestamp": datetime.now().isoformat(),
            },
        }

    def get_info(self) -> Dict[str, Any]:
        """Get tool metadata."""
        return {
            "name": self.name,
            "platform": self.platform,
            "description": self.description,
        }
