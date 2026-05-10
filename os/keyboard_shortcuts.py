"""
Keyboard Shortcut Handler - Manage and execute keyboard shortcuts
Support for complex combinations and Hyprland bindings.
"""

from typing import Dict, List, Callable, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class KeyModifier(Enum):
    """Keyboard modifiers"""
    CTRL = "CTRL"
    SHIFT = "SHIFT"
    ALT = "ALT"
    SUPER = "SUPER"
    META = "META"


@dataclass
class KeyboardShortcut:
    """Keyboard shortcut definition"""
    modifiers: List[KeyModifier]
    key: str
    action: str
    description: str = ""
    repeatable: bool = True


class KeyboardShortcutHandler:
    """
    Handle keyboard shortcuts and macros.
    Supports Hyprland bindings and custom actions.
    """

    def __init__(self):
        """Initialize handler"""
        self.shortcuts: Dict[str, KeyboardShortcut] = {}
        self.handlers: Dict[str, List[Callable]] = {}
        self._initialize_default_shortcuts()

    def _initialize_default_shortcuts(self):
        """Initialize default Hyprland shortcuts"""
        defaults = {
            # Window management
            "super+q": KeyboardShortcut(
                modifiers=[KeyModifier.SUPER],
                key="q",
                action="close_window",
                description="Close active window"
            ),
            "super+f": KeyboardShortcut(
                modifiers=[KeyModifier.SUPER],
                key="f",
                action="toggle_fullscreen",
                description="Toggle fullscreen"
            ),
            "super+space": KeyboardShortcut(
                modifiers=[KeyModifier.SUPER],
                key="space",
                action="toggle_floating",
                description="Toggle floating mode"
            ),
            # Workspace switching
            "super+1": KeyboardShortcut(
                modifiers=[KeyModifier.SUPER],
                key="1",
                action="switch_workspace_1",
                description="Switch to workspace 1"
            ),
            "super+2": KeyboardShortcut(
                modifiers=[KeyModifier.SUPER],
                key="2",
                action="switch_workspace_2",
                description="Switch to workspace 2"
            ),
            "super+3": KeyboardShortcut(
                modifiers=[KeyModifier.SUPER],
                key="3",
                action="switch_workspace_3",
                description="Switch to workspace 3"
            ),
            # Split management
            "super+h": KeyboardShortcut(
                modifiers=[KeyModifier.SUPER],
                key="h",
                action="split_left",
                description="Split left"
            ),
            "super+j": KeyboardShortcut(
                modifiers=[KeyModifier.SUPER],
                key="j",
                action="split_down",
                description="Split down"
            ),
            "super+k": KeyboardShortcut(
                modifiers=[KeyModifier.SUPER],
                key="k",
                action="split_up",
                description="Split up"
            ),
            "super+l": KeyboardShortcut(
                modifiers=[KeyModifier.SUPER],
                key="l",
                action="split_right",
                description="Split right"
            ),
        }

        for key, shortcut in defaults.items():
            self.shortcuts[key] = shortcut

    def register_shortcut(
        self,
        key_combo: str,
        action: str,
        description: str = "",
        repeatable: bool = True
    ) -> bool:
        """
        Register a keyboard shortcut.

        Args:
            key_combo: e.g., "super+a", "ctrl+shift+s"
            action: Action to execute
            description: Human-readable description
            repeatable: Can be held down to repeat

        Returns:
            Success status
        """
        try:
            modifiers, key = self._parse_key_combo(key_combo)

            shortcut = KeyboardShortcut(
                modifiers=modifiers,
                key=key,
                action=action,
                description=description,
                repeatable=repeatable
            )

            self.shortcuts[key_combo] = shortcut
            return True

        except Exception as e:
            print(f"Failed to register shortcut: {e}")
            return False

    def register_handler(self, action: str, callback: Callable) -> bool:
        """
        Register a handler for an action.

        Args:
            action: Action name
            callback: Callback function

        Returns:
            Success status
        """
        try:
            if action not in self.handlers:
                self.handlers[action] = []
            self.handlers[action].append(callback)
            return True
        except Exception as e:
            print(f"Failed to register handler: {e}")
            return False

    def execute_shortcut(self, key_combo: str) -> Tuple[bool, str]:
        """
        Execute a shortcut.

        Args:
            key_combo: e.g., "super+a"

        Returns:
            (success, message)
        """
        if key_combo not in self.shortcuts:
            return False, f"Unknown shortcut: {key_combo}"

        shortcut = self.shortcuts[key_combo]
        return self.execute_action(shortcut.action)

    def execute_action(self, action: str) -> Tuple[bool, str]:
        """
        Execute an action.

        Args:
            action: Action name

        Returns:
            (success, message)
        """
        if action not in self.handlers:
            return False, f"No handlers for action: {action}"

        results = []
        for handler in self.handlers[action]:
            try:
                result = handler()
                results.append(result)
            except Exception as e:
                results.append(f"Error: {e}")

        return True, "; ".join(str(r) for r in results)

    def _parse_key_combo(self, key_combo: str) -> Tuple[List[KeyModifier], str]:
        """
        Parse key combination.

        Args:
            key_combo: e.g., "super+shift+a"

        Returns:
            (modifiers, key)
        """
        parts = key_combo.lower().split("+")

        modifiers = []
        modifier_map = {
            "super": KeyModifier.SUPER,
            "meta": KeyModifier.META,
            "ctrl": KeyModifier.CTRL,
            "alt": KeyModifier.ALT,
            "shift": KeyModifier.SHIFT,
        }

        for part in parts[:-1]:
            if part in modifier_map:
                modifiers.append(modifier_map[part])

        key = parts[-1] if parts else ""
        return modifiers, key

    def list_shortcuts(self) -> List[Dict]:
        """List all registered shortcuts"""
        return [
            {
                "combo": combo,
                "action": shortcut.action,
                "description": shortcut.description,
            }
            for combo, shortcut in self.shortcuts.items()
        ]

    def get_shortcut_info(self, key_combo: str) -> Optional[Dict]:
        """Get info about a shortcut"""
        if key_combo not in self.shortcuts:
            return None

        shortcut = self.shortcuts[key_combo]
        return {
            "combo": key_combo,
            "modifiers": [m.value for m in shortcut.modifiers],
            "key": shortcut.key,
            "action": shortcut.action,
            "description": shortcut.description,
            "repeatable": shortcut.repeatable,
        }

    def generate_hyprland_config(self) -> str:
        """
        Generate Hyprland configuration for all shortcuts.

        Returns:
            Hyprland config content
        """
        config_lines = ["# Generated keyboard shortcuts\n"]

        for combo, shortcut in self.shortcuts.items():
            # Convert to Hyprland format: super+shift+a
            hyprland_combo = "+".join(m.value.lower() for m in shortcut.modifiers) + f"+{shortcut.key}"

            # Map action to dispatch command
            action_map = {
                "close_window": "killactive",
                "toggle_fullscreen": "fullscreen 0",
                "toggle_floating": "togglefloating",
                "split_left": "layoutmsg left",
                "split_right": "layoutmsg right",
                "split_up": "layoutmsg up",
                "split_down": "layoutmsg down",
            }

            dispatch_cmd = action_map.get(shortcut.action, shortcut.action)
            config_lines.append(f"bind = {hyprland_combo},dispatch,{dispatch_cmd}  # {shortcut.description}\n")

        return "".join(config_lines)

    # ========================================================================
    # PRESET CONFIGURATIONS
    # ========================================================================

    def load_vim_bindings(self):
        """Load Vim-style keybindings"""
        vim_bindings = {
            "super+h": ("split_left", "Move left (Vim: h)"),
            "super+j": ("split_down", "Move down (Vim: j)"),
            "super+k": ("split_up", "Move up (Vim: k)"),
            "super+l": ("split_right", "Move right (Vim: l)"),
        }

        for combo, (action, desc) in vim_bindings.items():
            self.register_shortcut(combo, action, desc)

    def load_i3_bindings(self):
        """Load i3-style keybindings"""
        i3_bindings = {
            "super+q": ("close_window", "Kill window"),
            "super+f": ("toggle_fullscreen", "Fullscreen"),
            "super+space": ("toggle_floating", "Toggle floating"),
        }

        for combo, (action, desc) in i3_bindings.items():
            self.register_shortcut(combo, action, desc)

    def get_status(self) -> Dict:
        """Get handler status"""
        return {
            "shortcuts_count": len(self.shortcuts),
            "handlers_count": len(self.handlers),
            "total_actions": len(set(s.action for s in self.shortcuts.values())),
        }
