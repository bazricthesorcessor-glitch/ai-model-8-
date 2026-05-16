# Tools Module

The `tools` package defines the assistant's tool catalog. It contains base tool types, schemas, registry code, and platform-specific namespaces under `tools/browser`, `tools/web`, `tools/system`, `tools/vision`, `tools/keyboard`, and `tools/mouse`.

## Main files

- `tool.py`: base tool abstraction.
- `definitions.py`, `schemas.py`: tool metadata and structure.
- `registry.py`: in-memory registry.
- `service.py`: service bridge helpers.
- `knowledge_router.py`, `unified_query_maker.py`, `query_maker*.py`: query and routing utilities.

## Subpackages

- `browser/`: browser-oriented tool namespace.
- `web/`: web lookup and page interaction tools.
- `system/`: system-level actions.
- `vision/`: vision-facing tools.
- `keyboard/`, `mouse/`: input-device tools.

## Role in the stack

Tool definitions live here. Planning stays in `brain/`, routing in `router/`, and execution in `executor/`.
