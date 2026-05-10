"""
Tool registry - central discovery and management of all tools.
"""

from typing import Dict, Any, Optional, List
from .tool import Tool


class ToolRegistry:
    """Central registry of all available tools."""

    def __init__(self):
        """Initialize empty registry."""
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """
        Register a tool.

        Args:
            tool: Tool instance
        """
        if not isinstance(tool, Tool):
            raise TypeError(f"Tool must be instance of Tool class, got {type(tool)}")

        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' already registered")

        self._tools[tool.name] = tool

    def get(self, tool_name: str) -> Optional[Tool]:
        """
        Get tool by name.

        Args:
            tool_name: Name of tool

        Returns:
            Tool instance or None
        """
        return self._tools.get(tool_name)

    def exists(self, tool_name: str) -> bool:
        """Check if tool exists."""
        return tool_name in self._tools

    def list(self) -> Dict[str, Tool]:
        """Get all tools."""
        return self._tools.copy()

    def list_names(self) -> List[str]:
        """Get list of all tool names."""
        return sorted(self._tools.keys())

    def list_by_platform(self, platform: str) -> Dict[str, Tool]:
        """
        Get tools for specific platform.

        Args:
            platform: Platform name (web, keyboard, mouse, vision, system)

        Returns:
            Dict of tools matching platform
        """
        return {
            name: tool
            for name, tool in self._tools.items()
            if tool.platform == platform
        }

    def get_platforms(self) -> List[str]:
        """Get list of all unique platforms."""
        platforms = set()
        for tool in self._tools.values():
            platforms.add(tool.platform)
        return sorted(platforms)

    def get_metadata(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get tool metadata for executor/brain.

        Args:
            tool_name: Name of tool

        Returns:
            Metadata dict or None
        """
        tool = self.get(tool_name)
        if not tool:
            return None

        return {
            "name": tool.name,
            "platform": tool.platform,
            "description": tool.description,
        }

    def get_all_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Get metadata for all tools."""
        result = {}
        for name in self._tools.keys():
            metadata = self.get_metadata(name)
            if metadata:
                result[name] = metadata
        return result

    def get_info(self) -> Dict[str, Any]:
        """Get registry info."""
        tools_by_platform = {}
        for platform in self.get_platforms():
            tools_by_platform[platform] = self.list_by_platform(platform)

        return {
            "total_tools": len(self._tools),
            "tools": sorted(self._tools.keys()),
            "platforms": self.get_platforms(),
            "tools_by_platform": {
                p: [t.name for t in tools.values()]
                for p, tools in tools_by_platform.items()
            },
        }

    def export_schemas(self) -> Dict[str, Any]:
        """
        Export tool schemas for LLM integration.
        Returns JSON-serializable tool information including descriptions.

        Returns:
            Dict mapping tool names to schema info
        """
        schemas = {}
        for name, tool in self._tools.items():
            schemas[name] = {
                "name": tool.name,
                "platform": tool.platform,
                "description": tool.description,
            }
        return schemas


# Global registry instance
REGISTRY = ToolRegistry()
