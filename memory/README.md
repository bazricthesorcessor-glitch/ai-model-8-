# Memory Module

The `memory` package stores assistant context beyond a single call. It contains lightweight runtime memory, logging utilities, search helpers, and the on-disk data model under `memory/data/`.

## Main files

- `core.py`: in-memory state container used during runtime.
- `memory.py`, `unified_memory.py`: higher-level memory orchestration.
- `reader.py`, `writer.py`, `search.py`, `compiler.py`, `cleaner.py`: storage and retrieval helpers.
- `schemas.py`, `paths.py`: structure and path definitions.

## Data layout

- `memory/data/active/`: recent logs and active context.
- `memory/data/archive/`: long-term retained records.
- `memory/data/identity/`: durable preferences and user-facing identity data.
- `memory/data/state/`: serialized state snapshots.
- `memory/data/tools/`: tool registry and tool-related memory artifacts.

## Scope

This folder mixes implementation code and data. Source files define how memory works; `memory/data/` holds the persisted artifacts the system reads and writes.
