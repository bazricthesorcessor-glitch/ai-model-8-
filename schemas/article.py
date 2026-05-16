from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class ArticleSummary(BaseModel):
    title: str = ""
    author: Optional[str] = None
    publication: Optional[str] = None
    published_at: Optional[str] = None
    summary: str = ""
    key_points: List[str] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)
    sentiment: Optional[str] = None
    source_url: Optional[HttpUrl] = None

