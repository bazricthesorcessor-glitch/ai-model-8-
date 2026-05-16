# Terminal Module

The `terminal` package provides shell execution primitives. It is the command-running layer used when a task needs subprocess execution rather than browser or desktop automation.

## Main files

- `terminal.py`: `TerminalExecutor`, result types, and helper functions.
- `test_terminal.py`: focused tests for terminal behavior.

## Supported behavior

- run commands in a selected shell
- capture stdout, stderr, exit code, and duration
- execute simple pipelines
- manage working directory and environment variables

## Constraints

This module executes commands only. It does not decide whether a command should run; that belongs to higher layers.
