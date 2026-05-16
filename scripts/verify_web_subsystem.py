#!/usr/bin/env python3
"""Verify the semantic web subsystem imports and core wiring."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DEFAULT_OLLAMA_MODEL, endpoint_of
from schemas import ArticleSummary, ProductInfo
from web import SCRAPE_SERVICE


def main() -> int:
    print("Semantic web subsystem verification")
    print(f"  default model: {DEFAULT_OLLAMA_MODEL}")
    print(f"  ollama endpoint: {endpoint_of('ollama')}")
    print(f"  cache endpoint: {endpoint_of('web_cache')}")
    print(f"  schemas: {ArticleSummary.__name__}, {ProductInfo.__name__}")
    print(f"  cache stats: {SCRAPE_SERVICE.cache.stats()}")
    print("  status: import and wiring OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
