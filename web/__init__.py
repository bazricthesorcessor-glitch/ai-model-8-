"""Elzyra semantic web extraction subsystem."""

from router import register_service

from .cache import WebCache
from .graph_manager import GraphManager
from .ollama_client import OllamaClient
from .playwright_manager import PageLoadResult, PlaywrightManager
from .schema_service import SchemaService
from .scrape_service import SemanticScrapeService, web_service
from .search_service import SearchService
from .web_observer import WebObserver

SCRAPE_SERVICE = SemanticScrapeService()


def semantic_extract(url: str, prompt: str, schema=None):
    return SCRAPE_SERVICE.semantic_extract(url, prompt, schema=schema)


def search_and_extract(query: str, prompt: str, limit: int = 5, schema=None):
    return SCRAPE_SERVICE.search_and_extract(query, prompt, limit=limit, schema=schema)


def extract_article(url: str):
    return SCRAPE_SERVICE.extract_article(url)


def extract_product(url: str):
    return SCRAPE_SERVICE.extract_product(url)


def extract_research(url: str):
    return SCRAPE_SERVICE.extract_research(url)


def summarize_page(url: str):
    return SCRAPE_SERVICE.summarize_page(url)


register_service("web", lambda message: web_service(message, service=SCRAPE_SERVICE))

__all__ = [
    "SCRAPE_SERVICE",
    "GraphManager",
    "OllamaClient",
    "PageLoadResult",
    "PlaywrightManager",
    "SchemaService",
    "SearchService",
    "SemanticScrapeService",
    "WebCache",
    "WebObserver",
    "extract_article",
    "extract_product",
    "extract_research",
    "search_and_extract",
    "semantic_extract",
    "summarize_page",
]

