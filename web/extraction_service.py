"""Typed extraction primitives built on top of the graph manager."""

from __future__ import annotations

from typing import Any, Dict, Optional

from schemas import ArticleSummary, GithubRepository, PersonProfile, ProductInfo, ResearchPaper


class ExtractionService:
    """Small composable extraction helpers for common content types."""

    def __init__(self, scrape_service: Any):
        self.scrape_service = scrape_service

    def extract_article(self, url: str) -> Dict[str, Any]:
        prompt = "Extract the article title, author, publication, publication date, concise summary, key points, and main topics."
        return self.scrape_service.semantic_extract(url, prompt, schema=ArticleSummary)

    def extract_product(self, url: str) -> Dict[str, Any]:
        prompt = "Extract the product name, brand, pricing, availability, rating, description, major features, category, and canonical source URL."
        return self.scrape_service.semantic_extract(url, prompt, schema=ProductInfo)

    def extract_research(self, url: str) -> Dict[str, Any]:
        prompt = "Extract the paper title, authors, abstract, methods, key findings, publication year, venue, DOI, and paper URL."
        return self.scrape_service.semantic_extract(url, prompt, schema=ResearchPaper)

    def extract_person(self, url: str) -> Dict[str, Any]:
        prompt = "Extract the person's full name, role, organization, location, biography, skills, and relevant public links."
        return self.scrape_service.semantic_extract(url, prompt, schema=PersonProfile)

    def extract_github_repo(self, url: str) -> Dict[str, Any]:
        prompt = "Extract the repository name, owner, description, primary language, stars, forks, topics, license, default branch, and canonical repo URL."
        return self.scrape_service.semantic_extract(url, prompt, schema=GithubRepository)

    def summarize_page(self, url: str) -> Dict[str, Any]:
        prompt = "Summarize the page clearly, extract the main points, and return a concise structured summary."
        return self.scrape_service.semantic_extract(url, prompt, schema="generic")

