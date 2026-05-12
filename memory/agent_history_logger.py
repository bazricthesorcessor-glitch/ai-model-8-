"""
Agent Communication History Logger - Scout ↔ Agent conversations.

Separate history for each agent, organized by date.
Creates new file each day automatically.

Files:
- ~/.avril/scout_executor_{YYYY-MM-DD}.txt    (Scout ↔ Executor)
- ~/.avril/scout_thinking_{YYYY-MM-DD}.txt    (Scout ↔ Thinking Model)
- ~/.avril/scout_router_{YYYY-MM-DD}.txt      (Scout ↔ Router Agent)
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List


class AgentHistoryLogger:
    """Log conversations between Scout and specific agents with daily rotation."""

    AGENTS = {
        "executor": "Scout ↔ Executor (UI/Terminal/Browser operations)",
        "thinking": "Scout ↔ Thinking Model (Deep reasoning & analysis)",
        "router": "Scout ↔ Router Agent (Task routing & dispatch)",
    }

    LOG_DIR = os.path.expanduser("~/.avril")

    def __init__(self, agent_name: str):
        """
        Initialize logger for specific agent.

        Args:
            agent_name: One of "executor", "thinking", "router"
        """
        if agent_name not in self.AGENTS:
            raise ValueError(f"Unknown agent: {agent_name}. Must be one of {list(self.AGENTS.keys())}")

        self.agent_name = agent_name
        self.agent_description = self.AGENTS[agent_name]

        # Ensure directory exists
        os.makedirs(self.LOG_DIR, exist_ok=True)

    def _get_log_file(self) -> str:
        """Get today's log file path."""
        today = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.LOG_DIR, f"scout_{self.agent_name}_{today}.txt")

    def append_scout(self, message: str) -> None:
        """Append Scout message."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"\n[{timestamp}] SCOUT:\n{message}\n"
        self._write(entry)

    def append_agent(self, message: str) -> None:
        """Append agent response."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        agent_label = self.agent_name.upper()
        entry = f"\n[{timestamp}] {agent_label}:\n{message}\n"
        self._write(entry)

    def append_task(self, task: str, details: Optional[str] = None) -> None:
        """Log a task being dispatched to agent."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"\n[{timestamp}] TASK: {task}"
        if details:
            entry += f"\n{details}"
        entry += "\n"
        self._write(entry)

    def append_result(self, success: bool, result: str) -> None:
        """Log task result."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "✓ SUCCESS" if success else "✗ FAILED"
        entry = f"\n[{timestamp}] RESULT [{status}]:\n{result}\n"
        self._write(entry)

    def append_section(self, title: str) -> None:
        """Append section header."""
        entry = f"\n{'─'*80}\n{title}\n{'─'*80}\n"
        self._write(entry)

    def append_raw(self, text: str) -> None:
        """Append raw text."""
        self._write(text + "\n")

    def _write(self, text: str) -> None:
        """Write to file (append)."""
        try:
            with open(self._get_log_file(), 'a', encoding='utf-8') as f:
                f.write(text)
                f.flush()
        except IOError as e:
            print(f"Error writing to log: {e}")

    def read_today(self) -> str:
        """Read today's history."""
        log_file = self._get_log_file()
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return "No history for today yet."

    def read_recent_lines(self, lines: int = 50) -> str:
        """Read last N lines of today's history."""
        log_file = self._get_log_file()
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                return ''.join(all_lines[-lines:])
        except FileNotFoundError:
            return "No history for today yet."

    def get_file_path(self) -> str:
        """Get today's log file path."""
        return self._get_log_file()

    def get_file_size(self) -> str:
        """Get file size in human readable format."""
        try:
            size = os.path.getsize(self._get_log_file())
            for unit in ['B', 'KB', 'MB']:
                if size < 1024:
                    return f"{size:.1f} {unit}"
                size /= 1024
            return f"{size:.1f} GB"
        except FileNotFoundError:
            return "0 B"

    def get_line_count(self) -> int:
        """Get total lines in today's history."""
        try:
            with open(self._get_log_file(), 'r', encoding='utf-8') as f:
                return len(f.readlines())
        except FileNotFoundError:
            return 0

    def print_info(self) -> None:
        """Print file info."""
        print(f"\n📊 {self.agent_description}")
        print(f"   File: {self.get_file_path()}")
        print(f"   Size: {self.get_file_size()}")
        print(f"   Lines: {self.get_line_count()}")


