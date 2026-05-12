"""
Router - Central nervous system infrastructure.
Routes packets between services based on source/target/action.
Does NOT think, decide, or plan - only transports and executes.
"""

from .message import Message, Response
from typing import Dict, Callable, Optional


# Service registry - loaded at startup
SERVICES: Dict[str, Callable] = {}


def register_service(name: str, handler: Callable):
    """Register a service handler (executor, coder, query_maker, etc)."""
    SERVICES[name] = handler


def dispatch(message: Message) -> Response:
    """
    Dispatch packet to target service.

    Routes based on message.target:
    - "executor" → execute tool/command
    - "query_maker1" → run query maker
    - "coder" → code generation
    - "thinker" → deep reasoning
    - etc.

    Args:
        message: Message with source, target, action, payload

    Returns:
        Response from service with success status and result
    """
    try:
        # Validate packet structure
        if not message.target:
            return Response(
                source="router",
                success=False,
                error="target required in packet"
            )

        # Look up service handler
        service = SERVICES.get(message.target)
        if not service:
            return Response(
                source="router",
                success=False,
                error=f"service '{message.target}' not registered. Available: {list(SERVICES.keys())}"
            )

        # Execute service with packet payload
        result = service(message)

        # Ensure response is Response object
        if not isinstance(result, Response):
            result = Response(
                source=message.target,
                success=True,
                result=result if isinstance(result, dict) else {"result": result}
            )

        return result

    except Exception as e:
        return Response(
            source="router",
            success=False,
            error=f"dispatch failed: {str(e)}"
        )


def send_to_service(target: str, action: str, payload: dict, context: dict = None) -> Response:
    """
    Convenience function - build packet and dispatch to service.

    Args:
        target: service name
        action: what to do
        payload: data for service
        context: optional execution context

    Returns:
        Response from service
    """
    message = Message(
        source="router",
        target=target,
        action=action,
        payload=payload,
        context=context or {}
    )
    return dispatch(message)
