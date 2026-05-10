"""
Tests for Web module.
10 comprehensive tests covering: search, scraping, browser automation.
"""

import pytest
import time
from web.web import WebInteractor, SearchResult, PageContent, InteractionResult
from web.api_backend import ApiSearchBackend
from web.scraper_backend import ScraperBackend
from web.browser_backend import BrowserAutomationBackend


class TestWebSearch:
    """Test web search functionality."""

    def test_search_mock_backend(self):
        """Test search with mock backend."""
        web = WebInteractor(backend="mock")
        success, results, error = web.search("python programming")

        assert success is True
        assert error is None
        assert results is not None
        assert len(results) > 0
        assert results[0].title is not None
        assert results[0].url is not None

    def test_search_empty_query(self):
        """Test search with empty query."""
        web = WebInteractor(backend="mock")
        success, results, error = web.search("")

        assert success is False
        assert error is not None
        assert results is None

    def test_search_custom_num_results(self):
        """Test search with custom number of results."""
        web = WebInteractor(backend="mock")
        success, results, error = web.search("test", num_results=3)

        assert success is True
        assert len(results) <= 3

    def test_api_search_backend_mock(self):
        """Test API search backend with mock provider."""
        backend = ApiSearchBackend(provider="mock")
        success, results, error = backend.search("test query")

        assert success is True
        assert error is None
        assert results is not None
        assert all(isinstance(r, type(results[0])) for r in results)

    def test_search_result_structure(self):
        """Test search result data structure."""
        web = WebInteractor(backend="mock")
        success, results, error = web.search("test")

        result = results[0]
        assert hasattr(result, 'title')
        assert hasattr(result, 'url')
        assert hasattr(result, 'snippet')
        assert hasattr(result, 'position')
        assert hasattr(result, 'source')


class TestWebScraping:
    """Test web scraping functionality."""

    def test_scraper_backend_mock(self):
        """Test scraper with mock URL."""
        web = WebInteractor(backend="mock")
        success, content, error = web.get_page_content("https://example.com")

        assert success is True
        assert error is None
        assert content is not None
        assert content.url == "https://example.com"
        assert content.title is not None

    def test_page_content_empty_url(self):
        """Test scraping with empty URL."""
        web = WebInteractor(backend="mock")
        success, content, error = web.get_page_content("")

        assert success is False
        assert error is not None

    def test_extract_text(self):
        """Test text extraction."""
        web = WebInteractor(backend="mock")
        success, text, error = web.extract_text("https://example.com")

        assert success is True
        assert error is None
        assert isinstance(text, str)

    def test_extract_links(self):
        """Test link extraction."""
        web = WebInteractor(backend="mock")
        success, links, error = web.extract_links("https://example.com")

        assert success is True
        assert error is None
        assert isinstance(links, list)

    def test_extract_images(self):
        """Test image extraction."""
        web = WebInteractor(backend="mock")
        success, images, error = web.extract_images("https://example.com")

        assert success is True
        assert error is None
        assert isinstance(images, list)

    def test_page_content_structure(self):
        """Test page content data structure."""
        web = WebInteractor(backend="mock")
        success, content, error = web.get_page_content("https://example.com")

        assert hasattr(content, 'url')
        assert hasattr(content, 'title')
        assert hasattr(content, 'text')
        assert hasattr(content, 'links')
        assert hasattr(content, 'images')
        assert hasattr(content, 'metadata')
        assert hasattr(content, 'status_code')


class TestBrowserAutomation:
    """Test browser automation functionality."""

    def test_browser_backend_mock(self):
        """Test browser backend initialization."""
        browser = BrowserAutomationBackend(browser_type="mock")
        success, message, error = browser.start()

        assert success is True
        assert error is None

    def test_browser_navigate_mock(self):
        """Test browser navigation with mock."""
        browser = BrowserAutomationBackend(browser_type="mock")
        browser.start()

        success, url, error = browser.navigate("https://example.com")

        assert success is True
        assert error is None
        assert url == "https://example.com"

    def test_browser_click_mock(self):
        """Test browser click with mock."""
        browser = BrowserAutomationBackend(browser_type="mock")
        browser.start()

        success, message, error = browser.click_element("//button")

        assert success is True
        assert error is None

    def test_browser_type_text_mock(self):
        """Test browser type text with mock."""
        browser = BrowserAutomationBackend(browser_type="mock")
        browser.start()

        success, message, error = browser.type_text("//input", "test text")

        assert success is True
        assert error is None

    def test_browser_state_mock(self):
        """Test getting browser state with mock."""
        browser = BrowserAutomationBackend(browser_type="mock")
        browser.start()

        success, state, error = browser.get_state()

        assert success is True
        assert error is None
        assert state is not None
        assert hasattr(state, 'current_url')
        assert hasattr(state, 'title')
        assert hasattr(state, 'window_size')


class TestWebInteractorIntegration:
    """Test WebInteractor integration."""

    def test_web_interactor_initialization(self):
        """Test WebInteractor initialization."""
        web = WebInteractor(
            backend="mock",
            search_provider="serpapi",
            browser_type="chrome"
        )

        assert web.backend == "mock"
        assert web.search_provider == "serpapi"
        assert web.browser_type == "chrome"
        assert web.is_browser_active is False

    def test_web_interactor_status(self):
        """Test getting WebInteractor status."""
        web = WebInteractor(backend="mock")
        status = web.get_status()

        assert status is not None
        assert "backend" in status
        assert "search_provider" in status
        assert "browser_active" in status
        assert status["backend"] == "mock"
        assert status["browser_active"] is False

    def test_interaction_result_structure(self):
        """Test InteractionResult data structure."""
        result = InteractionResult(
            success=True,
            action="click",
            message="Test",
        )

        assert result.success is True
        assert result.action == "click"
        assert hasattr(result, 'current_url')
        assert hasattr(result, 'page_title')
        assert hasattr(result, 'duration_ms')


class TestWebSearchProviders:
    """Test different search providers."""

    def test_api_backend_providers(self):
        """Test API backend supports multiple providers."""
        providers = ["mock", "serpapi", "duckduckgo", "google", "bing", "brave"]

        for provider in providers:
            backend = ApiSearchBackend(provider=provider)
            assert backend.provider == provider

    def test_web_interactor_search_provider_override(self):
        """Test overriding search provider in search call."""
        web = WebInteractor(backend="mock", search_provider="serpapi")

        # Should use mock results regardless of provider
        success, results, error = web.search("test", provider="duckduckgo")
        assert success is True


class TestStatelessDesign:
    """Test stateless/pure transformation design."""

    def test_search_is_stateless(self):
        """Test search operations are stateless."""
        web = WebInteractor(backend="mock")

        success1, results1, _ = web.search("python")
        success2, results2, _ = web.search("python")

        # Same input should give same results
        assert success1 == success2
        assert len(results1) == len(results2)

    def test_scraping_is_stateless(self):
        """Test scraping operations are stateless."""
        web = WebInteractor(backend="mock")

        success1, content1, _ = web.get_page_content("https://example.com")
        success2, content2, _ = web.get_page_content("https://example.com")

        # Same input should give same results
        assert success1 == success2
        assert content1.url == content2.url


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
