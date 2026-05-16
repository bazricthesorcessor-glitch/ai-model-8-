# Executor Module

The `executor` package runs structured steps produced by the brain or router. It owns execution flow, input control, and integration glue for capability-specific modules.

## Main files

- `executor.py`: primary execution path.
- `input_controller.py`: keyboard and mouse style input helpers.
- `caelestia_integration.py`: integration code for the Caelestia environment.

## Responsibilities

- execute ordered tool steps
- coordinate approval-sensitive actions
- normalize execution results for state and memory
- bridge high-level actions to lower-level modules

## Boundaries

- planning stays in `brain/`
- routing stays in `router/`
- tool definitions stay in `tools/`
