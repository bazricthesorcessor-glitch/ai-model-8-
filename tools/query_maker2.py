"""
Query Maker v2 - Adaptive Context Depth for Thinking Models

INTELLIGENCE = Knowing when to think deep vs. when to stay focused.

Three severity levels:

1. SMALL_IMPROVEMENT (happy user)
   → Minimal context: last message + current state + relevant tools
   → Keep latency low, attention clean, execution sharp

2. MAJOR_ISSUE (unhappy user / repeated failure)
   → Deep retrieval: entire session + previous failures + error patterns
   → Enable self-corrective cognition through failure analysis

3. ARCHITECTURAL_REDESIGN
   → Full historical retrieval + pattern analysis + design implications
   → Major rethinking with deep context

Tool Knowledge ≠ Tool Use:
- Models KNOW what tools exist (python, websearch, calculator, shell, etc.)
- Scout still CONTROLS permission + orchestration

Failure Pattern Memory:
Instead of raw chat, store:
  FAILURE_PATTERN:
    issue: [what went wrong]
    cause: [root cause]
    failed_attempts: [what was tried]
    successful_fix: [what worked]
    error_class: [categorization]
"""

from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from datetime import datetime


class SeverityLevel(Enum):
    """Problem severity classification."""
    SMALL_IMPROVEMENT = "small_improvement"      # User happy, minor enhancement
    MAJOR_ISSUE = "major_issue"                  # Repeated failure, major fix needed
    ARCHITECTURAL = "architectural"              # Fundamental redesign required
    UNKNOWN = "unknown"                          # Cannot determine


class ToolCapability:
    """Tool availability definition."""

    AVAILABLE_TOOLS = {
        "python": {
            "enabled": True,
            "description": "Execute Python code directly",
            "capabilities": ["execute_code", "import_modules", "run_snippets"],
        },
        "websearch": {
            "enabled": True,
            "description": "Search web, fetch content, parse HTML",
            "capabilities": ["google_search", "site_specific", "scraping"],
        },
        "calculator": {
            "enabled": True,
            "description": "Math operations, symbolic computation",
            "capabilities": ["arithmetic", "symbolic_math", "numerical_analysis"],
        },
        "filesystem": {
            "enabled": True,
            "description": "Read/write files, directory operations",
            "capabilities": ["read_files", "write_files", "directory_ops"],
        },
        "shell": {
            "enabled": True,
            "description": "Execute shell commands",
            "capabilities": ["bash", "fish", "process_control"],
        },
        "browser": {
            "enabled": True,
            "description": "Browser automation, DOM interaction",
            "capabilities": ["navigate", "click", "form_filling", "javascript"],
        },
        "database": {
            "enabled": True,
            "description": "Query databases, data retrieval",
            "capabilities": ["sql_queries", "data_analysis"],
        },
        "api": {
            "enabled": True,
            "description": "HTTP requests, API integration",
            "capabilities": ["get_requests", "post_requests", "auth"],
        },
    }

    @staticmethod
    def get_available() -> Dict[str, Dict[str, Any]]:
        """Get all available tools."""
        return {
            tool: spec
            for tool, spec in ToolCapability.AVAILABLE_TOOLS.items()
            if spec.get("enabled", True)
        }

    @staticmethod
    def format_for_model() -> str:
        """Format tool list for model context."""
        tools = ToolCapability.get_available()
        lines = []

        for tool, spec in tools.items():
            lines.append(f"- {tool.upper()}: {spec['description']}")
            if spec.get('capabilities'):
                for cap in spec['capabilities']:
                    lines.append(f"    • {cap}")

        return "\n".join(lines)


