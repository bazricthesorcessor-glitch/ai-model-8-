"""
Web tools for Elzyra.

This module keeps semantic extraction separate from UI/CDP browser control.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from tools.tool import Tool
from web import SCRAPE_SERVICE
from web_system.core.web import WebInteractor


class _SemanticWebTool(Tool):
    """Shared validation for semantic web tools."""

    required_fields: tuple[str, ...] = ()

    def validate_input(self, data: Dict[str, Any]) -> tuple[bool, str]:
        if not isinstance(data, dict):
            return False, "Input must be a dict"
        for field in self.required_fields:
            if field not in data or not data[field]:
                return False, f"Missing required field: {field}"
        return True, ""


class WebSearchTool(_SemanticWebTool):
    def __init__(self):
        super().__init__(
            name="web_search",
            platform="web",
            description="Search the web using API-backed search providers",
        )
        self.required_fields = ("query",)
        self.web = WebInteractor(backend="api", search_provider="duckduckgo")

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        success, results, error = self.web.search(
            data["query"],
            num_results=data.get("num_results", 10),
            provider=data.get("provider", "duckduckgo"),
        )
        return {
            "success": success,
            "result": {
                "query": data["query"],
                "results": [
                    {
                        "title": result.title,
                        "url": result.url,
                        "snippet": result.snippet,
                        "position": result.position,
                    }
                    for result in (results or [])
                ],
            } if success else None,
            "error": error,
        }


class FetchPageTool(_SemanticWebTool):
    def __init__(self):
        super().__init__(
            name="fetch_page",
            platform="web",
            description="Fetch page content with the legacy scraper backend",
        )
        self.required_fields = ("url",)
        self.web = WebInteractor(backend="scraper")

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        success, content, error = self.web.get_page_content(
            data["url"],
            extract_links=data.get("extract_links", True),
            extract_images=data.get("extract_images", True),
        )
        return {
            "success": success,
            "result": {
                "url": content.url,
                "title": content.title,
                "text": content.text,
                "metadata": content.metadata,
            } if success else None,
            "error": error,
        }


class ExtractTextTool(_SemanticWebTool):
    def __init__(self):
        super().__init__(
            name="extract_text",
            platform="web",
            description="Extract readable text from a page using the legacy scraper backend",
        )
        self.required_fields = ("url",)
        self.web = WebInteractor(backend="scraper")

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        success, text, error = self.web.extract_text(data["url"])
        return {
            "success": success,
            "result": {"url": data["url"], "text": text, "length": len(text or "")} if success else None,
            "error": error,
        }


class ExtractLinksTool(_SemanticWebTool):
    def __init__(self):
        super().__init__(
            name="extract_links",
            platform="web",
            description="Extract links from a page using the legacy scraper backend",
        )
        self.required_fields = ("url",)
        self.web = WebInteractor(backend="scraper")

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        success, links, error = self.web.extract_links(
            data["url"],
            internal_only=data.get("internal_only", False),
        )
        return {
            "success": success,
            "result": {
                "url": data["url"],
                "links": [
                    {"text": link.text, "url": link.url, "is_internal": link.is_internal}
                    for link in (links or [])
                ],
            } if success else None,
            "error": error,
        }


class SemanticExtractTool(_SemanticWebTool):
    def __init__(self):
        super().__init__(
            name="semantic_extract",
            platform="web",
            description="Semantically extract structured information from a webpage",
        )
        self.required_fields = ("url", "prompt")

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return SCRAPE_SERVICE.semantic_extract(
            url=data["url"],
            prompt=data["prompt"],
            schema=data.get("schema"),
        )


class SearchAndExtractTool(_SemanticWebTool):
    def __init__(self):
        super().__init__(
            name="search_and_extract",
            platform="web",
            description="Search for relevant pages and semantically extract them",
        )
        self.required_fields = ("query", "prompt")

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return SCRAPE_SERVICE.search_and_extract(
            query=data["query"],
            prompt=data["prompt"],
            limit=data.get("limit", 5),
            schema=data.get("schema"),
        )


class ExtractArticleTool(_SemanticWebTool):
    def __init__(self):
        super().__init__(
            name="extract_article",
            platform="web",
            description="Extract typed article information from a webpage",
        )
        self.required_fields = ("url",)

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return SCRAPE_SERVICE.extract_article(data["url"])


class ExtractProductTool(_SemanticWebTool):
    def __init__(self):
        super().__init__(
            name="extract_product",
            platform="web",
            description="Extract typed product information from a webpage",
        )
        self.required_fields = ("url",)

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return SCRAPE_SERVICE.extract_product(data["url"])


class ExtractResearchTool(_SemanticWebTool):
    def __init__(self):
        super().__init__(
            name="extract_research",
            platform="web",
            description="Extract typed research paper information from a webpage",
        )
        self.required_fields = ("url",)

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return SCRAPE_SERVICE.extract_research(data["url"])


class SummarizePageTool(_SemanticWebTool):
    def __init__(self):
        super().__init__(
            name="summarize_page",
            platform="web",
            description="Summarize a page into structured semantic output",
        )
        self.required_fields = ("url",)

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return SCRAPE_SERVICE.summarize_page(data["url"])


class BrowserNavigateTool(_SemanticWebTool):
    def __init__(self):
        super().__init__(
            name="browser_navigate",
            platform="web",
            description="Navigate to a URL in an automated browser backend",
        )
        self.required_fields = ("url",)
        self.web = WebInteractor(backend="browser")
        try:
            self.web.start_browser()
        except Exception:
            pass

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        success, current_url, error = self.web.navigate(data["url"])
        return {
            "success": success,
            "result": {"requested_url": data["url"], "current_url": current_url} if success else None,
            "error": error,
        }


class BrowserClickTool(_SemanticWebTool):
    def __init__(self):
        super().__init__(
            name="browser_click",
            platform="web",
            description="Click an element in the browser automation backend",
        )
        self.required_fields = ("selector",)
        self.web = WebInteractor(backend="browser")
        try:
            self.web.start_browser()
        except Exception:
            pass

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        success, result, error = self.web.click(data["selector"], by_type=data.get("by_type", "css"))
        return {"success": success, "result": result, "error": error}


class BrowserTypeTool(_SemanticWebTool):
    def __init__(self):
        super().__init__(
            name="browser_type",
            platform="web",
            description="Type text into an element in the browser automation backend",
        )
        self.required_fields = ("selector", "text")
        self.web = WebInteractor(backend="browser")
        try:
            self.web.start_browser()
        except Exception:
            pass

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        success, result, error = self.web.type_text(
            data["selector"],
            data["text"],
            by_type=data.get("by_type", "css"),
        )
        return {"success": success, "result": result, "error": error}


__all__ = [
    "BrowserClickTool",
    "BrowserNavigateTool",
    "BrowserTypeTool",
    "ExtractArticleTool",
    "ExtractLinksTool",
    "ExtractProductTool",
    "ExtractResearchTool",
    "ExtractTextTool",
    "FetchPageTool",
    "SearchAndExtractTool",
    "SemanticExtractTool",
    "SummarizePageTool",
    "WebSearchTool",
]
