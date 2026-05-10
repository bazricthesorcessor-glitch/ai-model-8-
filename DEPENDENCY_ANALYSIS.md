# 🔗 Inter-Folder Dependency Analysis

## Current Dependency Graph

### ✅ Healthy Dependencies

```
config/
  ├─ No external dependencies (GOOD - foundation)
  └─ Used by: brain/, executor/, memory/, tools/

router/
  ├─ imports: brain/, executor/, state/ (EXPECTED - router dispatches)
  └─ Used by: main.py, tests/

os/
  ├─ No external dependencies (GOOD - platform module)
  └─ Used by: terminal/, vision/, voice/, web_system/, tools/, memory/

main.py (Entry Point)
  ├─ imports: brain/, config/, executor/, memory/, router/, state/
  └─ Orchestrates all modules (EXPECTED)
```

### ⚠️ Problematic Dependencies

#### 1. **config/settings.py imports from os/** ❌
```python
# config/settings.py line 8
$caelestia = ~/.local/share/caelestia/hypr
```
- **Issue**: Config folder should NOT depend on os/ 
- **Why**: Creates circular dependency risk
- **Fix**: Remove os imports from settings.py, keep only string paths

#### 2. **executor/ imports from brain/** ❌
```python
# executor/executor.py
from brain import check_safety
```
- **Issue**: Executor should NOT call brain directly
- **Why**: Violates router pattern - all communication via router
- **Fix**: Receive safety checks through message context, not direct import

#### 3. **executor/ imports from state/** ❌
```python
# executor/executor.py
from state import update
```
- **Issue**: Executor should NOT call state directly
- **Why**: Violates router pattern - state updates via router messages
- **Fix**: Return results to router, let router update state

#### 4. **Multiple modules import from os/** (Partially OK)
```
terminal/ → os/
vision/ → os/
voice/ → os/
web_system/ → os/
tools/ → os/
memory/ → os/
```
- **Status**: ACCEPTABLE (os is platform module)
- **But should be careful**: These should only use os for platform operations

---

## Dependency Matrix

| From | To Config | To Router | To Brain | To Executor | To State | To OS |
|------|-----------|-----------|----------|-------------|----------|-------|
| **config** | - | ✓ Own | - | - | - | ❌ Remove |
| **router** | ✓ Reads | - | ✓ Calls | ✓ Calls | ✓ Calls | - |
| **brain** | ✓ Reads | - | - | - | - | ✓ Platform |
| **executor** | ✓ Reads | - | ❌ Fix | - | ❌ Fix | ✓ Platform |
| **state** | ✓ Reads | - | - | - | - | - |
| **memory** | ✓ Reads | - | - | - | - | ✓ Platform |
| **tools** | ✓ Reads | - | - | - | - | ✓ Platform |
| **terminal** | - | - | - | - | - | ✓ Platform |
| **vision** | - | - | - | - | - | ✓ Platform |
| **voice** | - | - | - | - | - | ✓ Platform |
| **web_system** | - | - | - | - | - | ✓ Platform |
| **os** | - | - | - | - | - | - |

---

## Issues to Fix

### Issue #1: config/settings.py has os path imports

**Current**: 
```python
# config/settings.py
"caelestia_base_dir": os.path.expanduser("~/.local/share/caelestia/hypr"),
```

**Problem**: settings.py shouldn't import `os` module OR reference OS paths

**Solution**: Make OS_CONFIG paths pure strings, let os/ module handle paths
```python
# config/settings.py - Fixed
OS_CONFIG = {
    "hyprland_config_dir": "~/.config/hypr",
    "shell_config_file": "~/.config/caelestia/shell.json",
    # ... (no os.path.expanduser)
}

# os/__init__.py - Handles path expansion
from config import OS_CONFIG
paths = {k: os.path.expanduser(v) for k, v in OS_CONFIG.items()}
```

### Issue #2: executor imports from brain and state

**Current**:
```python
# executor/executor.py
from brain import check_safety
from state import update

def execute(message):
    # Direct calls
    safe, severity, reason = check_safety(command)
    state.update(result)
```

**Problem**: Violates router pattern - executor shouldn't call other modules directly

**Solution**: Receive data through message, return results to router
```python
# executor/executor.py - Fixed
from router import Message

def execute(message: Message) -> Response:
    # Safety checks come from message context
    if message.data.get("requires_safety_check"):
        # Logic here, but NO direct brain calls
        pass
    
    # Execute step
    result = execute_step(message.steps[0])
    
    # Return for router to dispatch to state
    return Response(
        success=True,
        data={"action_result": result},
        message=Message(action="record_state", data=result)
    )
```

