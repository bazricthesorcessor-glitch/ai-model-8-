"""TTL cache primitives for semantic web extraction."""

from __future__ import annotations

import json
import time
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from config import CACHE_DIR
from config.web import WEB_CONFIG
from .utils import ensure_jsonable


class WebCache:
    """Small persistent TTL cache for expensive extraction operations."""

    def __init__(
        self,
        cache_path: Optional[Path] = None,
        ttl_seconds: Optional[int] = None,
        max_entries: Optional[int] = None,
    ):
        self.cache_path = cache_path or (CACHE_DIR / "web_cache.json")
        self.ttl_seconds = ttl_seconds or WEB_CONFIG["cache_ttl_seconds"]
        self.max_entries = max_entries or WEB_CONFIG["cache_max_entries"]
        self._persistence_enabled = True
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            self.cache_path = Path(tempfile.gettempdir()) / "elzyra_web_cache.json"
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self._memory: Dict[str, Dict[str, Any]] = {}
        self._load()

    def get(self, key: str) -> Optional[Any]:
        entry = self._memory.get(key)
        if not entry:
            return None
        if self._is_expired(entry):
            self.delete(key)
            return None
        return entry.get("value")

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        self._memory[key] = {
            "value": ensure_jsonable(value),
            "created_at": time.time(),
            "ttl_seconds": ttl_seconds or self.ttl_seconds,
        }
        self._enforce_max_entries()
        self._persist()

    def delete(self, key: str) -> None:
        self._memory.pop(key, None)
        self._persist()

    def clear(self) -> None:
        self._memory.clear()
        self._persist()

    def stats(self) -> Dict[str, Any]:
        active_entries = {
            key: value
            for key, value in self._memory.items()
            if not self._is_expired(value)
        }
        return {
            "entries": len(active_entries),
            "ttl_seconds": self.ttl_seconds,
            "max_entries": self.max_entries,
            "path": str(self.cache_path),
            "persistence_enabled": self._persistence_enabled,
        }

    def _is_expired(self, entry: Dict[str, Any]) -> bool:
        ttl = entry.get("ttl_seconds", self.ttl_seconds)
        created_at = entry.get("created_at", 0)
        return time.time() > (created_at + ttl)

    def _enforce_max_entries(self) -> None:
        while len(self._memory) > self.max_entries:
            oldest_key = min(
                self._memory,
                key=lambda key: self._memory[key].get("created_at", 0),
            )
            self._memory.pop(oldest_key, None)

    def _load(self) -> None:
        if not self.cache_path.exists():
            return
        try:
            data = json.loads(self.cache_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                self._memory = data
        except Exception:
            self._memory = {}

    def _persist(self) -> None:
        payload = json.dumps(self._memory, indent=2, sort_keys=True, default=str)
        try:
            self.cache_path.write_text(payload, encoding="utf-8")
        except OSError:
            self._persistence_enabled = False
