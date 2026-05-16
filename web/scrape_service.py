"""Main semantic extraction interface for Elzyra."""

from __future__ import annotations

from typing import Any, Dict, Iterable, Optional

from router.message import Message, Response

from config.web import WEB_CONFIG
from .cache import WebCache
from .extraction_service import ExtractionService
from .graph_manager import GraphManager
from .schema_service import SchemaService
from .search_service import SearchService
from .utils import cache_key_for, run_sync
from .web_observer import WebObserver


class SemanticScrapeService:
    """Production-facing semantic web extraction subsystem."""

    def __init__(
        self,
        graph_manager: Optional[GraphManager] = None,
        search_service: Optional[SearchService] = None,
        schema_service: Optional[SchemaService] = None,
        observer: Optional[WebObserver] = None,
        cache: Optional[WebCache] = None,
    ):
        self.schemas = schema_service or SchemaService()
        self.observer = observer or WebObserver()
        self.cache = cache or WebCache()
        self.graphs = graph_manager or GraphManager(schema_service=self.schemas, observer=self.observer)
        self.search = search_service or SearchService()
        self.extractors = ExtractionService(self)

    def semantic_extract(
        self,
        url: str,
        prompt: str,
        schema: Optional[Any] = None,
    ) -> Dict[str, Any]:
        key = cache_key_for("semantic_extract", url, prompt, self.schemas.schema_name(schema))
        cached = self._cache_get(key)
        if cached:
            return cached

        result = run_sync(self.graphs.run_semantic_extract(url=url, prompt=prompt, schema=schema))
        self._cache_set(key, result)
        return result

    def search_and_extract(
        self,
        query: str,
        prompt: str,
        limit: int = 5,
        schema: Optional[Any] = None,
    ) -> Dict[str, Any]:
        search_result = self.search.search(query=query, limit=limit)
        if not search_result["success"]:
            return search_result

        urls = [str(item.url) for item in search_result["result"].results]
        result = run_sync(self.graphs.run_search_graph(query=query, prompt=prompt, urls=urls, schema=schema))
        result["result"]["search_results"] = search_result["result"].model_dump()
        return result

    def extract_multiple(
        self,
        urls: Iterable[str],
        prompt: str,
        schema: Optional[Any] = None,
    ) -> Dict[str, Any]:
        result = run_sync(self.graphs.run_search_graph(query="multiple", prompt=prompt, urls=list(urls), schema=schema))
        return result

    def extract_article(self, url: str) -> Dict[str, Any]:
        return self.extractors.extract_article(url)

    def extract_product(self, url: str) -> Dict[str, Any]:
        return self.extractors.extract_product(url)

    def extract_research(self, url: str) -> Dict[str, Any]:
        return self.extractors.extract_research(url)

    def summarize_page(self, url: str) -> Dict[str, Any]:
        return self.extractors.summarize_page(url)

    def _cache_get(self, key: str) -> Optional[Dict[str, Any]]:
        if not WEB_CONFIG["cache_enabled"]:
            return None
        cached = self.cache.get(key)
        if isinstance(cached, dict):
            return cached
        return None

    def _cache_set(self, key: str, value: Dict[str, Any]) -> None:
        if WEB_CONFIG["cache_enabled"] and value.get("success"):
            self.cache.set(key, value)


def web_service(message: Message, service: Optional[SemanticScrapeService] = None) -> Response:
    """Router bridge for the semantic web subsystem."""
    service = service or SemanticScrapeService()
    action = message.payload.get("action")
    data = message.payload.get("data", {})

    handlers = {
        "semantic_extract": lambda: service.semantic_extract(
            url=data.get("url", ""),
            prompt=data.get("prompt", ""),
            schema=data.get("schema"),
        ),
        "search_and_extract": lambda: service.search_and_extract(
            query=data.get("query", ""),
            prompt=data.get("prompt", ""),
            limit=data.get("limit", WEB_CONFIG["default_result_limit"]),
            schema=data.get("schema"),
        ),
        "extract_article": lambda: service.extract_article(data.get("url", "")),
        "extract_product": lambda: service.extract_product(data.get("url", "")),
        "extract_research": lambda: service.extract_research(data.get("url", "")),
        "summarize_page": lambda: service.summarize_page(data.get("url", "")),
    }

    if action not in handlers:
        return Response(
            source="web",
            success=False,
            error=f"unknown web action: {action}. Available: {sorted(handlers)}",
        )

    try:
        result = handlers[action]()
        return Response(
            source="web",
            success=result.get("success", False),
            result=result,
            error=result.get("error"),
        )
    except Exception as exc:
        return Response(
            source="web",
            success=False,
            error=f"web service error: {exc}",
        )

