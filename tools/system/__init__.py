"""
System tools - system-level operations.
"""

from typing import Dict, Any, Tuple
import subprocess
from ..tool import Tool
from ..schemas import ToolSchemas


class OpenAppTool(Tool):
    """Open application."""

    def __init__(self):
        super().__init__(
            name="open_app",
            platform="system",
            description="Open an application",
        )

    def validate_input(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate input."""
        return ToolSchemas.validate("open_app", data)

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Open application."""
        app = data["app"]

        try:
            process = subprocess.Popen([app])
            pid = process.pid
            return {
                "success": True,
                "result": {
                    "app": app,
                    "opened": True,
                    "pid": pid,
                },
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to open app '{app}': {str(e)}",
                "result": {
                    "app": app,
                },
            }


class CloseAppTool(Tool):
    """Close application."""

    def __init__(self):
        super().__init__(
            name="close_app",
            platform="system",
            description="Close an application",
        )

    def validate_input(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate input."""
        return ToolSchemas.validate("close_app", data)

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Close application."""
        app = data["app"]

        return {
            "success": False,
            "error": "close_app not implemented - use system kill command instead",
            "result": {
                "app": app,
            },
        }


class ExecuteCommandTool(Tool):
    """Execute shell command."""

    def __init__(self):
        super().__init__(
            name="execute_command",
            platform="system",
            description="Execute shell command",
        )

    def validate_input(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate input."""
        return ToolSchemas.validate("execute_command", data)

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute command."""
        command = data["command"]
        timeout = data.get("timeout", 30)
        shell = data.get("shell", "/bin/bash")

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                executable=shell,
            )

            return {
                "success": result.returncode == 0,
                "result": {
                    "command": command,
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                },
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timed out after {timeout}s",
                "result": {
                    "command": command,
                    "timeout": timeout,
                },
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "result": {
                    "command": command,
                },
            }
