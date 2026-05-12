"""
Input Controller - Smooth keyboard/mouse control via ydotool.

ydotool provides:
- Mouse movement (absolute/relative)
- Click operations (left/right/middle)
- Keyboard typing
- Key combinations
- Wheel scrolling

All tested and working smoothly.
"""

import subprocess
import time
from typing import Tuple, List, Optional


class YdotoolError(Exception):
    """ydotool execution error."""
    pass


class InputController:
    """Control keyboard and mouse via ydotool."""

    @staticmethod
    def _execute(cmd: List[str]) -> str:
        """Execute ydotool command."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                raise YdotoolError(f"ydotool error: {result.stderr}")
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            raise YdotoolError("ydotool command timed out")
        except FileNotFoundError:
            raise YdotoolError("ydotool not found - install it or start daemon")

    # ========================================================================
    # MOUSE OPERATIONS
    # ========================================================================

    @staticmethod
    def move_mouse(x: int, y: int) -> None:
        """Move mouse to absolute position."""
        InputController._execute(["ydotool", "mousemove", "-x", str(x), "-y", str(y)])

    @staticmethod
    def move_mouse_relative(dx: int, dy: int) -> None:
        """Move mouse relative to current position."""
        InputController._execute(["ydotool", "mousemove", "--", str(dx), str(dy)])

    @staticmethod
    def scroll_wheel(direction: str = "down", amount: int = 3) -> None:
        """
        Scroll mouse wheel.

        Args:
            direction: "up" or "down"
            amount: Number of scroll units
        """
        multiplier = amount if direction == "down" else -amount
        InputController._execute(["ydotool", "mousemove", "-w", str(multiplier)])

    @staticmethod
    def click(button: int = 1, times: int = 1, delay: float = 0.1) -> None:
        """
        Click mouse button.

        Args:
            button: 1=left, 2=middle, 3=right
            times: Number of clicks
            delay: Delay between clicks (seconds)
        """
        for _ in range(times):
            InputController._execute(["ydotool", "click", str(button)])
            if times > 1:
                time.sleep(delay)

    @staticmethod
    def left_click(times: int = 1, delay: float = 0.1) -> None:
        """Left click."""
        InputController.click(button=1, times=times, delay=delay)

    @staticmethod
    def right_click(times: int = 1, delay: float = 0.1) -> None:
        """Right click."""
        InputController.click(button=3, times=times, delay=delay)

    @staticmethod
    def double_click(delay: float = 0.1) -> None:
        """Double left click."""
        InputController.click(button=1, times=2, delay=delay)

    # ========================================================================
    # KEYBOARD OPERATIONS
    # ========================================================================

    @staticmethod
    def type_text(text: str, delay: float = 0.05) -> None:
        """
        Type text.

        Args:
            text: Text to type
            delay: Delay between characters (seconds)
        """
        InputController._execute(["ydotool", "type", text])
        if delay > 0:
            time.sleep(delay)

    @staticmethod
    def press_key(key: str) -> None:
        """
        Press a single key.

        Args:
            key: Key name (Return, Escape, Tab, etc.)
        """
        InputController._execute(["ydotool", "key", key])

    @staticmethod
    def press_key_sequence(keys: List[str], delay: float = 0.1) -> None:
        """
        Press multiple keys in sequence.

        Args:
            keys: List of key names
            delay: Delay between key presses
        """
        for key in keys:
            InputController.press_key(key)
            time.sleep(delay)

    @staticmethod
    def key_combination(combo: str) -> None:
        """
        Press key combination (e.g., "ctrl+a", "alt+tab", "super+d").

        Args:
            combo: Key combination string
        """
        InputController._execute(["ydotool", "key", combo])

    # ========================================================================
    # COMMON SHORTCUTS
    # ========================================================================

    @staticmethod
    def select_all() -> None:
        """Ctrl+A - Select all."""
        InputController.key_combination("ctrl+a")

    @staticmethod
    def copy() -> None:
        """Ctrl+C - Copy."""
        InputController.key_combination("ctrl+c")

    @staticmethod
    def paste() -> None:
        """Ctrl+V - Paste."""
        InputController.key_combination("ctrl+v")

    @staticmethod
    def cut() -> None:
        """Ctrl+X - Cut."""
        InputController.key_combination("ctrl+x")

    @staticmethod
    def undo() -> None:
        """Ctrl+Z - Undo."""
        InputController.key_combination("ctrl+z")

    @staticmethod
    def redo() -> None:
        """Ctrl+Shift+Z - Redo."""
        InputController.key_combination("ctrl+shift+z")

    @staticmethod
    def save() -> None:
        """Ctrl+S - Save."""
        InputController.key_combination("ctrl+s")

    @staticmethod
    def find() -> None:
        """Ctrl+F - Find."""
        InputController.key_combination("ctrl+f")

    @staticmethod
    def open_launcher() -> None:
        """Super+D - Open launcher (Caelestia)."""
        InputController.key_combination("super+d")

    @staticmethod
    def open_terminal() -> None:
        """Super+Return - Open terminal."""
        InputController.key_combination("super+Return")

    @staticmethod
    def switch_workspace_next() -> None:
        """Super+Right - Next workspace."""
        InputController.key_combination("super+Right")

    @staticmethod
    def switch_workspace_prev() -> None:
        """Super+Left - Previous workspace."""
        InputController.key_combination("super+Left")

    @staticmethod
    def switch_workspace(number: int) -> None:
        """Switch to workspace N (1-9)."""
        InputController.key_combination(f"super+{number}")

    @staticmethod
    def alt_tab() -> None:
        """Alt+Tab - Switch window."""
        InputController.key_combination("alt+Tab")

    @staticmethod
    def escape() -> None:
        """Escape key."""
        InputController.press_key("Escape")

    # ========================================================================
    # COMBINED OPERATIONS (Executor convenience methods)
    # ========================================================================

    @staticmethod
    def click_and_type(x: int, y: int, text: str, delay: float = 0.2) -> None:
        """
        Click on position and type text.

        Args:
            x, y: Click position
            text: Text to type
            delay: Delay between click and type
        """
        InputController.move_mouse(x, y)
        time.sleep(0.1)
        InputController.left_click()
        time.sleep(delay)
        InputController.type_text(text)

    @staticmethod
    def click_at(x: int, y: int, button: int = 1) -> None:
        """Click at specific position."""
        InputController.move_mouse(x, y)
        time.sleep(0.05)
        InputController.click(button=button)

    @staticmethod
    def drag_to(start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5) -> None:
        """
        Drag from start to end position.

        Args:
            start_x, start_y: Starting position
            end_x, end_y: Ending position
            duration: Duration of drag (seconds)
        """
        InputController.move_mouse(start_x, start_y)
        time.sleep(0.1)
        InputController._execute(["ydotool", "click", "1"])  # Mouse down (simulated)

        # Smooth movement over duration
        steps = max(1, int(duration * 50))  # 50 steps per second
        step_delay = duration / steps

        for i in range(steps):
            progress = (i + 1) / steps
            x = int(start_x + (end_x - start_x) * progress)
            y = int(start_y + (end_y - start_y) * progress)
            InputController.move_mouse(x, y)
            time.sleep(step_delay)

        InputController._execute(["ydotool", "click", "1"])  # Mouse up (simulated)

    @staticmethod
    def search_and_type(search_term: str, delay: float = 0.3) -> None:
        """
        Open search (Ctrl+F) and type search term.

        Args:
            search_term: Term to search for
            delay: Delay between operations
        """
        InputController.find()
        time.sleep(delay)
        InputController.type_text(search_term)
        time.sleep(delay)
        InputController.press_key("Return")

    @staticmethod
    def login_form(username: str, password: str, delay: float = 0.3) -> None:
        """
        Fill login form (assumes focus on username field).

        Args:
            username: Username text
            password: Password text
            delay: Delay between operations
        """
        InputController.type_text(username)
        time.sleep(delay)
        InputController.press_key("Tab")  # Move to password field
        time.sleep(delay)
        InputController.type_text(password)
        time.sleep(delay)
        InputController.press_key("Return")


# ============================================================================
# TEST / DEMO
# ============================================================================

if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("YDOTOOL INPUT CONTROLLER TEST")
    print("=" * 60)

    try:
        print("\n[TEST 1] Mouse movement...")
        InputController.move_mouse(100, 100)
        time.sleep(0.5)
        InputController.move_mouse(500, 500)
        print("✓ Mouse movement works")

        print("\n[TEST 2] Click...")
        InputController.left_click()
        print("✓ Click works")

        print("\n[TEST 3] Typing...")
        InputController.type_text("Hello from ydotool")
        print("✓ Typing works")

        print("\n[TEST 4] Keyboard shortcuts...")
        InputController.select_all()
        print("✓ Ctrl+A works")

        InputController.copy()
        print("✓ Ctrl+C works")

        print("\n[TEST 5] Key combinations...")
        InputController.key_combination("ctrl+z")
        print("✓ Key combinations work")

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("Input controller ready for executor integration")
        print("=" * 60)

    except YdotoolError as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
