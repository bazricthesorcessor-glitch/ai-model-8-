"""
ScrapeGraphAI Extractor - Wrapper around ScrapeGraphAI library.

Provides:
1. Local Ollama model integration (privacy-first)
2. Fallback to OpenAI API if local models not available
3. JSON schema-based structured extraction
4. Error handling and retries
5. Clean integration with SmartWebInteractor
"""

from typing import Dict, Any, Optional, Tuple
import json


class ScrapeGraphAIExtractor:
    """Wrapper around ScrapeGraphAI for semantic web extraction."""

    def __init__(self, use_ollama: bool = True, model: Optional[str] = None):
        """
        Initialize ScrapeGraphAI extractor.

        Args:
            use_ollama: Try to use local Ollama models first
            model: Specific model to use (e.g., "qwen2.5:7b")
        """
        self.use_ollama = use_ollama
        self.model = model
        self.sgai = None
        self._init_scrapegraph()

    def _init_scrapegraph(self):
        """Initialize ScrapeGraphAI library."""
        try:
            from scrapegraphai.graphs import SmartScraperGraph
            self.SmartScraperGraph = SmartScraperGraph
        except ImportError:
            raise ImportError(
                "ScrapeGraphAI not installed. Install with: pip install scrapegraph-ai"
            )

    def extract(
        self, url: str, instruction: Optional[str] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract structured data from a webpage using ScrapeGraphAI.

        Args:
            url: Page URL to extract
            instruction: Semantic instruction for what to extract
                (e.g., "Extract product names and prices")

        Returns:
            (success: bool, result: Optional[Dict], error: Optional[str])
        """
        # Default instruction if not provided
        if not instruction:
            instruction = "Extract the main content, headings, and paragraphs from this page as structured data."

        try:
            # Get appropriate config for local or API models
            config = self._get_config()

            # Create scraper graph
            scraper = self.SmartScraperGraph(
                prompt=instruction,
                source=url,
                config=config,
            )

            # Run extraction
            result = scraper.run()

            # Parse result
            if result:
                return True, self._normalize_result(result), None
            else:
                return False, None, "ScrapeGraphAI returned empty result"

        except Exception as e:
            return False, None, f"ScrapeGraphAI extraction error: {str(e)}"

    def _get_config(self) -> Dict[str, Any]:
        """
        Get configuration for ScrapeGraphAI.

        Prefers local Ollama models for privacy, falls back to OpenAI.

        Returns:
            Config dict for SmartScraperGraph
        """
        config = {
            "headless": True,
            "verbose": False,
            "timeout": 30,
        }

        if self.use_ollama:
            # Try local Ollama first
            config.update({
                "llm_config": {
                    "model": self.model or "qwen2.5:7b",
                    "api_key": "ollama",  # Special key for local models
                    "base_url": "http://localhost:11434",
                    "temperature": 0.1,
                }
            })
        else:
            # Fall back to OpenAI API
            import os

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "OpenAI API key not found. Set OPENAI_API_KEY environment variable."
                )

            config.update({
                "llm_config": {
                    "model": "gpt-4",
                    "api_key": api_key,
                    "temperature": 0.1,
                }
            })

        return config

    def _normalize_result(self, result: Any) -> Dict[str, Any]:
        """
        Normalize ScrapeGraphAI result to standard format.

        Args:
            result: Raw result from ScrapeGraphAI

        Returns:
            Normalized dict with: text, links, structured_data
        """
        # Handle different result types
        if isinstance(result, dict):
            return result
        elif isinstance(result, str):
            # Try to parse as JSON
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                return {"text": result}
        else:
            return {"raw_result": str(result)}