class AllAgentsHistoryManager:
    """Manage all three agent histories at once."""

    def __init__(self):
        """Initialize manager for all agents."""
        self.executor_log = AgentHistoryLogger("executor")
        self.thinking_log = AgentHistoryLogger("thinking")
        self.router_log = AgentHistoryLogger("router")

    def log_to_executor(self, scout_msg: Optional[str] = None, agent_msg: Optional[str] = None) -> None:
        """Log Executor communication."""
        if scout_msg:
            self.executor_log.append_scout(scout_msg)
        if agent_msg:
            self.executor_log.append_agent(agent_msg)

    def log_to_thinking(self, scout_msg: Optional[str] = None, agent_msg: Optional[str] = None) -> None:
        """Log Thinking Model communication."""
        if scout_msg:
            self.thinking_log.append_scout(scout_msg)
        if agent_msg:
            self.thinking_log.append_agent(agent_msg)

    def log_to_router(self, scout_msg: Optional[str] = None, agent_msg: Optional[str] = None) -> None:
        """Log Router Agent communication."""
        if scout_msg:
            self.router_log.append_scout(scout_msg)
        if agent_msg:
            self.router_log.append_agent(agent_msg)

    def log_task_execution(
        self,
        agent: str,
        task: str,
        details: Optional[str] = None,
        result: Optional[str] = None,
        success: bool = True,
    ) -> None:
        """Log complete task execution to specific agent."""
        agent_log = None

        if agent == "executor":
            agent_log = self.executor_log
        elif agent == "thinking":
            agent_log = self.thinking_log
        elif agent == "router":
            agent_log = self.router_log
        else:
            return

        agent_log.append_task(task, details)
        if result:
            agent_log.append_result(success, result)

    def print_all_info(self) -> None:
        """Print info for all agent logs."""
        print("\n" + "="*80)
        print("SCOUT AGENT COMMUNICATION LOGS")
        print("="*80)
        self.executor_log.print_info()
        self.thinking_log.print_info()
        self.router_log.print_info()
        print("="*80 + "\n")

    def print_all_histories(self) -> None:
        """Print all agent histories."""
        print("\n" + "="*80)
        print("EXECUTOR AGENT HISTORY")
        print("="*80)
        print(self.executor_log.read_today())

        print("\n" + "="*80)
        print("THINKING MODEL HISTORY")
        print("="*80)
        print(self.thinking_log.read_today())

        print("\n" + "="*80)
        print("ROUTER AGENT HISTORY")
        print("="*80)
        print(self.router_log.read_today())


# ============================================================================
# DEMO
# ============================================================================

if __name__ == "__main__":
    print("🤖 SCOUT AGENT COMMUNICATION HISTORY DEMO\n")

    # Initialize manager for all agents
    manager = AllAgentsHistoryManager()

    # ===== EXECUTOR AGENT =====
    manager.executor_log.append_section("EXECUTOR OPERATIONS")

    manager.executor_log.append_scout("""
Task: Search YouTube for "One Piece"
Context: YouTube tab already open
Action: Reuse existing tab instead of opening new
    """)

    manager.executor_log.append_agent("""
✓ Switched to YouTube tab
✓ Clicked search field
✓ Typed "One Piece"
✓ Pressed Enter
✓ Results loaded
    """)

    manager.executor_log.append_result(True, "Search completed in 2.3 seconds")

    # ===== THINKING MODEL =====
    manager.thinking_log.append_section("THINKING MODEL ANALYSIS")

    manager.thinking_log.append_scout("""
Problem: User reported repeated timeout errors
Severity: MAJOR_ISSUE
Request: Deep analysis of failure patterns
    """)

    manager.thinking_log.append_agent("""
Analysis complete:

ROOT CAUSE IDENTIFIED:
- Blocking event loop in retry logic
- Timeout not properly cancelled
- Recursive retry attempts piling up

FAILURE PATTERN:
1. Request starts
2. Timeout occurs (5s)
3. Retry callback queued
4. New request starts before cancel
5. Loop continues indefinitely

SOLUTION:
Use cancellation token + timeout wrapper
Prevents stacked requests
Proper cleanup on timeout
    """)

    manager.thinking_log.append_result(True, "Solution ready for implementation")

    # ===== ROUTER AGENT =====
    manager.router_log.append_section("TASK ROUTING DECISIONS")

    manager.router_log.append_scout("""
User Query: "optimize my function"
Context: Small improvement request
Available agents: executor, thinking_model, router
    """)

    manager.router_log.append_agent("""
ROUTING DECISION:

Intent: IMPROVEMENT
Severity: SMALL_IMPROVEMENT
Confidence: 85%

Route To: EXECUTOR
Reason: Quick optimization, minimal context needed
Memory Depth: MINIMAL
Expected Latency: <500ms
    """)

    manager.router_log.append_result(True, "Routed to executor successfully")

    # Print all info
    manager.print_all_info()

    # Print sample histories
    print("\n" + "="*80)
    print("TODAY'S EXECUTOR HISTORY (Sample)")
    print("="*80)
    print(manager.executor_log.read_today())
