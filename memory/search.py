"""
Advanced search system for Scout's memory.
Provides keyword search, filtering, and semantic relationship queries.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
import re

from . import paths
from .reader import MemoryReader
from .schemas import SearchResult


class KeywordIndex:
    """Maintains keyword index for fast searching."""

    def __init__(self):
        """Initialize keyword index."""
        self.index: Dict[str, List[str]] = {}  # keyword → [item_ids]
        self.load_or_create()

    def load_or_create(self) -> None:
        """Load index from file or create new."""
        if paths.KEYWORD_INDEX_FILE.exists():
            with open(paths.KEYWORD_INDEX_FILE, 'r') as f:
                self.index = json.load(f)
        else:
            self.index = {}
            self.save()

    def save(self) -> None:
        """Save index to file."""
        paths.KEYWORD_INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(paths.KEYWORD_INDEX_FILE, 'w') as f:
            json.dump(self.index, f, indent=2)

    def add_entry(self, item_id: str, text: str) -> None:
        """Add entry to index.

        Args:
            item_id: Unique identifier for the item
            text: Text to index
        """
        # Extract keywords
        keywords = self._extract_keywords(text)

        for keyword in keywords:
            if keyword not in self.index:
                self.index[keyword] = []
            if item_id not in self.index[keyword]:
                self.index[keyword].append(item_id)

        self.save()

    def search(self, query: str, limit: int = 50) -> List[str]:
        """Search for items matching query.

        Args:
            query: Search query (space-separated terms)
            limit: Maximum results

        Returns:
            List of matching item IDs, ranked by relevance
        """
        # Parse query
        terms = self._extract_keywords(query)

        if not terms:
            return []

        # Find items matching all terms (AND search)
        matching_ids = None

        for term in terms:
            if term in self.index:
                term_items = set(self.index[term])
                if matching_ids is None:
                    matching_ids = term_items
                else:
                    matching_ids &= term_items
            else:
                matching_ids = set()
                break

        if matching_ids is None:
            matching_ids = set()

        # Rank by number of matching terms
        ranked = sorted(
            matching_ids,
            key=lambda item_id: sum(1 for term in terms if item_id in self.index.get(term, [])),
            reverse=True
        )

        return ranked[:limit]

    @staticmethod
    def _extract_keywords(text: str) -> List[str]:
        """Extract keywords from text.

        Args:
            text: Text to extract from

        Returns:
            List of lowercase keywords (min 3 chars)
        """
        # Remove special characters, convert to lowercase
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', '', text)

        # Split and filter
        words = text.split()
        keywords = [w for w in words if len(w) >= 3]

        return keywords


class MemorySearch:
    """Advanced search across all memory types."""

    def __init__(self):
        """Initialize search system."""
        self.keyword_index = KeywordIndex()

    # ========================================================================
    # SIMPLE SEARCHES
    # ========================================================================

    def search_daily_logs(
        self,
        query: str,
        days: int = 14,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search daily logs with keyword matching.

        Args:
            query: Search query
            days: Number of days to search
            limit: Maximum results

        Returns:
            List of matching log entries
        """
        # Get logs from past N days
        all_entries = MemoryReader.load_14_day_memory()[:days * 1000]

        # Filter by query (case-insensitive substring match)
        query_lower = query.lower()
        results = []

        for entry in all_entries:
            message = entry.get('message', '').lower()
            category = entry.get('category', '').lower()
            log_type = entry.get('type', '').lower()

            # Match in any field
            if (query_lower in message or
                query_lower in category or
                query_lower in log_type):
                results.append(entry)

            if len(results) >= limit:
                break

        return results

    def search_archives(
        self,
        query: str,
        archive_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search archive items.

        Args:
            query: Search query
            archive_type: Specific archive or None for all
            limit: Maximum results

        Returns:
            List of matching archive items
        """
        query_lower = query.lower()
        results = []

        # Determine which archives to search
        types = [archive_type] if archive_type else [
            "conversations", "failures", "projects", "sessions"
        ]

        for atype in types:
            items = MemoryReader.load_all_archive(atype)

            for item in items:
                # Convert to searchable string
                searchable = json.dumps(item).lower()

                if query_lower in searchable:
                    results.append(item)

                if len(results) >= limit:
                    return results

        return results

    def search_important_memory(
        self,
        query: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search important memories.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching important memories
        """
        important = MemoryReader.load_important_memory()
        query_lower = query.lower()
        results = []

        for item in important.get('items', []):
            content = item.get('content', '').lower()
            category = item.get('category', '').lower()

            if query_lower in content or query_lower in category:
                results.append(item)

            if len(results) >= limit:
                break

        return results

    # ========================================================================
    # ADVANCED SEARCHES
    # ========================================================================

    def search_by_category(
        self,
        category: str,
        days: int = 14,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Find all log entries in a category.

        Args:
            category: Category name
            days: Number of days to search
            limit: Maximum results

        Returns:
            List of entries in category
        """
        return MemoryReader.filter_daily_log(
            category=category
        )

    def search_by_severity(
        self,
        severity: str,
        days: int = 14,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Find all log entries with specific severity.

        Args:
            severity: Severity level (info, warning, error, critical)
            days: Number of days to search
            limit: Maximum results

        Returns:
            List of entries with that severity
        """
        return MemoryReader.filter_daily_log(
            severity=severity
        )

    def search_errors_and_failures(self, days: int = 14, limit: int = 100) -> Dict[str, Any]:
        """Comprehensive search for all errors and failures.

        Args:
            days: Number of days to search
            limit: Maximum results per category

        Returns:
            Dictionary with errors from logs and failures from archive
        """
        # Get critical/error logs
        logs = MemoryReader.filter_daily_log(severity="error")
        critical_logs = MemoryReader.filter_daily_log(severity="critical")

        # Get failures from archive
        failures = MemoryReader.load_all_archive("failures")[:limit]

        return {
            "error_logs": logs[:limit],
            "critical_logs": critical_logs[:limit],
            "failures": failures,
            "total_errors": len(logs) + len(critical_logs),
            "total_failures": len(failures)
        }

    def search_by_time_range(
        self,
        start_date: str,
        end_date: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Search logs within a time range.

        Args:
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            limit: Maximum results

        Returns:
            List of matching entries
        """
        results = []
        query_lower = ""  # Will check all

        try:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
        except ValueError:
            return []

        # Search through days in range
        current = start
        while current <= end:
            entries = MemoryReader.load_daily_log(current)

            for entry in entries:
                results.append(entry)

                if len(results) >= limit:
                    return results

            current += timedelta(days=1)

        return results

    def search_by_agent(
        self,
        agent_name: str,
        days: int = 14,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Find all entries related to a specific agent.

        Args:
            agent_name: Agent name
            days: Number of days to search
            limit: Maximum results

        Returns:
            List of agent-related entries
        """
        results = MemoryReader.search_daily_logs(
            query=agent_name,
            days=days
        )

        # Also search execution history
        history = MemoryReader.load_execution_history(limit=limit)
        history = [h for h in history if h.get('agent') == agent_name]

        return results[:limit] + history[:limit//2]

    # ========================================================================
    # CONTEXTUAL SEARCHES
    # ========================================================================

    def find_related_context(self, query: str) -> Dict[str, List[Any]]:
        """Find all related context for a query.

        Args:
            query: Query/topic

        Returns:
            Dictionary with all related information
        """
        return {
            "recent_mentions": self.search_daily_logs(query, days=14, limit=10),
            "important_memories": self.search_important_memory(query, limit=5),
            "failures": self.search_archives(query, "failures", limit=5),
            "projects": self.search_archives(query, "projects", limit=5),
            "conversations": self.search_archives(query, "conversations", limit=5),
        }

    def find_context_for_query(self, user_query: str) -> Dict[str, Any]:
        """Find comprehensive context to answer a user query.

        Args:
            user_query: User's question/task

        Returns:
            Dictionary with relevant context from all sources
        """
        context = {
            "query": user_query,
            "search_time": datetime.now().isoformat(),
            "recent_history": self.search_daily_logs(user_query, days=7, limit=15),
            "important_related": self.search_important_memory(user_query, limit=10),
            "relevant_failures": self.search_archives(user_query, "failures", limit=5),
            "relevant_projects": self.search_archives(user_query, "projects", limit=5),
            "similar_conversations": self.search_archives(user_query, "conversations", limit=3),
        }

        return context

    # ========================================================================
    # PATTERN SEARCHES
    # ========================================================================

    def find_recent_decisions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Find recent decision entries."""
        return MemoryReader.filter_daily_log(log_type="decision")[:limit]

    def find_recent_actions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Find recent action entries."""
        return MemoryReader.filter_daily_log(log_type="action")[:limit]

    def find_recent_errors(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Find recent error entries."""
        return MemoryReader.filter_daily_log(log_type="error")[:limit]

    def find_pattern_frequency(
        self,
        pattern: str,
        days: int = 14
    ) -> Dict[str, int]:
        """Find frequency of a pattern in recent history.

        Args:
            pattern: Pattern to search for
            days: Number of days to analyze

        Returns:
            Dictionary with frequency by type/category
        """
        results = self.search_daily_logs(pattern, days=days, limit=1000)

        frequency = {
            "by_type": Counter(),
            "by_category": Counter(),
            "by_severity": Counter(),
            "total": len(results)
        }

        for entry in results:
            frequency["by_type"][entry.get("type")] += 1
            if entry.get("category"):
                frequency["by_category"][entry.get("category")] += 1
            frequency["by_severity"][entry.get("severity")] += 1

        # Convert Counter to dict for JSON serialization
        return {
            "by_type": dict(frequency["by_type"]),
            "by_category": dict(frequency["by_category"]),
            "by_severity": dict(frequency["by_severity"]),
            "total": frequency["total"]
        }

    # ========================================================================
    # TREND ANALYSIS
    # ========================================================================

    def analyze_trends(self, days: int = 14) -> Dict[str, Any]:
        """Analyze trends in recent memory.

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with trend analysis
        """
        entries = MemoryReader.load_14_day_memory()

        # Count by type
        type_counts = Counter(e.get("type") for e in entries)

        # Count by severity
        severity_counts = Counter(e.get("severity") for e in entries)

        # Count errors and errors resolved
        errors = [e for e in entries if e.get("type") == "error"]
        resolved_errors = [e for e in entries if e.get("type") == "error" and e.get("data", {}).get("resolved")]

        # Most common categories
        categories = Counter(e.get("category") for e in entries if e.get("category"))

        return {
            "period_days": days,
            "total_entries": len(entries),
            "by_type": dict(type_counts),
            "by_severity": dict(severity_counts),
            "by_category": dict(categories.most_common(10)),
            "error_stats": {
                "total": len(errors),
                "resolved": len(resolved_errors),
                "unresolved": len(errors) - len(resolved_errors)
            },
            "analyzed_at": datetime.now().isoformat()
        }

    # ========================================================================
    # SEMANTIC SEARCH (ADVANCED)
    # ========================================================================

    def semantic_search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search using semantic relationships.

        Currently uses keyword matching as base for semantic search.
        Future: Implement embedding-based semantic search.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of semantically related items
        """
        # For now, use keyword search as semantic base
        # Future: Use embeddings/semantic similarity

        # Start with keyword search
        keyword_results = self.search_daily_logs(query, limit=limit*2)

        # Find related items from archives
        archive_results = self.search_archives(query, limit=limit)

        # Combine and deduplicate
        combined = keyword_results[:limit//2] + archive_results[:limit//2]

        return combined

    def find_semantic_graph_connections(self, item_id: str) -> Dict[str, Any]:
        """Find semantic relationships for an item.

        Args:
            item_id: Item identifier

        Returns:
            Dictionary with connected items
        """
        # Load semantic graph
        if paths.SEMANTIC_GRAPH_FILE.exists():
            with open(paths.SEMANTIC_GRAPH_FILE, 'r') as f:
                graph = json.load(f)
        else:
            graph = {"relations": []}

        # Find relations involving this item
        connections = {
            "incoming": [],  # Items pointing to this one
            "outgoing": []   # This item pointing to others
        }

        for relation in graph.get("relations", []):
            if relation.get("source_id") == item_id:
                connections["outgoing"].append(relation)
            elif relation.get("target_id") == item_id:
                connections["incoming"].append(relation)

        return connections


def get_search_stats() -> Dict[str, Any]:
    """Get statistics about search indexes."""
    keyword_index = KeywordIndex()

    return {
        "indexed_keywords": len(keyword_index.index),
        "total_keyword_references": sum(len(v) for v in keyword_index.index.values()),
        "index_file": str(paths.KEYWORD_INDEX_FILE),
        "index_size_kb": paths.KEYWORD_INDEX_FILE.stat().st_size / 1024 if paths.KEYWORD_INDEX_FILE.exists() else 0
    }


if __name__ == "__main__":
    print("Memory Search System Test")
    print("=" * 70)

    search = MemorySearch()

    # Test basic search
    results = search.search_daily_logs("memory", limit=5)
    print(f"\n✓ Daily log search: {len(results)} results")

    # Test category search
    recent_decisions = search.find_recent_decisions(limit=5)
    print(f"✓ Recent decisions: {len(recent_decisions)} found")

    # Test trend analysis
    trends = search.analyze_trends(days=14)
    print(f"\n✓ Trend Analysis:")
    print(f"  Total entries: {trends['total_entries']}")
    print(f"  Entry types: {len(trends['by_type'])}")

    # Test contextual search
    context = search.find_related_context("memory")
    print(f"\n✓ Contextual Search for 'memory':")
    for key, values in context.items():
        print(f"  {key}: {len(values)} items")

    # Print search stats
    stats = get_search_stats()
    print(f"\n✓ Search Index Stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
