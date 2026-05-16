# Web System Core

This directory contains the main implementation of the web stack.

## Files

- `web.py`: unified `WebInteractor` interface.
- `api_backend.py`: search-provider integrations.
- `scraper_backend.py`: page fetching and extraction.
- `browser_backend.py`: browser automation backend.
- `smart_interactor.py`: higher-level interaction helper.
- `examples.py`, `test_web.py`: examples and tests.

## Role

Most web behavior in the repository should route through this folder rather than calling providers directly.
