"""Playwright-backed page loader for semantic extraction."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, Optional

from config.web import WEB_CONFIG


@dataclass
class PageLoadResult:
    url: str
    title: str
    html: str
    text: str
    status: int
    backend: str


class PlaywrightManager:
    """Manage local page loading with Playwright and requests fallback."""

    def __init__(
        self,
        headless: Optional[bool] = None,
        timeout_ms: Optional[int] = None,
    ):
        self.headless = WEB_CONFIG["headless"] if headless is None else headless
        self.timeout_ms = timeout_ms or WEB_CONFIG["page_ready_timeout"]

    async def fetch_page(
        self,
        url: str,
        wait_until: Optional[str] = None,
    ) -> PageLoadResult:
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            return await self._fetch_with_requests(url)

        wait_until = wait_until or WEB_CONFIG["playwright_wait_until"]
        try:
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(headless=self.headless)
                page = await browser.new_page()
                try:
                    response = await page.goto(url, wait_until=wait_until, timeout=self.timeout_ms)
                    await page.wait_for_timeout(300)
                    html = await page.content()
                    title = await page.title()
                    text = await page.locator("body").inner_text(timeout=self.timeout_ms)
                    status = response.status if response else 200
                    return PageLoadResult(
                        url=page.url,
                        title=title,
                        html=html,
                        text=text,
                        status=status,
                        backend="playwright",
                    )
                finally:
                    await browser.close()
        except Exception:
            return await self._fetch_with_requests(url)

    async def _fetch_with_requests(self, url: str) -> PageLoadResult:
        import requests

        response = requests.get(url, timeout=WEB_CONFIG["request_timeout"])
        response.raise_for_status()
        html = response.text
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "lxml")
            text = soup.get_text(separator=" ", strip=True)
            title = soup.title.string.strip() if soup.title and soup.title.string else ""
        except ImportError:
            import re

            text = " ".join(re.sub(r"<[^>]+>", " ", html).split())
            title = ""
        return PageLoadResult(
            url=response.url,
            title=title,
            html=html,
            text=text,
            status=response.status_code,
            backend="requests_fallback",
        )
