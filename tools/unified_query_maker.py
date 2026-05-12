"""
UNIFIED QUERY MAKER - Context Compilation Engine

Consolidates:
- query_maker1.py (state-aware context)
- query_maker2.py (adaptive depth for thinking)

Single system that decides what enters the 1M token context window for any agent.
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from memory.unified_memory import UnifiedMemory


class SeverityLevel(Enum):
    """Problem severity classification."""
    SMALL_FIX = 1            # Small improvement, user happy
    MAJOR_ISSUE = 2          # Repeated failure, needs deep analysis
    ARCHITECTURAL = 3        # Fundamental redesign required


class ContextCompiler:
    """Builds optimal context for any agent."""

    def __init__(self, memory: UnifiedMemory):
        self.memory = memory

    def compile(
        self,
        agent: str,
        task: str,
        severity: SeverityLevel = SeverityLevel.SMALL_FIX,
        token_limit: int = 1_000_000,
    ) -> Dict[str, Any]:
        """
        Compile context for an agent.

        Args:
            agent: Agent name ('scout', 'executor', 'coder', 'thinker')
            task: Current task description
            severity: How deep to search memory
            token_limit: Max tokens available

        Returns:
            Context dict with all sections
        """
        context = {}

        # Allocate tokens based on severity
        allocation = self._allocate_tokens(severity, token_limit)

        # 1. IDENTITY (always included)
        context["identity"] = self._get_identity(agent)

        # 2. CURRENT STATE (most important for execution)
        context["state"] = self._get_current_state()

        # 3. ACTIVE MEMORY (exact recent logs)
        context["active_memory"] = self._get_active_memory(
            agent=agent,
            tokens=allocation["active_memory"],
        )

        # 4. RELEVANT ARCHIVE (based on severity)
        context["archive"] = self._get_relevant_archive(
            agent=agent,
            task=task,
            severity=severity,
            tokens=allocation["archive"],
        )

        # 5. TOOLS/CAPABILITIES
        context["tools"] = self._get_tool_capabilities(agent)

        # 6. CONSTRAINTS
        context["constraints"] = self._get_constraints(agent)

        return context

    def _allocate_tokens(
        self,
        severity: SeverityLevel,
        total: int,
    ) -> Dict[str, int]:
        """Allocate tokens based on severity level."""
        if severity == SeverityLevel.SMALL_FIX:
            # Keep focused for small improvements
            return {
                "identity": 50_000,
                "state": 150_000,
                "active_memory": 300_000,
                "archive": 100_000,
                "tools": 100_000,
                "constraints": 50_000,
                "task": 50_000,
                "buffer": 200_000,
            }

        elif severity == SeverityLevel.MAJOR_ISSUE:
            # Deep context for major problems
            return {
                "identity": 80_000,
                "state": 150_000,
                "active_memory": 250_000,
                "archive": 300_000,  # More archive
                "tools": 100_000,
                "constraints": 50_000,
                "task": 50_000,
                "buffer": 20_000,
            }

        elif severity == SeverityLevel.ARCHITECTURAL:
            # Full deep dive
            return {
                "identity": 100_000,
                "state": 150_000,
                "active_memory": 200_000,
                "archive": 400_000,  # Maximum archive
                "tools": 100_000,
                "constraints": 50_000,
                "task": 50_000,
                "buffer": 0,
            }

        return {}

    def _get_identity(self, agent: str) -> Dict[str, Any]:
        """Get agent's permanent identity/personality."""
        identities = {
            "scout": {
                "role": "Master Coordinator",
                "duties": [
                    "Coordinate all agents",
                    "Manage context",
                    "Track state",
                    "Make decisions",
                ],
                "constraints": [
                    "Never execute directly",
                    "Verify agent responses",
                    "Track memory",
                ],
            },
            "executor": {
                "role": "System Executor",
                "duties": [
                    "Execute system commands",
                    "Control browser",
                    "Manage keyboard/mouse",
                    "Handle UI",
                ],
                "constraints": [
                    "Only execute approved tasks",
                    "Reuse existing windows",
                    "Don't duplicate tabs",
                    "State-aware execution",
                ],
            },
            "coder": {
                "role": "Code Operations",
                "duties": [
                    "Analyze code",
                    "Write code",
                    "Fix bugs",
                    "Refactor",
                ],
                "constraints": [
                    "Follow existing patterns",
                    "Test before committing",
                    "Document changes",
                ],
            },
            "thinker": {
                "role": "Strategic Thinking",
                "duties": [
                    "Analyze problems",
                    "Plan solutions",
                    "Learn from failures",
                    "Suggest improvements",
                ],
                "constraints": [
                    "Don't over-optimize",
                    "Respect user preferences",
                    "Explain reasoning",
                ],
            },
        }

        return identities.get(agent, {})

    def _get_current_state(self) -> Dict[str, Any]:
        """Get current system state."""
        state = self.memory.get_state()

        if state is None:
            return {
                "browser": {},
                "workspace": {},
                "agents": {},
                "system": {},
                "tasks": {},
            }

        return {
            "browser": state.browser,
            "workspace": state.workspace,
            "agents": state.agents,
            "system": state.system,
            "tasks": state.tasks,
        }

    def _get_active_memory(
        self,
        agent: str,
        tokens: int,
    ) -> List[Dict[str, Any]]:
        """Get active memory relevant to agent."""
        # Get 2-week exact logs
        entries = self.memory.recall(
            days=14,
            agent_role=agent,
            limit=50,  # Top 50 entries by recency
        )

        # Convert to context-friendly format
        return [
            {
                "timestamp": e.timestamp,
                "speaker": e.speaker,
                "message": e.message,
                "priority": e.priority_score,
                "tags": e.tags,
            }
            for e in entries
        ]

    def _get_relevant_archive(
        self,
        agent: str,
        task: str,
        severity: SeverityLevel,
        tokens: int,
    ) -> List[Dict[str, Any]]:
        """Search archive based on task and severity."""
        results = []

        # Always search failures
        failures = self.memory.search(
            query=task,
            category="failures",
            limit=5,
        )
        results.extend(failures)

        # For major issues, search more deeply
        if severity in (SeverityLevel.MAJOR_ISSUE, SeverityLevel.ARCHITECTURAL):
            projects = self.memory.search(
                query=task,
                category="projects",
                limit=10,
            )
            results.extend(projects)

            conversations = self.memory.search(
                query=task,
                category="conversations",
                limit=10,
            )
            results.extend(conversations)

        return results[:20]  # Limit to 20 archive entries

    def _get_tool_capabilities(self, agent: str) -> Dict[str, List[str]]:
        """Get available tools for agent."""
        tools = {
            "scout": [
                "memory_access",
                "agent_coordination",
                "state_tracking",
                "decision_making",
            ],
            "executor": [
                "shell_commands",
                "browser_automation",
                "keyboard_mouse",
                "window_management",
                "file_operations",
            ],
            "coder": [
                "python_execution",
                "file_read_write",
                "code_analysis",
                "version_control",
                "testing",
            ],
            "thinker": [
                "logical_reasoning",
                "pattern_analysis",
                "failure_investigation",
                "optimization",
                "planning",
            ],
        }

        return tools.get(agent, [])

    def _get_constraints(self, agent: str) -> List[str]:
        """Get operational constraints for agent."""
        constraints = {
            "scout": [
                "Never execute directly",
                "Always coordinate through agents",
                "Track all state changes",
                "Verify agent responses",
            ],
            "executor": [
                "Only approved tasks",
                "Reuse existing windows/tabs",
                "State-aware execution",
                "Verify success before continuing",
            ],
            "coder": [
                "Write idiomatic Python",
                "Follow existing patterns",
                "Test before submitting",
                "No breaking changes",
            ],
            "thinker": [
                "Explain reasoning",
                "Learn from failures",
                "Respect user preferences",
                "Don't over-engineer",
            ],
        }

        return constraints.get(agent, [])


