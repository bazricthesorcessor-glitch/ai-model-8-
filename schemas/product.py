from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class ProductInfo(BaseModel):
    name: str = ""
    brand: Optional[str] = None
    price: Optional[str] = None
    currency: Optional[str] = None
    availability: Optional[str] = None
    rating: Optional[float] = Field(default=None, ge=0.0, le=5.0)
    review_count: Optional[int] = Field(default=None, ge=0)
    description: str = ""
    features: List[str] = Field(default_factory=list)
    category: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    source_url: Optional[HttpUrl] = None

