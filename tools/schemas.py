"""
Input validation schemas for tools.
Centralized schema definitions and validation.
"""

from typing import Dict, Any, Tuple, List, Union


class ToolSchemas:
    """Validation schemas for all tools."""

    SCHEMAS = {
        "click_element": {
            "required": ["selector"],
            "optional": ["timeout", "visible"],
            "types": {
                "selector": str,
                "timeout": (int, float),
                "visible": bool,
            },
            "defaults": {
                "timeout": 5,
                "visible": True,
            },
        },
        "type_text": {
            "required": ["text"],
            "optional": ["selector", "delay"],
            "types": {
                "text": str,
                "selector": str,
                "delay": (int, float),
            },
            "defaults": {
                "delay": 0.0,
            },
        },
        "navigate": {
            "required": ["url"],
            "optional": ["timeout"],
            "types": {
                "url": str,
                "timeout": (int, float),
            },
            "defaults": {
                "timeout": 30,
            },
        },
        "read_content": {
            "required": [],
            "optional": ["selector", "timeout"],
            "types": {
                "selector": str,
                "timeout": (int, float),
            },
            "defaults": {
                "timeout": 5,
            },
        },
        "keyboard_type": {
            "required": ["text"],
            "optional": ["delay"],
            "types": {
                "text": str,
                "delay": (int, float),
            },
            "defaults": {
                "delay": 0.0,
            },
        },
        "hotkey": {
            "required": ["keys"],
            "optional": [],
            "types": {
                "keys": str,
            },
        },
        "mouse_click": {
            "required": ["x", "y"],
            "optional": ["button"],
            "types": {
                "x": int,
                "y": int,
                "button": str,
            },
            "defaults": {
                "button": "left",
            },
        },
        "mouse_move": {
            "required": ["x", "y"],
            "optional": ["duration"],
            "types": {
                "x": int,
                "y": int,
                "duration": (int, float),
            },
            "defaults": {
                "duration": 0.5,
            },
        },
        "drag_drop": {
            "required": ["src_x", "src_y", "dst_x", "dst_y"],
            "optional": ["duration"],
            "types": {
                "src_x": int,
                "src_y": int,
                "dst_x": int,
                "dst_y": int,
                "duration": (int, float),
            },
            "defaults": {
                "duration": 1.0,
            },
        },
        "screenshot": {
            "required": [],
            "optional": ["region", "save_path"],
            "types": {
                "region": (list, tuple),
                "save_path": str,
            },
        },
        "find_element": {
            "required": ["description"],
            "optional": ["timeout", "confidence"],
            "types": {
                "description": str,
                "timeout": (int, float),
                "confidence": (int, float),
            },
            "defaults": {
                "timeout": 5,
                "confidence": 0.8,
            },
        },
        "read_text": {
            "required": [],
            "optional": ["region", "language"],
            "types": {
                "region": (list, tuple),
                "language": str,
            },
            "defaults": {
                "language": "en",
            },
        },
        "open_app": {
            "required": ["app"],
            "optional": [],
            "types": {
                "app": str,
            },
        },
        "close_app": {
            "required": ["app"],
            "optional": [],
            "types": {
                "app": str,
            },
        },
        "execute_command": {
            "required": ["command"],
            "optional": ["timeout", "shell"],
            "types": {
                "command": str,
                "timeout": (int, float),
                "shell": str,
            },
            "defaults": {
                "timeout": 30,
                "shell": "/bin/bash",
            },
        },
    }

    @staticmethod
    def validate(tool_name: str, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate input data for tool.

        Args:
            tool_name: Name of tool
            data: Input data dict

        Returns:
            (is_valid: bool, error_message: str)
        """
        schema = ToolSchemas.SCHEMAS.get(tool_name)
        if not schema:
            return False, f"Unknown tool: {tool_name}"

        # Check required fields
        for field in schema["required"]:
            if field not in data:
                return False, f"Required field missing: {field}"

        # Check types
        for field, expected_type in schema["types"].items():
            if field in data:
                if not isinstance(data[field], expected_type):
                    type_names = (
                        ", ".join(t.__name__ for t in expected_type)
                        if isinstance(expected_type, tuple)
                        else expected_type.__name__
                    )
                    return False, f"Invalid type for {field}: expected {type_names}, got {type(data[field]).__name__}"

        # Check for unknown fields
        allowed_fields = set(schema["required"]) | set(schema.get("optional", []))
        unknown_fields = set(data.keys()) - allowed_fields
        if unknown_fields:
            return False, f"Unknown fields: {', '.join(unknown_fields)}"

        return True, ""

    @staticmethod
    def get_schema(tool_name: str) -> Union[Dict[str, Any], None]:
        """Get schema for a tool."""
        return ToolSchemas.SCHEMAS.get(tool_name)

    @staticmethod
    def list_schemas() -> Dict[str, Dict[str, Any]]:
        """List all schemas."""
        return ToolSchemas.SCHEMAS.copy()
