"""
Router Configuration - Mapping definitions for AdvancedRouter.
This is the ONLY place where action→module mapping happens.
No hardcoding in router logic. All mapping here.
"""

from typing import Dict, Any, Callable

# These will be imported at runtime
# Format: "action" → "platform" → handler_function


def build_routing_table() -> Dict[str, Dict[str, Callable]]:
    """
    Build routing table by importing module handlers.
    Called at initialization time to wire everything up.

    Returns:
        routing_table[action][platform] = handler_callable
    """
    
    # Import handlers lazily to avoid circular imports
    from brain import analyze_intent, generate_action, check_safety
    from executor import execute
    from state import update_state, get_state, get_last_actions
    
    # Pure mapping table - NO LOGIC
    routing_table = {
        # ===== DECIDE ACTIONS =====
        "decide": {
            "cli": analyze_intent,           # CLI: analyze user input intent
            "gui": analyze_intent,           # GUI: same handler (platform-agnostic)
            "web": analyze_intent,           # WEB: same handler
            "*": analyze_intent,             # Wildcard: default to analyze_intent
        },

        # ===== EXECUTE ACTIONS =====
        "execute": {
            "cli": execute,                  # CLI: run shell commands
            "gui": execute,                  # GUI: run UI commands (same handler, message.data differs)
            "*": execute,                    # Default: execute handler
        },

        # ===== STATE ACTIONS =====
        "record_state": {
            "*": update_state,               # State updates are platform-agnostic
        },

        "get_state": {
            "*": get_state,                  # State retrieval is platform-agnostic
        },

        # ===== SAFETY ACTIONS =====
        "check_safety": {
            "cli": check_safety,             # CLI: check command safety
            "*": check_safety,               # Default: same check
        },

        # ===== FUTURE ACTIONS =====
        # "record_memory": { "*": memory.log_action },
        # "get_context": { "*": state.get_last_actions },
        # "abort": { "*": executor.abort },
    }

    return routing_table


# Pre-built routing table (initialized at module load)
ROUTING_TABLE = None


def get_routing_table() -> Dict[str, Dict[str, Callable]]:
    """Lazy-load routing table on first access."""
    global ROUTING_TABLE
    if ROUTING_TABLE is None:
        ROUTING_TABLE = build_routing_table()
    return ROUTING_TABLE


# ===== CONFIG REFERENCE =====
"""
How to use the routing table:

1. Add new action:
   routing_table["my_action"] = {
       "cli": my_handler,
       "gui": my_handler,
   }

2. Use wildcard for platform-agnostic handlers:
   routing_table["my_action"] = {
       "*": universal_handler,
   }

3. Mix specific + wildcard:
   routing_table["my_action"] = {
       "cli": cli_specific_handler,
       "*": fallback_handler,
   }

4. No decision logic here. Just mapping.
   If you need routing logic, you're doing it wrong.
"""
