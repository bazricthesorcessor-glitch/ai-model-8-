"""
Advanced Router Module - Pure Dispatch Layer
Receives messages, routes to modules using config mappings ONLY.
Zero decision making. Zero interpretation. Pure mapping + forward.
"""

from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass
from .message import Message, Response


@dataclass
class Route:
    """Single routing rule - maps action+platform to module handler."""
    action: str                    # action type from message
    platform: str                  # platform type from message
    handler: Callable             # function to call
    description: str = ""         # documentation only


class AdvancedRouter:
    """
    Deterministic router using config-driven routing table.
    
    NO decision logic. NO interpretation. Pure mapping.
    Message in → Table lookup → Handler call → Result out.
    """

    def __init__(self, routing_config: Dict[str, Dict[str, Callable]]):
        """
        Initialize router with config-driven routing table.

        Args:
            routing_config: Dict[action][platform] = handler_function
            
        Example:
            {
                "decide": {
                    "cli": brain.decide,
                    "gui": brain.decide_gui,
                },
                "execute": {
                    "cli": executor.execute_cli,
                    "gui": executor.execute_gui,
                },
                "record_state": {
                    "*": state.update,  # wildcard - any platform
                },
            }
        """
        self.routing_table = routing_config
        self.stats = {
            "total_routed": 0,
            "routed_by_action": {},
            "errors": [],
        }

    def route(self, message: Message) -> Response:
        """
        Route message to handler using ONLY config table lookup.
        Zero interpretation. Zero modification.

        Flow:
        1. Extract action + platform from message (no interpretation)
        2. Look up in routing_table[action][platform]
        3. Call handler with unmodified message
        4. Return response as-is

        Args:
            message: Structured message (unmodified)

        Returns:
            Response object from handler
        """
        # Track stats
        self.stats["total_routed"] += 1
        if message.action not in self.stats["routed_by_action"]:
            self.stats["routed_by_action"][message.action] = 0
        self.stats["routed_by_action"][message.action] += 1

        # Step 1: Extract routing key (no interpretation)
        action = message.action
        platform = message.platform

        # Step 2: Look up handler in config (pure mapping)
        handler = self._lookup_handler(action, platform)

        if handler is None:
            error_msg = f"No route: action='{action}', platform='{platform}'"
            self.stats["errors"].append(error_msg)
            return Response(
                success=False,
                action=action,
                error=error_msg,
            )

        # Step 3: Call handler with unmodified message
        try:
            result = handler(message)
            return self._wrap_result(result, action)
        except Exception as e:
            error_msg = f"Handler error for {action}/{platform}: {str(e)}"
            self.stats["errors"].append(error_msg)
            return Response(
                success=False,
                action=action,
                error=error_msg,
            )

    def _lookup_handler(self, action: str, platform: str) -> Optional[Callable]:
        """
        Look up handler in routing table using ONLY table structure.
        No interpretation. No fallbacks. Pure mapping.

        Lookup order:
        1. action + exact platform match
        2. action + wildcard platform match (*)
        3. None (error)

        Args:
            action: Message action field
            platform: Message platform field

        Returns:
            Handler function or None if not found
        """
        # Check if action exists in table
        if action not in self.routing_table:
            return None

        action_routes = self.routing_table[action]

        # Try exact platform match
        if platform in action_routes:
            return action_routes[platform]

        # Try wildcard match (for platform-agnostic handlers)
        if "*" in action_routes:
            return action_routes["*"]

        # No match found
        return None

    def _wrap_result(self, result: Any, action: str) -> Response:
        """
        Wrap handler result in Response if needed.
        Handler may return Response directly or raw dict.

        Args:
            result: Return value from handler
            action: Message action (for context)

        Returns:
            Response object
        """
        if isinstance(result, Response):
            return result

        # Assume dict result, wrap it
        if isinstance(result, dict):
            return Response(
                success=result.get("success", True),
                action=action,
                data=result.get("data", result),
                error=result.get("error"),
            )

        # Unexpected result type
        return Response(
            success=True,
            action=action,
            data={"raw_result": str(result)},
        )

    def add_route(self, action: str, platform: str, handler: Callable) -> None:
        """
        Register a new route dynamically (config update).

        Args:
            action: Action type
            platform: Platform type
            handler: Callable to handle this route
        """
        if action not in self.routing_table:
            self.routing_table[action] = {}
        self.routing_table[action][platform] = handler

    def get_routing_table(self) -> Dict[str, Dict[str, str]]:
        """
        Get human-readable routing table (for debugging/docs).

        Returns:
            Dict showing all registered routes
        """
        result = {}
        for action, platforms in self.routing_table.items():
            result[action] = {}
            for platform, handler in platforms.items():
                result[action][platform] = handler.__name__ if hasattr(handler, "__name__") else str(handler)
        return result

    def get_stats(self) -> Dict[str, Any]:
        """Get router statistics."""
        return self.stats.copy()


def create_router_from_config(config: Dict[str, Any]) -> AdvancedRouter:
    """
    Factory function to create router from config dict.
    Builds routing table by importing and wiring modules.

    Args:
        config: Config dict with routing rules

    Returns:
        Initialized AdvancedRouter instance
    """
    routing_table = {}

    for action, platforms in config.items():
        routing_table[action] = {}
        for platform, handler_spec in platforms.items():
            if callable(handler_spec):
                # Already a function
                routing_table[action][platform] = handler_spec
            else:
                # String reference like "brain.decide" - would need dynamic import
                # For now, assume pre-initialized handlers
                pass

    return AdvancedRouter(routing_table)
