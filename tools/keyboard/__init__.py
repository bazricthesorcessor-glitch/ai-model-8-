"""
Keyboard input tools.
"""

from typing import Dict, Any, Tuple
from ..tool import Tool
from ..schemas import ToolSchemas


class KeyboardTypeTool(Tool):
    """Type text using keyboard."""

    def __init__(self):
        super().__init__(
            name="keyboard_type",
            platform="keyboard",
            description="Type text using keyboard",
        )

    def validate_input(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate input."""
        return ToolSchemas.validate("keyboard_type", data)

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Type text."""
        text = data["text"]
        delay = data.get("delay", 0.0)

        # Placeholder: would use pynput/pyautogui
        # keyboard = Controller()
        # for char in text:
        #     keyboard.type(char)
        #     if delay: time.sleep(delay)

        return {
            "success": True,
            "result": {
                "text_typed": text,
                "length": len(text),
                "method": "keyboard",
            },
        }


class HotKeyTool(Tool):
    """Execute keyboard shortcut."""

    def __init__(self):
        super().__init__(
            name="hotkey",
            platform="keyboard",
            description="Execute keyboard shortcut (Ctrl+C, Alt+Tab, etc.)",
        )

    def validate_input(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate input."""
        return ToolSchemas.validate("hotkey", data)

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute hotkey."""
        keys = data["keys"].lower()

        # Placeholder: would use pynput
        # hotkey_parts = keys.split("+")
        # keyboard.hotkey(*hotkey_parts)

        return {
            "success": True,
            "result": {
                "keys": keys,
                "executed": True,
                "modifiers": keys.count("+") > 0,
            },
        }
