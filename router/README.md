# Router Module

The `router` package is the dispatch layer between high-level requests and subsystem handlers. It provides message types, routing rules, and older routing experiments kept for reference.

## Main files

- `router.py`: current routing entry points.
- `message.py`: shared request and response structures.
- `routing_config.py`: route selection configuration.
- `advanced_router_legacy.py`, `model_selector_legacy.py`: older implementations retained for comparison.

## Responsibilities

- normalize message flow between modules
- choose the right handler or service target
- keep module boundaries explicit

## Related modules

- `brain/` decides what should happen
- `executor/` performs the work
- `state/` and `memory/` capture the result
