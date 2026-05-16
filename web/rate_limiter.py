"""Rate limiting primitives for semantic web extraction."""

from __future__ import annotations

import asyncio
import time
from contextlib import asynccontextmanager
from typing import Dict, Optional

from config.web import WEB_CONFIG
from .utils import domain_of


class DomainRateLimiter:
    """Per-domain cooldown and concurrency limiter."""

    def __init__(
        self,
        cooldown_seconds: Optional[float] = None,
        max_concurrency: Optional[int] = None,
    ):
        self.cooldown_seconds = cooldown_seconds or WEB_CONFIG["rate_limit_per_domain_seconds"]
        self.max_concurrency = max_concurrency or WEB_CONFIG["domain_concurrency"]
        self._semaphores: Dict[str, asyncio.Semaphore] = {}
        self._last_access: Dict[str, float] = {}

    @asynccontextmanager
    async def limit(self, url: str):
        domain = domain_of(url)
        semaphore = self._semaphores.setdefault(domain, asyncio.Semaphore(self.max_concurrency))

        async with semaphore:
            await self._wait_cooldown(domain)
            try:
                yield
            finally:
                self._last_access[domain] = time.monotonic()

    async def _wait_cooldown(self, domain: str) -> None:
        previous = self._last_access.get(domain)
        if previous is None:
            return
        elapsed = time.monotonic() - previous
        if elapsed < self.cooldown_seconds:
            await asyncio.sleep(self.cooldown_seconds - elapsed)

