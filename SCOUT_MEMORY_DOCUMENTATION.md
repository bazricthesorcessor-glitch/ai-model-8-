"""
SCOUT COGNITIVE MEMORY SYSTEM - COMPLETE DOCUMENTATION

Scout is the master coordinator agent. It needs persistent, intelligent memory:

┌─────────────────────────────────────────────────────────────────────┐
│  SCOUT MEMORY ARCHITECTURE - 3 TIER SYSTEM                          │
└─────────────────────────────────────────────────────────────────────┘

TIER 1: ACTIVE MEMORY (14-day exact rollng window)
  └─ What Scout receives MOST of the time
  └─ Exact conversations, decisions, failures
  └─ NOT summarized - pure continuity
  └─ Files: memory/active/daily_logs/YYYY-MM-DD.jsonl

TIER 2: ARCHIVE MEMORY (Infinite searchable history)
  └─ Full lifetime storage
  └─ Searched deeply when needed
  └─ Multi-chunk retrieval for huge logs
  └─ Files: memory/archive/conversations/, failures/, projects/

TIER 3: STATE MEMORY (Current reality)
  └─ Browser tabs, workspaces, agents, tasks
  └─ Most important - agents need THIS not history
  └─ Files: memory/state/*.json

PLUS:
  - Identity/personality (permanent, never summarized)
  - Agent-specific memory (each agent's scoped knowledge)
  - Event log (all Scout decisions, delegations, completions)
  - Semantic graph (relationships and patterns)

=============================================================================
IMPLEMENTATIONS
=============================================================================

1. memory/scout_memory.py - ScoutMemoryManager
   ├─ Add/retrieve active memory
   ├─ Manage 2-week rolling window
   ├─ Archive old logs
   ├─ Update current state
   ├─ Search archive
   └─ Get memory statistics

2. memory/scout_history_logger.py - ScoutHistoryLogger
   ├─ Text log (human readable)
   ├─ Event log (structured JSON)
   ├─ Log decisions
   ├─ Log delegations
   ├─ Log completions
   ├─ Log errors
   └─ Log state changes

=============================================================================
USAGE EXAMPLES
=============================================================================

SETUP:

    from memory.scout_memory import ScoutMemoryManager, StateSnapshot
    from memory.scout_history_logger import ScoutHistoryLogger
    import time

    mem = ScoutMemoryManager()
    hist = ScoutHistoryLogger()

---

ADD TO ACTIVE MEMORY:

    # Scout heard user request
    mem.add_to_active_memory(
        speaker="user",
        message="Take a screenshot and send to ChatGPT",
        importance=8,
        tags=["task", "chatgpt", "screenshot"],
    )

    # Scout made decision
    mem.add_to_active_memory(
        speaker="scout",
        message="Delegating to Executor: screenshot workflow",
        importance=7,
        tags=["decision", "delegation"],
        agent="scout",
    )

---

UPDATE STATE:

    state = StateSnapshot(
        timestamp=time.time(),
        ui_state={
            "active_window": "Firefox",
            "workspace": 2,
            "fullscreen": False,
        },
        browser_state={
            "open_tabs": [
                {"title": "YouTube", "url": "youtube.com"},
                {"title": "ChatGPT", "url": "chat.openai.com"},
            ],
            "active_tab": "ChatGPT",
        },
        workspace_state={
            "workspace_1": "coding",
            "workspace_2": "media",
            "workspace_3": "browser",
            "active_workspace": 2,
        },
        agent_state={
            "executor_busy": True,
            "scout_busy": False,
            "coder_busy": False,
        },
        system_state={
            "brightness": 0.8,
            "volume": 0.5,
            "battery": 85,
            "network": "connected",
        },
        task_state={
            "active_tasks": ["task_001_screenshot"],
            "completed_tasks": [],
            "failed_tasks": [],
        },
    )

    mem.update_state(state)

---

RETRIEVE ACTIVE MEMORY:

    # Get last 2 weeks
    recent = mem.get_active_memory(days=14)

    for entry in recent:
        print(f"[{entry.speaker}] {entry.message}")
        print(f"  Priority: {entry.priority_score}")
        print(f"  Tags: {entry.tags}")

---

LOG SCOUT EVENTS:

    # Decision
    hist.log_decision(
        description="Decided to use Executor for brightness control",
        task_id="task_001",
        tags=["brightness", "decision"],
    )

    # Delegation
    hist.log_delegation(
        agent="executor",
        description="Delegated brightness increase",
        task_id="task_001",
    )

    # Completion
    hist.log_completion(
        description="Brightness increase completed successfully",
        result={"success": True, "level": 0.9},
        task_id="task_001",
    )

    # Error
    hist.log_error(
        description="Screenshot attempt failed",
        error="No screenshot tool available",
        task_id="task_002",
    )

    # State change
    hist.log_state_change(
        description="Workspace switched",
        old_state={"workspace": 1},
        new_state={"workspace": 2},
    )

---

GET SESSION SUMMARY:

    summary = hist.get_session_summary()
    print(f"Session: {summary['session_id']}")
    print(f"Total events: {summary['total_events']}")
    print(f"Decisions: {summary['decisions']}")
    print(f"Delegations: {summary['delegations']}")
    print(f"Completions: {summary['completions']}")
    print(f"Errors: {summary['errors']}")

---

SEARCH ARCHIVE:

    failures = mem.search_archive(
        query="screenshot",
        category="failures",
        limit=10,
    )

    for failure in failures:
        print(f"[{failure['timestamp']}] {failure['content']['problem']}")

---

GET MEMORY STATISTICS:

    stats = mem.get_memory_stats()
    print(f"Active entries: {stats['active_entries']}")
    print(f"Archive entries: {stats['archive_entries']}")
    print(f"Retention: {stats['retention_days']} days")

=============================================================================
PRIORITY SCORING
=============================================================================

Each memory gets a score (0-50):

    importance (0-10)        - How important is this?
    recency (0-10)           - How recent?
    task_relevance (0-10)    - Related to current task?
    emotional_weight (0-10)  - User upset? Excited?
    user_pinned (0-10)       - User explicitly saved?

    total_score = importance + recency + task_relevance + emotional_weight + user_pinned

Examples:

    - "I forgot my password" → HIGH (emotional, important)
    - "exam on May 20" → CRITICAL (user_pinned + importance)
    - "random joke" → LOW (no relevance)
    - Repeated failure → HIGH (prevents future mistakes)
    - "hi how are you" → LOW (small talk)

=============================================================================
AUTO-CLEANUP
=============================================================================

Scout automatically removes stale memory:

    # Logs older than 14 days move to archive
    mem._cleanup_old_logs()

    # Browser tabs that closed get removed from state
    # Finished tasks lose priority
    # Exam dates < today move to archive

This prevents bloat while keeping important stuff.

=============================================================================
2-WEEK EXACT MEMORY
=============================================================================

This is unique and important.

WRONG WAY:
    "Scout, you did X on May 5. You're an AI, you don't remember details."
    (This breaks continuity. Scout feels dumb and forgets context.)

RIGHT WAY:
    Scout has EXACT logs from last 14 days.
    "May 5 you worked on project_xyz. You solved bug #123 but created bug #456."
    (Scout feels continuous, remembers exact context, can reason from memory.)

The difference:
    - Without exact memory: AI feels stateless, repeats mistakes
    - With exact memory: AI feels persistent, learns from history

That's what makes Scout feel ALIVE.

=============================================================================
STATE MEMORY IS CRITICAL
=============================================================================

This is where most AI agents fail.

They confuse:
    "I remember you said X" (conversation memory)
WITH:
    "You currently have YouTube open in workspace 2" (state memory)

Scout NEEDS both, but state is more important for execution.

Example:

    Scout is given: "open YouTube"

    WITH STATE MEMORY:
        → Checks browser_state
        → Finds YouTube already open in workspace 2
        → Switches to workspace 2
        → DONE (1 second, efficient)

    WITHOUT STATE MEMORY:
        → Opens YouTube in new tab
        → Now has 2 YouTube tabs
        → User confused ("I already had it open!")
        → Executor stuck

State memory prevents wasteful duplicate actions.

=============================================================================
CONTEXT COMPILATION (1M TOKEN WINDOW)
=============================================================================

Scout's context should look like:

    [SYSTEM_RULES] (50k)
        ├─ Scout duties
        ├─ Safety rules
        └─ How to think

    [PERSONALITY] (50k)
        ├─ Speaking style
        ├─ Preferences
        └─ Quirks

    [CURRENT_STATE] (150k)
        ├─ Open tabs
        ├─ Active workspace
        ├─ Agent status
        └─ Tasks

    [RECENT_EXACT_MEMORY] (300k)
        ├─ Last 14 days exact logs
        ├─ No summaries
        └─ Full continuity

    [RELEVANT_ARCHIVE] (200k)
        ├─ Search results from deeper history
        ├─ Failure patterns
        └─ Project context

    [TASK_CONTEXT] (100k)
        ├─ Current task
        ├─ Subtasks
        └─ Blockers

    [AGENT_MEMORY] (100k)
        ├─ Executor knowledge
        ├─ Coder knowledge
        └─ Thinker knowledge

    [SEMANTIC_GRAPH] (50k)
        ├─ Relationships
        ├─ Patterns
        └─ Timeline

This compilation order is important.

Scout sees CURRENT STATE first (most relevant to immediate action).
Then EXACT RECENT memory (continuity).
Then ARCHIVE (deeper context if needed).

=============================================================================
EVENT-BASED LOGGING
=============================================================================

Scout's decisions should be logged:

    log_decision("Chose to delegate to Executor")
    log_delegation("Executor", "brightness control")
    log_completion("brightness increased", result)
    log_error("screenshot failed", error_msg)
    log_state_change("workspace changed", old, new)

This creates a decision audit trail.

Later, if something goes wrong, Scout can:
    "Why did we try that? Because on May 10 we failed at X.
    So on May 12 I delegated to Executor instead.
    Good decision."

That's learning.

=============================================================================
INTEGRATION WITH AGENTS
=============================================================================

Each agent gets scoped memory:

EXECUTOR MEMORY:
    ├─ Shell commands
    ├─ Keyboard shortcuts
    ├─ Browser workflows
    ├─ System tools
    └─ Last 10 command results

CODER MEMORY:
    ├─ Code structure
    ├─ APIs
    ├─ Bug history
    ├─ Architecture
    └─ Dependencies

THINKER MEMORY:
    ├─ Reasoning patterns
    ├─ Failed strategies
    ├─ Optimization lessons
    └─ Planning approaches

Scout coordinates but doesn't force them to share raw memory.
Each agent remembers its own domain.

=============================================================================
FILE STRUCTURE
=============================================================================

memory/
├── active/
│   ├── daily_logs/
│   │   ├── 2026-05-10.jsonl
│   │   ├── 2026-05-11.jsonl
│   │   └── 2026-05-12.jsonl
│   ├── rolling_context/
│   │   ├── current_context.md
│   │   └── current_priorities.md
│   └── active_index.json
│
├── archive/
│   ├── conversations/
│   ├── failures/
│   ├── projects/
│   ├── scout_events/
│   └── scout_logs/
│
├── state/
│   ├── current_state.json
│   ├── browser_state.json
│   └── workspace_state.json
│
├── identity/
│   ├── personality.json
│   ├── duties.json
│   ├── abilities.json
│   └── important_memory.json
│
├── agents/
│   ├── executor/
│   ├── coder/
│   ├── thinker/
│   └── scout/
│
├── semantic/
│   ├── entities.json
│   ├── relations.json
│   └── timeline.json
│
└── indexes/
    ├── keywords.db
    ├── semantic.db
    └── dates.db

=============================================================================
KEY PRINCIPLES
=============================================================================

1. SEPARATION OF CONCERNS
   - Don't mix conversation + state
   - Each gets its own memory

2. EXACT OVER SUMMARY
   - 2-week exact logs beat 90-day summaries
   - Summaries lose nuance
   - Exact memory builds continuity

3. STATE PRIORITY
   - What exists NOW matters most
   - "YouTube is open" > "we talked about YouTube"
   - Prevents wasteful duplicate actions

4. PRIORITY SCORING
   - Not all memories equal
   - Important/recent/relevant memories get loaded
   - Low-priority stuff archived but searchable

5. ASYMMETRIC RETRIEVAL
   - Small task: recent memory only
   - Big failure: deep archive search
   - Adapt memory depth to task size

6. AUTO-CLEANUP
   - Logs > 14 days move to archive
   - Closed tabs removed from state
   - Completed tasks lose priority
   - Prevents bloat

7. NEVER HALLUCINATE
   - Verify state against reality
   - "Tab says it's open but it's not" → remove from state
   - Reality > memory

=============================================================================
TESTING
=============================================================================

python memory/scout_memory.py
    → Tests memory manager, state updates, statistics

python memory/scout_history_logger.py
    → Tests event logging, session summaries

=============================================================================
NEXT STEPS
=============================================================================

After this foundation:

1. Build context compiler (query_maker.py)
   - Assembles 1M token window
   - Decides what enters context
   - Most important file

2. Build memory retrieval engine
   - Keyword search (ripgrep, sqlite FTS5)
   - Semantic search (embeddings later)
   - Multi-chunk deep search

3. Build auto-cleaner
   - Archive old logs
   - Remove stale state
   - Compress memory

4. Wire into Scout
   - Load memory on startup
   - Update state after actions
   - Save decisions to history
   - Log completions

5. Test with real agents
   - See if Scout feels continuous
   - Verify state tracking works
   - Check memory doesn't bloat

=============================================================================
"""

