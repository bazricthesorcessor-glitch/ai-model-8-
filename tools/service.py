"""
Tool service - Router bridge for tool dispatch and execution.
Converts router Messages into tool registry calls.
"""

from router.message import Message, Response
from .registry import REGISTRY


def tool_service(message: Message) -> Response:
    """
    Execute tool via router service interface.

    Message format:
    {
        "source": "supervisor",
        "target": "tools",
        "action": "dispatch_tool",
        "payload": {
            "tool": "execute_command",
            "data": {
                "command": "ls -la",
                "shell": "fish"
            }
        }
    }

    Args:
        message: Router Message with tool name and data in payload

    Returns:
        Response with tool execution result
    """
    try:
        # Extract tool name from payload
        tool_name = message.payload.get("tool")
        if not tool_name:
            return Response(
                source="tools",
                success=False,
                error="payload.tool is required"
            )

        # Get tool from registry
        tool = REGISTRY.get(tool_name)
        if not tool:
            available = REGISTRY.list_names()
            return Response(
                source="tools",
                success=False,
                error=f"tool '{tool_name}' not found. Available: {available}"
            )

        # Extract data payload
        data = message.payload.get("data", {})

        # Run tool (returns Tool-wrapped result with success/error/result)
        tool_result = tool.run(data, context=message.context)

        # Tool result already has success/error/result fields
        # Wrap it in a Response for router compatibility
        return Response(
            source="tools",
            success=tool_result.get("success", False),
            result=tool_result,
            error=tool_result.get("error")
        )

    except Exception as e:
        return Response(
            source="tools",
            success=False,
            error=f"tool service error: {str(e)}"
        )