class SeverityClassifier:
    """Determine problem severity from context."""

    @staticmethod
    def classify(
        user_message: str,
        scout_message: Optional[Dict[str, Any]] = None,
        session_history: Optional[List[Dict[str, Any]]] = None,
    ) -> Tuple[SeverityLevel, float]:
        """
        Classify severity level.

        Args:
            user_message: Current user message
            scout_message: Scout's analysis/context
            session_history: Previous messages in session

        Returns:
            (severity_level, confidence: 0.0-1.0)
        """
        user_lower = user_message.lower()
        confidence = 0.5

        # ARCHITECTURAL signals (highest severity)
        if any(phrase in user_lower for phrase in [
            "redesign", "rethink", "completely rewrite", "start over",
            "major change", "fundamental problem", "architecture",
        ]):
            return SeverityLevel.ARCHITECTURAL, 0.95

        # MAJOR_ISSUE signals
        if any(phrase in user_lower for phrase in [
            "broken", "not working", "error", "failed", "doesn't work",
            "still failing", "again", "still broken", "repeated",
            "why is this", "what's wrong", "fix this",
        ]):
            confidence = 0.90

            # Check if repeated failure (deeper signal)
            if session_history and len(session_history) > 3:
                recent_failures = sum(
                    1 for msg in session_history[-5:]
                    if any(word in msg.get("content", "").lower()
                           for word in ["error", "failed", "broken"])
                )
                if recent_failures >= 2:
                    return SeverityLevel.MAJOR_ISSUE, 0.98

            return SeverityLevel.MAJOR_ISSUE, confidence

        # SMALL_IMPROVEMENT signals
        if any(phrase in user_lower for phrase in [
            "can you", "could you", "would you", "improve", "add",
            "enhance", "better", "optimize", "refactor", "clean up",
            "make it", "make sure", "check if",
        ]):
            return SeverityLevel.SMALL_IMPROVEMENT, 0.85

        # Default based on session length
        if session_history and len(session_history) > 10:
            return SeverityLevel.SMALL_IMPROVEMENT, 0.60

        return SeverityLevel.UNKNOWN, 0.40

    @staticmethod
    def explain_classification(severity: SeverityLevel, confidence: float) -> str:
        """Human-readable explanation of classification."""
        if severity == SeverityLevel.ARCHITECTURAL:
            return f"Architectural redesign required (confidence: {confidence:.0%})"
        elif severity == SeverityLevel.MAJOR_ISSUE:
            return f"Major issue detected - deep analysis needed (confidence: {confidence:.0%})"
        elif severity == SeverityLevel.SMALL_IMPROVEMENT:
            return f"Small improvement - focused context sufficient (confidence: {confidence:.0%})"
        else:
            return f"Severity unclear - using default context (confidence: {confidence:.0%})"


