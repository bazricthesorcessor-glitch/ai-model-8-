# Brain Module

The `brain` package turns user input into structured work. It handles intent analysis, safety checks, planning helpers, and model-backed parsing without executing tools directly.

## Main files

- `brain.py`: intent analysis and action generation entry points.
- `llm.py`: model client integration.
- `planner.py`, `supervisor.py`, `observer.py`: higher-level coordination helpers.
- `action_parser.py`, `json_utils.py`: parsing and normalization utilities.

## Responsibilities

- classify conversational vs task-oriented input
- apply safety checks before execution
- translate requests into executor-friendly steps
- keep model-facing logic isolated from tool-running code

## Related modules

- `router/` forwards messages into the system
- `executor/` runs the steps produced here
- `config/` supplies model and safety configuration
