"""
Scout Context Router - Routes to correct query maker based on conversation partner.

ROUTING LOGIC:
  Scout ↔ LLM (llama3.2:8b)  → Query Maker 1 (full context)
  Scout ↔ Agents             → Query Maker 2 (agent-specific context)
  Main.py startup            → Load last conversation from memory
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from enum import Enum

from memory.unified_memory import UnifiedMemory
from tools.query_maker1 import StateGatherer
from tools.unified_query_maker import ContextCompiler, SeverityLevel


class ConversationPartner(Enum):
    """Types of conversation partners."""
    LLM = "llm"              # llama3.2:8b or other external LLM
    EXECUTOR = "executor"    # Executor agent
    CODER = "coder"          # Coder agent
    THINKER = "thinker"      # Thinker agent


class ScoutContextRouter:
    """Routes Scout conversations to correct query maker."""

    def __init__(self, memory_root: str = "memory"):
        self.memory = UnifiedMemory(memory_root)
        self.compiler = ContextCompiler(self.memory)

        # Track last conversation for continuity
        self.last_session_file = Path(memory_root) / "state" / "last_session.json"
        self.current_conversation = []

    # ========================================================================
    # CONVERSATION ROUTING
    # ========================================================================

    def get_context(
        self,
        partner: ConversationPartner,
        current_task: str,
        severity: SeverityLevel = SeverityLevel.SMALL_FIX,
        task_description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Route to correct query maker based on conversation partner.

        Args:
            partner: Who Scout is talking to
            current_task: What's being worked on
            severity: Problem severity
            task_description: Detailed task description

        Returns:
            Complete context dict for the conversation
        """
        if partner == ConversationPartner.LLM:
            return self._get_llm_context(current_task, severity, task_description)
        else:
            return self._get_agent_context(partner, current_task, severity)

    # ========================================================================
    # QUERY MAKER 1: LLM CONTEXT (FULL & RICH)
    # ========================================================================

    def _get_llm_context(
        self,
        current_task: str,
        severity: SeverityLevel,
        task_description: Optional[str],
    ) -> Dict[str, Any]:
        """
        Query Maker 1: Context for talking with external LLM.

        LLM (llama3.2:8b) needs:
        - Full system state
        - Complete recent memory
        - Deep archive for learning
        - Detailed task context
        """
        context = {
            "partner": "llm",
            "query_maker": "query_maker_1",
            "timestamp": time.time(),
        }

        # Get full state awareness
        context["system_state"] = self._get_full_state()

        # Get complete memory (no truncation for LLM)
        context["memory"] = {
            "recent": self.memory.recall(days=14, limit=100),
            "relevant_archive": self.memory.search(current_task, limit=20),
            "conversation_history": self.current_conversation[-30:],  # Last 30 messages
        }

        # Get task details
        context["task"] = {
            "name": current_task,
            "description": task_description or "",
            "severity": severity.name,
        }

        # Get all available capabilities
        context["capabilities"] = {
            "agents": ["executor", "coder", "thinker"],
            "tools": [
                "python",
                "shell",
                "browser",
                "filesystem",
                "websearch",
            ],
            "state_access": True,
            "memory_access": True,
        }

        # Scout's decision context
        context["scout_role"] = {
            "role": "Coordinator asking external LLM for strategic thinking",
            "can_execute": False,
            "can_delegate": True,
            "needs_reasoning": True,
        }

        return context

    # ========================================================================
    # QUERY MAKER 2: AGENT CONTEXT (FOCUSED & SPECIFIC)
    # ========================================================================

    def _get_agent_context(
        self,
        partner: ConversationPartner,
        current_task: str,
        severity: SeverityLevel,
    ) -> Dict[str, Any]:
        """
        Query Maker 2: Context for talking with internal agents.

        Agents need:
        - Focused, action-oriented context
        - Current state (most important)
        - Recent memory for their domain
        - Constraints and capabilities
        """
        context = {
            "partner": partner.value,
            "query_maker": "query_maker_2",
            "timestamp": time.time(),
        }

        # Current state is CRITICAL for agents
        context["current_state"] = self.memory.get_state()

        # Agent-specific context from compiler
        agent_context = self.compiler.compile(
            agent=partner.value,
            task=current_task,
            severity=severity,
        )

        # Merge in agent-specific info
        context.update(agent_context)

        # Add instructions for this specific agent
        context["instructions"] = self._get_agent_instructions(partner)

        return context

    # ========================================================================
    # STATE RETRIEVAL
    # ========================================================================

    def _get_full_state(self) -> Dict[str, Any]:
        """Get complete system state for LLM context."""
        state = self.memory.get_state()

        if state is None:
            return {"status": "no_current_state"}

        return {
            "browser": state.browser,
            "workspace": state.workspace,
            "agents": state.agents,
            "system": state.system,
            "tasks": state.tasks,
            "timestamp": state.timestamp,
        }

    def _get_agent_instructions(self, partner: ConversationPartner) -> str:
        """Get specific instructions for agent."""
        instructions = {
            ConversationPartner.EXECUTOR: """
Execute the task using available system tools.
- Check current state first (don't duplicate actions)
- Reuse existing windows/tabs
- Log all actions and results
- Report success/failure clearly
""",
            ConversationPartner.CODER: """
Analyze/write code following these principles:
- Follow existing patterns
- Test before submitting
- Document changes
- Don't over-engineer
""",
            ConversationPartner.THINKER: """
Analyze the problem strategically:
- Explain your reasoning
- Learn from failures
- Suggest improvements
- Respect constraints
""",
        }

        return instructions.get(partner, "")

    # ========================================================================
    # CONVERSATION TRACKING
    # ========================================================================

    def add_message(
        self,
        speaker: str,
        message: str,
        partner: ConversationPartner,
    ) -> None:
        """
        Track message in conversation and memory.

        Args:
            speaker: Who said it ('user', 'scout', 'llm', 'executor', etc.)
            message: What they said
            partner: Who they're talking to
        """
        # Add to conversation history
        self.current_conversation.append({
            "timestamp": time.time(),
            "speaker": speaker,
            "message": message,
            "partner": partner.value,
        })

        # Add to memory
        importance = 8 if speaker in ("llm", "scout") else 6

        self.memory.remember(
            speaker=speaker,
            message=message,
            agent_role="scout",  # Scout is coordinating
            importance=importance,
            tags=[partner.value, "conversation"],
        )

    def save_session(self) -> None:
        """Save current session for continuity."""
        session_data = {
            "timestamp": time.time(),
            "messages": self.current_conversation,
            "last_partner": self.current_conversation[-1]["partner"]
            if self.current_conversation else None,
        }

        with open(self.last_session_file, "w") as f:
            json.dump(session_data, f, indent=2, default=str)

    def load_last_session(self) -> Dict[str, Any]:
        """Load last conversation for continuity."""
        if not self.last_session_file.exists():
            return {"status": "no_previous_session"}

        try:
            with open(self.last_session_file, "r") as f:
                session = json.load(f)

            # Reconstruct conversation
            self.current_conversation = session.get("messages", [])

            return {
                "status": "loaded",
                "messages": len(self.current_conversation),
                "last_partner": session.get("last_partner"),
                "timestamp": session.get("timestamp"),
            }
        except json.JSONDecodeError:
            return {"status": "error_loading_session"}

    # ========================================================================
    # CONTEXT SUMMARY
    # ========================================================================

    def get_context_summary(self, context: Dict[str, Any]) -> str:
        """Generate human-readable summary of context."""
        partner = context.get("partner", "unknown")
        query_maker = context.get("query_maker", "unknown")

        if query_maker == "query_maker_1":
            summary = f"""
CONTEXT FOR LLM ({partner}):
  Query Maker: {query_maker} (full context)
  Task: {context.get('task', {}).get('name', 'unknown')}
  Severity: {context.get('task', {}).get('severity', 'unknown')}

  Memory:
    - Recent: {len(context.get('memory', {}).get('recent', []))} entries
    - Archive: {len(context.get('memory', {}).get('relevant_archive', []))} results
    - Conversation: {len(context.get('memory', {}).get('conversation_history', []))} messages

  Capabilities: {len(context.get('capabilities', {}).get('agents', []))} agents, {len(context.get('capabilities', {}).get('tools', []))} tools
"""
        else:
            summary = f"""
CONTEXT FOR AGENT ({partner}):
  Query Maker: {query_maker} (focused context)
  Task: {context.get('identity', {}).get('role', 'unknown')}

  Current State:
    - Browser tabs: {len(context.get('current_state', {}).get('browser', {}).get('tabs', []))}
    - Active workspace: {context.get('current_state', {}).get('workspace', {}).get('active', 'unknown')}
    - Active tasks: {len(context.get('current_state', {}).get('tasks', {}).get('active', []))}

  Available Tools: {len(context.get('tools', []))} tools
  Constraints: {len(context.get('constraints', []))} constraints
"""

        return summary


