from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ExtractionEnvelope(BaseModel):
    source_url: str = Field(default="", description="Source URL used for extraction")
    strategy: str = Field(default="", description="Extraction strategy used")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    warnings: List[str] = Field(default_factory=list)


class GenericExtraction(BaseModel):
    title: str = ""
    summary: str = ""
    key_points: List[str] = Field(default_factory=list)
    entities: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    raw_text_excerpt: Optional[str] = None

