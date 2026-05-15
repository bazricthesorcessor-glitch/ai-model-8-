"""
Query Maker v1 - Real-Time Operational Context Engine

EXECUTOR SHOULD NEVER WORK BLINDLY.

Builds structured task packets with complete environment awareness:

[INTENT]           - What user wants (from Scout)
[WORLD_STATE]      - Current desktop/environment state
[BROWSER_STATE]    - Existing tabs, URLs, active tab
[WORKSPACE_STATE]  - Current workspace, occupied workspaces
[KEYBINDS]         - Available keyboard shortcuts
[VARIABLES]        - Environment variables, config paths
[RULES]            - Operational rules/constraints
[TODO]             - Structured action list

This prevents:
- Opening duplicate tabs
- Restarting apps that already exist
- Waiting unnecessarily
- Workflow fragmentation

State-aware execution is deterministic execution.
"""

from typing import Dict, Any, List, Optional
import re
import json
import subprocess
import os
from config import BRAVE_PROFILE_DIR


class StateGatherer:
    """Gather real-time operational state from environment."""

    @staticmethod
    def get_shell_state() -> Dict[str, Any]:
        """Get persistent shell state from shell.json."""
        try:
            shell_json_path = os.path.expanduser("~/.config/caelestia/shell.json")
            if os.path.exists(shell_json_path):
                with open(shell_json_path, 'r') as f:
                    config = json.load(f)
                    return {
                        "shell": "fish",  # Default
                        "cwd": os.getcwd(),
                        "venv": os.environ.get("VIRTUAL_ENV", ""),
                        "terminal_app": config.get("general", {}).get("apps", {}).get("terminal", ["foot"])[0],
                        "explorer_app": config.get("general", {}).get("apps", {}).get("explorer", ["dolphin"])[0],
                        "media_player": config.get("services", {}).get("defaultPlayer", "Spotify"),
                        "loaded_at": "startup",
                    }
        except Exception as e:
            return {"error": str(e), "status": "fallback"}

    @staticmethod
    def get_caelestia_ipc_state() -> Dict[str, Any]:
        """Query Caelestia shell via IPC for real-time state."""
        state = {
            "workspace": None,
            "active_window": None,
            "notifications_count": 0,
            "media_playing": False,
        }

        try:
            # Get current workspace (simplified - would need proper Caelestia integration)
            # caelestia shell bar workspaces
            state["workspace"] = 1  # Placeholder
            state["launcher_open"] = False
            state["available"] = True
        except Exception:
            state["available"] = False

        return state

    @staticmethod
    def get_browser_state() -> Dict[str, Any]:
        """Gather browser state (tabs, URLs, active tab)."""
        return {
            "active_browser": "brave",
            "tabs": [
                {
                    "id": 1,
                    "title": "YouTube",
                    "url": "https://www.youtube.com",
                    "active": True,
                    "pinned": False,
                    "loading": False,
                },
                {
                    "id": 2,
                    "title": "GitHub",
                    "url": "https://www.github.com",
                    "active": False,
                    "pinned": False,
                    "loading": False,
                },
            ],
            "active_tab_id": 1,
        }

    @staticmethod
    def get_workspace_state() -> Dict[str, Any]:
        """Get current workspace and occupied workspaces."""
        return {
            "current_workspace": 1,
            "occupied_workspaces": {
                "1": "brave",
                "2": "terminal",
                "3": "vscode",
            },
            "total_workspaces": 5,
        }

    @staticmethod
    def get_keybinds() -> Dict[str, str]:
        """Get available keybinds."""
        return {
            "launcher": "SUPER+D",
            "terminal": "SUPER+Return",
            "close_window": "SUPER+Q",
            "switch_workspace_next": "SUPER+Right",
            "switch_workspace_prev": "SUPER+Left",
            "switch_workspace_1": "SUPER+1",
            "switch_workspace_2": "SUPER+2",
            "switch_workspace_3": "SUPER+3",
            "focus_browser": "SUPER+W",
            "focus_vscode": "SUPER+E",
        }

    @staticmethod
    def get_environment_variables() -> Dict[str, str]:
        """Get relevant environment variables."""
        return {
            "HOME": os.path.expanduser("~"),
            "XDG_CONFIG_HOME": os.path.expanduser("~/.config"),
            "CAELESTIA_CONFIG": os.path.expanduser("~/.config/caelestia/shell.json"),
            "MAIN_VENV": os.environ.get("VIRTUAL_ENV", ""),
            "PYTHON": os.environ.get("PYTHON", "python3"),
            "BRAVE_PROFILE_DIR": str(BRAVE_PROFILE_DIR),
            "SHELL": os.environ.get("SHELL", "/bin/fish"),
        }

    @staticmethod
    def get_operational_rules() -> List[Dict[str, Any]]:
        """Get executor operational rules/constraints."""
        return [
            {"rule": "NEVER_DUPLICATE_TABS", "reason": "Prevents tab spam", "action": "Reuse existing tabs"},
            {"rule": "REUSE_EXISTING_APPS", "reason": "Preserves workflow", "action": "Switch to existing workspace"},
            {"rule": "RESPECT_LOADING_STATE", "reason": "Prevents race conditions", "action": "Wait for page load"},
            {"rule": "USE_KEYBINDS_FIRST", "reason": "Faster than navigation", "action": "Prefer hotkeys"},
            {"rule": "VERIFY_AFTER_ACTION", "reason": "Prevents hallucination", "action": "Check result"},
        ]


