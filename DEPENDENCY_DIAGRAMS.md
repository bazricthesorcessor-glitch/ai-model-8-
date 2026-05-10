# Dependency Architecture Diagrams

## Current Architecture (WITH ISSUES)

```
┌─────────────────────────────────────────────────────────────┐
│                        main.py (Entry Point)                 │
└──────┬─────────────────────────────────────────────────────┬┘
       │                                                       │
       ├─→ router/ ◄──────────────────────┐                  │
       │    └─ route(message)              │                  │
       │       ├─→ brain/  ◄─ config/ ◄───┼──────────┐       │
       │       │            └─ check_safety│          │       │
       │       │                           │          │       │
       │       ├─→ executor/ ◄─ config/ ◄──┤  ❌     │       │
       │       │    └─ execute()  └─ brain/ (WRONG!)  │       │
       │       │                   └─ state/          │       │
       │       │                                       │       │
       │       ├─→ state/ ◄─ config/                  │       │
       │       │   └─ update()                         │       │
       │       │                                       │       │
       │       └─→ memory/ ◄─ config/                 │       │
       │           └─ log()   └─ os/ (✓ OK)           │       │
       │                                               │       │
       ├─ config/ ◄─────────────────────────────┐    │       │
       │  └─ settings.py ─────────→ os/ ❌(WRONG!)   │       │
       │                                         │    │       │
       ├─ terminal/ ◄─ os/                      │    │       │
       ├─ vision/ ◄─ os/                        │    │       │
       ├─ voice/ ◄─ os/                         │    │       │
       ├─ web_system/ ◄─ os/                    │    │       │
       ├─ tools/ ◄─ config/, os/                │    │       │
       │                                         │    │       │
       └─ agent/, tests/, todo/ ◄─ various      │    │       │

Legend:
  ─→  Direct import/call
  ◄─  Dependency
  ❌  Problematic dependency (violates pattern)
  ✓   Healthy dependency
```

## Ideal Architecture (FIXED)

```
┌─────────────────────────────────────────────────────────────┐
│                        main.py (Entry Point)                 │
└──────────────┬───────────────────────────────────────────┬──┘
               │                                           │
               └─→ router/ (Central Dispatcher)           │
                   ├─ route(message)                       │
                   │  ├─→ brain/ ◄─ config/ ✓            │
                   │  │   └─ decide(msg)                  │
                   │  │                                    │
                   │  ├─→ executor/ ◄─ config/ ✓         │
                   │  │   └─ execute(msg)                 │
                   │  │   └─ returns Message              │
                   │  │   └─ (no direct brain/state calls)│
                   │  │                                    │
                   │  ├─→ state/ ◄─ config/ ✓            │
                   │  │   └─ update(msg)                  │
                   │  │                                    │
                   │  └─→ memory/ ◄─ config/ ✓           │
                   │      └─ log(msg)                     │
                   │                                       │
                   ├─ config/ (Read-only foundation) ✓   │
                   │  └─ settings.py                      │
                   │     └─ (no external deps)            │
                   │                                       │
                   ├─ Platform Modules (Independent) ✓   │
                   │  ├─ os/ ─→ [terminal, vision, voice]│
                   │  ├─ web_system/ ─→ uses os/ if need │
                   │  ├─ terminal/                         │
                   │  ├─ vision/                           │
                   │  └─ voice/                            │
                   │                                       │
                   └─ Utilities                            │
                      ├─ tools/ ◄─ config/, os/ ✓        │
                      ├─ memory/ ◄─ config/ ✓            │
                      └─ agent/, tests/, todo/             │

Legend:
  ─→  Direct call
  ◄─  One-way dependency
  ✓   Healthy pattern (allowed)
  ❌  Removed (not allowed)
```

## Dependency Rules (Enforce These)

### ✅ ALLOWED Patterns

