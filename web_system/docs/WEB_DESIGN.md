# Web Interaction Module - Design Documentation

## Overview

The **Web Interaction Module** provides complete internet access and web automation capabilities. It integrates:

- **API-Based Search**: Multiple search providers (SerpAPI, Google, Bing, DuckDuckGo, Brave)
- **Web Scraping**: Extract content, links, images, metadata from pages
- **Browser Automation**: Human-like interactions (click, type, navigate, wait)
- **Vision Integration**: Understand web pages visually (planned)
- **Keyboard/Mouse Control**: UI automation and interaction

## Architecture

### Pure Transformation Design

```
Input → Processing → Structured Output
(stateless, deterministic, reusable)

Search Query      → API Backend    → List[SearchResult]
URL               → Scraper Backend → PageContent
Selector + Action → Browser Backend → InteractionResult
```

### No Cross-Backend State

- Each backend is independent
- No shared state between backends
- Same input always produces same output
- Backends can be used in any order

### Backend Separation

```
web/
├── api_backend.py         # Search APIs
├── scraper_backend.py     # Web scraping
├── browser_backend.py     # Browser automation
└── web.py                 # Unified interface
```

## Components

### 1. API Search Backend (`api_backend.py`)

**Purpose**: Search the web using APIs

**Supported Providers**:
- `mock` - Testing (no API key required)
- `serpapi` - Google/Bing/DuckDuckGo (requires SERPAPI_KEY)
- `duckduckgo` - Private search (no key required)
- `google` - Google Custom Search (requires GOOGLE_SEARCH_API_KEY + cx)
- `bing` - Bing Search (requires BING_SEARCH_API_KEY)
- `brave` - Brave Search (requires BRAVE_SEARCH_API_KEY)

**Usage**:
```python
backend = ApiSearchBackend(provider="serpapi")
success, results, error = backend.search("python tutorials", num_results=10)

# Returns List[ApiSearchResult]
for result in results:
    print(result.title, result.url, result.snippet)
```

**Data Structures**:
```python
@dataclass
class ApiSearchResult:
    title: str          # Result title
    url: str           # Result URL
    snippet: str       # Text preview
    position: int      # Position in results
    source: str        # Provider name
    metadata: Dict     # Provider-specific data
```

### 2. Scraper Backend (`scraper_backend.py`)

**Purpose**: Fetch and extract page content

**Features**:
- Fetch page HTML and text
- Extract links (internal/external)
- Extract images with metadata
- Extract page metadata (title, description, etc.)
- Parse structured data from HTML

**Usage**:
```python
scraper = ScraperBackend()
success, content, error = scraper.fetch_page("https://example.com")

# Returns ScrapedPageContent
print(content.title)
print(content.text)
for link in content.links:
    print(link.text, link.url)
```

**Data Structures**:
```python
@dataclass
class ScrapedPageContent:
    url: str                    # Page URL
    title: str                  # Page title
    text: str                   # Extracted text
    html: str                   # Full HTML
    links: List[PageLink]       # Links on page
    images: List[PageImage]     # Images on page
    metadata: Dict              # Page metadata
    status_code: int            # HTTP status
    timestamp: float            # Fetch time

@dataclass
class PageLink:
    text: str           # Link text
    url: str           # Full URL
    title: Optional[str]
    is_internal: bool  # Same domain?

@dataclass
class PageImage:
    src: str           # Image URL
    alt: str          # Alt text
    title: Optional[str]
    width: Optional[int]
    height: Optional[int]
```

### 3. Browser Automation Backend (`browser_backend.py`)

**Purpose**: Human-like browser interactions

**Technology**: Selenium WebDriver

**Supported Browsers**:
- `chrome` - Google Chrome
- `firefox` - Mozilla Firefox
- `edge` - Microsoft Edge
- `safari` - Apple Safari
- `mock` - Testing only

**Operations**:
```python
browser = BrowserAutomationBackend(browser_type="chrome", headless=True)

# Session management
browser.start()           # Start browser
browser.close()           # Close browser

# Navigation
browser.navigate(url)     # Go to URL
browser.get_current_url() # Get current URL
browser.get_title()       # Get page title

# Interaction
browser.click_element(selector)              # Click element
browser.type_text(selector, text)            # Type in field
browser.wait_for_element(selector, timeout)  # Wait for element

# Content
browser.get_page_source()  # Get HTML
browser.take_screenshot(filepath)  # Screenshot

# State
browser.get_state()  # Get BrowserState
```

**Data Structures**:
```python
@dataclass
class BrowserState:
    current_url: str
    title: str
    window_size: Tuple[int, int]
    is_headless: bool
    cookies: List[Dict]
    local_storage: Dict
```

