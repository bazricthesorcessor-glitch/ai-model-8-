from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class GithubRepository(BaseModel):
    name: str = ""
    owner: str = ""
    description: str = ""
    primary_language: Optional[str] = None
    stars: Optional[int] = Field(default=None, ge=0)
    forks: Optional[int] = Field(default=None, ge=0)
    topics: List[str] = Field(default_factory=list)
    license_name: Optional[str] = None
    default_branch: Optional[str] = None
    repo_url: Optional[HttpUrl] = None