```
1. Any module can READ from config/
   ├─ brain/ ◄─ config/
   ├─ executor/ ◄─ config/
   ├─ state/ ◄─ config/
   └─ tools/ ◄─ config/

2. router/ can CALL other modules
   ├─ router → brain/
   ├─ router → executor/
   ├─ router → state/
   └─ router → memory/

3. Platform modules can use os/
   ├─ terminal/ → os/
   ├─ vision/ → os/
   ├─ voice/ → os/
   └─ web_system/ → os/
```

### ❌ FORBIDDEN Patterns

```
1. Cross-module direct calls
   ❌ executor → brain
   ❌ executor → state
   ❌ state → brain
   ❌ brain → executor

2. config/ with external dependencies
   ❌ config → os
   ❌ config → terminal
   ❌ config → any platform module

3. Circular dependencies
   ❌ A → B → A
   ❌ A → B → C → A
```

## Dependency Levels

```
Level 0 (Foundation - No dependencies)
├─ config/
└─ os/

Level 1 (Depends on Level 0 only)
├─ brain/ ◄─ config
├─ state/ ◄─ config
├─ memory/ ◄─ config
└─ tools/ ◄─ config

Level 2 (Depends on Level 0-1, uses router)
├─ executor/ ◄─ config, message
├─ terminal/ ◄─ os
├─ vision/ ◄─ os
├─ voice/ ◄─ os
└─ web_system/ ◄─ os

Level 3 (Entry points, uses router)
├─ router/ ◄─ brain, executor, state, memory
├─ main.py ◄─ router
└─ tests/ ◄─ multiple modules
```

## File-by-File Fixes Needed

### 1. executor/executor.py
**Current problematic imports**:
```python
from brain import check_safety        # ❌ Remove
from state import update              # ❌ Remove
```

**Fix approach**:
```python
# ✅ FIXED: No direct imports
# Safety checks received via message.data["requires_approval"]
# State updates returned as Message(action="record_state")

def execute(message: Message) -> Response:
    # No direct calls to brain or state
    result = execute_step(message)
    
    # Return results for router to dispatch
    return Response(
        success=True,
        data=result,
        messages=[
            Message(action="record_state", data=result)
        ]
    )
```

### 2. config/settings.py
**Current problematic code**:
```python
import os  # ❌ Remove

OS_CONFIG = {
    "hyprland_config_dir": os.path.expanduser("~/.config/hypr"),  # ❌ Remove
}
```

**Fix approach**:
```python
# ✅ FIXED: No imports, pure strings

OS_CONFIG = {
    "hyprland_config_dir": "~/.config/hypr",  # ✓ Just strings
    "shell_config_file": "~/.config/caelestia/shell.json",
    # ... etc
}

# OS module handles expansion
# os/__init__.py:
# import os
# from config import OS_CONFIG
# EXPANDED_CONFIG = {k: os.path.expanduser(v) for k, v in OS_CONFIG.items()}
```

### 3. web_system/core/api_backend.py (if importing os module)
**Check & fix if needed**:
```python
# ❌ BAD: from os import HyprlandManager
# If this exists, remove it

# ✓ GOOD: Only import when actually using OS operations
# from os import HyprlandManager  # Only if API backend actually needs this
```

---

## Verification Checklist

After fixes, verify:

- [ ] executor/executor.py has no imports from brain/
- [ ] executor/executor.py has no imports from state/
- [ ] config/settings.py has no imports from os/
- [ ] config/settings.py has no os.path.expanduser calls
- [ ] router/router.py still has imports from brain/executor/state ✓
- [ ] main.py still imports from router ✓
- [ ] All test files run without import errors
- [ ] All modules still function correctly
- [ ] Only level 0 modules have zero external dependencies

---

## Expected Result After Fixes

```
✅ Dependency graph becomes acyclic
✅ router is the only orchestrator
✅ config is read-only foundation
✅ os is independent platform module
✅ Each module has clear responsibility
✅ No circular dependencies
✅ Follows single responsibility principle
```
