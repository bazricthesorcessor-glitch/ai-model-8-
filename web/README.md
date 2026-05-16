# Web Subsystem

This package is Elzyra's semantic web extraction subsystem. It is separate from UI automation.

## Separation of concerns

- `ui/`: browser tabs, CDP, workspace-controlled interactive browsing
- `web/`: semantic extraction, search, schema validation, caching, local-first research

The subsystem does not click through user sessions or drive provider tabs. It extracts structured information from web pages and search results.

## Architecture

- `scrape_service.py`: first-class entry point for semantic extraction
- `search_service.py`: search primitives
- `extraction_service.py`: typed extraction helpers
- `schema_service.py`: schema resolution and validation
- `graph_manager.py`: ScrapeGraphAI and fallback orchestration
- `ollama_client.py`: local model client
- `playwright_manager.py`: JS-capable page loading
- `web_observer.py`: extraction quality checks
- `cache.py`: TTL cache
- `rate_limiter.py`: per-domain throttling
- `utils.py`: shared helpers

## Execution model

Primary path:
1. search or direct URL input
2. semantic extraction via ScrapeGraphAI
3. schema validation
4. observer quality checks
5. cached structured result

Fallback path:
1. Playwright or requests loads the page
2. local Ollama model extracts structured JSON
3. schema validation and observer checks run before success is returned

## Local-first design

The subsystem prefers:
- local Ollama models
- local Playwright Chromium
- local cache persistence

Cloud search providers can still be used through the existing API backend, but the extraction path is designed to work locally first.

## Scaling direction

The current design keeps primitives small so Scout and Brain can compose them:
- `semantic_extract`
- `search_and_extract`
- `extract_article`
- `extract_product`
- `extract_research`
- `summarize_page`

Future graph types can be added in `graph_manager.py` without coupling them to UI automation.