# ============================================================================
# MAIN.PY INTEGRATION
# ============================================================================

def init_scout_session() -> ScoutContextRouter:
    """
    Initialize Scout session with continuity from last conversation.

    Call this in main.py:
        scout = init_scout_session()
        last_session = scout.load_last_session()
        print(f"Loaded {last_session['messages']} messages from last session")
    """
    router = ScoutContextRouter()

    # Load last conversation
    last = router.load_last_session()
    print(f"[Scout] Last session: {last['status']}")

    if last['status'] == 'loaded':
        print(f"[Scout] Restoring {last['messages']} messages from last session")
        print(f"[Scout] Last partner was: {last['last_partner']}")

    return router


def scout_talk_to_llm(
    router: ScoutContextRouter,
    task: str,
    user_message: str,
    severity: SeverityLevel = SeverityLevel.SMALL_FIX,
) -> Dict[str, Any]:
    """
    Scout talks to LLM (llama3.2:8b).

    Usage in main.py:
        result = scout_talk_to_llm(
            router=scout,
            task="optimize function",
            user_message="Can you make this faster?",
        )
    """
    # Get full context for LLM
    context = router.get_context(
        partner=ConversationPartner.LLM,
        current_task=task,
        severity=severity,
        task_description=user_message,
    )

    # Track the conversation
    router.add_message("user", user_message, ConversationPartner.LLM)

    return {
        "context": context,
        "summary": router.get_context_summary(context),
        "ready_for_llm": True,
    }


