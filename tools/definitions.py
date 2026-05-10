"""
Tool definitions - tool schema only, no logic.
References to handlers are string-based to avoid circular imports.
"""

from typing import Dict, Any, Optional
from config import TOOL_REGISTRY as CONFIG_TOOL_REGISTRY


def get_tool_definition(tool_name: str) -> Optional[Dict[str, Any]]:
    """Get tool definition by name."""
    return CONFIG_TOOL_REGISTRY.get(tool_name)


def list_tools() -> Dict[str, Dict[str, Any]]:
    """List all available tools."""
    return CONFIG_TOOL_REGISTRY.copy()


def get_tools_by_platform(platform: str) -> Dict[str, Dict[str, Any]]:
    """Get tools available on a specific platform."""
    return {
        name: tool
        for name, tool in CONFIG_TOOL_REGISTRY.items()
        if tool.get("platform") == platform
    }


TOOL_REGISTRY = CONFIG_TOOL_REGISTRY
