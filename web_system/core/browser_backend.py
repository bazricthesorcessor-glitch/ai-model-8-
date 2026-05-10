"""
Browser automation backend.
Selenium/Playwright for human-like web interactions (click, type, navigate, wait).
Integrates with vision for element detection and keyboard/mouse for interactions.
"""

from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum
import time


class BrowserType(Enum):
    """Supported browsers."""
    CHROME = "chrome"
    FIREFOX = "firefox"
    SAFARI = "safari"
    EDGE = "edge"
    MOCK = "mock"


@dataclass
class BrowserState:
    """Current browser state."""
    current_url: str
    title: str
    window_size: Tuple[int, int]
    is_headless: bool
    cookies: List[Dict[str, str]]
    local_storage: Dict[str, str]


class BrowserAutomationBackend:
    """
    Browser automation using Selenium.
    Enables human-like web interactions: navigate, click, type, wait, screenshot.
    """

    def __init__(
        self,
        browser_type: str = "chrome",
        headless: bool = True,
        timeout: int = 10
    ):
        """
        Initialize browser automation backend.

        Args:
            browser_type: Browser type (chrome, firefox, safari, edge, mock)
            headless: Run browser in headless mode
            timeout: Default timeout for operations
        """
        self.browser_type = browser_type
        self.headless = headless
        self.timeout = timeout
        self.driver = None
        self.is_mock = browser_type == "mock"

        # Lazy load selenium only when needed
        self.webdriver = None
        self.By = None
        self.WebDriverWait = None
        self.EC = None

    def _init_selenium(self):
        """Initialize selenium lazily."""
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            self.webdriver = webdriver
            self.By = By
            self.WebDriverWait = WebDriverWait
            self.EC = EC
        except ImportError:
            raise ImportError(
                "Selenium not installed. Install with: pip install selenium"
            )

    def start(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Start browser session.

        Returns:
            (success: bool, message: Optional[str], error: Optional[str])
        """
        try:
            if self.is_mock:
                return True, "Mock browser started", None

            # Lazy load selenium when needed
            if self.webdriver is None:
                self._init_selenium()

            if self.browser_type == "chrome":
                options = self.webdriver.ChromeOptions()
                if self.headless:
                    options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                self.driver = self.webdriver.Chrome(options=options)
            elif self.browser_type == "firefox":
                options = self.webdriver.FirefoxOptions()
                if self.headless:
                    options.add_argument("--headless")
                self.driver = self.webdriver.Firefox(options=options)
            elif self.browser_type == "edge":
                options = self.webdriver.EdgeOptions()
                if self.headless:
                    options.add_argument("--headless")
                self.driver = self.webdriver.Edge(options=options)
            else:
                return False, None, f"Unsupported browser: {self.browser_type}"

            self.driver.set_page_load_timeout(self.timeout)
            return True, f"{self.browser_type} browser started", None

        except Exception as e:
            return False, None, str(e)

    def navigate(
        self,
        url: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Navigate to URL.

        Args:
            url: Target URL

        Returns:
            (success: bool, current_url: Optional[str], error: Optional[str])
        """
        if not url:
            return False, None, "URL cannot be empty"

        try:
            if self.is_mock:
                return True, url, None

            if not self.driver:
                return False, None, "Browser not started"

            self.driver.get(url)
            return True, self.driver.current_url, None

        except Exception as e:
            return False, None, str(e)

    def click_element(
        self,
        selector: str,
        by_type: str = "xpath"
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Click an element.

        Args:
            selector: Element selector (XPath, CSS, ID, etc.)
            by_type: Selector type (xpath, css, id, class_name, link_text, tag_name)

        Returns:
            (success: bool, message: Optional[str], error: Optional[str])
        """
        try:
            if self.is_mock:
                return True, f"Clicked {selector}", None

            if not self.driver:
                return False, None, "Browser not started"

            # Map string to By constant
            by_map = {
                "xpath": self.By.XPATH,
                "css": self.By.CSS_SELECTOR,
                "id": self.By.ID,
                "class": self.By.CLASS_NAME,
                "link": self.By.LINK_TEXT,
                "tag": self.By.TAG_NAME,
            }
            by = by_map.get(by_type, self.By.XPATH)

            element = self.WebDriverWait(self.driver, self.timeout).until(
                self.EC.element_to_be_clickable((by, selector))
            )
            element.click()
            return True, "Element clicked", None

        except Exception as e:
            return False, None, str(e)

    def type_text(
        self,
        selector: str,
        text: str,
        by_type: str = "xpath",
        clear_first: bool = True
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Type text into an element.

        Args:
            selector: Element selector
            text: Text to type
            by_type: Selector type
            clear_first: Clear field before typing

        Returns:
            (success: bool, message: Optional[str], error: Optional[str])
        """
        try:
            if self.is_mock:
                return True, f"Typed '{text}' into {selector}", None

            if not self.driver:
                return False, None, "Browser not started"

            by_map = {
                "xpath": self.By.XPATH,
                "css": self.By.CSS_SELECTOR,
                "id": self.By.ID,
                "class": self.By.CLASS_NAME,
            }
            by = by_map.get(by_type, self.By.XPATH)

            element = self.WebDriverWait(self.driver, self.timeout).until(
                self.EC.presence_of_element_located((by, selector))
            )

            if clear_first:
                element.clear()

            element.send_keys(text)
            return True, "Text entered", None

        except Exception as e:
            return False, None, str(e)

    def get_page_source(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Get current page HTML.

        Returns:
            (success: bool, html: Optional[str], error: Optional[str])
        """
        try:
            if self.is_mock:
                return True, "<html><body>Mock page</body></html>", None

            if not self.driver:
                return False, None, "Browser not started"

            return True, self.driver.page_source, None

        except Exception as e:
            return False, None, str(e)

    def get_title(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Get current page title.

        Returns:
            (success: bool, title: Optional[str], error: Optional[str])
        """
        try:
            if self.is_mock:
                return True, "Mock Page", None

            if not self.driver:
                return False, None, "Browser not started"

            return True, self.driver.title, None

        except Exception as e:
            return False, None, str(e)

    def get_current_url(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Get current URL.

        Returns:
            (success: bool, url: Optional[str], error: Optional[str])
        """
        try:
            if self.is_mock:
                return True, "https://example.com", None

            if not self.driver:
                return False, None, "Browser not started"

            return True, self.driver.current_url, None

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
            timeout: Wait timeout (uses default if None)

        Returns:
            (success: bool, message: Optional[str], error: Optional[str])
        """
        try:
            if self.is_mock:
                return True, "Element found", None

            if not self.driver:
                return False, None, "Browser not started"

            wait_time = timeout or self.timeout
            by_map = {
                "xpath": self.By.XPATH,
                "css": self.By.CSS_SELECTOR,
                "id": self.By.ID,
                "class": self.By.CLASS_NAME,
            }
            by = by_map.get(by_type, self.By.XPATH)

            self.WebDriverWait(self.driver, wait_time).until(
                self.EC.presence_of_element_located((by, selector))
            )
            return True, "Element found", None

        except Exception as e:
            return False, None, str(e)

    def take_screenshot(
        self,
        filepath: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Take screenshot of current page.

        Args:
            filepath: Where to save screenshot

        Returns:
            (success: bool, filepath: Optional[str], error: Optional[str])
        """
        try:
            if self.is_mock:
                return True, filepath, None

            if not self.driver:
                return False, None, "Browser not started"

            self.driver.save_screenshot(filepath)
            return True, filepath, None

        except Exception as e:
            return False, None, str(e)

    def close(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Close browser session.

        Returns:
            (success: bool, message: Optional[str], error: Optional[str])
        """
        try:
            if self.is_mock:
                return True, "Mock browser closed", None

            if self.driver:
                self.driver.quit()
            return True, f"{self.browser_type} browser closed", None

        except Exception as e:
            return False, None, str(e)

    def get_state(self) -> Tuple[bool, Optional[BrowserState], Optional[str]]:
        """
        Get current browser state.

        Returns:
            (success: bool, state: Optional[BrowserState], error: Optional[str])
        """
        try:
            if self.is_mock:
                return True, BrowserState(
                    current_url="https://example.com",
                    title="Mock Page",
                    window_size=(1920, 1080),
                    is_headless=self.headless,
                    cookies=[],
                    local_storage={}
                ), None

            if not self.driver:
                return False, None, "Browser not started"

            cookies = []
            try:
                cookies = self.driver.get_cookies()
            except:
                pass

            state = BrowserState(
                current_url=self.driver.current_url,
                title=self.driver.title,
                window_size=self.driver.get_window_size().values(),
                is_headless=self.headless,
                cookies=cookies,
                local_storage={}
            )

            return True, state, None

        except Exception as e:
            return False, None, str(e)
