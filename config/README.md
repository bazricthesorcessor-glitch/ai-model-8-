# Config Module

The `config` package is the shared source of settings, paths, endpoints, and app-level defaults. Other modules import configuration from here instead of hardcoding paths or environment assumptions.

## Main files

- `settings.py`: runtime defaults and configuration maps.
- `paths.py`: semantic path resolution helpers.
- `endpoints.py`, `app.py`: endpoint and app-specific settings.
- `web.py`: semantic web subsystem defaults.
- `workspaces.py`: Elzyra workspace registry and selection helpers.
- `HYPRLAND_CONFIG_GUIDE.md`: desktop-specific reference material.

## What belongs here

- model and execution defaults
- file system paths
- service endpoints
- workspace boundary rules for Elzyra-controlled UI actions
- feature toggles shared across modules

## What does not belong here

- business logic
- tool execution
- module-to-module orchestration

## Browser isolation note

Brave no longer uses a dedicated Elzyra profile directory. The normal Brave
session is shared, and Hyprland workspaces are now the isolation boundary for
Elzyra-controlled browser actions.
