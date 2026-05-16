# Web System

`web_system` is the repository's web capability package. It groups search backends, scraping, browser automation, extractors, examples, tests, and integration-friendly tool wrappers.

## Layout

- `core/`: main interfaces and concrete backends.
- `docs/`: design notes and quick-start material.
- `extractors/`: specialized extraction implementations.
- `tools/`: tool-facing wrappers for the broader assistant.
- `examples/`: importable examples.
- `tests/`: package-level tests.

## Primary entry point

`web_system/core/web.py` exposes `WebInteractor`, which combines:

- web search
- page scraping
- browser automation
- shared status and result normalization

## Notes

- networked backends depend on external APIs or local browser drivers
- mock paths exist for testing and local development