# Quick usage example:

if __name__ == "__main__":
    from memory.scout_memory import ScoutMemoryManager, StateSnapshot
    from memory.scout_history_logger import ScoutHistoryLogger
    import time

    print(__doc__)

    print("\n" + "=" * 70)
    print("QUICK START EXAMPLE")
    print("=" * 70 + "\n")

    mem = ScoutMemoryManager()
    hist = ScoutHistoryLogger()

    # Example: User asks Scout to take screenshot
    print("[1] User request logged...")
    mem.add_to_active_memory(
        speaker="user",
        message="Take screenshot and send to ChatGPT",
        importance=8,
        tags=["task"],
    )

    print("[2] Scout decision logged...")
    hist.log_decision(
        description="Delegating screenshot to Executor",
        task_id="task_001",
    )

    print("[3] Delegation logged...")
    hist.log_delegation(
        agent="executor",
        description="Execute screenshot workflow",
        task_id="task_001",
    )

    print("[4] Retrieving recent memory...")
    recent = mem.get_active_memory(days=1)
    print(f"   Found {len(recent)} entries from today")

    print("[5] Getting session summary...")
    summary = hist.get_session_summary()
    print(f"   Session: {summary['session_id']}")
    print(f"   Decisions: {summary['decisions']}")
    print(f"   Delegations: {summary['delegations']}")

    print("\n✓ Scout memory system working!\n")
