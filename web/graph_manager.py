"""Graph orchestration for semantic web extraction."""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any, Dict, Iterable, List, Optional

from config.web import WEB_CONFIG
from .ollama_client import OllamaClient
from .playwright_manager import PlaywrightManager
from .rate_limiter import DomainRateLimiter
from .schema_service import SchemaService
from .utils import compact_text, normalize_url, optional_import_error
from .web_observer import WebObserver


class GraphManager:
    """Create and execute semantic extraction graphs with fallback handling."""

    def __init__(
        self,
        ollama_client: Optional[OllamaClient] = None,
        playwright_manager: Optional[PlaywrightManager] = None,
        schema_service: Optional[SchemaService] = None,
        observer: Optional[WebObserver] = None,
        rate_limiter: Optional[DomainRateLimiter] = None,
    ):
        self.ollama = ollama_client or OllamaClient()
        self.playwright = playwright_manager or PlaywrightManager()
        self.schemas = schema_service or SchemaService()
        self.observer = observer or WebObserver()
        self.rate_limiter = rate_limiter or DomainRateLimiter()
        self.metrics = {
            "smart_scraper_runs": 0,
            "search_graph_runs": 0,
            "fallback_runs": 0,
            "failures": 0,
            "last_duration_seconds": 0.0,
        }

    async def run_semantic_extract(
        self,
        url: str,
        prompt: str,
        schema: Optional[Any] = None,
    ) -> Dict[str, Any]:
        started = time.perf_counter()
        normalized_url = normalize_url(url)

        async with self.rate_limiter.limit(normalized_url):
            last_error = None
            for attempt in range(1, WEB_CONFIG["max_retries"] + 1):
                try:
                    result = await self._run_scrapegraph_smart_scraper(normalized_url, prompt, schema)
                    self.metrics["smart_scraper_runs"] += 1
                    self.metrics["last_duration_seconds"] = time.perf_counter() - started
                    return result
                except Exception as exc:
                    last_error = str(exc)
                    await asyncio.sleep((attempt - 1) * WEB_CONFIG["retry_backoff_seconds"])

            try:
                fallback_result = await self._run_local_semantic_extract(normalized_url, prompt, schema)
            except Exception as exc:
                fallback_result = {
                    "success": False,
                    "result": None,
                    "error": str(exc),
                    "metadata": {"strategy": "fallback_failed"},
                }
            self.metrics["fallback_runs"] += 1
            self.metrics["last_duration_seconds"] = time.perf_counter() - started
            if not fallback_result["success"]:
                self.metrics["failures"] += 1
                fallback_result["error"] = fallback_result.get("error") or last_error
            return fallback_result

    async def run_search_graph(
        self,
        query: str,
        prompt: str,
        urls: Iterable[str],
        schema: Optional[Any] = None,
    ) -> Dict[str, Any]:
        started = time.perf_counter()
        results = await asyncio.gather(
            *[
                self.run_semantic_extract(url=url, prompt=prompt, schema=schema)
                for url in urls
            ],
            return_exceptions=True,
        )
        self.metrics["search_graph_runs"] += 1
        self.metrics["last_duration_seconds"] = time.perf_counter() - started

        normalized_results = []
        for result in results:
            if isinstance(result, Exception):
                normalized_results.append({"success": False, "error": str(result), "result": None})
            else:
                normalized_results.append(result)

        return {
            "success": any(item.get("success") for item in normalized_results),
            "result": {
                "query": query,
                "results": normalized_results,
            },
            "error": None if any(item.get("success") for item in normalized_results) else "all extractions failed",
        }

    async def _run_scrapegraph_smart_scraper(
        self,
        url: str,
        prompt: str,
        schema: Optional[Any] = None,
    ) -> Dict[str, Any]:
        schema_cls = self.schemas.resolve(schema)

        try:
            from scrapegraphai.graphs import SmartScraperGraph
        except ImportError as exc:
            raise RuntimeError(f"ScrapeGraphAI unavailable: {exc}") from exc

        config = {
            "llm": {
                "model": f"ollama/{WEB_CONFIG['ollama_model']}",
                "base_url": WEB_CONFIG["ollama_base_url"],
                "model_tokens": 4096,
                "temperature": 0,
            },
            "headless": WEB_CONFIG["headless"],
            "verbose": False,
        }

        kwargs = {
            "prompt": prompt,
            "source": url,
            "config": config,
        }
        if schema_cls is not None:
            kwargs["schema"] = schema_cls

        graph = SmartScraperGraph(**kwargs)
        raw_result = await asyncio.to_thread(graph.run)
        payload = self.schemas.dump(raw_result)
        validated = self.schemas.validate(schema_cls, payload)
        observation = self.observer.assess(validated, schema_cls)
        return {
            "success": observation["success"],
            "result": self.schemas.dump(validated),
            "error": None if observation["success"] else f"observer rejected extraction: {observation['issues']}",
            "metadata": {
                "strategy": "scrapegraph_smart_scraper",
                "quality": observation,
            },
        }

    async def _run_local_semantic_extract(
        self,
        url: str,
        prompt: str,
        schema: Optional[Any] = None,
    ) -> Dict[str, Any]:
        schema_cls = self.schemas.resolve(schema)
        page = await self.playwright.fetch_page(url)
        text = self._html_to_text(page.html)
        text = compact_text(text, WEB_CONFIG["max_page_text_chars"])

        schema_json = self.schemas.json_schema(schema_cls)
        llm_prompt = (
            f"Extract structured information from the following webpage.\n"
            f"URL: {page.url}\n"
            f"Title: {page.title}\n"
            f"Instruction: {prompt}\n"
            f"Return only JSON matching the schema when provided.\n\n"
            f"CONTENT:\n{text}"
        )
        generation = self.ollama.generate(
            prompt=llm_prompt,
            format_schema=schema_json,
            options={"temperature": 0},
        )
        if not generation["success"]:
            return {
                "success": False,
                "result": None,
                "error": generation["error"],
                "metadata": {"strategy": page.backend},
            }

        response_text = (
            generation["result"].get("response")
            if isinstance(generation["result"], dict)
            else None
        )
        payload = self._parse_response_payload(response_text, page, prompt)
        validated = self.schemas.validate(schema_cls, payload) if schema_cls is not None else payload
        observation = self.observer.assess(validated, schema_cls)
        return {
            "success": observation["success"],
            "result": self.schemas.dump(validated),
            "error": None if observation["success"] else f"observer rejected extraction: {observation['issues']}",
            "metadata": {
                "strategy": page.backend,
                "quality": observation,
                "page_title": page.title,
            },
        }

    def _parse_response_payload(self, response_text: Optional[str], page: Any, prompt: str) -> Dict[str, Any]:
        if not response_text:
            return {
                "title": page.title,
                "summary": "",
                "key_points": [],
                "metadata": {"url": page.url, "prompt": prompt},
            }
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            return {
                "title": page.title,
                "summary": response_text,
                "key_points": [],
                "metadata": {"url": page.url, "prompt": prompt},
            }

    @staticmethod
    def _html_to_text(html: str) -> str:
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            import re

            stripped = re.sub(r"<[^>]+>", " ", html or "")
            return " ".join(stripped.split())

        soup = BeautifulSoup(html, "lxml")
        return soup.get_text(separator=" ", strip=True)