### 4. Main Interface (`web.py`)

**Purpose**: Unified interface for all backends

**Class**: `WebInteractor`

**Initialization**:
```python
web = WebInteractor(
    backend="mock",              # Primary backend
    search_provider="serpapi",   # Search provider
    browser_type="chrome",       # Browser type
    headless=True                # Headless mode
)
```

**Search Methods**:
```python
# Web search via API
success, results, error = web.search(
    query="machine learning",
    num_results=10,
    provider="serpapi"  # Optional override
)
# Returns: List[SearchResult]
```

**Scraping Methods**:
```python
# Get full page content
success, content, error = web.get_page_content(
    url="https://example.com",
    extract_links=True,
    extract_images=True
)
# Returns: PageContent

# Extract just text
success, text, error = web.extract_text(url)
# Returns: str

# Extract links
success, links, error = web.extract_links(url, internal_only=False)
# Returns: List[PageLink]

# Extract images
success, images, error = web.extract_images(url)
# Returns: List[PageImage]
```

**Browser Methods**:
```python
# Session control
web.start_browser()
web.close_browser()

# Navigation
web.navigate("https://example.com")

# Interaction
web.click(selector, by_type="xpath")
web.type_text(selector, "text", by_type="xpath")
web.wait_for_element(selector, timeout=10)

# Content
web.get_page_source()
web.take_screenshot("/path/to/screenshot.png")

# State
web.get_browser_state()
```

**Utility**:
```python
# Status
status = web.get_status()
# Returns: Dict with backend info, browser state, timing
```

## Return Format

All methods follow the consistent tuple return format:

```python
(success: bool, data: Optional[T], error: Optional[str])

# Example
success, results, error = web.search("test")

if success:
    # Process results
    for result in results:
        print(result.title)
else:
    # Handle error
    print(f"Error: {error}")
```

## Use Cases

### 1. Research Automation

```python
web = WebInteractor(backend="api", search_provider="serpapi")

# Search for topic
success, results, _ = web.search("quantum computing applications")

# Analyze each result
for result in results:
    success, content, _ = web.get_page_content(result.url)
    
    if success:
        # Extract links for further research
        success, links, _ = web.extract_links(result.url)
        # Process links...
```

### 2. Web Form Automation

```python
web = WebInteractor(backend="browser", browser_type="chrome")

web.start_browser()
web.navigate("https://example.com/form")

# Fill form
web.type_text("//input[@id='name']", "John Doe")
web.type_text("//input[@id='email']", "john@example.com")
web.type_text("//textarea[@id='message']", "Test message")

# Submit
web.click("//button[@type='submit']")

web.close_browser()
```

### 3. Content Extraction

```python
web = WebInteractor(backend="scraper")

urls = [
    "https://site1.com",
    "https://site2.com",
    "https://site3.com",
]

for url in urls:
    success, text, _ = web.extract_text(url)
    
    if success:
        # Process text...
        print(f"Got {len(text)} chars from {url}")
```

### 4. Product Monitoring

```python
web = WebInteractor(backend="scraper")

product_urls = [...] # List of product pages

for url in product_urls:
    success, content, _ = web.get_page_content(url)
    
    if success:
        # Extract product info
        metadata = content.metadata
        text = content.text
        
        # Store price, availability, etc.
        # Alert if changed...
```

### 5. Vision-Based Testing (Planned)

```python
web = WebInteractor(backend="browser", browser_type="chrome")
vision = VisionAnalyzer()  # Planned integration

web.start_browser()
web.navigate("https://example.com")

# Take screenshot
web.take_screenshot("/tmp/page.png")

# Analyze with vision
success, screen_data, _ = vision.analyze_screen()

# Detect buttons, inputs, links visually
for element in screen_data.elements:
    if element.type == "button":
        # Click detected button
        web.click(f"//{element.type}[{element.text}]")
```

## Configuration

### Environment Variables

For API-based search:

```bash
# SerpAPI (recommended - supports multiple providers)
export SERPAPI_KEY="your-key"

# Google Custom Search
export GOOGLE_SEARCH_API_KEY="your-key"
export GOOGLE_SEARCH_ENGINE_ID="cx-value"

# Bing Search
export BING_SEARCH_API_KEY="your-key"

# Brave Search
export BRAVE_SEARCH_API_KEY="your-key"

# DuckDuckGo (no key needed)
```

### Browser Options

```python
web = WebInteractor(
    browser_type="chrome",  # chrome, firefox, edge, safari
    headless=True,          # Headless mode (no UI)
    timeout=10              # Operation timeout
)
```

