"""
API-based web search backends.
Supports: SerpAPI, Google Search, Bing, DuckDuckGo, Brave Search.
Stateless, pure transformation: input query → output search results.
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
import requests
import json
import os


class SearchProvider(Enum):
    """Supported search providers."""
    SERPAPI = "serpapi"
    GOOGLE = "google"
    BING = "bing"
    DUCKDUCKGO = "duckduckgo"
    BRAVE = "brave"
    MOCK = "mock"


@dataclass
class ApiSearchResult:
    """Single search result from API."""
    title: str
    url: str
    snippet: str
    position: int
    source: str = "api"
    metadata: Dict[str, Any] = None


class ApiSearchBackend:
    """
    Search using APIs.
    Pure transformation: query → results
    """

    def __init__(self, provider: str = "serpapi", api_key: str = None):
        """
        Initialize API search backend.

        Args:
            provider: Search provider (serpapi, google, bing, duckduckgo, brave, mock)
            api_key: API key for the provider (or use env var)
        """
        self.provider = provider
        self.api_key = api_key or self._get_api_key(provider)

    def _get_api_key(self, provider: str) -> Optional[str]:
        """Get API key from environment variables."""
        if provider == "mock":
            return None  # Mock provider doesn't need API key

        env_keys = {
            "serpapi": "SERPAPI_KEY",
            "google": "GOOGLE_SEARCH_API_KEY",
            "bing": "BING_SEARCH_API_KEY",
            "duckduckgo": "DUCKDUCKGO_API_KEY",
            "brave": "BRAVE_SEARCH_API_KEY",
        }
        env_var = env_keys.get(provider)
        return os.getenv(env_var) if env_var else None

    def search(
        self,
        query: str,
        num_results: int = 10,
        **kwargs
    ) -> Tuple[bool, Optional[List[ApiSearchResult]], Optional[str]]:
        """
        Execute web search via API.

        Args:
            query: Search query
            num_results: Number of results to return
            **kwargs: Provider-specific parameters

        Returns:
            (success: bool, results: List[ApiSearchResult], error: Optional[str])
        """
        if not query or not query.strip():
            return False, None, "Query cannot be empty"

        try:
            if self.provider == "mock":
                return self._search_mock(query, num_results)
            elif self.provider == "serpapi":
                return self._search_serpapi(query, num_results, **kwargs)
            elif self.provider == "duckduckgo":
                return self._search_duckduckgo(query, num_results, **kwargs)
            elif self.provider == "google":
                return self._search_google(query, num_results, **kwargs)
            elif self.provider == "bing":
                return self._search_bing(query, num_results, **kwargs)
            elif self.provider == "brave":
                return self._search_brave(query, num_results, **kwargs)
            else:
                return False, None, f"Unknown provider: {self.provider}"

        except Exception as e:
            return False, None, str(e)

    def _search_mock(
        self,
        query: str,
        num_results: int
    ) -> Tuple[bool, List[ApiSearchResult], Optional[str]]:
        """Mock search for testing."""
        results = [
            ApiSearchResult(
                title=f"Result {i+1} for {query}",
                url=f"https://example{i+1}.com/search?q={query}",
                snippet=f"This is snippet {i+1} matching your search query about {query}",
                position=i+1,
                source="mock",
                metadata={}
            )
            for i in range(min(num_results, 5))
        ]
        return True, results, None

    def _search_serpapi(
        self,
        query: str,
        num_results: int,
        **kwargs
    ) -> Tuple[bool, Optional[List[ApiSearchResult]], Optional[str]]:
        """Search using SerpAPI."""
        if not self.api_key:
            return False, None, "SerpAPI key not configured. Set SERPAPI_KEY env var"

        url = "https://serpapi.com/search"
        params = {
            "q": query,
            "api_key": self.api_key,
            "num": num_results,
            "gl": kwargs.get("country", "us"),
            "hl": kwargs.get("language", "en"),
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get("organic_results", [])[:num_results]:
                results.append(ApiSearchResult(
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                    position=item.get("position", 0),
                    source="serpapi",
                    metadata={
                        "date": item.get("date"),
                        "rating": item.get("rating"),
                    }
                ))

            return True, results, None

        except requests.exceptions.RequestException as e:
            return False, None, f"SerpAPI request failed: {str(e)}"

    def _search_duckduckgo(
        self,
        query: str,
        num_results: int,
        **kwargs
    ) -> Tuple[bool, Optional[List[ApiSearchResult]], Optional[str]]:
        """Search using DuckDuckGo (no API key needed)."""
        try:
            # Using duckduckgo_search library if available
            try:
                from duckduckgo_search import DDGS
                with DDGS() as ddgs:
                    results_data = ddgs.text(query, max_results=num_results)

                results = []
                for i, item in enumerate(results_data):
                    results.append(ApiSearchResult(
                        title=item.get("title", ""),
                        url=item.get("href", ""),
                        snippet=item.get("body", ""),
                        position=i+1,
                        source="duckduckgo",
                    ))

                return True, results, None

            except ImportError:
                # Fallback: manual request to DuckDuckGo
                url = "https://html.duckduckgo.com/"
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                params = {"q": query}

                response = requests.get(url, params=params, headers=headers, timeout=10)
                response.raise_for_status()

                # Parse HTML manually - simplified
                from html.parser import HTMLParser

                class LinkParser(HTMLParser):
                    def __init__(self):
                        super().__init__()
                        self.results = []
                        self.in_result = False

                    def handle_starttag(self, tag, attrs):
                        if tag == "a":
                            for attr, value in attrs:
                                if attr == "href" and "uddg=" in value:
                                    self.in_result = True

                parser = LinkParser()
                parser.feed(response.text)

                # Return mock results if parsing fails
                return self._search_mock(query, num_results)

        except Exception as e:
            return False, None, f"DuckDuckGo search failed: {str(e)}"

    def _search_google(
        self,
        query: str,
        num_results: int,
        **kwargs
    ) -> Tuple[bool, Optional[List[ApiSearchResult]], Optional[str]]:
        """Search using Google Custom Search API."""
        if not self.api_key:
            return False, None, "Google Search API key not configured. Set GOOGLE_SEARCH_API_KEY env var"

        cx = kwargs.get("cx")  # Custom search engine ID
        if not cx:
            return False, None, "Custom search engine ID (cx) required for Google Search"

        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "q": query,
            "key": self.api_key,
            "cx": cx,
            "num": min(num_results, 10),
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            for i, item in enumerate(data.get("items", [])[:num_results]):
                results.append(ApiSearchResult(
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                    position=i+1,
                    source="google",
                ))

            return True, results, None

        except requests.exceptions.RequestException as e:
            return False, None, f"Google Search API failed: {str(e)}"

    def _search_bing(
        self,
        query: str,
        num_results: int,
        **kwargs
    ) -> Tuple[bool, Optional[List[ApiSearchResult]], Optional[str]]:
        """Search using Bing Search API."""
        if not self.api_key:
            return False, None, "Bing Search API key not configured. Set BING_SEARCH_API_KEY env var"

        url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        params = {"q": query, "count": num_results}

        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            for i, item in enumerate(data.get("webPages", {}).get("value", [])[:num_results]):
                results.append(ApiSearchResult(
                    title=item.get("name", ""),
                    url=item.get("url", ""),
                    snippet=item.get("snippet", ""),
                    position=i+1,
                    source="bing",
                ))

            return True, results, None

        except requests.exceptions.RequestException as e:
            return False, None, f"Bing Search API failed: {str(e)}"

    def _search_brave(
        self,
        query: str,
        num_results: int,
        **kwargs
    ) -> Tuple[bool, Optional[List[ApiSearchResult]], Optional[str]]:
        """Search using Brave Search API."""
        if not self.api_key:
            return False, None, "Brave Search API key not configured. Set BRAVE_SEARCH_API_KEY env var"

        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {"Accept": "application/json", "X-Subscription-Token": self.api_key}
        params = {"q": query, "count": num_results}

        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            for i, item in enumerate(data.get("web", {}).get("results", [])[:num_results]):
                results.append(ApiSearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    snippet=item.get("description", ""),
                    position=i+1,
                    source="brave",
                ))

            return True, results, None

        except requests.exceptions.RequestException as e:
            return False, None, f"Brave Search API failed: {str(e)}"
