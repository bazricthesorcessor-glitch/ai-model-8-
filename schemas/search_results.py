from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class SearchResultItem(BaseModel):
    title: str = ""
    url: HttpUrl
    snippet: str = ""
    position: int = Field(default=0, ge=0)
    source: Optional[str] = None


class SearchResultsPage(BaseModel):
    query: str
    provider: str
    results: List[SearchResultItem] = Field(default_factory=list)

