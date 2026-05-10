"""
Router dispatcher - routes messages between modules.
Central nervous system. No decision logic - only mapping.
"""

from .message import Message, Response


def route(message: Message) -> Response:
    """
    Route a message to the appropriate module based on action.
    This is the ONLY place where modules are imported/called.

    Routing:
    - "decide" → brain module (decision making)
    - "execute" → executor module (step execution)
    - "record_state" → state module (update status)
    - "get_state" → state module (retrieve status)

    Args:
        message: Message object with action, platform, mode, data, steps

    Returns:
        Response object with success status and result data
    """

    try:
        if message.action == "decide":
            # Import here to avoid circular dependencies
            from brain import analyze_intent, generate_action

            intent = analyze_intent(message.data.get("user_input", ""))
            action = generate_action(
                message.data.get("user_input", ""),
                context=message.context
            )
            return Response(
                success=True,
                action="decide",
                data={
                    "intent": intent,
                    "action": action,
                }
            )

        elif message.action == "execute":
            # Import here to avoid circular dependencies
            from executor import execute

            result = execute(message)
            return Response(
                success=result.get("success", False),
                action="execute",
                data=result
            )

        elif message.action == "record_state":
            # Import here to avoid circular dependencies
            from state import update_state

            result = update_state(message.data)
            return Response(
                success=result.get("success", False),
                action="record_state",
                data=result
            )

        elif message.action == "get_state":
            # Import here to avoid circular dependencies
            from state import get_state

            result = get_state()
            return Response(
                success=True,
                action="get_state",
                data=result
            )

        else:
            return Response(
                success=False,
                action=message.action,
                error=f"Unknown action: {message.action}"
            )

    except ImportError as e:
        return Response(
            success=False,
            action=message.action,
            error=f"Module import error: {str(e)}"
        )
    except Exception as e:
        return Response(
            success=False,
            action=message.action,
            error=f"Routing error: {str(e)}"
        )
