"""
Central registry of localhost services used by Elzyra.
"""

ENDPOINTS = {
    "brave_cdp": "http://127.0.0.1:9222",
    "brave_tabs": "http://127.0.0.1:9222/json",
    "ollama": "http://127.0.0.1:11434",
    "ollama_generate": "http://127.0.0.1:11434/api/generate",
}


def endpoint_of(name: str) -> str:
    """Return a registered endpoint by semantic name."""
    if name not in ENDPOINTS:
        available = ", ".join(sorted(ENDPOINTS))
        raise ValueError(f"Endpoint not found: '{name}'. Available: {available}")
    return ENDPOINTS[name]
