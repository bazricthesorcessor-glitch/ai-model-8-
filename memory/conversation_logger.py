"""
Conversation Logger - Store Scout↔User conversation history.

Appends every message to a persistent log file with:
- Timestamps
- Severity level
- Context/metadata
- Clean readability

File: ~/.avril/scout_conversation.log
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path


class ConversationLogger:
    """Log and retrieve Scout↔User conversations."""

    # Default log file location
    DEFAULT_LOG_DIR = os.path.expanduser("~/.avril")
    DEFAULT_LOG_FILE = os.path.join(DEFAULT_LOG_DIR, "scout_conversation.log")

    def __init__(self, log_file: Optional[str] = None):
        """
        Initialize conversation logger.

        Args:
            log_file: Path to log file (default: ~/.avril/scout_conversation.log)
        """
        self.log_file = log_file or self.DEFAULT_LOG_FILE

        # Ensure directory exists
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

        # Create log file if doesn't exist
        if not os.path.exists(self.log_file):
            Path(self.log_file).touch()

    def log_user_message(
        self,
        message: str,
        intent: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log a user message.

        Args:
            message: User's message/query
            intent: Inferred intent (improvement, bug_fix, etc.)
            context: Additional context
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "USER",
            "message": message,
            "intent": intent,
            "context": context or {},
        }
        self._append_entry(entry)

    def log_scout_message(
        self,
        message: str,
        severity: Optional[str] = None,
        analysis: Optional[Dict[str, Any]] = None,
        action: Optional[str] = None,
    ) -> None:
        """
        Log a Scout message.

        Args:
            message: Scout's response/analysis
            severity: Problem severity (small_improvement, major_issue, architectural)
            analysis: Scout's analysis data
            action: What Scout is routing to (executor, thinking_model, etc.)
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "SCOUT",
            "message": message,
            "severity": severity,
            "analysis": analysis or {},
            "action": action,
        }
        self._append_entry(entry)

    def log_context(
        self,
        severity: str,
        tools_available: List[str],
        memory_depth: str,
        instructions: str,
    ) -> None:
        """
        Log context/state information.

        Args:
            severity: Severity level
            tools_available: Available tools
            memory_depth: Memory retrieval depth
            instructions: Thinking instructions
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "CONTEXT",
            "severity": severity,
            "tools_available": tools_available,
            "memory_depth": memory_depth,
            "instructions": instructions,
        }
        self._append_entry(entry)

    def log_session_start(self, session_id: Optional[str] = None) -> None:
        """Log session start."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "SESSION_START",
            "session_id": session_id or datetime.now().strftime("%Y%m%d_%H%M%S"),
        }
        self._append_entry(entry)

    def log_session_end(self, summary: Optional[Dict[str, Any]] = None) -> None:
        """Log session end."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "SESSION_END",
            "summary": summary or {},
        }
        self._append_entry(entry)

    def _append_entry(self, entry: Dict[str, Any]) -> None:
        """
        Append a single entry to log file.

        Args:
            entry: Entry dictionary
        """
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                # Write as JSON for structured parsing
                f.write(json.dumps(entry) + "\n")
                f.flush()
        except IOError as e:
            print(f"Error writing to log file: {e}")

    def get_session_history(
        self,
        limit: Optional[int] = None,
        message_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history.

        Args:
            limit: Limit number of entries (None = all)
            message_type: Filter by type (USER, SCOUT, CONTEXT, SESSION_START, SESSION_END)

        Returns:
            List of log entries
        """
        entries = []

        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            entry = json.loads(line)

                            # Filter by type if specified
                            if message_type and entry.get("type") != message_type:
                                continue

                            entries.append(entry)
                        except json.JSONDecodeError:
                            continue
        except FileNotFoundError:
            return []

        # Apply limit (last N entries)
        if limit:
            entries = entries[-limit:]

        return entries

    def get_user_messages(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get only user messages."""
        return self.get_session_history(limit=limit, message_type="USER")

    def get_scout_messages(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get only Scout messages."""
        return self.get_session_history(limit=limit, message_type="SCOUT")

    def get_formatted_history(
        self,
        limit: Optional[int] = None,
        include_metadata: bool = True,
    ) -> str:
        """
        Get formatted conversation history for reading.

        Args:
            limit: Limit number of entries
            include_metadata: Include timestamps and metadata

        Returns:
            Formatted string
        """
        entries = self.get_session_history(limit=limit)
        lines = []

        lines.append("=" * 80)
        lines.append("SCOUT ↔ USER CONVERSATION HISTORY")
        lines.append("=" * 80)

        current_session = None

        for entry in entries:
            entry_type = entry.get("type")
            timestamp = entry.get("timestamp", "")

            # Session markers
            if entry_type == "SESSION_START":
                current_session = entry.get("session_id")
                lines.append("\n" + "─" * 80)
                lines.append(f"📍 SESSION START: {current_session}")
                lines.append("─" * 80 + "\n")
                continue

            elif entry_type == "SESSION_END":
                lines.append("\n" + "─" * 80)
                lines.append(f"🏁 SESSION END")
                if entry.get("summary"):
                    for key, val in entry["summary"].items():
                        lines.append(f"  {key}: {val}")
                lines.append("─" * 80 + "\n")
                continue

            # Context entries
            elif entry_type == "CONTEXT":
                lines.append("\n[CONTEXT UPDATE]")
                if include_metadata:
                    lines.append(f"  Timestamp: {timestamp}")
                lines.append(f"  Severity: {entry.get('severity')}")
                lines.append(f"  Memory Depth: {entry.get('memory_depth')}")
                lines.append(f"  Tools: {', '.join(entry.get('tools_available', []))}")
                lines.append("")
                continue

            # Messages
            if entry_type == "USER":
                lines.append("\n👤 USER:")
                if include_metadata:
                    lines.append(f"   [{timestamp}]")
                    if entry.get("intent"):
                        lines.append(f"   Intent: {entry['intent']}")
                message = entry.get("message", "")
                for msg_line in message.split("\n"):
                    lines.append(f"   {msg_line}")

            elif entry_type == "SCOUT":
                lines.append("\n🤖 SCOUT:")
                if include_metadata:
                    lines.append(f"   [{timestamp}]")
                    if entry.get("severity"):
                        lines.append(f"   Severity: {entry['severity']}")
                    if entry.get("action"):
                        lines.append(f"   Routing to: {entry['action']}")
                message = entry.get("message", "")
                for msg_line in message.split("\n"):
                    lines.append(f"   {msg_line}")

        lines.append("\n" + "=" * 80)

        return "\n".join(lines)

    def clear_history(self) -> None:
        """Clear conversation history (DESTRUCTIVE)."""
        try:
            Path(self.log_file).write_text("")
            print(f"✓ Conversation history cleared: {self.log_file}")
        except IOError as e:
            print(f"Error clearing history: {e}")

    def export_json(self, output_file: str) -> None:
        """
        Export conversation history as JSON.

        Args:
            output_file: Path to export to
        """
        entries = self.get_session_history()

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(entries, f, indent=2)
            print(f"✓ Exported {len(entries)} entries to {output_file}")
        except IOError as e:
            print(f"Error exporting: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get conversation statistics."""
        entries = self.get_session_history()

        user_messages = [e for e in entries if e.get("type") == "USER"]
        scout_messages = [e for e in entries if e.get("type") == "SCOUT"]

        severities = {}
        for entry in scout_messages:
            severity = entry.get("severity")
            if severity:
                severities[severity] = severities.get(severity, 0) + 1

        return {
            "total_entries": len(entries),
            "user_messages": len(user_messages),
            "scout_messages": len(scout_messages),
            "severity_breakdown": severities,
            "log_file": self.log_file,
        }

    def print_statistics(self) -> None:
        """Print conversation statistics."""
        stats = self.get_statistics()

        print("\n" + "=" * 60)
        print("CONVERSATION STATISTICS")
        print("=" * 60)
        print(f"Total entries: {stats['total_entries']}")
        print(f"User messages: {stats['user_messages']}")
        print(f"Scout messages: {stats['scout_messages']}")

        if stats['severity_breakdown']:
            print("\nSeverity breakdown:")
            for severity, count in stats['severity_breakdown'].items():
                print(f"  {severity}: {count}")

        print(f"\nLog file: {stats['log_file']}")
        print("=" * 60 + "\n")


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Initialize logger
    logger = ConversationLogger()

    print("📝 CONVERSATION LOGGER DEMO\n")

    # Simulate session
    logger.log_session_start()

    # User message
    logger.log_user_message(
        message="Can you optimize my function for better performance?",
        intent="improvement",
    )

    # Scout response
    logger.log_scout_message(
        message="I'll analyze your function and suggest optimizations.",
        severity="small_improvement",
        action="executor",
    )

    # Context update
    logger.log_context(
        severity="small_improvement",
        tools_available=["python", "websearch"],
        memory_depth="minimal",
        instructions="Quick, surgical fix. Don't over-engineer.",
    )

    # Another exchange
    logger.log_user_message(
        message="This is still broken. Same error as before!",
        intent="bug_fix",
    )

    logger.log_scout_message(
        message="Detected repeated failure. Doing deep analysis of previous attempts.",
        severity="major_issue",
        action="thinking_model",
    )

    # End session
    logger.log_session_end(summary={"fixes_applied": 2, "issues_resolved": 1})

    # Print formatted history
    print(logger.get_formatted_history())

    # Print statistics
    logger.print_statistics()

    # Show JSON entries (for integration)
    print("\n📊 RAW LOG ENTRIES (JSON):")
    entries = logger.get_session_history()
    for entry in entries[-3:]:  # Last 3 entries
        print(json.dumps(entry, indent=2))