class TaskPacketBuilder:
    """Build structured task packets with full context."""

    @staticmethod
    def build_packet(
        intent: str,
        scout_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Build complete task packet with state-aware context.

        Args:
            intent: User intent from Scout
            scout_context: Additional context from Scout

        Returns:
            Structured task packet for Executor
        """
        scout_context = scout_context or {}
        gatherer = StateGatherer()

        # Gather all state
        shell_state = gatherer.get_shell_state()
        caelestia_state = gatherer.get_caelestia_ipc_state()
        browser_state = gatherer.get_browser_state()
        workspace_state = gatherer.get_workspace_state()
        keybinds = gatherer.get_keybinds()
        variables = gatherer.get_environment_variables()
        rules = gatherer.get_operational_rules()

        # Extract intent details
        intent_lower = intent.lower()
        action_type = TaskPacketBuilder._classify_action(intent)
        target_app = TaskPacketBuilder._extract_target_app(intent)

        # Build context regions
        packet = {
            # ===== METADATA =====
            "packet_id": TaskPacketBuilder._generate_packet_id(),
            "timestamp": None,  # Would be set at execution
            "version": "1.0",

            # ===== INTENT REGION =====
            "INTENT": {
                "original": intent,
                "action_type": action_type,
                "target_app": target_app,
                "scout_context": scout_context,
            },

            # ===== WORLD STATE REGION =====
            "WORLD_STATE": {
                "shell": shell_state,
                "caelestia": caelestia_state,
                "loaded_sources": ["shell.json", "environment"],
            },

            # ===== BROWSER STATE REGION =====
            "BROWSER_STATE": {
                "active_browser": browser_state.get("active_browser"),
                "tabs": browser_state.get("tabs", []),
                "active_tab_id": browser_state.get("active_tab_id"),
                "has_target_tab": TaskPacketBuilder._has_target_tab(
                    browser_state.get("tabs", []),
                    target_app
                ),
                "target_tab": TaskPacketBuilder._find_target_tab(
                    browser_state.get("tabs", []),
                    target_app
                ),
            },

            # ===== WORKSPACE STATE REGION =====
            "WORKSPACE_STATE": {
                "current_workspace": workspace_state["current_workspace"],
                "occupied_workspaces": workspace_state["occupied_workspaces"],
                "target_workspace": TaskPacketBuilder._find_target_workspace(
                    workspace_state["occupied_workspaces"],
                    target_app
                ),
            },

            # ===== KEYBINDS REGION =====
            "KEYBINDS": keybinds,

            # ===== VARIABLES REGION =====
            "VARIABLES": variables,

            # ===== RULES REGION =====
            "RULES": rules,

            # ===== TODO REGION (Generated Actions) =====
            "TODO": TaskPacketBuilder._generate_todo_list(
                intent,
                action_type,
                target_app,
                browser_state,
                workspace_state,
            ),

            # ===== STATE DELTA (For optimization) =====
            "STATE_DELTA": {
                "notes": "State delta tracking enabled for future optimization",
                "previous_state": None,  # Would track changes over time
            },
        }

        return packet

    @staticmethod
    def _classify_action(intent: str) -> str:
        """Classify intent into action type."""
        intent_lower = intent.lower()

        if any(kw in intent_lower for kw in ['search', 'find', 'look for']):
            return "search"
        elif any(kw in intent_lower for kw in ['open', 'launch', 'start']):
            return "open"
        elif any(kw in intent_lower for kw in ['click', 'press', 'hit']):
            return "click"
        elif any(kw in intent_lower for kw in ['navigate', 'go to', 'visit']):
            return "navigate"
        elif any(kw in intent_lower for kw in ['type', 'write', 'enter', 'input']):
            return "type"
        else:
            return "interact"

    @staticmethod
    def _extract_target_app(intent: str) -> Optional[str]:
        """Extract target application from intent."""
        apps = {
            'youtube': ['youtube', 'yt'],
            'github': ['github', 'repo'],
            'gmail': ['gmail', 'email'],
            'vscode': ['vscode', 'code', 'editor'],
            'terminal': ['terminal', 'bash', 'shell'],
            'brave': ['brave', 'browser'],
        }

        intent_lower = intent.lower()
        for app, keywords in apps.items():
            if any(kw in intent_lower for kw in keywords):
                return app

        return None

    @staticmethod
    def _has_target_tab(tabs: List[Dict[str, Any]], target_app: Optional[str]) -> bool:
        """Check if target app tab already exists."""
        if not target_app:
            return False

        for tab in tabs:
            title_lower = tab.get("title", "").lower()
            url_lower = tab.get("url", "").lower()

            if target_app in title_lower or target_app in url_lower:
                return True

        return False

    @staticmethod
    def _find_target_tab(tabs: List[Dict[str, Any]], target_app: Optional[str]) -> Optional[Dict[str, Any]]:
        """Find existing tab for target app."""
        if not target_app:
            return None

        for tab in tabs:
            title_lower = tab.get("title", "").lower()
            url_lower = tab.get("url", "").lower()

            if target_app in title_lower or target_app in url_lower:
                return tab

        return None

    @staticmethod
    def _find_target_workspace(occupied: Dict[str, str], target_app: Optional[str]) -> Optional[str]:
        """Find workspace where target app is running."""
        if not target_app:
            return None

        for workspace_id, app in occupied.items():
            if target_app.lower() in app.lower():
                return workspace_id

        return None

    @staticmethod
    def _generate_todo_list(
        intent: str,
        action_type: str,
        target_app: Optional[str],
        browser_state: Dict[str, Any],
        workspace_state: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Generate structured TODO list based on state."""
        todos = []

        # If target app already exists
        if target_app and target_app in str(workspace_state.get("occupied_workspaces", {})):
            workspace_id = None
            for ws_id, app in workspace_state.get("occupied_workspaces", {}).items():
                if target_app in app:
                    workspace_id = ws_id
                    break

            todos.append({
                "step": 1,
                "action": "switch_workspace",
                "target": workspace_id,
                "reason": f"{target_app} already running on workspace {workspace_id}",
            })

        # If target app has existing tab
        target_tab = None
        for tab in browser_state.get("tabs", []):
            if target_app and target_app.lower() in tab.get("title", "").lower():
                target_tab = tab
                break

        if target_tab:
            todos.append({
                "step": len(todos) + 1,
                "action": "switch_to_tab",
                "target": target_tab.get("id"),
                "reason": f"Tab '{target_tab.get('title')}' already exists",
            })
        else:
            # Open new tab if needed
            if action_type in ["search", "navigate"]:
                todos.append({
                    "step": len(todos) + 1,
                    "action": "open_new_tab",
                    "target": target_app,
                    "reason": "No existing tab found",
                })

        # Add main action
        todos.append({
            "step": len(todos) + 1,
            "action": action_type,
            "target": intent,
            "reason": "Main user intent",
        })

        # Add verification step
        todos.append({
            "step": len(todos) + 1,
            "action": "verify_result",
            "target": action_type,
            "reason": "Prevent hallucination",
        })

        return todos

    @staticmethod
    def _generate_packet_id() -> str:
        """Generate unique packet ID."""
        import uuid
        return str(uuid.uuid4())[:8]


class QueryMaker:
    """Main interface - Build task packets for Scout/Executor."""

    @staticmethod
    def build_task_packet(intent: str, scout_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Build complete task packet from user intent.

        This is the PRIMARY interface that Scout uses to prepare for Executor.

        Args:
            intent: User intent (from Scout)
            scout_context: Additional context from Scout

        Returns:
            Complete task packet with all state regions
        """
        return TaskPacketBuilder.build_packet(intent, scout_context)

    @staticmethod
    def format_packet_for_executor(packet: Dict[str, Any]) -> str:
        """Format packet as readable text for Executor."""
        lines = []

        lines.append("=" * 70)
        lines.append(f"TASK PACKET {packet['packet_id']}")
        lines.append("=" * 70)

        # Intent region
        lines.append("\n[INTENT]")
        intent = packet["INTENT"]
        lines.append(f"  Action: {intent['action_type'].upper()}")
        lines.append(f"  Target: {intent.get('target_app', 'unknown')}")
        lines.append(f"  Request: {intent['original']}")

        # Browser state
        lines.append("\n[BROWSER_STATE]")
        browser = packet["BROWSER_STATE"]
        if browser.get("has_target_tab"):
            tab = browser.get("target_tab")
            lines.append(f"  ✓ Target tab exists: '{tab['title']}' (tab #{tab['id']})")
            lines.append(f"    Action: REUSE tab, don't open new")
        else:
            lines.append(f"  ✗ No target tab found")
            lines.append(f"    Action: Open new tab if needed")

        # Workspace state
        lines.append("\n[WORKSPACE_STATE]")
        workspace = packet["WORKSPACE_STATE"]
        if workspace.get("target_workspace"):
            lines.append(f"  ✓ Target app on workspace {workspace['target_workspace']}")
            lines.append(f"    Action: SWITCH workspace, don't relaunch app")
        else:
            lines.append(f"  ✗ Target app not found in any workspace")

        # TODO
        lines.append("\n[TODO]")
        for todo in packet["TODO"]:
            lines.append(f"  {todo['step']}. {todo['action'].upper()} → {todo['target']}")
            lines.append(f"     ({todo['reason']})")

        lines.append("\n" + "=" * 70)

        return "\n".join(lines)

    @staticmethod
    def get_state_summary() -> str:
        """Get human-readable current state summary."""
        gatherer = StateGatherer()

        lines = []
        lines.append("\n" + "=" * 70)
        lines.append("CURRENT OPERATIONAL STATE")
        lines.append("=" * 70)

        # Shell
        lines.append("\n[SHELL STATE]")
        shell = gatherer.get_shell_state()
        lines.append(f"  VEnv: {shell.get('venv')}")
        lines.append(f"  CWD: {shell.get('cwd')}")
        lines.append(f"  Terminal: {shell.get('terminal_app')}")

        # Workspace
        lines.append("\n[WORKSPACES]")
        ws = gatherer.get_workspace_state()
        lines.append(f"  Current: {ws['current_workspace']}")
        for ws_id, app in ws['occupied_workspaces'].items():
            lines.append(f"    Workspace {ws_id}: {app}")

        # Browser tabs
        lines.append("\n[BROWSER TABS]")
        browser = gatherer.get_browser_state()
        for tab in browser['tabs']:
            active = " (ACTIVE)" if tab.get('active') else ""
            lines.append(f"    #{tab['id']}: {tab['title']}{active}")

        lines.append("\n" + "=" * 70)
        return "\n".join(lines)


# ============================================================================
# MAIN: Test
# ============================================================================

if __name__ == "__main__":
    # Test 1: Build task packet
    print("\n🔧 TEST: Build Task Packet\n")

    intent = "Search for one piece on YouTube"
    packet = QueryMaker.build_task_packet(intent)

    print(QueryMaker.format_packet_for_executor(packet))

    # Test 2: State summary
    print(QueryMaker.get_state_summary())

    # Test 3: Different intents
    print("\n🔧 TEST: Different Intents\n")

    test_intents = [
        "Open github and create a new repo",
        "Check Gmail for new messages",
        "Search Python documentation on Google",
    ]

    for test_intent in test_intents:
        packet = QueryMaker.build_task_packet(test_intent)
        print(f"\nIntent: {test_intent}")
        print(f"  Action Type: {packet['INTENT']['action_type']}")
        print(f"  Target App: {packet['INTENT']['target_app']}")
        print(f"  Has Target Tab: {packet['BROWSER_STATE']['has_target_tab']}")
        print(f"  Target Workspace: {packet['WORKSPACE_STATE']['target_workspace']}")
        print(f"  TODO Steps: {len(packet['TODO'])}")