# ============================================================================
# QUERY MAKER CONVENIENCE FUNCTION
# ============================================================================

def make_query(
    memory: UnifiedMemory,
    agent: str,
    task: str,
    severity: SeverityLevel = SeverityLevel.SMALL_FIX,
) -> Dict[str, Any]:
    """
    Quick function to compile context for an agent.

    Usage:
        context = make_query(
            memory=mem,
            agent="executor",
            task="Take screenshot",
            severity=SeverityLevel.SMALL_FIX,
        )
    """
    compiler = ContextCompiler(memory)
    return compiler.compile(
        agent=agent,
        task=task,
        severity=severity,
    )


# ============================================================================
# DEMO
# ============================================================================

if __name__ == "__main__":
    from memory.unified_memory import UnifiedMemory, SystemState
    import time

    print("=" * 70)
    print("UNIFIED QUERY MAKER TEST")
    print("=" * 70)

    mem = UnifiedMemory()

    # Setup some memory
    print("\n[SETUP] Creating memory...")
    mem.remember(
        speaker="user",
        message="Take screenshot and send to ChatGPT",
        agent_role="scout",
        importance=8,
    )
    mem.remember(
        speaker="executor",
        message="Screenshot taken",
        agent_role="executor",
        importance=7,
    )

    # Setup state
    state = SystemState(
        timestamp=time.time(),
        browser={"tabs": ["ChatGPT"], "active": "ChatGPT"},
        workspace={"active": 2},
        agents={"executor": "idle"},
        system={"brightness": 0.8},
        tasks={"active": ["task_001"]},
    )
    mem.update_state(state)

    # Test: Compile context for Executor
    print("\n[TEST] Compiling context for Executor...")
    context = make_query(
        memory=mem,
        agent="executor",
        task="Take screenshot",
        severity=SeverityLevel.SMALL_FIX,
    )

    print(f"Context sections: {list(context.keys())}")
    print(f"Identity: {context['identity']['role']}")
    print(f"State: {context['state']['browser']}")
    print(f"Active memory entries: {len(context['active_memory'])}")
    print(f"Tools available: {len(context['tools'])} tools")

    print("\n" + "=" * 70)
    print("✓ QUERY MAKER TEST PASSED")
    print("=" * 70)
