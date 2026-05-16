"""
Scout Context Compiler - MOST CRITICAL FILE
Builds comprehensive Scout prompt with all necessary context for decision-making.

Structure:
  [IDENTITY] - Scout's identity and preferences
  [TIME_DATE] - Current time and date context
  [STATE] - Current system state (browser, workspace, agents, tasks)
  [AGENTS] - Status and capabilities of other agents
  [IMPORTANT MEMORY] - User-explicit important memories
  [RECENT 14 DAYS] - Recent decision/action history
  [RELEVANT ARCHIVE] - Contextual archive items (projects, failures, conversations)
  [TOOLS] - Available tools and their status
  [CURRENT QUERY] - The immediate query/task
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from . import paths
from .reader import MemoryReader
from .writer import MemoryWriter


class ContextCompiler:
    """Compiles comprehensive context for Scout."""

    # ========================================================================
    # TOKEN ALLOCATION (10M token window)
    # ========================================================================
    TOTAL_TOKENS = 10_000_000
    RESERVED_TOKENS = 1_000_000  # For response generation

    # Default allocation percentages
    TOKEN_ALLOCATION = {
        "identity": 0.02,           # 20K
        "time_date": 0.005,         # 5K
        "state": 0.10,              # 100K
        "agents": 0.05,             # 50K
        "important_memory": 0.08,   # 80K
        "recent_14_days": 0.20,     # 200K
        "relevant_archive": 0.25,   # 250K
        "tools": 0.10,              # 100K
        "current_query": 0.15,      # 150K
    }

    @staticmethod
    def get_token_budget(section: str) -> int:
        """Get token budget for a specific section."""
        available = ContextCompiler.TOTAL_TOKENS - ContextCompiler.RESERVED_TOKENS
        percentage = ContextCompiler.TOKEN_ALLOCATION.get(section, 0.1)
        return int(available * percentage)

    # ========================================================================
    # CONTEXT SECTION BUILDERS
    # ========================================================================

    @staticmethod
    def build_identity_section() -> str:
        """Build [IDENTITY] section - Scout's core identity."""
        identity = MemoryReader.load_identity()
        preferences = MemoryReader.load_user_preferences()

        section = """[IDENTITY]
Scout - Persistent Memory and Decision-Making System
Role: Maintains 14-day active memory, archives important information, coordinates with agents
Personality: Logical, systematic, detail-oriented
Core Responsibility: Being the system's long-term memory and strategic coordinator

Key Preferences:
"""
        if preferences:
            for key, value in preferences.items():
                section += f"  - {key}: {value}\n"
        else:
            section += "  - (No preferences configured)\n"

        if identity:
            section += "\nIdentity Data:\n"
            section += json.dumps(identity, indent=2)

        return section

    @staticmethod
    def build_time_date_section() -> str:
        """Build [TIME_DATE] section - Current temporal context."""
        now = datetime.now()

        section = f"""[TIME_DATE]
Current Time: {now.strftime('%Y-%m-%d %H:%M:%S')}
Date: {now.strftime('%A, %B %d, %Y')}
Day of Week: {now.strftime('%A')}
Week Number: {now.isocalendar().week}

Time Context:
"""
        # Add upcoming events
        upcoming_deadlines = MemoryReader.get_upcoming_deadlines(days=7)
        upcoming_exams = MemoryReader.get_upcoming_exams(days=7)

        if upcoming_deadlines:
            section += "  Upcoming Deadlines:\n"
            for deadline in upcoming_deadlines:
                section += f"    - {deadline.get('title')}: {deadline.get('date')}\n"

        if upcoming_exams:
            section += "  Upcoming Exams:\n"
            for exam in upcoming_exams:
                section += f"    - {exam.get('name')}: {exam.get('date')}\n"

        if not upcoming_deadlines and not upcoming_exams:
            section += "  (No upcoming deadlines or exams in next 7 days)\n"

        return section

    @staticmethod
    def build_state_section() -> str:
        """Build [STATE] section - Current system state."""
        current_state = MemoryReader.load_current_state()
        agents_state = MemoryReader.load_agents_state()
        browser_state = MemoryReader.load_browser_state()
        workspace_state = MemoryReader.load_workspace_state()

        section = "[STATE]\nCurrent System State:\n"

        if current_state.get("state"):
            section += f"  General State: {current_state.get('state')}\n"

        if agents_state.get("agents"):
            section += "  Agents Status:\n"
            for agent, status in agents_state.get("agents", {}).items():
                section += f"    - {agent}: {status}\n"

        if browser_state:
            section += "  Browser State:\n"
            section += f"    - Current URL: {browser_state.get('current_url', 'N/A')}\n"
            section += f"    - Tabs Open: {browser_state.get('tabs_count', 0)}\n"

        if workspace_state:
            section += "  Workspace State:\n"
            section += f"    - Focused Window: {workspace_state.get('focused_window', 'N/A')}\n"
            section += f"    - Active Workspace: {workspace_state.get('active_workspace', 'N/A')}\n"

        return section

    @staticmethod
    def build_agents_section() -> str:
        """Build [AGENTS] section - Other agents' capabilities and status."""
        section = """[AGENTS]
Available Agents and Capabilities:

Executor Agent:
  - Responsibility: Execute system commands, control UI, browser automation
  - Capabilities: Keyboard/mouse control, window management, application launch
  - Memory Type: Recent context only (from Query Maker 2)
  - Current Status: (Query for current status)

Query Makers:
  - Query Maker 1: Compiles full Scout context for LLM reasoning
  - Query Maker 2: Compiles agent-specific context (their type only, focused)
  - Both route through Scout context system

Other Agents:
  - (Additional agents can be registered here as they're added)
"""
        return section

    @staticmethod
    def build_important_memory_section(limit: int = 50) -> str:
        """Build [IMPORTANT MEMORY] section - Explicitly saved important items."""
        important = MemoryReader.load_important_memory()
        items = important.get("items", [])[:limit]

        if not items:
            return "[IMPORTANT MEMORY]\n(No important memories)\n"

        section = "[IMPORTANT MEMORY]\nUser-Explicit Important Memories:\n\n"

        for item in items:
            category = item.get("category", "general")
            content = item.get("content", "")
            section += f"[{category}] {content}\n"
            if item.get("tags"):
                section += f"  Tags: {', '.join(item.get('tags', []))}\n"
            section += "\n"

        return section

    @staticmethod
    def build_recent_14_days_section(limit: int = 100) -> str:
        """Build [RECENT 14 DAYS] section - Recent decision/action history."""
        entries = MemoryReader.load_14_day_memory()[:limit]

        if not entries:
            return "[RECENT 14 DAYS]\n(No recent history)\n"

        section = "[RECENT 14 DAYS]\nRecent Actions and Decisions:\n\n"

        # Group by date
        by_date = {}
        for entry in entries:
            timestamp = entry.get("timestamp", "")
            date = timestamp.split("T")[0] if timestamp else "unknown"

            if date not in by_date:
                by_date[date] = []
            by_date[date].append(entry)

        # Format by date
        for date in sorted(by_date.keys(), reverse=True):
            section += f"Date: {date}\n"

            for entry in by_date[date]:
                log_type = entry.get("type", "")
                message = entry.get("message", "")
                category = entry.get("category", "")

                if category:
                    section += f"  [{log_type}] ({category}) {message}\n"
                else:
                    section += f"  [{log_type}] {message}\n"

                if entry.get("data"):
                    section += f"    Data: {json.dumps(entry.get('data'))}\n"

            section += "\n"

        return section

    @staticmethod
    def build_relevant_archive_section(query: str, limit: int = 20) -> str:
        """Build [RELEVANT ARCHIVE] section - Contextual archive items.

        Args:
            query: Current query/task (used to find relevant archive items)
            limit: Maximum archive items to include
        """
        section = "[RELEVANT ARCHIVE]\nRelevant Archived Context:\n\n"

        # Search for relevant items
        conversations = MemoryReader.search_archives(query, "conversations")[:limit//4]
        failures = MemoryReader.search_archives(query, "failures")[:limit//4]
        projects = MemoryReader.search_archives(query, "projects")[:limit//4]
        sessions = MemoryReader.search_archives(query, "sessions")[:limit//4]

        if conversations:
            section += "Related Conversations:\n"
            for item in conversations:
                section += f"  - {item.get('title', 'Untitled')}\n"
            section += "\n"

        if failures:
            section += "Related Failures/Errors:\n"
            for item in failures:
                section += f"  - {item.get('title', 'Untitled')}: {item.get('description', '')}\n"
            section += "\n"

        if projects:
            section += "Related Projects:\n"
            for item in projects:
                section += f"  - {item.get('name', 'Untitled')}: {item.get('status', 'Unknown')}\n"
            section += "\n"

        if sessions:
            section += "Related Sessions:\n"
            for item in sessions:
                section += f"  - {item.get('name', 'Untitled')}\n"
            section += "\n"

        if not any([conversations, failures, projects, sessions]):
            section += "(No relevant archive items found)\n"

        return section

    @staticmethod
    def build_tools_section() -> str:
        """Build [TOOLS] section - Available tools and capabilities."""
        registry = MemoryReader.load_tool_registry()
        tools = registry.get("tools", {})

        section = "[TOOLS]\nAvailable Tools and Capabilities:\n\n"

        if not tools:
            section += "(No tools registered)\n"
            return section

        for tool_name, tool_info in tools.items():
            description = tool_info.get("description", "No description")
            section += f"- {tool_name}: {description}\n"

            if tool_info.get("capabilities"):
                for capability in tool_info.get("capabilities", []):
                    section += f"  • {capability}\n"

            section += "\n"

        return section

    @staticmethod
    def build_current_query_section(query: str) -> str:
        """Build [CURRENT QUERY] section - The immediate task/query."""
        section = f"""[CURRENT QUERY]
Immediate Task/Query:
{query}

Query Analysis:
  - Type: (To be analyzed)
  - Priority: (To be determined)
  - Related Agents: (To be identified)
  - Required Tools: (To be identified)
"""
        return section

    # ========================================================================
    # MAIN COMPILATION
    # ========================================================================

    @staticmethod
    def compile_scout_context(
        query: str,
        include_sections: Optional[List[str]] = None,
        custom_token_allocation: Optional[Dict[str, float]] = None
    ) -> str:
        """Compile complete Scout context for decision-making.

        Args:
            query: Current query/task
            include_sections: Specific sections to include (None = all)
            custom_token_allocation: Custom token allocation percentages

        Returns:
            Formatted prompt text with all context
        """
        if custom_token_allocation:
            ContextCompiler.TOKEN_ALLOCATION = custom_token_allocation

        # Default to all sections
        if include_sections is None:
            include_sections = [
                "identity",
                "time_date",
                "state",
                "agents",
                "important_memory",
                "recent_14_days",
                "relevant_archive",
                "tools",
                "current_query",
            ]

        sections = []

        if "identity" in include_sections:
            sections.append(ContextCompiler.build_identity_section())

        if "time_date" in include_sections:
            sections.append(ContextCompiler.build_time_date_section())

        if "state" in include_sections:
            sections.append(ContextCompiler.build_state_section())

        if "agents" in include_sections:
            sections.append(ContextCompiler.build_agents_section())

        if "important_memory" in include_sections:
            sections.append(ContextCompiler.build_important_memory_section())

        if "recent_14_days" in include_sections:
            sections.append(ContextCompiler.build_recent_14_days_section())

        if "relevant_archive" in include_sections:
            sections.append(ContextCompiler.build_relevant_archive_section(query))

        if "tools" in include_sections:
            sections.append(ContextCompiler.build_tools_section())

        if "current_query" in include_sections:
            sections.append(ContextCompiler.build_current_query_section(query))

        # Join all sections
        full_context = "\n".join(sections)

        # Log context compilation
        entry = MemoryWriter.create_daily_log_entry(
            log_type="context_compilation",
            message=f"Compiled Scout context for query: {query[:50]}...",
            category="system",
            severity="info",
            data={"sections": include_sections}
        )
        MemoryWriter.log_to_daily(entry)

        return full_context

    @staticmethod
    def compile_agent_context(
        agent_name: str,
        query: str,
        memory_type: str = "recent"
    ) -> str:
        """Compile context for a specific agent (agent's own memory type only).

        Args:
            agent_name: Name of the agent
            query: Current query/task
            memory_type: Agent's memory type (recent, archive, learned, context)

        Returns:
            Formatted prompt text with agent-specific context
        """
        context = f"""[AGENT: {agent_name}]
Assigned Query: {query}

Agent Memory ({memory_type}):
"""
        agent_memory = MemoryReader.load_agent_memory(agent_name, memory_type)

        if agent_memory:
            context += json.dumps(agent_memory, indent=2)
        else:
            context += "(No previous memory for this agent type)"

        context += "\n\nTools Available:\n"
        registry = MemoryReader.load_tool_registry()
        tools = registry.get("tools", {})

        for tool_name, tool_info in tools.items():
            context += f"- {tool_name}: {tool_info.get('description', '')}\n"

        # Log context compilation for agent
        entry = MemoryWriter.create_daily_log_entry(
            log_type="agent_context",
            message=f"Compiled context for agent '{agent_name}' with query: {query[:50]}...",
            category=f"agent_{agent_name}",
            severity="info"
        )
        MemoryWriter.log_to_daily(entry)

        return context

    @staticmethod
    def get_context_summary() -> Dict[str, Any]:
        """Get summary of current context availability."""
        return {
            "identity": bool(MemoryReader.load_identity()),
            "preferences": bool(MemoryReader.load_user_preferences()),
            "current_state": bool(MemoryReader.load_current_state().get("state")),
            "important_memories": len(MemoryReader.load_important_memory().get("items", [])),
            "14day_entries": len(MemoryReader.load_14_day_memory()),
            "archive_items": (
                len(MemoryReader.list_archive("conversations")) +
                len(MemoryReader.list_archive("failures")) +
                len(MemoryReader.list_archive("projects"))
            ),
            "tools_available": len(MemoryReader.load_tool_registry().get("tools", {})),
            "upcoming_deadlines": len(MemoryReader.get_upcoming_deadlines()),
        }


if __name__ == "__main__":
    print("Context Compiler Test")
    print("=" * 70)

    summary = ContextCompiler.get_context_summary()
    print("\nContext Availability:")
    for key, value in summary.items():
        print(f"  {key}: {value}")

    print("\nCompiling full Scout context for sample query...")
    print("=" * 70)

    sample_query = "Help me prioritize my tasks for today"
    context = ContextCompiler.compile_scout_context(sample_query)

    # Print first 2000 chars
    print(context[:2000])
    print(f"\n... (Total context length: {len(context)} chars)")
