"""Structured extraction schemas for Elzyra's semantic web subsystem."""

from .article import ArticleSummary
from .generic import ExtractionEnvelope, GenericExtraction
from .github_repo import GithubRepository
from .person import PersonProfile
from .product import ProductInfo
from .research import ResearchPaper
from .search_results import SearchResultItem, SearchResultsPage

SCHEMA_REGISTRY = {
    "article": ArticleSummary,
    "generic": GenericExtraction,
    "github_repo": GithubRepository,
    "person": PersonProfile,
    "product": ProductInfo,
    "research": ResearchPaper,
    "search_results": SearchResultsPage,
}

__all__ = [
    "ArticleSummary",
    "ExtractionEnvelope",
    "GenericExtraction",
    "GithubRepository",
    "PersonProfile",
    "ProductInfo",
    "ResearchPaper",
    "SearchResultItem",
    "SearchResultsPage",
    "SCHEMA_REGISTRY",
]

