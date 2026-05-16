from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class PersonProfile(BaseModel):
    full_name: str = ""
    role: Optional[str] = None
    organization: Optional[str] = None
    location: Optional[str] = None
    bio: str = ""
    skills: List[str] = Field(default_factory=list)
    links: List[HttpUrl] = Field(default_factory=list)

