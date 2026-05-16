"""Search primitives for the semantic web subsystem."""

from __future__ import annotations

from typing import Any, Dict, Optional

from config.web import WEB_CONFIG
from schemas import SearchResultItem, SearchResultsPage


class SearchService:
    """Search the web using the existing API backend infrastructure."""

    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or WEB_CONFIG["search_provider"]

    def search(
        self,
        query: str,
        limit: int = 5,
        provider: Optional[str] = None,
    ) -> Dict[str, Any]:
        from web_system.core.api_backend import ApiSearchBackend

        backend = ApiSearchBackend(provider=provider or self.provider)
        success, results, error = backend.search(query, num_results=limit)
        if not success:
            return {"success": False, "result": None, "error": error}

        page = SearchResultsPage(
            query=query,
            provider=provider or self.provider,
            results=[
                SearchResultItem(
                    title=result.title,
                    url=result.url,
                    snippet=result.snippet,
                    position=result.position,
                    source=result.source,
                )
                for result in (results or [])
            ],
        )
        return {"success": True, "result": page, "error": None}

