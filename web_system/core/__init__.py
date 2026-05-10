"""
Web System Core - Internet access, web search, and browser automation.
Enables API-based search, web scraping, and human-like browser interactions.
Integrates with vision module for understanding pages and keyboard/mouse for interactions.
"""

from .web import (
    WebInteractor,
    SearchResult,
    PageContent,
    InteractionResult,
    WebBackend,
)
from .api_backend import ApiSearchBackend, SearchProvider, ApiSearchResult
from .scraper_backend import ScraperBackend, ScrapedPageContent, PageLink, PageImage
from .browser_backend import BrowserAutomationBackend, BrowserType, BrowserState

__all__ = [
    # Main interface
    "WebInteractor",
    "SearchResult",
    "PageContent",
    "InteractionResult",
    "WebBackend",
    # API backend
    "ApiSearchBackend",
    "SearchProvider",
    "ApiSearchResult",
    # Scraper backend
    "ScraperBackend",
    "ScrapedPageContent",
    "PageLink",
    "PageImage",
    # Browser backend
    "BrowserAutomationBackend",
    "BrowserType",
    "BrowserState",
]
