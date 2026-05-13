"""
Terminal module - advanced shell command execution.
Pure input/output transformation, no logic or decision making.
Stateless, optional dependency.
"""

from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum
import subprocess
import shlex
import os
import platform


class ShellType(Enum):
    """Supported shell types."""
    BASH = "bash"
    ZSH = "zsh"
    FISH = "fish"
    POWERSHELL = "powershell"
    CMD = "cmd"
    SH = "sh"


@dataclass
class CommandResult:
    """Result of command execution."""
    stdout: str
    stderr: str
    exit_code: int
    command: str
    shell: str
    duration: float


class TerminalExecutor:
    """
    Pure command execution - no decisions, just transformation.
    Transforms command strings → execution results.
    """

    def __init__(self, shell: str = "fish", cwd: Optional[str] = None):
        """
        Initialize terminal executor.

        Args:
            shell: Shell type (bash, zsh, fish, powershell, cmd, sh)
            cwd: Working directory for commands
        """
        self.shell = shell
        self.cwd = cwd or os.getcwd()

        # Verify shell is supported
        valid_shells = {s.value for s in ShellType}
        if shell not in valid_shells:
            raise ValueError(f"Invalid shell: {shell}")

        # Verify shell exists
        if not self._shell_exists(shell):
            raise ValueError(f"Shell not found: {shell}")

    def _shell_exists(self, shell: str) -> bool:
        """Check if shell is available on system."""
        try:
            result = subprocess.run(
                ["which", shell] if platform.system() != "Windows" else ["where", shell],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except:
            return False

    def execute(
        self,
        command: str,
        timeout: int = 30,
        capture_output: bool = True,
    ) -> Tuple[bool, Optional[CommandResult], Optional[str]]:
        """
        Execute shell command.

        Args:
            command: Command to execute
            timeout: Timeout in seconds
            capture_output: Whether to capture output

        Returns:
            (success: bool, result: Optional[CommandResult], error: Optional[str])
        """
        if not command or not command.strip():
            return False, None, "Command is empty"

        try:
            import time
            start_time = time.time()

            # Prepare command
            if self.shell in ["bash", "zsh", "sh", "fish"]:
                shell_cmd = [self.shell, "-c", command]
            elif self.shell == "powershell":
                shell_cmd = ["powershell", "-Command", command]
            elif self.shell == "cmd":
                shell_cmd = ["cmd", "/c", command]
            else:
                return False, None, f"Unsupported shell: {self.shell}"

            # Execute
            result = subprocess.run(
                shell_cmd,
                cwd=self.cwd,
                capture_output=capture_output,
                timeout=timeout,
                text=True
            )

            duration = time.time() - start_time

            # Build result
            command_result = CommandResult(
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode,
                command=command,
                shell=self.shell,
                duration=duration
            )

            if result.returncode == 0:
                return True, command_result, None
            else:
                error = result.stderr or f"Command failed with exit code {result.returncode}"
                return False, command_result, error

        except subprocess.TimeoutExpired:
            return False, None, f"Command timed out after {timeout}s"
        except FileNotFoundError:
            return False, None, f"Shell not found: {self.shell}"
        except Exception as e:
            return False, None, f"Execution error: {str(e)}"

    def execute_pipe(
        self,
        commands: List[str],
        timeout: int = 30,
    ) -> Tuple[bool, Optional[CommandResult], Optional[str]]:
        """
        Execute piped commands (cmd1 | cmd2 | cmd3).

        Args:
            commands: List of commands to pipe
            timeout: Timeout in seconds

        Returns:
            (success, result, error)
        """
        if not commands:
            return False, None, "No commands provided"

        # Combine with pipes
        piped_command = " | ".join(commands)
        return self.execute(piped_command, timeout=timeout)

    def change_directory(self, path: str) -> Tuple[bool, str, Optional[str]]:
        """
        Change working directory.

        Args:
            path: Directory path

        Returns:
            (success, new_cwd, error)
        """
        if not path:
            return False, self.cwd, "Path is empty"

        if not os.path.isdir(path):
            return False, self.cwd, f"Directory not found: {path}"

        try:
            self.cwd = os.path.abspath(path)
            return True, self.cwd, None
        except Exception as e:
            return False, self.cwd, f"Failed to change directory: {str(e)}"

    def get_cwd(self) -> str:
        """Get current working directory."""
        return self.cwd

    def set_env_var(self, name: str, value: str) -> bool:
        """Set environment variable."""
        try:
            os.environ[name] = value
            return True
        except:
            return False

    def get_env_var(self, name: str, default: str = "") -> str:
        """Get environment variable."""
        return os.environ.get(name, default)


# ============================================================================
# Convenience Functions (Stateless Helpers)
# ============================================================================

def execute_command(
    command: str,
    shell: str = "fish",
    timeout: int = 30,
    cwd: Optional[str] = None,
) -> Tuple[bool, Optional[CommandResult], Optional[str]]:
    """
    Execute shell command (convenience function).

    Args:
        command: Command to execute
        shell: Shell to use
        timeout: Timeout in seconds
        cwd: Working directory

    Returns:
        (success, result, error)
    """
    try:
        executor = TerminalExecutor(shell=shell, cwd=cwd)
        return executor.execute(command, timeout=timeout)
    except ValueError as e:
        return False, None, str(e)


def execute_bash(
    command: str,
    timeout: int = 30,
    cwd: Optional[str] = None,
) -> Tuple[bool, Optional[CommandResult], Optional[str]]:
    """Execute bash command."""
    return execute_command(command, shell="bash", timeout=timeout, cwd=cwd)


def execute_python(
    code: str,
    timeout: int = 30,
) -> Tuple[bool, Optional[CommandResult], Optional[str]]:
    """Execute Python code."""
    return execute_command(f'python -c "{code}"', timeout=timeout)


def list_directory(
    path: str = ".",
    show_hidden: bool = False,
) -> Tuple[bool, List[str], Optional[str]]:
    """List directory contents."""
    try:
        if not os.path.isdir(path):
            return False, [], f"Not a directory: {path}"

        items = os.listdir(path)

        if not show_hidden:
            items = [i for i in items if not i.startswith(".")]

        items.sort()
        return True, items, None

    except Exception as e:
        return False, [], str(e)


def read_file(
    filepath: str,
    max_lines: Optional[int] = None,
) -> Tuple[bool, str, Optional[str]]:
    """Read file contents."""
    try:
        with open(filepath, "r") as f:
            if max_lines:
                lines = [f.readline() for _ in range(max_lines)]
                content = "".join(lines)
            else:
                content = f.read()

        return True, content, None

    except FileNotFoundError:
        return False, "", f"File not found: {filepath}"
    except Exception as e:
        return False, "", str(e)


def get_system_info() -> Dict[str, str]:
    """Get system information."""
    return {
        "os": platform.system(),
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "hostname": os.uname()[1] if hasattr(os, "uname") else "unknown",
        "cwd": os.getcwd(),
    }
