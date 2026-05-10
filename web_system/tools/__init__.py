"""
Web search and interaction tools.
Integrates web module with tools registry.
"""

from typing import Dict, Any, Optional
from tools.tool import Tool
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from web_system.core import WebInteractor


class WebSearchTool(Tool):
    """Search the web using multiple providers."""

    def __init__(self):
        super().__init__(
            name="web_search",
            platform="web",
            description="Search the web using APIs (SerpAPI, Google, Bing, DuckDuckGo, Brave)"
        )
        self.web = WebInteractor(backend="api", search_provider="serpapi")

    def validate_input(self, data: Dict[str, Any]) -> tuple:
        """Validate search input."""
        if not isinstance(data, dict):
            return False, "Input must be a dict"

        if "query" not in data:
            return False, "Missing required field: query"

        if not isinstance(data["query"], str) or not data["query"].strip():
            return False, "Query must be non-empty string"

        return True, ""

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute web search."""
        query = data["query"]
        num_results = data.get("num_results", 10)
        provider = data.get("provider", "serpapi")

        success, results, error = self.web.search(
            query,
            num_results=num_results,
            provider=provider
        )

        return {
            "success": success,
            "result": {
                "query": query,
                "provider": provider,
                "num_results": len(results) if results else 0,
                "results": [
                    {
                        "title": r.title,
                        "url": r.url,
                        "snippet": r.snippet,
                        "position": r.position,
                    }
                    for r in (results or [])
                ],
            },
            "error": error,
        }


class FetchPageTool(Tool):
    """Fetch and extract page content."""

    def __init__(self):
        super().__init__(
            name="fetch_page",
            platform="web",
            description="Fetch and extract content from a web page (text, links, images, metadata)"
        )
        self.web = WebInteractor(backend="scraper")

    def validate_input(self, data: Dict[str, Any]) -> tuple:
        """Validate fetch input."""
        if not isinstance(data, dict):
            return False, "Input must be a dict"

        if "url" not in data:
            return False, "Missing required field: url"

        if not isinstance(data["url"], str) or not data["url"].strip():
            return False, "URL must be non-empty string"

        return True, ""

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute page fetch."""
        url = data["url"]
        extract_links = data.get("extract_links", True)
        extract_images = data.get("extract_images", True)

        success, content, error = self.web.get_page_content(
            url,
            extract_links=extract_links,
            extract_images=extract_images
        )

        if not success:
            return {
                "success": False,
                "result": None,
                "error": error,
            }

        return {
            "success": True,
            "result": {
                "url": content.url,
                "title": content.title,
                "text_length": len(content.text),
                "text_preview": content.text[:500],
                "links_count": len(content.links),
                "images_count": len(content.images),
                "status_code": content.status_code,
                "metadata": content.metadata,
            },
            "error": None,
        }


class ExtractTextTool(Tool):
    """Extract text content from a page."""

    def __init__(self):
        super().__init__(
            name="extract_text",
            platform="web",
            description="Extract readable text from a web page"
        )
        self.web = WebInteractor(backend="scraper")

    def validate_input(self, data: Dict[str, Any]) -> tuple:
        """Validate input."""
        if not isinstance(data, dict):
            return False, "Input must be a dict"

        if "url" not in data:
            return False, "Missing required field: url"

        return True, ""

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute text extraction."""
        url = data["url"]

        success, text, error = self.web.extract_text(url)

        return {
            "success": success,
            "result": {
                "url": url,
                "text": text,
                "length": len(text) if text else 0,
            } if success else None,
            "error": error,
        }


class ExtractLinksTool(Tool):
    """Extract links from a page."""

    def __init__(self):
        super().__init__(
            name="extract_links",
            platform="web",
            description="Extract links from a web page"
        )
        self.web = WebInteractor(backend="scraper")

    def validate_input(self, data: Dict[str, Any]) -> tuple:
        """Validate input."""
        if not isinstance(data, dict):
            return False, "Input must be a dict"

        if "url" not in data:
            return False, "Missing required field: url"

        return True, ""

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute link extraction."""
        url = data["url"]
        internal_only = data.get("internal_only", False)

        success, links, error = self.web.extract_links(url, internal_only=internal_only)

        return {
            "success": success,
            "result": {
                "url": url,
                "links_count": len(links) if links else 0,
                "links": [
                    {
                        "text": l.text,
                        "url": l.url,
                        "is_internal": l.is_internal,
                    }
                    for l in (links or [])[:20]  # Limit to first 20
                ],
            } if success else None,
            "error": error,
        }


class BrowserNavigateTool(Tool):
    """Navigate to a URL in browser."""

    def __init__(self):
        super().__init__(
            name="browser_navigate",
            platform="web",
            description="Navigate to a URL in an automated browser"
        )
        self.web = WebInteractor(backend="browser")
        self.web.start_browser()

    def validate_input(self, data: Dict[str, Any]) -> tuple:
        """Validate input."""
        if not isinstance(data, dict):
            return False, "Input must be a dict"

        if "url" not in data:
            return False, "Missing required field: url"

        return True, ""

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute navigation."""
        url = data["url"]

        success, current_url, error = self.web.navigate(url)

        return {
            "success": success,
            "result": {
                "requested_url": url,
                "current_url": current_url,
            } if success else None,
            "error": error,
        }


class BrowserClickTool(Tool):
    """Click an element in the browser."""

    def __init__(self):
        super().__init__(
            name="browser_click",
            platform="web",
            description="Click an element in the browser by XPath or CSS selector"
        )
        self.web = WebInteractor(backend="browser")

    def validate_input(self, data: Dict[str, Any]) -> tuple:
        """Validate input."""
        if not isinstance(data, dict):
            return False, "Input must be a dict"

        if "selector" not in data:
            return False, "Missing required field: selector"

        return True, ""

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute click."""
        selector = data["selector"]
        by_type = data.get("by_type", "xpath")

        if not self.web.is_browser_active:
            self.web.start_browser()

        success, result, error = self.web.click(selector, by_type=by_type)

        return {
            "success": success,
            "result": {
                "selector": selector,
                "by_type": by_type,
                "message": result.message if result else None,
                "current_url": result.current_url if result else None,
            } if success else None,
            "error": error,
        }


class BrowserTypeTool(Tool):
    """Type text in a browser field."""

    def __init__(self):
        super().__init__(
            name="browser_type",
            platform="web",
            description="Type text into a form field in the browser"
        )
        self.web = WebInteractor(backend="browser")

    def validate_input(self, data: Dict[str, Any]) -> tuple:
        """Validate input."""
        if not isinstance(data, dict):
            return False, "Input must be a dict"

        required = ["selector", "text"]
        for field in required:
            if field not in data:
                return False, f"Missing required field: {field}"

        return True, ""

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute typing."""
        selector = data["selector"]
        text = data["text"]
        by_type = data.get("by_type", "xpath")
        clear_first = data.get("clear_first", True)

        if not self.web.is_browser_active:
            self.web.start_browser()

        success, result, error = self.web.type_text(
            selector,
            text,
            by_type=by_type,
            clear_first=clear_first
        )

        return {
            "success": success,
            "result": {
                "selector": selector,
                "text_length": len(text),
                "message": result.message if result else None,
            } if success else None,
            "error": error,
        }
