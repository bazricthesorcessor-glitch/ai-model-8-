# AI Agent System - Complete Documentation

A comprehensive, modular AI system for desktop automation with internet access, web automation, vision understanding, terminal control, and intelligent task management.

## 🎯 Core Features

### 1. **Web & Internet Access** ⭐ NEW
- **API-Based Search**: SerpAPI, Google, Bing, DuckDuckGo, Brave
- **Web Scraping**: Extract text, links, images, metadata from any page
- **Browser Automation**: Selenium-powered human-like interactions (click, type, navigate)
- **Vision Integration**: Understand web pages visually (planned)
- **Keyboard/Mouse Control**: UI automation and interaction
- **Multiple Search Providers**: Switch between providers seamlessly

### 2. **Vision Module**
- Screen capture and analysis
- OCR (Tesseract, PaddleOCR, Google Cloud, Azure)
- Element detection and location
- Layout understanding
- Structured data extraction

### 3. **Terminal & Command Execution**
- Multi-shell support (bash, zsh, fish, powershell, cmd)
- Working directory management
- Environment variable handling
- Timeout and error handling
- Piped command support

### 4. **Task Management (TODO)**
- Task tracking with status (pending, in_progress, completed, blocked)
- Persistent JSON storage
- Progress visualization
- Task notes and timestamps

### 5. **Audio/Voice**
- Text-to-speech (multiple providers)
- Speech-to-text recognition
- Voice integration

### 6. **Memory System**
- Current task tracking
- Last action history
- Status persistence
- Thread-safe operations

### 7. **Router & Execution**
- Intent-based routing
- Multi-response handling
- Safety checks and approval system
- Tool registry integration

## 📦 System Architecture

```
                              User Input
                                  |
                                  v
                            ┌─────────────┐
                            │   Brain     │
                            │ (LLM/Logic) │
                            └──────┬──────┘
                                   |
                        ┌──────────┼──────────┐
                        |          |          |
                        v          v          v
                      Router    Memory   Executor
                        |          |          |
        ┌──────────┬────┴────┬─────┴─┬────┬──┴──┬─────────┐
        |          |         |       |    |     |         |
        v          v         v       v    v     v         v
      Web      Terminal    Vision  Voice Tools State   Config
    (Search, (Bash/Zsh)  (Capture) (STT/TTS) (Click, (Track) (Defaults)
   Scraping,            (OCR)                Type)
   Browser)             (Detect)
```

### Design Principles

- **Stateless**: Each operation is independent, deterministic
- **Pure Transformation**: Input → Processing → Output
- **Modular**: No cross-module imports (except router)
- **Pluggable Backends**: Multiple implementations per capability
- **Consistent Format**: All return `(success, data, error)` tuples
- **Thread-Safe**: RLock for atomic operations
- **Minimal Dependencies**: Only required libraries

## 🚀 Quick Start

### 1. Installation

```bash
cd ~/ai\ model\ 8

# Install core dependencies
pip install requests beautifulsoup4 pillow

# Optional: For browser automation
pip install selenium

# Optional: For OCR
pip install pytesseract paddleocr google-cloud-vision azure-cognitiveservices-vision-computervision

# Optional: For speech
pip install pyttsx3 SpeechRecognition
```

### 2. Web Search Example

```python
from web.web import WebInteractor

web = WebInteractor(backend="mock", search_provider="serpapi")

# Search
success, results, error = web.search("machine learning", num_results=5)
if success:
    for result in results:
        print(f"{result.title}\n{result.url}\n")

# Scrape page
success, content, error = web.get_page_content("https://example.com")
if success:
    print(content.title)
    print(content.text[:500])
```

### 3. Terminal Execution

```python
from terminal.terminal import TerminalExecutor

executor = TerminalExecutor(shell="bash")

# Execute command
success, result, error = executor.execute("ls -la /home")
if success:
    print(result.stdout)

# Execute python
success, result, error = executor.execute_python("print('Hello')")
```

### 4. Task Management

