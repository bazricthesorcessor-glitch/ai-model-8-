# UI Module

The `ui` package contains desktop-facing interfaces, dashboards, helpers, and examples.

## Main files

- `dashboard.py`, `service.py`, `caelestia_controller.py`: runtime UI surfaces and integration points.
- `quick_terminal.py`, `ai_tabs.py`: interactive UI features.
- `screenshot_manager.py`: screenshot utilities.
- `*_examples.py`, `test_*.py`: examples and focused tests.

## Notes

This folder mixes runnable UI components, local experiments, and supporting scripts such as `shortcuts.sh`.

Brave automation now uses the normal shared Brave session. Elzyra stays inside
dedicated Hyprland workspaces, so the workspace is the UI isolation boundary
instead of a separate browser profile.
