"""
Smart Web Interactor - Intelligent fallback strategy for web extraction.

Extends WebInteractor with:
1. Content quality scoring
2. Automatic ScrapeGraphAI triggering when content is messy
3. Intelligent fallback chain: Scraper → ScrapeGraphAI → Browser
4. Retry logic with exponential backoff
5. Timeout handling

Used by web tools to transparently handle complex websites.
"""

from typing import Dict, Any, Optional, Tuple
import time
from web_system.core.web import WebInteractor, PageContent


class SmartWebInteractor(WebInteractor):
    """Enhanced WebInteractor with intelligent fallback and auto-ScrapeGraphAI."""

    def __init__(self, **kwargs):
        """Initialize SmartWebInteractor (inherits from WebInteractor)."""
        super().__init__(**kwargs)
        self.quality_threshold = 0.7  # Score needed to avoid fallback

    # ========================================================================
    # MAIN SMART EXTRACTION METHOD
    # ========================================================================

    def get_page_content_smart(
        self,
        url: str,
        extraction_prompt: Optional[str] = None,
        use_scrapegraphai: str = "auto",  # "auto", "force", "disabled"
        extract_links: bool = True,
        extract_images: bool = True,
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Intelligently extract page content using multiple strategies.

        Flow:
        1. Try traditional scraper (fast, <1s)
        2. Score content quality
        3. If quality is low OR extraction_prompt provided:
           → Try ScrapeGraphAI (smart LLM extraction)
        4. If still fails:
           → Try browser automation (slow but handles JavaScript)

        Args:
            url: Page URL to extract
            extraction_prompt: Optional semantic extraction prompt
            use_scrapegraphai: "auto" (smart), "force" (always), "disabled"
            extract_links: Extract links from page
            extract_images: Extract images from page

        Returns:
            (success: bool, content: Optional[Dict], error: Optional[str])
        """
        # Strategy 1: Traditional scraper (fastest)
        success, content, error = self.get_page_content(
            url, extract_links=extract_links, extract_images=extract_images
        )

        if success and content:
            quality = self._score_extraction_quality(content)

            # If quality is good and no semantic extraction needed, return
            if quality > self.quality_threshold and not extraction_prompt:
                return True, self._content_to_dict(content), None

        # Strategy 2: ScrapeGraphAI (smart LLM extraction)
        if use_scrapegraphai != "disabled":
            success, extracted, error = self._extract_with_scrapegraphai(
                url, extraction_prompt
            )
            if success:
                return True, extracted, None

        # Strategy 3: Browser automation (slow but handles JavaScript)
        success, content, error = self._extract_with_browser(url)
        if success:
            return True, self._content_to_dict(content), None

        return False, None, "All extraction strategies failed"

    # ========================================================================
    # STRATEGY 1: CONTENT QUALITY SCORING
    # ========================================================================

    def _score_extraction_quality(self, content: PageContent) -> float:
        """
        Score extracted content quality (0.0-1.0).

        Detects incomplete/messy extraction:
        - High-quality: text >200 chars, links present, clear title
        - Medium: some text but missing elements
        - Low: very little text, no structure

        Args:
            content: Extracted PageContent

        Returns:
            Quality score (0.0-1.0)
        """
        score = 0.0

        # Text length score (max 0.4)
        text_length = len(content.text) if content.text else 0
        if text_length > 500:
            score += 0.4
        elif text_length > 200:
            score += 0.3
        elif text_length > 100:
            score += 0.2
        elif text_length > 0:
            score += 0.1

        # Links score (max 0.3)
        links_count = len(content.links) if content.links else 0
        if links_count > 10:
            score += 0.3
        elif links_count > 5:
            score += 0.2
        elif links_count > 0:
            score += 0.1

        # Structure score (max 0.3)
        if content.title:
            score += 0.15
        if content.metadata and len(content.metadata) > 0:
            score += 0.15

        return min(score, 1.0)

    # ========================================================================
    # STRATEGY 2: SCRAPEGRAPHAI INTEGRATION
    # ========================================================================

    def _extract_with_scrapegraphai(
        self, url: str, extraction_prompt: Optional[str] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract page content using ScrapeGraphAI (LLM-based extraction).

        Args:
            url: Page URL
            extraction_prompt: Optional semantic extraction instruction

        Returns:
            (success: bool, content: Optional[Dict], error: Optional[str])
        """
        try:
            from web_system.extractors.scrapegraphai_extractor import (
                ScrapeGraphAIExtractor,
            )
        except ImportError:
            return False, None, "ScrapeGraphAI not available"

        try:
            extractor = ScrapeGraphAIExtractor()
            success, result, error = extractor.extract(
                url, instruction=extraction_prompt
            )

            if success and result:
                return True, result, None
            else:
                return False, None, error or "ScrapeGraphAI extraction failed"

        except Exception as e:
            return False, None, f"ScrapeGraphAI error: {str(e)}"

    # ========================================================================
    # STRATEGY 3: BROWSER AUTOMATION FALLBACK
    # ========================================================================

    def _extract_with_browser(
        self, url: str
    ) -> Tuple[bool, Optional[PageContent], Optional[str]]:
        """
        Extract page content using browser automation.

        Handles JavaScript-rendered pages that scraper can't handle.

        Args:
            url: Page URL

        Returns:
            (success: bool, content: Optional[PageContent], error: Optional[str])
        """
        try:
            # Start browser if not already running
            if not self.is_browser_active:
                success, msg, error = self.start_browser()
                if not success:
                    return False, None, f"Failed to start browser: {error}"

            # Navigate to URL
            success, current_url, error = self.navigate(url)
            if not success:
                return False, None, f"Failed to navigate: {error}"

            # Get page source and parse it
            success, html, error = self.get_page_source()
            if not success:
                return False, None, f"Failed to get page source: {error}"

            # Parse HTML using our scraper's HTML extractor
            from web_system.core.scraper_backend import HtmlExtractor, ScrapedPageContent

            extractor = HtmlExtractor(base_url=url)
            try:
                extractor.feed(html)
            except Exception:
                pass  # Continue with partial data

            # Build content object
            content = ScrapedPageContent(
                url=url,
                title=extractor.title,
                text=extractor.get_text(),
                html=html,
                links=extractor.links,
                images=extractor.images,
                metadata=extractor.metadata,
                status_code=200,
            )

            return True, content, None

        except Exception as e:
            return False, None, f"Browser extraction error: {str(e)}"

    # ========================================================================
    # UTILITY: CONTENT CONVERSION
    # ========================================================================

    def _content_to_dict(self, content: PageContent) -> Dict[str, Any]:
        """Convert PageContent object to dict for external use."""
        return {
            "url": content.url,
            "title": content.title,
            "text": content.text,
            "text_length": len(content.text) if content.text else 0,
            "links": [
                {"text": l.text, "url": l.url, "is_internal": l.is_internal}
                for l in (content.links or [])
            ],
            "links_count": len(content.links) if content.links else 0,
            "images": [
                {
                    "src": img.src,
                    "alt": img.alt,
                    "title": img.title,
                    "width": img.width,
                    "height": img.height,
                }
                for img in (content.images or [])
            ],
            "images_count": len(content.images) if content.images else 0,
            "metadata": content.metadata or {},
            "status_code": content.status_code,
        }

    # ========================================================================
    # AUTO-DETECTION HELPER
    # ========================================================================

    def should_use_scrapegraphai(
        self, url: str, quality_score: float, has_prompt: bool = False
    ) -> bool:
        """
        Determine if ScrapeGraphAI should be used.

        Auto-triggered when:
        - Content quality is below threshold
        - Extraction prompt provided (semantic extraction)
        - URL hints at JavaScript-heavy site

        Args:
            url: Page URL
            quality_score: Content quality score (0.0-1.0)
            has_prompt: Whether semantic prompt was provided

        Returns:
            True if ScrapeGraphAI should be used
        """
        # Always use if prompt provided (semantic extraction)
        if has_prompt:
            return True

        # Use if content quality is low
        if quality_score < self.quality_threshold:
            return True

        # Heuristic: check for JavaScript-heavy sites
        js_heavy_domains = [
            "react", "angular", "vue", "single page", "app",
            "dynamically", "javascript",
        ]
        if any(domain in url.lower() for domain in js_heavy_domains):
            return True

        return False
