# Elzyra

Elzyra is a modular Python assistant for desktop automation, tool orchestration, memory, and web interaction. The repository is organized by subsystem so routing, execution, state, UI helpers, and integrations can evolve independently.

## Entry points

- `main.py`: interactive integration runner for the current modular stack.
- `agent/`: daemon and CLI wrappers around the assistant.
- `brain/`: intent analysis, planning, and model-facing logic.
- `executor/`: step execution and input control.
- `router/`: dispatch layer between modules.
- `memory/` and `state/`: long-lived data and in-process status tracking.
- `tools/` and `web_system/`: tool registry plus web search and scraping support.

## Repository layout

- `agent/`, `brain/`, `executor/`, `router/`, `state/`: core orchestration modules.
- `config/`: shared configuration, paths, and endpoint settings.
- `memory/`: memory implementation plus on-disk data under `memory/data/`.
- `os/`, `terminal/`, `vision/`, `voice/`, `ui/`: capability-specific runtime modules.
- `tests/`: cross-module integration coverage.
- `scripts/`: setup and environment checks.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

## Notes

- The repo contains both current modules and older design/reference documents.
- Browser, OCR, voice, and desktop automation features have extra system dependencies outside Python packages.
- Generated caches and memory data live inside the repository and are intentionally separate from source modules.
- Brave automation uses the normal shared Brave session; Elzyra is isolated by
  Hyprland workspaces rather than a custom browser profile.
