"""
UI Service - Router bridge for UI primitives.
Exposes composable UI actions for Scout/Brain to orchestrate.

Design:
- No workflow logic (decomposed)
- Only tiny primitives
- Each action is observable
- Used by Router for target="ui"

Example dispatch:
    Message(
        source="scout",
        target="ui",
        action="dispatch_action",
        payload={
            "action": "capture_screenshot",
            "data": {"region": None, "persistent": False}
        }
    )
"""

from router.message import Message, Response
from .screenshot_manager import ScreenshotManager
from .ai_tabs import AITabsManager
from typing import Dict, Any


# Initialize managers
_screenshot_manager = ScreenshotManager()
_ai_tabs_manager = AITabsManager()


def ui_service(message: Message) -> Response:
    """
    Execute UI action via router service interface.

    Message format:
    {
        "source": "scout",
        "target": "ui",
        "action": "dispatch_action",
        "payload": {
            "action": "capture_screenshot",
            "data": {"region": None, "persistent": False}
        }
    }

    Supported actions:
    - capture_screenshot
    - get_latest_screenshot
    - clear_screenshot_buffer
    - copy_screenshot_to_clipboard
    - focus_provider
    - list_providers
    - get_current_provider

    Args:
        message: Router Message

    Returns:
        Response with action result
    """
    try:
        # Extract action from payload
        action = message.payload.get("action")
        if not action:
            return Response(
                source="ui",
                success=False,
                error="payload.action is required",
            )

        # Extract data (arguments for the action)
        data = message.payload.get("data", {})

        # Route to appropriate handler
        result = _handle_action(action, data)

        # Wrap in Response
        return Response(
            source="ui",
            success=result.get("success", False),
            result=result,
            error=result.get("error"),
        )

    except Exception as e:
        return Response(
            source="ui",
            success=False,
            error=f"ui service error: {str(e)}",
        )


def _handle_action(action: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle specific UI action.

    Args:
        action: Action name
        data: Action arguments

    Returns:
        Action result dict with success/error/result fields
    """

    # ========================================================================
    # SCREENSHOT PRIMITIVES
    # ========================================================================

    if action == "capture_screenshot":
        region = data.get("region")
        persistent = data.get("persistent", False)
        return _screenshot_manager.capture_screen(region, persistent)

    elif action == "get_latest_screenshot":
        return _screenshot_manager.get_latest_screenshot()

    elif action == "clear_screenshot_buffer":
        return _screenshot_manager.clear_buffer()

    elif action == "copy_screenshot_to_clipboard":
        return _screenshot_manager.copy_latest_to_clipboard()

    # ========================================================================
    # AI PROVIDER PRIMITIVES
    # ========================================================================

    elif action == "focus_provider":
        provider = data.get("provider")
        if not provider:
            return {"success": False, "error": "provider name required"}
        return _ai_tabs_manager.focus_provider(provider)

    elif action == "list_providers":
        return _ai_tabs_manager.list_providers()

    elif action == "get_current_provider":
        return _ai_tabs_manager.get_current_provider()

    elif action == "detect_provider":
        window_title = data.get("window_title")
        if not window_title:
            return {"success": False, "error": "window_title required"}
        provider = _ai_tabs_manager.detect_provider_tab(window_title)
        return {
            "success": provider is not None,
            "provider": provider,
        }

    # ========================================================================
    # UNKNOWN ACTION
    # ========================================================================

    else:
        available_actions = [
            "capture_screenshot",
            "get_latest_screenshot",
            "clear_screenshot_buffer",
            "copy_screenshot_to_clipboard",
            "focus_provider",
            "list_providers",
            "get_current_provider",
            "detect_provider",
        ]
        return {
            "success": False,
            "error": f"unknown action: {action}. Available: {available_actions}",
        }