```python
from todo.todo import TodoManager

manager = TodoManager()

# Create task list
manager.create_todo_list("My Tasks")

# Add task
manager.add_task(
    content="Implement web search",
    active_form="Implementing web search"
)

# Mark in progress
manager.mark_in_progress(0)

# Save
manager.save_todo_list("my_tasks")
```

### 5. Vision Analysis

```python
from vision.vision import VisionAnalyzer

vision = VisionAnalyzer(backend="mock")

# Capture screen
success, image_bytes, error = vision.capture_screen()

# Extract text
success, text, error = vision.extract_text(image_bytes)

# Detect elements
success, elements, error = vision.detect_elements(image_bytes)
```

## 📚 Module Documentation

### Web Module (`web/`)
- **Purpose**: Complete internet access and web automation
- **Features**: Search, scraping, browser automation, vision integration
- **Docs**: [WEB_DESIGN.md](web/WEB_DESIGN.md)
- **Tests**: 15+ test cases
- **Examples**: 15 working examples in [examples.py](web/examples.py)

### Terminal Module (`terminal/`)
- **Purpose**: Execute shell commands across multiple shells
- **Features**: bash, zsh, fish, powershell, cmd, timeout, env vars
- **Docs**: [TERMINAL_TODO_GUIDE.md](TERMINAL_TODO_GUIDE.md)
- **Tests**: 9/10 test cases passing

### TODO System (`todo/`)
- **Purpose**: Task tracking with persistent storage
- **Features**: Status tracking, progress visualization, JSON storage
- **Docs**: [TERMINAL_TODO_GUIDE.md](TERMINAL_TODO_GUIDE.md)
- **Integration**: Works with Vision for element verification

### Vision Module (`vision/`)
- **Purpose**: Screen understanding and OCR
- **Features**: 6+ OCR backends, element detection, text extraction
- **Docs**: [vision/VISION_DESIGN.md](vision/VISION_DESIGN.md)
- **Tests**: 10/10 test cases passing

### Router (`router/`)
- **Purpose**: Intent detection and module routing
- **Features**: Config-driven routing, multi-response handling
- **Docs**: [README.md](router/README.md)

### Memory (`memory/`)
- **Purpose**: Task and state tracking
- **Features**: Persistent storage, thread-safe operations
- **Docs**: [memory/README.md](memory/README.md)

### Voice (`voice/`)
- **Purpose**: TTS and STT
- **Features**: Multiple backends for speech
- **Docs**: [voice/README.md](voice/README.md)

## 🔌 Web Module API Reference

### Web Search
```python
success, results, error = web.search(
    query="python tutorials",
    num_results=10,
    provider="serpapi"  # or google, bing, duckduckgo, brave
)

# Returns: List[SearchResult]
# - title, url, snippet, position, source, metadata
```

### Page Scraping
```python
success, content, error = web.get_page_content(
    url="https://example.com",
    extract_links=True,
    extract_images=True
)

# Returns: PageContent
# - title, text, links, images, metadata, status_code
```

### Text Extraction
```python
success, text, error = web.extract_text("https://example.com")
# Returns: str
```

### Link Extraction
```python
success, links, error = web.extract_links(
    "https://example.com",
    internal_only=False
)
# Returns: List[PageLink]
```

### Browser Automation
```python
web.start_browser()
web.navigate("https://example.com")
web.click("//button[@id='submit']", by_type="xpath")
web.type_text("//input[@id='search']", "query")
web.wait_for_element("//div[@class='results']")
web.take_screenshot("/tmp/page.png")
web.close_browser()
```

## 🎛️ Configuration

### Environment Variables

```bash
# Web Search APIs
export SERPAPI_KEY="your-key"
export GOOGLE_SEARCH_API_KEY="your-key"
export BING_SEARCH_API_KEY="your-key"
export BRAVE_SEARCH_API_KEY="your-key"

# Vision backends
export GOOGLE_CLOUD_VISION_KEY="your-key"
export AZURE_VISION_KEY="your-key"

# Arch Linux specific
export PACMAN_CACHE="/var/cache/pacman/pkg"
```

