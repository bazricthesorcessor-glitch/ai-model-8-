"""
Web Interaction Module - Complete internet access and web automation.
Integrates: API search, web scraping, browser automation, vision, keyboard/mouse.
Pure transformation: inputs → structured data.
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import time

from .api_backend import ApiSearchBackend, ApiSearchResult, SearchProvider
from .scraper_backend import ScraperBackend, ScrapedPageContent, PageLink, PageImage
from .browser_backend import BrowserAutomationBackend, BrowserState


class WebBackend(Enum):
    """Supported web backends."""
    MOCK = "mock"
    API = "api"
    SCRAPER = "scraper"
    BROWSER = "browser"


@dataclass
class SearchResult:
    """Search result from any source."""
    title: str
    url: str
    snippet: str
    position: int
    source: str = "api"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PageContent:
    """Extracted page content from any source."""
    url: str
    title: str
    text: str
    links: List[PageLink] = field(default_factory=list)
    images: List[PageImage] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    status_code: int = 200
    source: str = "scraper"


@dataclass
class InteractionResult:
    """Result of browser interaction."""
    success: bool
    action: str
    message: str
    current_url: Optional[str] = None
    page_title: Optional[str] = None
    screenshot_path: Optional[str] = None
    duration_ms: float = 0.0


class WebInteractor:
    """
    Main web interaction module.
    Unified interface for:
    - Web search (multiple API providers)
    - Web scraping (page content extraction)
    - Browser automation (human-like interactions)
    - Vision integration (page understanding)
    - Keyboard/mouse control (UI automation)
    """

    def __init__(
        self,
        backend: str = "mock",
        search_provider: str = "serpapi",
        browser_type: str = "chrome",
        headless: bool = True
    ):
        """
        Initialize web interactor.

        Args:
            backend: Primary backend (mock, api, scraper, browser)
            search_provider: Search provider for API (serpapi, google, bing, duckduckgo, brave)
            browser_type: Browser type (chrome, firefox, edge, safari)
            headless: Run browser in headless mode
        """
        self.backend = backend
        self.search_provider = search_provider
        self.browser_type = browser_type

        # Initialize backends
        self.api_backend = ApiSearchBackend(provider=search_provider)
        self.scraper_backend = ScraperBackend()
        self.browser_backend = BrowserAutomationBackend(
            browser_type=browser_type,
            headless=headless
        )

        # State tracking
        self.is_browser_active = False
        self.last_operation_time = 0.0

    # ========================================================================
    # WEB SEARCH
    # ========================================================================

    def search(
        self,
        query: str,
        num_results: int = 10,
        provider: Optional[str] = None,
        **kwargs
    ) -> Tuple[bool, Optional[List[SearchResult]], Optional[str]]:
        """
        Search the web using API.

        Args:
            query: Search query
            num_results: Number of results to return
            provider: Override default search provider
            **kwargs: Provider-specific options

        Returns:
            (success: bool, results: Optional[List[SearchResult]], error: Optional[str])
        """
        start_time = time.time()

        try:
            if not query or not query.strip():
                return False, None, "Query cannot be empty"

            # Use specified provider or default
            provider_name = provider or self.search_provider

            # For mock backend, return mock results
            if self.backend == "mock":
                results = [
                    SearchResult(
                        title=f"Result {i+1}: {query}",
                        url=f"https://example{i+1}.com/search?q={query}",
                        snippet=f"Snippet for result {i+1} about {query}",
                        position=i+1
                    )
                    for i in range(min(num_results, 5))
                ]
                self._record_operation(start_time)
                return True, results, None

            # Use API backend
            success, api_results, error = self.api_backend.search(
                query,
                num_results=num_results,
                **kwargs
            )

            if not success:
                return False, None, error

            # Convert ApiSearchResult to SearchResult
            results = [
                SearchResult(
                    title=r.title,
                    url=r.url,
                    snippet=r.snippet,
                    position=r.position,
                    source=r.source,
                    metadata=r.metadata or {}
                )
                for r in api_results
            ]

            self._record_operation(start_time)
            return True, results, None

        except Exception as e:
            return False, None, str(e)

    # ========================================================================
    # WEB SCRAPING
    # ========================================================================

    def get_page_content(
        self,
        url: str,
        extract_links: bool = True,
        extract_images: bool = True
    ) -> Tuple[bool, Optional[PageContent], Optional[str]]:
        """
        Fetch and extract page content.

        Args:
            url: Page URL
            extract_links: Extract links from page
            extract_images: Extract images from page

        Returns:
            (success: bool, content: Optional[PageContent], error: Optional[str])
        """
        start_time = time.time()

        try:
            if not url or not url.strip():
                return False, None, "URL cannot be empty"

            if self.backend == "mock":
                content = PageContent(
                    url=url,
                    title="Mock Page",
                    text="This is mock page content",
                    links=[],
                    images=[],
                )
                self._record_operation(start_time)
                return True, content, None

            # Use scraper backend
            success, page, error = self.scraper_backend.fetch_page(url)
            if not success:
                return False, None, error

            # Convert to PageContent
            content = PageContent(
                url=page.url,
                title=page.title,
                text=page.text,
                links=page.links if extract_links else [],
                images=page.images if extract_images else [],
                metadata={
                    "status_code": page.status_code,
                    "html_size": len(page.html),
                    "text_length": len(page.text),
                    "timestamp": page.timestamp,
                    "page_metadata": page.metadata,
                },
                status_code=page.status_code,
                source="scraper"
            )

            self._record_operation(start_time)
            return True, content, None

        except Exception as e:
            return False, None, str(e)

    def extract_text(
        self,
        url: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Extract just the text from a page.

        Args:
            url: Page URL

        Returns:
            (success: bool, text: Optional[str], error: Optional[str])
        """
        success, content, error = self.get_page_content(url)
        if not success:
            return False, None, error

        return True, content.text, None

    def extract_links(
        self,
        url: str,
        internal_only: bool = False
    ) -> Tuple[bool, Optional[List[PageLink]], Optional[str]]:
        """
        Extract links from a page.

        Args:
            url: Page URL
            internal_only: Only return internal links

        Returns:
            (success: bool, links: Optional[List[PageLink]], error: Optional[str])
        """
        success, content, error = self.get_page_content(url, extract_images=False)
        if not success:
            return False, None, error

        links = content.links
        if internal_only:
            links = [l for l in links if l.is_internal]

        return True, links, None

    def extract_images(
        self,
        url: str
    ) -> Tuple[bool, Optional[List[PageImage]], Optional[str]]:
        """
        Extract images from a page.

        Args:
            url: Page URL

        Returns:
            (success: bool, images: Optional[List[PageImage]], error: Optional[str])
        """
        success, content, error = self.get_page_content(url, extract_links=False)
        if not success:
            return False, None, error

        return True, content.images, None

    # ========================================================================
    # BROWSER AUTOMATION
    # ========================================================================

    def start_browser(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Start browser session.

        Returns:
            (success: bool, message: Optional[str], error: Optional[str])
        """
        try:
            if self.is_browser_active:
                return False, None, "Browser already active"

            success, message, error = self.browser_backend.start()
            if success:
                self.is_browser_active = True

            return success, message, error

        except Exception as e:
            return False, None, str(e)

    def navigate(self, url: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Navigate to URL in browser.

        Args:
            url: Target URL

        Returns:
            (success: bool, current_url: Optional[str], error: Optional[str])
        """
        try:
            if not self.is_browser_active:
                return False, None, "Browser not started"

            return self.browser_backend.navigate(url)

        except Exception as e:
            return False, None, str(e)

    def click(
        self,
        selector: str,
        by_type: str = "xpath"
    ) -> Tuple[bool, Optional[InteractionResult], Optional[str]]:
        """
        Click element in browser.

        Args:
            selector: Element selector
            by_type: Selector type (xpath, css, id, class, link, tag)

        Returns:
            (success: bool, result: Optional[InteractionResult], error: Optional[str])
        """
        start_time = time.time()

        try:
            if not self.is_browser_active:
                return False, None, "Browser not started"

            success, message, error = self.browser_backend.click_element(
                selector,
                by_type=by_type
            )

            result = InteractionResult(
                success=success,
                action="click",
                message=message or error or "",
                duration_ms=(time.time() - start_time) * 1000
            )

            if success:
                _, url, _ = self.browser_backend.get_current_url()
                _, title, _ = self.browser_backend.get_title()
                result.current_url = url
                result.page_title = title

            return success, result, error

        except Exception as e:
            return False, None, str(e)

    def type_text(
        self,
        selector: str,
        text: str,
        by_type: str = "xpath",
        clear_first: bool = True
    ) -> Tuple[bool, Optional[InteractionResult], Optional[str]]:
        """
        Type text into element.

        Args:
            selector: Element selector
            text: Text to type
            by_type: Selector type
            clear_first: Clear field before typing

        Returns:
            (success: bool, result: Optional[InteractionResult], error: Optional[str])
        """
        start_time = time.time()

        try:
            if not self.is_browser_active:
                return False, None, "Browser not started"

            success, message, error = self.browser_backend.type_text(
                selector,
                text,
                by_type=by_type,
                clear_first=clear_first
            )

            result = InteractionResult(
                success=success,
                action="type",
                message=message or error or "",
                duration_ms=(time.time() - start_time) * 1000
            )

            return success, result, error

        except Exception as e:
            return False, None, str(e)

    def take_screenshot(self, filepath: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Take browser screenshot.

        Args:
            filepath: Where to save screenshot

        Returns:
            (success: bool, filepath: Optional[str], error: Optional[str])
        """
        try:
            if not self.is_browser_active:
                return False, None, "Browser not started"

            return self.browser_backend.take_screenshot(filepath)

        except Exception as e:
            return False, None, str(e)

    def wait_for_element(
        self,
        selector: str,
        by_type: str = "xpath",
        timeout: int = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Wait for element to appear.

        Args:
            selector: Element selector
            by_type: Selector type
            timeout: Wait timeout

        Returns:
            (success: bool, message: Optional[str], error: Optional[str])
        """
        try:
            if not self.is_browser_active:
                return False, None, "Browser not started"

            return self.browser_backend.wait_for_element(
                selector,
                by_type=by_type,
                timeout=timeout
            )

        except Exception as e:
            return False, None, str(e)

    def get_page_source(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Get current page HTML.

        Returns:
            (success: bool, html: Optional[str], error: Optional[str])
        """
        try:
            if not self.is_browser_active:
                return False, None, "Browser not started"

            return self.browser_backend.get_page_source()

        except Exception as e:
            return False, None, str(e)

    def get_browser_state(self) -> Tuple[bool, Optional[BrowserState], Optional[str]]:
        """
        Get current browser state.

        Returns:
            (success: bool, state: Optional[BrowserState], error: Optional[str])
        """
        try:
            if not self.is_browser_active:
                return False, None, "Browser not started"

            return self.browser_backend.get_state()

        except Exception as e:
            return False, None, str(e)

    def close_browser(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Close browser session.

        Returns:
            (success: bool, message: Optional[str], error: Optional[str])
        """
        try:
            if not self.is_browser_active:
                return False, None, "Browser not started"

            success, message, error = self.browser_backend.close()
            if success:
                self.is_browser_active = False

            return success, message, error

        except Exception as e:
            return False, None, str(e)

    # ========================================================================
    # UTILITY
    # ========================================================================

    def _record_operation(self, start_time: float):
        """Record operation time."""
        self.last_operation_time = time.time() - start_time

    def get_status(self) -> Dict[str, Any]:
        """
        Get module status.

        Returns:
            Status dict with backend info, browser state, last operation time
        """
        return {
            "backend": self.backend,
            "search_provider": self.search_provider,
            "browser_type": self.browser_type,
            "browser_active": self.is_browser_active,
            "last_operation_time_ms": self.last_operation_time * 1000,
            "supported_backends": [b.value for b in WebBackend],
            "supported_search_providers": [p.value for p in SearchProvider],
        }
