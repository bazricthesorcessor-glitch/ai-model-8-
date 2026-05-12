"""
Executor Caelestia Integration - Connect executor commands to UI control.

The executor says simple commands, this translates them to actual system actions.
"""

from typing import Dict, Any
from ui.caelestia_controller import CaelestiaController, ExecutorAdapter


class ExecutorCaelestiaInterface:
    """Interface for executor to control Caelestia UI."""

    def __init__(self):
        """Initialize executor interface."""
        self.adapter = ExecutorAdapter()
        self.controller = self.adapter.controller

    def execute_command(self, command: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute command from executor.

        Example from executor:
            {
                "tool": "caelestia",
                "action": "increase_brightness"
            }

        Or with parameters:
            {
                "tool": "caelestia",
                "action": "set_volume",
                "params": {"level": 0.5}
            }
        """
        params = params or {}

        # Direct command execution
        if not params:
            return self.adapter.execute(command)

        # Command with parameters
        return self.adapter.execute(command, **params)

    def execute_browser_command(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute browser automation command."""
        browser = self.controller.get_browser()

        action_map = {
            "navigate": browser.navigate,
            "click": browser.click,
            "type_text": browser.type_text,
            "scroll": browser.scroll,
            "search": browser.search,
            "refresh": browser.refresh,
            "go_back": browser.go_back,
            "go_forward": browser.go_forward,
            "new_tab": browser.new_tab,
            "close_tab": browser.close_tab,
        }

        handler = action_map.get(action)
        if not handler:
            return {"success": False, "error": f"Unknown browser action: {action}"}

        try:
            return handler(**kwargs)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_controller_state(self) -> Dict[str, Any]:
        """Get full controller state."""
        return self.controller.get_state()


# ============================================================================
# EXAMPLE EXECUTOR INTEGRATION
# ============================================================================

def example_executor_step(step: Dict[str, Any]) -> Dict[str, Any]:
    """
    Example of how executor would use Caelestia controller.

    Step format:
    {
        "tool": "caelestia",
        "action": "increase_brightness",
        "params": {}  # Optional
    }

    Or for browser:
    {
        "tool": "caelestia_browser",
        "action": "navigate",
        "params": {"url": "https://example.com"}
    }
    """
    interface = ExecutorCaelestiaInterface()
    tool = step.get("tool")
    action = step.get("action")
    params = step.get("params", {})

    if tool == "caelestia":
        return interface.execute_command(action, params)
    elif tool == "caelestia_browser":
        return interface.execute_browser_command(action, **params)
    else:
        return {"success": False, "error": f"Unknown tool: {tool}"}


# ============================================================================
# EXAMPLE STEPS FOR EXECUTOR
# ============================================================================

EXAMPLE_EXECUTOR_STEPS = [
    # Brightness adjustment
    {
        "tool": "caelestia",
        "action": "increase_brightness",
    },
    # Volume control
    {
        "tool": "caelestia",
        "action": "set_volume",
        "params": {"level": 0.5},
    },
    # Workspace switch
    {
        "tool": "caelestia",
        "action": "switch_workspace",
        "params": {"number": 2},
    },
    # Window split
    {
        "tool": "caelestia",
        "action": "split_left",
    },
    # Browser automation
    {
        "tool": "caelestia_browser",
        "action": "navigate",
        "params": {"url": "https://example.com"},
    },
    # Browser search
    {
        "tool": "caelestia_browser",
        "action": "search",
        "params": {"term": "python"},
    },
    # Toggle game mode
    {
        "tool": "caelestia",
        "action": "toggle_game_mode",
    },
]


if __name__ == "__main__":
    print("=" * 80)
    print("EXECUTOR CAELESTIA INTEGRATION EXAMPLE")
    print("=" * 80)

    interface = ExecutorCaelestiaInterface()

    # Example 1: Simple brightness increase
    print("\n[EXAMPLE 1] Executor says: 'increase brightness'")
    result = interface.execute_command("increase_brightness")
    print(f"Result: {result}")

    # Example 2: Set volume with parameter
    print("\n[EXAMPLE 2] Executor says: 'set volume to 50%'")
    result = interface.execute_command("set_volume", {"level": 0.5})
    print(f"Result: {result}")

    # Example 3: Switch workspace
    print("\n[EXAMPLE 3] Executor says: 'switch to workspace 3'")
    result = interface.execute_command("switch_workspace", {"number": 3})
    print(f"Result: {result}")

    # Example 4: Get state
    print("\n[EXAMPLE 4] Get controller state")
    state = interface.get_controller_state()
    print(f"Current brightness: {state['brightness']['level']}")
    print(f"Current volume: {state['volume']['level']}")
    print(f"Current workspace: {state['workspaces']['current']}")

    # Example 5: Browser navigation (if browser available)
    print("\n[EXAMPLE 5] Browser automation: navigate to Google")
    # result = interface.execute_browser_command("navigate", url="https://google.com")
    # print(f"Result: {result}")

    print("\n" + "=" * 80)
    print("INTEGRATION READY FOR EXECUTOR")
    print("=" * 80)