### Config File (`config/settings.py`)

```python
WEB_CONFIG = {
    "backend": "mock",              # api, scraper, browser, mock
    "search_provider": "serpapi",   # serpapi, google, bing, duckduckgo, brave
    "browser_type": "chrome",       # chrome, firefox, edge, safari
    "browser_headless": True,
    "browser_timeout": 10,
}

SCREEN_CONFIG = {
    "width": 1920,
    "height": 1200,
    "refresh_rate": 60,
}
```

## 📁 Directory Structure

```
ai\ model\ 8/
├── web/                     # Web module (NEW)
│   ├── api_backend.py      # Search APIs
│   ├── scraper_backend.py  # Web scraping
│   ├── browser_backend.py  # Browser automation
│   ├── web.py              # Main interface
│   ├── test_web.py         # 15+ tests
│   ├── examples.py         # 15 examples
│   ├── __init__.py
│   └── WEB_DESIGN.md       # Design doc
│
├── terminal/               # Terminal execution
│   ├── terminal.py
│   ├── test_terminal.py
│   └── examples.py
│
├── todo/                   # Task management
│   ├── todo.py
│   └── __init__.py
│
├── vision/                 # Screen analysis
│   ├── vision.py
│   ├── test_vision.py
│   └── VISION_DESIGN.md
│
├── router/                 # Intent routing
│   ├── router.py
│   ├── advanced_router.py
│   └── test_router.py
│
├── memory/                 # State tracking
│   ├── memory.py
│   ├── core.py
│   └── test_memory.py
│
├── voice/                  # Audio
│   ├── voice.py
│   └── test_voice.py
│
├── tools/                  # Tool registry
│   ├── tool.py
│   ├── registry.py
│   ├── web/               # Web tools
│   │   └── __init__.py
│   └── test_tools.py
│
├── config/                 # Configuration
│   └── settings.py
│
├── README.md              # This file
├── WEB_DESIGN.md          # Web module documentation
├── ARCH_LINUX_GUIDE.md    # Arch Linux setup
└── TERMINAL_TODO_GUIDE.md # Terminal & TODO guide
```

## 🔧 Common Usage Patterns

### Pattern 1: Research Automation
```python
web = WebInteractor(backend="api", search_provider="serpapi")

# Search
success, results, _ = web.search("quantum computing")

# Analyze each result
for result in results[:5]:
    success, content, _ = web.get_page_content(result.url)
    if success:
        success, links, _ = web.extract_links(result.url)
        # Process links for further research...
```

### Pattern 2: Form Automation with Vision
```python
web = WebInteractor(backend="browser")
vision = VisionAnalyzer()

web.start_browser()
web.navigate("https://example.com/form")

# Take screenshot and analyze
web.take_screenshot("/tmp/form.png")
success, screen_data, _ = vision.analyze_screen()

# Detect and fill fields
for element in screen_data.elements:
    if element.type == "input":
        web.type_text(f"//*[contains(text(), '{element.text}')]", "value")
```

### Pattern 3: Content Monitoring
```python
web = WebInteractor(backend="scraper")
memory = MemoryManager()

urls = ["https://site1.com", "https://site2.com"]

for url in urls:
    success, content, _ = web.get_page_content(url)
    
    if success:
        # Store for comparison
        memory.store("page_content", {
            "url": url,
            "title": content.title,
            "text": content.text,
            "timestamp": time.time()
        })
```

### Pattern 4: Task-Based Workflow
```python
from todo.todo import TodoManager
from web.web import WebInteractor

# Create task list
todo = TodoManager()
todo.create_todo_list("Research Project")

# Add research tasks
todo.add_task("Search for papers", "Searching for papers")
todo.add_task("Analyze results", "Analyzing results")

# Start task
todo.mark_in_progress(0)

# Execute web search
web = WebInteractor()
success, results, _ = web.search("neural networks")

# Mark complete
todo.mark_completed(0)
todo.save_todo_list("research_project")
```

