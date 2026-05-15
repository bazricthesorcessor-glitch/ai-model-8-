# ELZYRA SYSTEM CONTEXT SEED - 2026-05-12

**Generated:** 2026-05-12 14:30:00  
**System:** Modular AI Assistant Foundation  
**Status:** Core architecture complete, testing ready

---

## SYSTEM ARCHITECTURE

### 3-Tier Cognitive Architecture

**Tier 1: EXECUTOR** (Llama 3.1 8B)
- Silent operational cortex
- UI/Terminal/Browser operations
- Fast, deterministic, task-oriented
- Controlled entirely by Scout

**Tier 2: SCOUT** (Intelligence layer)
- Understands user intent
- Manages memory & continuity
- Routes cognition between tiers
- Owns identity & planning

**Tier 3: CORE** (Long-term knowledge)
- Persistent learning
- Architectural patterns
- Failure analysis

---

## COMPLETED COMPONENTS

### 1. Query Maker v1 - Real-Time Operational Context Engine
**File:** `tools/query_maker1.py`

**Purpose:** State-aware task packet builder for Executor

**Features:**
- Gathers shell state (venv, cwd, terminal app)
- Browser state (tabs, URLs, active tab)
- Workspace state (current workspace, occupied workspaces)
- Keybinds mapping
- Environment variables
- Operational rules
- Structured TODO list generation

**Key Innovation:** Detects existing resources to prevent duplication
- "YouTube tab exists → reuse it, don't open new"
- "Brave on workspace 2 → switch to it, don't relaunch"

**Structured Context Regions:**
```
[INTENT]           - User's goal
[WORLD_STATE]      - Desktop environment
[BROWSER_STATE]    - Existing tabs
[WORKSPACE_STATE]  - Workspace layout
[KEYBINDS]         - Available hotkeys
[VARIABLES]        - Config & paths
[RULES]            - Operational constraints
[TODO]             - Structured actions
```

**Usage:**
```python
from tools.query_maker1 import QueryMaker
packet = QueryMaker.build_task_packet("Search YouTube for One Piece")
print(QueryMaker.format_packet_for_executor(packet))
```

---

### 2. Query Maker v2 - Adaptive Context Depth for Thinking Models
**File:** `tools/query_maker2.py`

**Purpose:** Intelligent memory depth selection for reasoning models

**Three Severity Levels:**

**SMALL_IMPROVEMENT** (85% confidence)
- Minimal context: last message + current state + tools
- Keep latency low, attention clean
- Quick surgical fix approach

**MAJOR_ISSUE** (98% confidence)
- Deep context: full session + failure patterns + attempted solutions
- Self-corrective cognition through failure analysis
- Deep retrospective approach

**ARCHITECTURAL** (95% confidence)
- Full context: complete history + architectural analysis
- Identify root causes & design patterns
- Major rethinking approach

**Tool Knowledge (No Tool Use):**
- Models KNOW: python, websearch, calculator, filesystem, shell, browser, database, api
- Scout CONTROLS: execution permission & orchestration

**Failure Pattern Memory:**
```yaml
FAILURE_PATTERN:
  issue: [what went wrong]
  cause: [root cause]
  failed_attempts: [what was tried]
  error_class: [TIMEOUT, LOOP, SYNTAX, RESOURCE, etc.]
```

**Usage:**
```python
from tools.query_maker2 import QueryMaker2
packet = QueryMaker2.build_thinking_packet(
    user_query="This still doesn't work!",
    session_history=[...],
    current_state={...}
)
print(QueryMaker2.format_for_model(packet))
```

---

### 3. Input Controller - Smooth Keyboard & Mouse
**File:** `executor/input_controller.py`

**Status:** ✅ Tested & working smoothly (ydotool daemon active)

**Operations:**
- Mouse movement (absolute/relative)
- Click operations (L/R/M, single/double)
- Keyboard typing with configurable delay
- Key combinations (Ctrl+A, Super+D, Alt+Tab, etc.)
- Scroll wheel control
- Drag & drop support

**High-Level Methods:**
```python
InputController.move_mouse(x, y)
InputController.left_click()
InputController.type_text("text")
InputController.key_combination("ctrl+a")
InputController.click_and_type(x, y, "text")
InputController.drag_to(x1, y1, x2, y2)
InputController.search_and_type("query")
InputController.login_form("user", "pass")
```

**System Status:**
- ✓ ydotool daemon: /usr/bin/ydotoold (running)
- ✓ Mouse movement: smooth
- ✓ Keyboard input: smooth
- ✓ Click operations: working
- ✓ Mixed sequences: flawless

---

### 4. Scout History Logger - Absolute User History
**File:** `memory/scout_history_logger.py`
**Location:** `~/.elzyra/scout_history.txt`

**Purpose:** Plain text log that grows forever

**Features:**
- Appends every user ↔ Scout message
- Timestamps: [YYYY-MM-DD HH:MM:SS]
- Human-readable format
- One file, no rotation
- Searchable via grep/tools

**Usage:**
```python
from memory.scout_history_logger import ScoutHistoryLogger
logger = ScoutHistoryLogger()
logger.append_user("User message")
logger.append_scout("Scout response")
logger.append_section("Section Title")
print(logger.read_all())
print(logger.get_file_size())
```

---

### 5. Agent History Logger - Daily Agent Logs
**File:** `memory/agent_history_logger.py`
**Location:** `~/.elzyra/scout_{agent}_{YYYY-MM-DD}.txt`

