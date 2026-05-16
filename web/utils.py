"""Shared helpers for Elzyra's semantic web subsystem."""

from __future__ import annotations

import asyncio
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, Optional
from urllib.parse import urlparse


def normalize_url(url: str) -> str:
    """Normalize a URL-like string into an absolute HTTP URL."""
    if "://" in url:
        return url
    return f"https://{url}"


def domain_of(url: str) -> str:
    parsed = urlparse(normalize_url(url))
    return parsed.netloc.lower()


def cache_key_for(*parts: Any) -> str:
    payload = json.dumps(parts, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def ensure_jsonable(value: Any) -> Any:
    """Convert models and dataclasses into JSON-safe payloads."""
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "__dict__"):
        return {
            key: ensure_jsonable(item)
            for key, item in value.__dict__.items()
            if not key.startswith("_")
        }
    if isinstance(value, dict):
        return {str(key): ensure_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [ensure_jsonable(item) for item in value]
    return value


def run_sync(coro: Any) -> Any:
    """Run an async coroutine from sync code, even if an event loop exists."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()

    return asyncio.run(coro)


def compact_text(text: str, max_chars: int) -> str:
    """Truncate text conservatively for model prompts."""
    text = (text or "").strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def optional_import_error(module_name: str, extra: Optional[str] = None) -> str:
    message = f"Optional dependency '{module_name}' is not installed"
    if extra:
        message = f"{message}. {extra}"
    return message

