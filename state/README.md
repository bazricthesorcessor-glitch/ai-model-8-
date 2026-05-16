# State Module

The `state` package tracks current execution status for the running process. It is separate from long-term memory and focuses on immediate progress, recent actions, and approval state.

## Main files

- `state.py`: state container and update helpers.
- `__init__.py`: public exports for the rest of the system.

## Stored concepts

- current execution status
- recent action history
- latest tool outputs
- approval and error state

## Relationship to memory

`state/` is the short-lived operational view. `memory/` handles broader persistence, logging, and retrieval.