## Integration Points

### With Vision Module (Planned)

```python
from vision import VisionAnalyzer
from web import WebInteractor

web = WebInteractor(backend="browser")
vision = VisionAnalyzer(backend="tesseract")

web.start_browser()
web.navigate("https://example.com")

# Take screenshot
web.take_screenshot("/tmp/page.png")

# Analyze visually
success, screen_data, _ = vision.analyze_screen()

# Interact with detected elements
for element in screen_data.elements:
    if element.type == "button":
        # Get element location from vision
        x, y, w, h = element.location
        # Click it
        web.click(...)
```

### With Keyboard/Mouse (Planned)

```python
from terminal import TerminalExecutor
from web import WebInteractor

web = WebInteractor(backend="browser")
term = TerminalExecutor(shell="bash")

web.start_browser()
web.navigate("https://example.com")

# Type using keyboard module
web.type_text("//input[@id='search']", "query")

# Screenshot for verification
web.take_screenshot("/tmp/result.png")
```

### With Memory Module (Planned)

```python
from memory import MemoryManager
from web import WebInteractor

web = WebInteractor()
memory = MemoryManager()

# Store search history
success, results, _ = web.search("machine learning")
memory.store("searches", {"query": "machine learning", "results_count": len(results)})

# Track state
memory.store("current_page", web.get_browser_state())
```

## Best Practices

### 1. API Rate Limiting

```python
import time

web = WebInteractor(backend="api")

queries = ["python", "javascript", "rust"]
for query in queries:
    web.search(query)
    time.sleep(1)  # Rate limit: 1 request per second
```

### 2. Error Handling

```python
success, results, error = web.search("query")

if not success:
    if "API key" in error:
        # Handle missing credentials
        pass
    elif "timeout" in error:
        # Handle timeout
        pass
    else:
        # Handle other errors
        pass
```

### 3. Resource Management

```python
web = WebInteractor(backend="browser")

try:
    web.start_browser()
    web.navigate("https://example.com")
    # ... do work ...
finally:
    web.close_browser()  # Always close
```

### 4. Caching Results

```python
cache = {}
web = WebInteractor(backend="scraper")

def get_page_cached(url):
    if url in cache:
        return cache[url]
    
    success, content, _ = web.get_page_content(url)
    if success:
        cache[url] = content
    
    return content if success else None
```

## Testing

All backends support mock mode for testing:

```python
web = WebInteractor(
    backend="mock",
    search_provider="mock",
    browser_type="mock"
)

# All operations return mock data
success, results, _ = web.search("test")
success, content, _ = web.get_page_content("https://example.com")
web.start_browser()  # No actual browser started
```

## Performance

### Timing

The module tracks operation timing:

```python
success, results, _ = web.search("query")
print(web.last_operation_time)  # Seconds
```

### Optimization

1. **Scraping**: Use headless browsers for speed
2. **Search**: Use API for faster results than scraping
3. **Caching**: Cache frequently accessed pages
4. **Parallel**: Process multiple searches/pages in parallel
5. **Headless**: Browser automation is faster in headless mode

## Limitations

### Current

- Browser automation requires Chrome/Firefox/Edge installed
- Some websites block automated access
- Vision integration not yet implemented
- No keyboard/mouse binding yet

### Planned

- Proxy support for anonymity
- Cookie persistence across sessions
- JavaScript execution tracking
- Visual element detection (Vision integration)
- Mobile browser support
- Distributed scraping

## Dependencies

### Required

```
requests          # HTTP requests
beautifulsoup4    # HTML parsing
```

### Optional

```
selenium          # Browser automation
duckduckgo_search # DuckDuckGo API
Pillow            # Image processing (for Vision integration)
```

### API Keys (Optional)

```
SERPAPI_KEY           # SerpAPI search
GOOGLE_SEARCH_API_KEY # Google Custom Search
BING_SEARCH_API_KEY   # Bing Search
BRAVE_SEARCH_API_KEY  # Brave Search
```

## Examples

See `examples.py` for 15 working examples:

1. Basic web search
2. Multiple search providers
3. Page scraping
4. Text extraction
5. Link extraction
6. Image extraction
7. Browser automation
8. Advanced interactions
9. Integrated workflow
10. Multiple backends
11. API search backend
12. Scraper backend
13. Browser backend
14. Error handling
15. Vision integration (planned)

## Testing

Run tests:

```bash
pytest web/test_web.py -v
```

Tests cover:
- Web search (multiple providers)
- Page scraping (text, links, images)
- Browser automation (navigate, click, type)
- Data structures
- Error handling
- Stateless design