**Three Agent Logs (Daily Rotation):**
1. `scout_executor_2026-05-12.txt` - Scout ↔ Executor
2. `scout_thinking_2026-05-12.txt` - Scout ↔ Thinking Model
3. `scout_router_2026-05-12.txt` - Scout ↔ Router Agent

**Features:**
- New file each day automatically
- Timestamps for every entry
- Task/Result tracking
- Section markers
- One manager controls all three

**Usage:**
```python
from memory.agent_history_logger import AllAgentsHistoryManager
manager = AllAgentsHistoryManager()

# Log to executor
manager.log_to_executor(
    scout_msg="Task: Search YouTube",
    agent_msg="✓ Completed"
)

# Log task execution
manager.log_task_execution(
    agent="thinking",
    task="Analyze failure pattern",
    result="Root cause: timeout loop",
    success=True
)
```

**Files Per Day: 3 (one per agent)**
**Files Total: 1 absolute + 3N dated files** (N = days)

---

## MEMORY SYSTEM

### Persistent Memory Types (in /home/dmannu/.claude/projects/-home-dmannu-ai-model-8/memory/)

**1. Executor Memory Architecture** (`executor_memory_architecture.md`)
- Type: project
- 3-tier Elzyra system design
- Executor operations, memory tree structure
- Keybinds, variables, rules, workflows

**2. Hybrid Search Implementation** (`hybrid_search_implementation.md`)
- Type: project
- 4-tier intelligent search system
- Knowledge router, tool dispatch, LLM integration
- ScrapeGraphAI, smart web interactor

**3. Project Complete** (`project_complete.md`)
- Type: project
- Modular AI assistant foundation (April 29)

---

## VENV CONFIGURATION

**Active VEnv:** `/mnt/D/venvs/elzyra-main`  
**Python:** `/mnt/D/venvs/elzyra-main/bin/python3`  
**Shebang:** `#!/mnt/D/venvs/elzyra-main/bin/python3`

**Main Script:** `/home/dmannu/ai-model-8/main.py`

---

## GROQ API STATUS

**API:** ✅ Working perfectly  
**Model:** `llama-3.1-8b-instant` (Groq hosted)  
**Status:** Integrated into `brain/llm.py`

**Testing:**
```bash
/mnt/D/venvs/elzyra-main/bin/python3 main.py --mode test --command "what is 2+2"
```

Output shows: `📡 Calling Groq API (llama-3.1-8b-instant)...` → `✓ Groq response received`

---

## SYSTEM STATE FILES

**Caelestia Shell Config:**
- Location: `~/.config/caelestia/shell.json`
- Contains: Appearance, launcher, dashboard, bar, keybinds, services
- Wallpapers: `/home/dmannu/Pictures/Wallpapers`

**Shell State (from config):**
- Terminal: foot
- Explorer: dolphin
- Media Player: Spotify
- Clock: 12-hour format

---

## KEY DESIGN PRINCIPLES

✅ **State-Aware Execution**
- Never work blindly
- Know current workspace, tabs, apps
- Prevent duplicate operations

✅ **Adaptive Context Depth**
- Small issues: minimal context (fast)
- Major issues: deep context (thorough)
- Architectural: full context (complete)

✅ **Deterministic Operations**
- Executor: fast, reflex-based
- Scout: manages planning & continuity
- Tool use only with permission

✅ **Tool Knowledge ≠ Tool Use**
- Models know what tools exist
- Scout controls execution permission

✅ **Failure Pattern Memory**
- Store: issue, cause, attempts, fix
- Enable self-corrective cognition
- Avoid repeating mistakes

---

## FILE STRUCTURE

```
/home/dmannu/ai-model-8/
├── main.py                     (entry point)
├── brain/
│   ├── brain.py               (intent, safety, action generation)
│   ├── llm.py                 (Groq API integration)
│   ├── action_parser.py       (parse LLM responses)
│   ├── README.md
│   └── __init__.py
├── tools/
│   ├── query_maker1.py        ✅ Executor context engine
│   ├── query_maker2.py        ✅ Thinking model adapter
│   ├── knowledge_router.py    (4-tier router)
│   ├── registry.py            (tool registry)
│   └── __init__.py
├── executor/
│   ├── executor.py            (execution engine)
│   ├── input_controller.py    ✅ Keyboard/mouse control
│   └── __init__.py
├── memory/
│   ├── scout_history_logger.py    ✅ Absolute history
│   ├── agent_history_logger.py    ✅ Daily agent logs
│   ├── conversation_logger.py     (structured JSON logging)
│   └── MEMORY.md              (memory index)
├── config/
│   ├── settings.py            (LLM, safety, intent config)
│   └── __init__.py
├── router/
│   ├── router.py
│   ├── message.py
│   └── __init__.py
├── state/
│   └── __init__.py
└── requirements.txt
```

---

## NEXT SESSION CHECKLIST

When next session starts:

1. ✅ Read this seed file for context
2. ✅ Check Groq API status
3. ✅ Verify ydotool daemon running
4. ✅ Test query_maker1.py & query_maker2.py
5. ✅ Review conversation logs (scout_history.txt)
6. ✅ Check agent logs (scout_executor_YYYY-MM-DD.txt, etc.)
7. ✅ Load memory from ~/.claude/projects/.../memory/MEMORY.md

---

## READY FOR

- ✅ Full Executor integration with query_maker1
- ✅ Thinking model optimization with query_maker2
- ✅ Input automation with input_controller
- ✅ Complete conversation tracking
- ✅ Daily agent communication logs

---

**Last Updated:** 2026-05-12 14:30:00  
**System Status:** 🟢 Operational  
**Ready to Deploy:** Yes
