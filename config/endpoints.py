"""Central registry of local services and runtime resources used by Elzyra."""

from pathlib import Path

_WEB_CACHE_PATH = Path.home() / ".cache" / "elzyra" / "web"

ENDPOINTS = {
    "brave_cdp": "http://127.0.0.1:9222",
    "brave_tabs": "http://127.0.0.1:9222/json",
    "ollama": "http://127.0.0.1:11434",
    "ollama_generate": "http://127.0.0.1:11434/api/generate",
    "scrapegraph_service": "local://elzyra/web/scrapegraph",
    "playwright": "local://playwright/chromium",
    "web_cache": f"file://{_WEB_CACHE_PATH}",
}


def endpoint_of(name: str) -> str:
    """Return a registered endpoint by semantic name."""
    if name not in ENDPOINTS:
        available = ", ".join(sorted(ENDPOINTS))
        raise ValueError(f"Endpoint not found: '{name}'. Available: {available}")
    return ENDPOINTS[name]
