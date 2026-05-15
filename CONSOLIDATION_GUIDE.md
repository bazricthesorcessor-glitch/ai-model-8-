"""
UNIFIED MEMORY & QUERY SYSTEM - CONSOLIDATION GUIDE

PREVIOUS STATE (FRAGMENTED):
============================

MEMORY (3 systems):
  1. memory/memory.py
     - Simple action logging
     - Monthly log files
     - No structure

  2. memory/scout_memory.py
     - 3-tier (active/archive/state)
     - Scout-specific
     - Good design but isolated

  3. executor/caelestia_integration.py
     - Executor context
     - No persistent memory
     - Incomplete

QUERY MAKERS (2 systems):
  1. tools/query_maker1.py
     - State-aware context for Executor
     - Gathers browser/workspace/shell state
     - No memory integration

  2. tools/query_maker2.py
     - Adaptive context depth
     - Severity-based retrieval
     - No actual memory backend

PROBLEMS:
  ✗ No unified memory pool
  ✗ Agents can't share knowledge
  ✗ Duplicate code for similar tasks
  ✗ State tracking scattered
  ✗ Query makers don't access memory
  ✗ Executor integration incomplete

---

NEW STATE (UNIFIED):
====================

SINGLE MEMORY SYSTEM:
  memory/unified_memory.py
    ├── Tier 1: Active Memory (14-day exact logs)
    ├── Tier 2: Archive Memory (searchable history)
    └── Tier 3: State Memory (current reality)

  Serves ALL agents:
    - Scout (coordinator)
    - Executor (system actions)
    - Coder (code operations)
    - Thinker (strategic thinking)

SINGLE QUERY MAKER:
  tools/unified_query_maker.py
    - Context compilation for any agent
    - Severity-based token allocation
    - Integrated memory access
    - Tool/constraint management

BENEFITS:
  ✓ Unified memory pool
  ✓ Agents share knowledge
  ✓ No code duplication
  ✓ Centralized state
  ✓ Query makers use real memory
  ✓ Easy to extend

---

MIGRATION PLAN:
================

STEP 1: Replace memory.py
  OLD: memory/memory.py (simple logging)
  NEW: memory/unified_memory.py
  
  Change:
    from memory import log_action
    TO:
    from memory.unified_memory import UnifiedMemory
    mem = UnifiedMemory()
    mem.log_action(agent, action, result)

STEP 2: Consolidate scout_memory.py
  OLD: memory/scout_memory.py (Scout-specific)
  NEW: memory/unified_memory.py (universal)
  
  Same API:
    mem.remember(speaker, message, agent_role)
    mem.recall(days, agent_role)
    mem.archive(category, data)

STEP 3: Replace both query_makers
  OLD: tools/query_maker1.py
       tools/query_maker2.py
  NEW: tools/unified_query_maker.py
  
  Change:
    context = make_query(
        memory=mem,
        agent="executor",
        task="Take screenshot",
        severity=SeverityLevel.SMALL_FIX,
    )

STEP 4: Update Executor integration
  OLD: executor/caelestia_integration.py (basic)
  NEW: Uses unified_query_maker + unified_memory
  
  Executor now gets:
    - Current state (browser, workspace, tasks)
    - Recent exact memory (14 days)
    - Relevant archive (failures, projects)
    - Capabilities + constraints
    - All in one context dict

---

FILE MAPPING:
==============

KEEP (Updated):
  memory/unified_memory.py        ← consolidates: memory.py + scout_memory.py
  tools/unified_query_maker.py    ← consolidates: query_maker1.py + query_maker2.py
  memory/scout_history_logger.py  ← already good, just uses unified_memory now
  executor/caelestia_integration.py ← uses unified_query_maker

DEPRECATE (Remove after migration):
  memory/memory.py                ← replaced by unified_memory
  memory/scout_memory.py          ← merged into unified_memory
  tools/query_maker1.py           ← replaced by unified_query_maker
  tools/query_maker2.py           ← replaced by unified_query_maker

---

CODE EXAMPLES - BEFORE & AFTER:
================================

SCENARIO 1: Executor executes brightness increase

BEFORE:
-------
from tools.query_maker1 import StateGatherer
from executor import InputController

state = StateGatherer.get_browser_state()
# ... manually build context ...
InputController.brightness_up()

AFTER:
------
from memory.unified_memory import UnifiedMemory
from tools.unified_query_maker import make_query, SeverityLevel
from ui.caelestia_controller import CaelestiaController

mem = UnifiedMemory()
context = make_query(mem, "executor", "increase brightness")
controller = CaelestiaController()
controller.increase_brightness()
mem.log_action("executor", "increase brightness", {"success": True})

---

SCENARIO 2: Scout delegates to Executor after failure

BEFORE:
-------
# No way to track failures or retrieve them
# Scout can't learn from past mistakes

AFTER:
------
from memory.unified_memory import UnifiedMemory
from tools.unified_query_maker import SeverityLevel, make_query

mem = UnifiedMemory()

# Log the failure
mem.log_error("executor", "Screenshot failed", "gnome-screenshot")

# Scout can now search for similar failures
failures = mem.search("screenshot", category="failures")

# On retry, use MAJOR_ISSUE severity for deep context
context = make_query(
    mem,
    agent="executor",
    task="Take screenshot",
    severity=SeverityLevel.MAJOR_ISSUE,  # Deep context
)
# Executor has full failure history + patterns

---

SCENARIO 3: Scout checks system state

BEFORE:
-------
# State scattered across multiple systems
state_file1 = load_json("~/.elzyra/ui_state.json")
state_file2 = load_json("~/.elzyra/browser_state.json")
state_file3 = load_json("~/.elzyra/workspace_state.json")
# No unified view

AFTER:
------
from memory.unified_memory import UnifiedMemory

mem = UnifiedMemory()
state = mem.get_state()
print(state.browser)      # Current browser state
print(state.workspace)    # Current workspace
print(state.agents)       # Agent statuses
print(state.tasks)        # Active tasks
# Single unified source of truth

---

IMPLEMENTATION CHECKLIST:
==========================

[ ] Create memory/unified_memory.py (DONE)
[ ] Create tools/unified_query_maker.py (DONE)
[ ] Update scout_history_logger.py to use unified_memory (already done)
[ ] Update executor/caelestia_integration.py to use unified_query_maker
[ ] Update all agents to use: mem.remember(), mem.recall(), mem.archive()
[ ] Update all agents to use: make_query() for context compilation
[ ] Test memory sharing between agents
[ ] Test state synchronization
[ ] Test query maker context allocation
[ ] Remove old memory.py
[ ] Remove old scout_memory.py (merge features into agent code)
[ ] Remove old query_maker1.py
[ ] Remove old query_maker2.py

---

USAGE FOR EACH AGENT:
======================

SCOUT:
  from memory.unified_memory import UnifiedMemory
  from tools.unified_query_maker import make_query
  
  mem = UnifiedMemory()
  
  # Coordinate other agents
  context = make_query(mem, "executor", task, severity)
  # Execute through Executor
  mem.remember("scout", "decision", "scout", importance=8)

EXECUTOR:
  from memory.unified_memory import UnifiedMemory
  from tools.unified_query_maker import make_query
  
  mem = UnifiedMemory()
  
  # Get context from Scout
  context = make_query(mem, "executor", task, severity)
  # Use current state to avoid duplicate actions
  state = mem.get_state()
  # Log execution
  mem.log_action("executor", action, result)

CODER:
  from memory.unified_memory import UnifiedMemory
  
  mem = UnifiedMemory()
  
  # Remember code patterns
  mem.remember("coder", "pattern", "coder", tags=["pattern"])
  # Search for similar code issues
  failures = mem.search("bug type", category="failures")
  # Log completion
  mem.log_action("coder", "fixed bug", result)

THINKER:
  from memory.unified_memory import UnifiedMemory
  
  mem = UnifiedMemory()
  
  # Learn from failures
  failures = mem.search("repeated_issue")
  # Remember patterns
  mem.remember("thinker", "pattern", "thinker", tags=["learned"])
  # Archive insights
  mem.archive("patterns", {"insight": "...", "applicability": "..."})

---

TESTING:
=========

Unit tests for unified_memory.py:
  python memory/unified_memory.py
  
Unit tests for unified_query_maker.py:
  python tools/unified_query_maker.py

Integration tests:
  [ ] Scout-Executor communication
  [ ] State synchronization
  [ ] Memory sharing
  [ ] Query context compilation
  [ ] Failure tracking and learning

---

BENEFITS OF UNIFIED SYSTEM:
=============================

1. KNOWLEDGE SHARING
   Before: Scout, Executor, Coder each have separate memory
   After: All agents draw from shared memory pool

2. FAILURE LEARNING
   Before: Failed screenshot? Start fresh, might fail again
   After: Search failures, learn from patterns, succeed faster

3. STATE AWARENESS
   Before: Executor blindly opens YouTube in new tab (duplicate!)
   After: Executor checks state, reuses existing tab

4. ADAPTIVE LEARNING
   Before: Same context for all problems
   After: Small fix = focused context, major issue = deep history

5. NO CODE DUPLICATION
   Before: StateGatherer in query_maker1, similar code elsewhere
   After: Single StateMemory class, used everywhere

6. EASY EXTENSION
   Before: Add new agent? Copy-paste memory code
   After: New agent just uses UnifiedMemory API

7. DEBUGGING
   Before: Memory scattered across files
   After: Single memory system, easy to inspect/debug

---

KEY PRINCIPLE:
===============

Before: Each agent's memory = isolated silo

[Scout Memory]  [Executor Memory]  [Coder Memory]  [Thinker Memory]
    ✗ Can't     ✗ Can't share     ✗ Can't        ✗ Can't
   share with    with others       learn from     coordinate
   others                          others         globally


After: Single shared memory pool

         ┌─────────────────────────────────────────┐
         │    UNIFIED MEMORY SYSTEM                │
         │                                         │
         │  ├─ Active Memory (14 days exact)      │
         │  ├─ Archive Memory (infinite search)   │
         │  └─ State Memory (current reality)     │
         │                                         │
         └─────────────────────────────────────────┘
                      ↑      ↑      ↑      ↑
                 Scout  Executor  Coder  Thinker
                 (all draw from same source)

All agents learn together, avoid repeated mistakes, share knowledge.

=============================================================================
"""

print(__doc__)