class MemoryRetriever:
    """Retrieve memory at appropriate context depth."""

    @staticmethod
    def retrieve_minimal(
        session_history: List[Dict[str, Any]],
        current_state: Dict[str, Any],
    ) -> Dict[str, Any]:
        """SMALL_IMPROVEMENT: Minimal focused context."""
        last_message = session_history[-1] if session_history else {}

        return {
            "context_depth": "minimal",
            "items_retrieved": 1,
            "memory": {
                "last_message": last_message,
                "current_state": current_state,
                "available_tools": ToolCapability.get_available(),
            }
        }

    @staticmethod
    def retrieve_deep(
        session_history: List[Dict[str, Any]],
        current_state: Dict[str, Any],
    ) -> Dict[str, Any]:
        """MAJOR_ISSUE: Deep retrospective retrieval."""
        failures = MemoryRetriever._extract_failures(session_history)
        error_patterns = MemoryRetriever._classify_error_patterns(failures)

        return {
            "context_depth": "deep",
            "items_retrieved": len(session_history),
            "memory": {
                "full_session": session_history,
                "failure_patterns": failures,
                "error_patterns": error_patterns,
                "attempted_solutions": MemoryRetriever._extract_attempted_solutions(session_history),
                "current_state": current_state,
                "available_tools": ToolCapability.get_available(),
            }
        }

    @staticmethod
    def retrieve_full(
        session_history: List[Dict[str, Any]],
        model_history: Optional[List[Dict[str, Any]]] = None,
        current_state: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """ARCHITECTURAL: Full historical retrieval."""
        failures = MemoryRetriever._extract_failures(session_history)
        error_patterns = MemoryRetriever._classify_error_patterns(failures)

        return {
            "context_depth": "full",
            "items_retrieved": len(session_history) + (len(model_history) if model_history else 0),
            "memory": {
                "current_session": session_history,
                "previous_sessions": model_history or [],
                "failure_analysis": {
                    "failures": failures,
                    "patterns": error_patterns,
                    "recurring_issues": MemoryRetriever._find_recurring_issues(failures),
                },
                "current_state": current_state,
                "available_tools": ToolCapability.get_available(),
            }
        }

    @staticmethod
    def _extract_failures(history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract failure records from history."""
        failures = []
        for i, msg in enumerate(history):
            if any(word in msg.get("content", "").lower()
                   for word in ["error", "failed", "broken", "issue"]):
                failures.append({
                    "index": i,
                    "message": msg,
                    "timestamp": msg.get("timestamp"),
                })
        return failures

    @staticmethod
    def _classify_error_patterns(failures: List[Dict[str, Any]]) -> List[str]:
        """Classify error types."""
        patterns = []
        for failure in failures:
            content = failure.get("message", {}).get("content", "").lower()

            if "timeout" in content:
                patterns.append("TIMEOUT_PATTERN")
            elif "recursion" in content or "loop" in content:
                patterns.append("LOOP_PATTERN")
            elif "syntax" in content:
                patterns.append("SYNTAX_PATTERN")
            elif "memory" in content or "out of" in content:
                patterns.append("RESOURCE_PATTERN")
            elif "not found" in content or "404" in content:
                patterns.append("NOT_FOUND_PATTERN")
            elif "connection" in content:
                patterns.append("CONNECTION_PATTERN")

        return list(set(patterns))

    @staticmethod
    def _extract_attempted_solutions(history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract what solutions were attempted."""
        solutions = []
        for msg in history:
            if any(verb in msg.get("content", "").lower()
                   for verb in ["try", "attempt", "implement", "change"]):
                solutions.append({
                    "message": msg,
                    "success": "success" in msg.get("content", "").lower()
                                or "working" in msg.get("content", "").lower(),
                })
        return solutions

    @staticmethod
    def _find_recurring_issues(failures: List[Dict[str, Any]]) -> List[str]:
        """Find issues that appear multiple times."""
        issue_types = []
        for failure in failures:
            content = failure.get("message", {}).get("content", "")
            if "error" in content.lower():
                issue_types.append("error")
            if "timeout" in content.lower():
                issue_types.append("timeout")

        return [
            issue for issue in issue_types
            if issue_types.count(issue) > 1
        ]


class ThinkingModelPacketBuilder:
    """Build optimized prompts for thinking models."""

    @staticmethod
    def build_packet(
        user_query: str,
        scout_message: Optional[Dict[str, Any]] = None,
        session_history: Optional[List[Dict[str, Any]]] = None,
        current_state: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Build comprehensive packet for thinking model."""
        session_history = session_history or []
        current_state = current_state or {}

        # Step 1: Classify severity
        severity, confidence = SeverityClassifier.classify(
            user_query,
            scout_message,
            session_history,
        )

        # Step 2: Retrieve memory at appropriate depth
        if severity == SeverityLevel.ARCHITECTURAL:
            memory = MemoryRetriever.retrieve_full(session_history, current_state=current_state)
        elif severity == SeverityLevel.MAJOR_ISSUE:
            memory = MemoryRetriever.retrieve_deep(session_history, current_state)
        else:
            memory = MemoryRetriever.retrieve_minimal(session_history, current_state)

        # Step 3: Build packet
        packet = {
            "packet_id": f"thinking_{datetime.now().isoformat()[:8]}",
            "model_type": "thinking",
            "severity": {
                "level": severity.value,
                "confidence": confidence,
                "explanation": SeverityClassifier.explain_classification(severity, confidence),
            },

            "USER_QUERY": {
                "raw": user_query,
                "inferred_intent": ThinkingModelPacketBuilder._infer_intent(user_query),
            },

            "SCOUT_MESSAGE": scout_message or {},

            "AVAILABLE_TOOLS": ToolCapability.get_available(),
            "TOOLS_DESCRIPTION": ToolCapability.format_for_model(),

            "MEMORY": memory,

            "CURRENT_STATE": current_state,

            "THINKING_INSTRUCTIONS": ThinkingModelPacketBuilder._get_thinking_instructions(severity),

            "VERIFICATION_CHECKLIST": ThinkingModelPacketBuilder._build_verification_checklist(severity),
        }

        return packet

    @staticmethod
    def _infer_intent(query: str) -> str:
        """Infer user's intent from query."""
        query_lower = query.lower()

        if any(word in query_lower for word in ["improve", "enhance", "optimize"]):
            return "improvement"
        elif any(word in query_lower for word in ["fix", "broken", "error", "issue"]):
            return "bug_fix"
        elif any(word in query_lower for word in ["explain", "understand", "how"]):
            return "explanation"
        elif any(word in query_lower for word in ["implement", "create", "add"]):
            return "implementation"
        elif any(word in query_lower for word in ["refactor", "redesign", "rewrite"]):
            return "refactoring"
        else:
            return "unclear"

    @staticmethod
    def _get_thinking_instructions(severity: SeverityLevel) -> str:
        """Get instructions tailored to severity."""
        if severity == SeverityLevel.ARCHITECTURAL:
            return """You have full context. Think deeply:
1. Analyze the COMPLETE failure history
2. Identify recurring pattern/root cause
3. Propose FUNDAMENTAL redesign
4. Verify against past failures
5. Ensure solution doesn't repeat mistakes"""

        elif severity == SeverityLevel.MAJOR_ISSUE:
            return """Major issue detected. Approach:
1. Review FAILURE PATTERNS in memory
2. Compare against attempted solutions
3. Identify what was tried and failed
4. Propose novel solution
5. Verify it addresses root cause"""

        else:  # SMALL_IMPROVEMENT
            return """Small improvement requested. Stay focused:
1. Reference ONLY relevant last context
2. Make MINIMAL changes
3. Verify against current state
4. Quick, surgical fix
5. Don't over-engineer"""

    @staticmethod
    def _build_verification_checklist(severity: SeverityLevel) -> List[str]:
        """Build verification checklist based on severity."""
        if severity == SeverityLevel.ARCHITECTURAL:
            return [
                "Does solution address ROOT CAUSE?",
                "Does it avoid ALL previous failure patterns?",
                "Is architectural design sound?",
                "Will it scale?",
                "Have I documented the reasoning?",
            ]
        elif severity == SeverityLevel.MAJOR_ISSUE:
            return [
                "Does solution fix the actual problem?",
                "Why did previous attempts fail?",
                "Does this solution avoid those pitfalls?",
                "Is the fix stable?",
                "Can I verify it works?",
            ]
        else:
            return [
                "Is the change minimal and focused?",
                "Does it work with current state?",
                "Are there side effects?",
                "Can user verify quickly?",
            ]


class QueryMaker2:
    """Main interface for thinking model context."""

    @staticmethod
    def build_thinking_packet(
        user_query: str,
        scout_message: Optional[Dict[str, Any]] = None,
        session_history: Optional[List[Dict[str, Any]]] = None,
        current_state: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Build optimized packet for thinking model."""
        return ThinkingModelPacketBuilder.build_packet(
            user_query,
            scout_message,
            session_history,
            current_state,
        )

    @staticmethod
    def format_for_model(packet: Dict[str, Any]) -> str:
        """Format packet as readable prompt for model."""
        lines = []

        lines.append("=" * 70)
        lines.append(f"THINKING MODEL CONTEXT PACKET")
        lines.append(f"Severity: {packet['severity']['level'].upper()}")
        lines.append(f"Confidence: {packet['severity']['confidence']:.0%}")
        lines.append("=" * 70)

        lines.append("\n[USER QUERY]")
        lines.append(f"  {packet['USER_QUERY']['raw']}")
        lines.append(f"  Intent: {packet['USER_QUERY']['inferred_intent']}")

        lines.append("\n[SEVERITY ANALYSIS]")
        lines.append(f"  {packet['severity']['explanation']}")

        lines.append("\n[MEMORY DEPTH]")
        memory = packet.get("MEMORY", {})
        lines.append(f"  Context depth: {memory.get('context_depth', 'unknown')}")
        lines.append(f"  Items retrieved: {memory.get('items_retrieved', 0)}")

        lines.append("\n[AVAILABLE TOOLS]")
        tools = packet.get("AVAILABLE_TOOLS", {})
        for tool, spec in tools.items():
            lines.append(f"  ✓ {tool}")

        lines.append("\n[THINKING INSTRUCTIONS]")
        for line in packet.get("THINKING_INSTRUCTIONS", "").split("\n"):
            if line.strip():
                lines.append(f"  {line}")

        lines.append("\n[VERIFICATION CHECKLIST]")
        for item in packet.get("VERIFICATION_CHECKLIST", []):
            lines.append(f"  □ {item}")

        lines.append("\n" + "=" * 70)

        return "\n".join(lines)


if __name__ == "__main__":
    print("\n🧠 TEST: Thinking Model Query Maker v2\n")

    # Test Case 1: Small improvement
    print("[TEST 1] Small improvement request")
    packet1 = QueryMaker2.build_thinking_packet(
        user_query="Can you optimize this function for better performance?",
        session_history=[
            {"content": "Here's my function", "timestamp": "now"},
            {"content": "This looks good", "timestamp": "now"},
        ],
    )
    print(QueryMaker2.format_for_model(packet1))

    # Test Case 2: Major issue
    print("\n[TEST 2] Major issue / repeated failure")
    packet2 = QueryMaker2.build_thinking_packet(
        user_query="This still doesn't work! Why is it broken again?",
        session_history=[
            {"content": "Error: timeout occurred", "timestamp": "t1"},
            {"content": "Tried fix with retry logic", "timestamp": "t2"},
            {"content": "Still getting errors", "timestamp": "t3"},
            {"content": "Failed again", "timestamp": "t4"},
        ],
    )
    print(QueryMaker2.format_for_model(packet2))

    # Test Case 3: Architectural
    print("\n[TEST 3] Architectural redesign")
    packet3 = QueryMaker2.build_thinking_packet(
        user_query="I need to completely redesign the architecture",
        session_history=[
            {"content": "Initial implementation", "timestamp": "t1"},
            {"content": "Error: design flaw", "timestamp": "t2"},
            {"content": "Major architectural issue", "timestamp": "t3"},
        ],
    )
    print(QueryMaker2.format_for_model(packet3))