### Issue #3: Some modules import from os when they shouldn't

**Current problematic imports**:
```python
# web_system/core/api_backend.py
from os import HyprlandManager  # WRONG!

# vision/vision.py
from os import WindowManager  # WRONG!
```

**Problem**: These should NOT import from os/ folder - they're getting confused

**Solution**: These should only use os/ for actual OS operations
```python
# web_system/core/api_backend.py - Fixed
# Remove: from os import ...
# Only use: from os import HyprlandManager  if needed for ACTUAL OS operations
```

---

## Healthy Dependency Patterns

### ✅ Pattern 1: Config Read-Only
```
config/ 
  └─ Used by: [brain, executor, memory, tools, router]
  └─ Direction: ONE-WAY (modules read from config)
```

### ✅ Pattern 2: Router as Dispatcher
```
router/
  ├─ Imports: [brain, executor, state]
  ├─ Direction: Calls other modules, routes messages
  └─ Used by: main.py, entry points
```

### ✅ Pattern 3: OS as Platform Module
```
os/
  ├─ No external dependencies
  ├─ Used by: terminal/, vision/, voice/, web_system/
  └─ Direction: ONE-WAY (modules call os when needed)
```

### ❌ Pattern: Circular/Cross Dependencies
```
executor → brain  ❌ (should go through router)
executor → state  ❌ (should go through router)
brain → executor  ❌ (should go through router)
```

---

## Recommended Fixes (Priority Order)

### 1. **HIGH PRIORITY**: Fix executor direct imports
**Files affected**:
- executor/executor.py
- executor/__init__.py

**Action**: Remove direct imports of brain/ and state/, use router messages

**Before**:
```python
from brain import check_safety
from state import update
```

**After**:
```python
# No direct imports - all via message context
```

---

### 2. **HIGH PRIORITY**: Fix config/ circular dependency
**Files affected**:
- config/settings.py

**Action**: Remove os.path imports, use plain strings for paths

**Before**:
```python
"shell_config_file": os.path.expanduser("~/.config/caelestia/shell.json")
```

**After**:
```python
"shell_config_file": "~/.config/caelestia/shell.json"
```

---

### 3. **MEDIUM PRIORITY**: Clean up os imports in web/vision/voice
**Files affected**:
- web_system/core/*.py
- vision/vision.py
- voice/voice.py

**Action**: Verify imports are actual OS operations, not module confusion

**Check**:
```python
# Is this needed?
from os import HyprlandManager

# If only using for OS operations, keep it
# If using for unrelated things, remove it
```

---

### 4. **LOW PRIORITY**: Router cleanup
**Files affected**:
- router/router.py
- router/routing_config.py

**Status**: Actually OK - router needs to import brain/executor/state

**Keep as-is**: This is the correct pattern

---

## Dependency Flow (Ideal)

```
User Input
    ↓
main.py
    ↓
router.route(message)
    ├─ message.action == "decide"
    │   └─ brain.decide(message)
    │       └─ reads: config/
    │
    ├─ message.action == "execute"  
    │   └─ executor.execute(message)
    │       └─ uses: os/ (for platform ops)
    │       └─ returns: results to router
    │
    ├─ message.action == "record_state"
    │   └─ state.update(message)
    │       └─ reads: config/
    │
    └─ message.action == "get_state"
        └─ state.get(message)
```

**Key**: No module calls another module directly except:
- router calls all modules (dispatcher)
- config is read-only by all modules
- os is called by platform-specific modules

---

## Summary

| Metric | Status | Notes |
|--------|--------|-------|
| Total Files | 71 | Organized |
| Folders | 14 | Clean structure |
| **Problematic Dependencies** | 3 | executor→brain, executor→state, config→os |
| **Healthy Dependencies** | Most | config/router/os patterns OK |
| **Cross-folder imports** | Moderate | Need executor cleanup |
| **Architectural Pattern** | Mixed | Router pattern partially implemented |

---

## Next Steps

1. ✅ **Analyze** - DONE (this document)
2. ⏳ **Fix executor imports** - Remove direct brain/state calls
3. ⏳ **Fix config imports** - Remove os.path usage
4. ⏳ **Verify web/vision/voice imports** - Ensure they're OS ops
5. ⏳ **Test** - Verify all modules still work after fixes
6. ⏳ **Document** - Update module README files with correct patterns

---

**Status**: Architecture mostly sound, 3 critical issues need fixing.