def scout_talk_to_agent(
    router: ScoutContextRouter,
    agent: str,
    task: str,
    severity: SeverityLevel = SeverityLevel.SMALL_FIX,
) -> Dict[str, Any]:
    """
    Scout talks to internal agent.

    Usage in main.py:
        result = scout_talk_to_agent(
            router=scout,
            agent="executor",
            task="take screenshot",
        )
    """
    # Map agent name to enum
    partner_map = {
        "executor": ConversationPartner.EXECUTOR,
        "coder": ConversationPartner.CODER,
        "thinker": ConversationPartner.THINKER,
    }

    partner = partner_map.get(agent)
    if not partner:
        return {"error": f"Unknown agent: {agent}"}

    # Get focused context for agent
    context = router.get_context(
        partner=partner,
        current_task=task,
        severity=severity,
    )

    # Track the delegation
    router.add_message("scout", f"Delegating to {agent}: {task}", partner)

    return {
        "context": context,
        "summary": router.get_context_summary(context),
        "agent": agent,
        "ready_for_agent": True,
    }


# ============================================================================
# DEMO / TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("SCOUT CONTEXT ROUTER TEST")
    print("=" * 70)

    # Initialize Scout with session continuity
    print("\n[1] Initializing Scout...")
    scout = init_scout_session()

    # Test: Talk to LLM
    print("\n[2] Scout talks to LLM...")
    result = scout_talk_to_llm(
        router=scout,
        task="optimize code",
        user_message="Can you make this function faster?",
        severity=SeverityLevel.SMALL_FIX,
    )
    print(result["summary"])

    # Test: Talk to Executor
    print("\n[3] Scout talks to Executor...")
    result = scout_talk_to_agent(
        router=scout,
        agent="executor",
        task="take screenshot",
        severity=SeverityLevel.SMALL_FIX,
    )
    print(result["summary"])

    # Save session
    print("\n[4] Saving session...")
    scout.save_session()
    print("✓ Session saved")

    print("\n" + "=" * 70)
    print("✓ ROUTER TEST PASSED")
    print("=" * 70)