## 🧪 Testing

Run all tests:
```bash
# Web module
python -m pytest web/test_web.py -v

# Terminal module
python -m pytest terminal/test_terminal.py -v

# Vision module
python -m pytest vision/test_vision.py -v

# All modules
python -m pytest -v
```

Run examples:
```bash
# Web module
python -m web.examples

# Terminal module
python -m terminal.examples

# Vision module
python -m vision.examples
```

## 🔐 Safety & Security

### Safety Rules
- No destructive operations without confirmation
- Forbidden patterns (rm -rf, etc.) are blocked
- Requires approval for sensitive commands
- URL validation for web requests
- Timeout protection on all operations

### Best Practices
1. Use mock backends for testing
2. Validate user input before processing
3. Handle errors gracefully
4. Cache frequently accessed pages
5. Rate limit API requests
6. Use environment variables for API keys
7. Clean up resources (close browsers, etc.)

## 📊 Performance

### Optimization Tips
1. Use `backend="mock"` for testing
2. Enable `headless=True` for browser automation
3. Implement request caching
4. Use connection pooling for multiple requests
5. Process in parallel when possible
6. Set appropriate timeouts

### Benchmarks
- API Search: ~1-2 seconds per query
- Web Scraping: ~2-5 seconds per page
- Browser Automation: ~5-10 seconds per page
- Vision Analysis: ~1-3 seconds per image

## 🛠️ Troubleshooting

### Web Module Issues

**"Selenium not installed"**
```bash
pip install selenium
```

**Search returns no results**
- Check API key environment variable
- Try mock backend: `backend="mock"`
- Verify internet connection

**Browser automation hangs**
- Check timeout settings
- Verify element selectors
- Use headless mode for speed

### Terminal Module Issues

**"Shell not found"**
```bash
which bash zsh fish
# Then update terminal.py to use available shell
```

**Timeout errors**
- Increase timeout parameter
- Check if command is actually hanging
- Use background execution for long tasks

### Vision Module Issues

**"OCR not accurate"**
- Try different backend (Tesseract vs PaddleOCR)
- Ensure image quality
- Use appropriate confidence thresholds

## 🤝 Integration Examples

### With Brain Module
```python
# Brain decides action, Router routes, Web executes
brain.decide()  # "Search for Python tutorials"
router.route()  # Routes to web_search tool
web.search("Python tutorials")
```

### With Memory Module
```python
# Store search history
memory.store("searches", {"query": "ML", "results": 10})

# Store browser state
memory.store("browser_state", web.get_browser_state())

# Retrieve later
history = memory.retrieve("searches")
```

### With Vision Module
```python
# Capture screen
web.take_screenshot("/tmp/page.png")

# Analyze with vision
vision.analyze_screen("/tmp/page.png")

# Interact with detected elements
for element in screen_data.elements:
    web.click(element.location)
```

## 📖 Documentation Files

- **[README.md](README.md)** - This file
- **[WEB_DESIGN.md](web/WEB_DESIGN.md)** - Web module design
- **[VISION_DESIGN.md](vision/VISION_DESIGN.md)** - Vision module design
- **[ARCH_LINUX_GUIDE.md](ARCH_LINUX_GUIDE.md)** - Arch Linux setup
- **[TERMINAL_TODO_GUIDE.md](TERMINAL_TODO_GUIDE.md)** - Terminal & TODO guide

## 📝 License

MIT License - Feel free to use and modify

## 🎓 Learning Resources

- Start with `web/examples.py` for web module usage
- Check `terminal/examples.py` for shell execution
- Read design docs for architecture details
- Review test files for edge cases
- Explore tool implementations in `tools/`

## 🚀 Next Steps

1. Try the web search examples
2. Configure your API keys
3. Explore browser automation
4. Integrate with your workflow
5. Build custom tools on top

---

**Happy automating! 🎉**
