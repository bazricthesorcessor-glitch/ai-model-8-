from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class ResearchPaper(BaseModel):
    title: str = ""
    authors: List[str] = Field(default_factory=list)
    abstract: str = ""
    key_findings: List[str] = Field(default_factory=list)
    methods: List[str] = Field(default_factory=list)
    publication_year: Optional[int] = Field(default=None, ge=1900)
    venue: Optional[str] = None
    doi: Optional[str] = None
    paper_url: Optional[HttpUrl] = None

