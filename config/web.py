"""
Configuration for Elzyra's semantic web extraction subsystem.

This module is intentionally separate from UI/browser-control settings.
It configures semantic extraction, local model usage, caching, and scraping.
"""

from __future__ import annotations

from .endpoints import endpoint_of


DEFAULT_OLLAMA_MODEL = "llama3.1:8b"
DEFAULT_EMBEDDING_MODEL = "nomic-embed-text"

WEB_CONFIG = {
    "timeout": 60,
    "max_concurrency": 5,
    "cache_enabled": True,
    "cache_ttl_seconds": 1800,
    "cache_max_entries": 256,
    "headless": True,
    "max_retries": 3,
    "retry_backoff_seconds": 1.5,
    "default_result_limit": 5,
    "playwright_wait_until": "networkidle",
    "page_ready_timeout": 30000,
    "request_timeout": 30,
    "max_page_text_chars": 24000,
    "rate_limit_per_domain_seconds": 1.0,
    "domain_concurrency": 2,
    "browser_backend": "playwright",
    "ollama_model": DEFAULT_OLLAMA_MODEL,
    "embedding_model": DEFAULT_EMBEDDING_MODEL,
    "ollama_base_url": endpoint_of("ollama"),
    "ollama_generate_url": endpoint_of("ollama_generate"),
    "search_provider": "duckduckgo",
}

