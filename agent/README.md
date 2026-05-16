# Agent Module

The `agent` package contains user-facing wrappers around the assistant runtime.

## Files

- `agent_daemon.py`: background service entry point.
- `agent_cli.py`: command-line client.
- `agent_config.py`: agent-specific settings.

## Purpose

Use this folder for daemon lifecycle, CLI interaction, and agent-facing configuration rather than core reasoning or execution logic.
