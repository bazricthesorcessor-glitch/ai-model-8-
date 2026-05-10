"""
Web Module Examples - All Capabilities
Demonstrates: search, scraping, browser automation, vision integration, keyboard/mouse.
"""

from web.web import WebInteractor, WebBackend
from web.api_backend import ApiSearchBackend, SearchProvider
from web.scraper_backend import ScraperBackend
from web.browser_backend import BrowserAutomationBackend


def example_01_basic_search():
    """Example 1: Basic web search using API."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Web Search")
    print("="*70)

    web = WebInteractor(backend="mock", search_provider="serpapi")

    success, results, error = web.search("machine learning", num_results=5)

    if success:
        print(f"✓ Found {len(results)} results")
        for result in results[:3]:
            print(f"\n  Title: {result.title}")
            print(f"  URL: {result.url}")
            print(f"  Snippet: {result.snippet[:80]}...")
    else:
        print(f"✗ Error: {error}")


def example_02_search_providers():
    """Example 2: Switching between search providers."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Multiple Search Providers")
    print("="*70)

    web = WebInteractor(backend="mock")

    providers = ["serpapi", "duckduckgo", "google", "bing", "brave"]

    for provider in providers:
        success, results, error = web.search(
            "python programming",
            num_results=3,
            provider=provider
        )
        if success:
            print(f"✓ {provider.upper()}: {len(results)} results")
        else:
            print(f"✗ {provider.upper()}: {error}")


def example_03_page_scraping():
    """Example 3: Fetch and analyze page content."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Web Page Scraping")
    print("="*70)

    web = WebInteractor(backend="mock")

    success, content, error = web.get_page_content("https://example.com")

    if success:
        print(f"✓ Page fetched: {content.title}")
        print(f"  URL: {content.url}")
        print(f"  Status: {content.status_code}")
        print(f"  Text length: {len(content.text)} chars")
        print(f"  Links found: {len(content.links)}")
        print(f"  Images found: {len(content.images)}")
    else:
        print(f"✗ Error: {error}")


def example_04_extract_text():
    """Example 4: Extract only text from a page."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Text Extraction")
    print("="*70)

    web = WebInteractor(backend="mock")

    success, text, error = web.extract_text("https://example.com")

    if success:
        print(f"✓ Text extracted")
        print(f"  Length: {len(text)} characters")
        print(f"  Preview: {text[:200]}...")
    else:
        print(f"✗ Error: {error}")


