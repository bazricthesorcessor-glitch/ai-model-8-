"""
Memory module - Scout's persistent memory system with runtime state tracking.

Complete Architecture:
1. Runtime Memory (core.py): Current task, action, status (in-memory, fast)

2. Persistent Memory Foundation:
   - paths.py: File structure and storage locations
   - writer.py: Save operations (daily logs, archives, state snapshots)
   - reader.py: Load operations (14-day memory, archives, searches)
   - compiler.py: Context compilation for Scout decision-making (CRITICAL)

3. Data Management:
   - schemas.py: Type-safe data models for all memory types
   - search.py: Advanced search with keyword indexing and trend analysis
   - cleaner.py: Auto-cleanup, expiry management, and integrity validation

Scout Memory System:
- Scout gets: ALL memory types (14-day, archives, important, state, tools, agents)
- Agents get: Only their specific memory type (from Query Maker 2)
- Context compilation is 1M token window with intelligent allocation
- Full-text search across all memory types
- Automatic cleanup and maintenance

Quick Start:
  from memory import initialize_memory_system, MemoryWriter, MemoryReader, ContextCompiler
  initialize_memory_system()
  MemoryWriter.log_to_daily({"type": "action", "message": "test"})
  context = ContextCompiler.compile_scout_context("what next?")
"""

from .core import Memory, MEMORY
from .memory import log_action, get_log_file, get_action_log

# Expose Scout persistent memory system
from . import paths
from .writer import MemoryWriter, initialize_memory_system
from .reader import MemoryReader, get_memory_status
from .compiler import ContextCompiler
from .search import MemorySearch, KeywordIndex, get_search_stats
from .cleaner import MemoryCleaner, schedule_automatic_cleanup
from . import schemas

__all__ = [
    # Runtime memory
    "Memory",
    "MEMORY",
    "log_action",
    "get_log_file",
    "get_action_log",
    # Paths and initialization
    "paths",
    "initialize_memory_system",
    # Core operations
    "MemoryWriter",
    "MemoryReader",
    "ContextCompiler",
    "get_memory_status",
    # Advanced operations
    "MemorySearch",
    "KeywordIndex",
    "get_search_stats",
    "MemoryCleaner",
    "schedule_automatic_cleanup",
    # Data models
    "schemas",
]