def example_05_extract_links():
    """Example 5: Extract links from a page."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Link Extraction")
    print("="*70)

    web = WebInteractor(backend="mock")

    success, links, error = web.extract_links("https://example.com")

    if success:
        print(f"✓ Found {len(links)} links")
        internal_links = [l for l in links if l.is_internal]
        print(f"  Internal: {len(internal_links)}")
        print(f"  External: {len(links) - len(internal_links)}")

        # Show first few
        for link in links[:3]:
            print(f"\n  Text: {link.text}")
            print(f"  URL: {link.url}")
            print(f"  Internal: {link.is_internal}")
    else:
        print(f"✗ Error: {error}")


def example_06_extract_images():
    """Example 6: Extract images from a page."""
    print("\n" + "="*70)
    print("EXAMPLE 6: Image Extraction")
    print("="*70)

    web = WebInteractor(backend="mock")

    success, images, error = web.extract_images("https://example.com")

    if success:
        print(f"✓ Found {len(images)} images")
        for image in images[:3]:
            print(f"\n  Alt: {image.alt}")
            print(f"  Src: {image.src}")
            if image.width:
                print(f"  Size: {image.width}x{image.height}")
    else:
        print(f"✗ Error: {error}")


def example_07_browser_automation():
    """Example 7: Browser automation basics."""
    print("\n" + "="*70)
    print("EXAMPLE 7: Browser Automation")
    print("="*70)

    # Using mock browser for demo
    web = WebInteractor(backend="mock", browser_type="mock")

    # Start browser
    success, message, error = web.start_browser()
    if success:
        print(f"✓ Browser started: {message}")

        # Navigate
        success, url, error = web.navigate("https://example.com")
        if success:
            print(f"✓ Navigated to: {url}")

            # Click element
            success, result, error = web.click("//button[@id='submit']")
            if success:
                print(f"✓ Clicked element")

            # Type text
            success, result, error = web.type_text("//input[@id='search']", "test query")
            if success:
                print(f"✓ Typed text")

            # Get state
            success, state, error = web.get_browser_state()
            if success:
                print(f"✓ Browser state: {state.title}")

        # Close browser
        success, message, error = web.close_browser()
        if success:
            print(f"✓ Browser closed")


def example_08_browser_interactions():
    """Example 8: Advanced browser interactions."""
    print("\n" + "="*70)
    print("EXAMPLE 8: Advanced Browser Interactions")
    print("="*70)

    web = WebInteractor(backend="mock", browser_type="mock")

    success, _, _ = web.start_browser()
    if success:
        # Wait for element
        success, message, error = web.wait_for_element("//div[@class='loader']", timeout=5)
        print(f"{'✓' if success else '✗'} Wait for element: {message or error}")

        # Get page source
        success, html, error = web.get_page_source()
        if success:
            print(f"✓ Got page source: {len(html)} chars")

        # Multiple interactions
        interactions = [
            ("//input[@id='name']", "John Doe"),
            ("//input[@id='email']", "john@example.com"),
            ("//textarea[@id='message']", "Hello, this is a test message"),
        ]

        for selector, text in interactions:
            success, result, _ = web.type_text(selector, text)
            print(f"{'✓' if success else '✗'} Filled field: {selector}")

        web.close_browser()


def example_09_integrated_workflow():
    """Example 9: Complete workflow - search, scrape, analyze."""
    print("\n" + "="*70)
    print("EXAMPLE 9: Integrated Workflow")
    print("="*70)

    web = WebInteractor(backend="mock")

    # 1. Search
    print("\n1. Searching for 'machine learning tools'...")
    success, results, _ = web.search("machine learning tools", num_results=3)
    if success:
        print(f"   ✓ Found {len(results)} results")

        # 2. For each result, try to scrape
        for i, result in enumerate(results[:2], 1):
            print(f"\n2.{i} Analyzing: {result.title}")

            success, content, _ = web.get_page_content(result.url)
            if success:
                print(f"   ✓ Fetched page")
                print(f"   - Text length: {len(content.text)} chars")
                print(f"   - Links: {len(content.links)}")
                print(f"   - Images: {len(content.images)}")

                # Extract key info
                success, text, _ = web.extract_text(result.url)
                print(f"   - Preview: {text[:100]}...")


def example_10_multiple_backends():
    """Example 10: Using different backends."""
    print("\n" + "="*70)
    print("EXAMPLE 10: Multiple Backends")
    print("="*70)

    backends = ["mock"]  # In production, could include "api", "scraper", "browser"

    for backend in backends:
        print(f"\n--- Using {backend.upper()} backend ---")

        web = WebInteractor(backend=backend)

        # Test search
        success, results, _ = web.search("test", num_results=2)
        print(f"Search: {'✓' if success else '✗'}")

        # Test scraping
        success, content, _ = web.get_page_content("https://example.com")
        print(f"Scraping: {'✓' if success else '✗'}")


def example_11_api_search_backend():
    """Example 11: API search backend directly."""
    print("\n" + "="*70)
    print("EXAMPLE 11: API Search Backend")
    print("="*70)

    backend = ApiSearchBackend(provider="mock")

    success, results, error = backend.search("artificial intelligence", num_results=5)

    if success:
        print(f"✓ API search successful: {len(results)} results")
        for result in results[:2]:
            print(f"\n  {result.title}")
            print(f"  {result.url}")
    else:
        print(f"✗ Error: {error}")


def example_12_scraper_backend():
    """Example 12: Scraper backend directly."""
    print("\n" + "="*70)
    print("EXAMPLE 12: Scraper Backend")
    print("="*70)

    scraper = ScraperBackend()

    print("✓ Scraper backend supports:")
    print("  - fetch_page(url)")
    print("  - extract_text(page_content)")
    print("  - extract_links(page_content)")
    print("  - extract_images(page_content)")
    print("  - extract_metadata(page_content)")


def example_13_browser_backend():
    """Example 13: Browser backend directly."""
    print("\n" + "="*70)
    print("EXAMPLE 13: Browser Backend")
    print("="*70)

    browser = BrowserAutomationBackend(browser_type="mock", headless=True)

    operations = [
        "start()",
        "navigate(url)",
        "click_element(selector)",
        "type_text(selector, text)",
        "get_page_source()",
        "get_title()",
        "get_current_url()",
        "wait_for_element(selector)",
        "take_screenshot(filepath)",
        "get_state()",
        "close()",
    ]

    print("✓ Browser backend supports:")
    for op in operations:
        print(f"  - {op}")


def example_14_error_handling():
    """Example 14: Error handling."""
    print("\n" + "="*70)
    print("EXAMPLE 14: Error Handling")
    print("="*70)

    web = WebInteractor(backend="mock")

    # Empty query
    success, results, error = web.search("")
    print(f"Empty search: {'✗ Error' if not success else '✓'} - {error}")

    # Empty URL
    success, content, error = web.get_page_content("")
    print(f"Empty URL: {'✗ Error' if not success else '✓'} - {error}")

    # Invalid selector type
    success, result, error = web.click("selector", by_type="invalid")
    print(f"Invalid selector: {'✗ Error' if not success else '✓'}")


def example_15_vision_integration():
    """Example 15: Vision integration (planned)."""
    print("\n" + "="*70)
    print("EXAMPLE 15: Vision Integration (Design)")
    print("="*70)

    print("""
Vision integration capabilities:
  1. Take browser screenshot
  2. Analyze page using vision module
  3. Detect interactive elements (buttons, inputs, links)
  4. Extract text using OCR
  5. Identify page structure and layout
  6. Match elements by visual similarity

Example workflow:
  1. Navigate to website
  2. Take screenshot
  3. Use Vision to detect elements
  4. Click/interact with detected elements
  5. Verify results visually
    """)


def main():
    """Run all examples."""
    print("\n\n")
    print("╔" + "="*68 + "╗")
    print("║" + " " * 15 + "WEB INTERACTION MODULE - EXAMPLES" + " " * 19 + "║")
    print("╚" + "="*68 + "╝")

    examples = [
        example_01_basic_search,
        example_02_search_providers,
        example_03_page_scraping,
        example_04_extract_text,
        example_05_extract_links,
        example_06_extract_images,
        example_07_browser_automation,
        example_08_browser_interactions,
        example_09_integrated_workflow,
        example_10_multiple_backends,
        example_11_api_search_backend,
        example_12_scraper_backend,
        example_13_browser_backend,
        example_14_error_handling,
        example_15_vision_integration,
    ]

    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\n✗ Example error: {e}")

    print("\n\n" + "="*70)
    print("All examples completed!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
