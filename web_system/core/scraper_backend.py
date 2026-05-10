"""
Web scraping backend.
Fetches page content and extracts structured data (text, links, metadata, images).
Stateless, pure transformation: URL → page content.
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
import requests
from urllib.parse import urljoin, urlparse
from html.parser import HTMLParser
import json


@dataclass
class PageLink:
    """Link found on a page."""
    text: str
    url: str
    title: Optional[str] = None
    is_internal: bool = False


@dataclass
class PageImage:
    """Image found on a page."""
    src: str
    alt: str
    title: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None


@dataclass
class ScrapedPageContent:
    """Extracted page content."""
    url: str
    title: str
    text: str
    html: str
    links: List[PageLink] = field(default_factory=list)
    images: List[PageImage] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    status_code: int = 200
    timestamp: float = 0.0


class HtmlExtractor(HTMLParser):
    """Extract structured data from HTML."""

    def __init__(self, base_url: str = ""):
        super().__init__()
        self.base_url = base_url
        self.text_parts = []
        self.links = []
        self.images = []
        self.in_script = False
        self.in_style = False
        self.title = ""
        self.in_title = False
        self.metadata = {}

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        if tag == "title":
            self.in_title = True
        elif tag == "script":
            self.in_script = True
        elif tag == "style":
            self.in_style = True
        elif tag == "a":
            url = attrs_dict.get("href", "")
            title = attrs_dict.get("title", "")
            if url:
                full_url = urljoin(self.base_url, url)
                is_internal = urlparse(full_url).netloc == urlparse(self.base_url).netloc
                self.links.append(PageLink(
                    text="",
                    url=full_url,
                    title=title,
                    is_internal=is_internal,
                ))
        elif tag == "img":
            src = attrs_dict.get("src", "")
            if src:
                full_src = urljoin(self.base_url, src)
                self.images.append(PageImage(
                    src=full_src,
                    alt=attrs_dict.get("alt", ""),
                    title=attrs_dict.get("title"),
                    width=int(attrs_dict.get("width", 0)) or None,
                    height=int(attrs_dict.get("height", 0)) or None,
                ))
        elif tag == "meta":
            name = attrs_dict.get("name", "").lower()
            content = attrs_dict.get("content", "")
            if name:
                self.metadata[name] = content

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag == "script":
            self.in_script = False
        elif tag == "style":
            self.in_style = False

    def handle_data(self, data):
        if not self.in_script and not self.in_style:
            if self.in_title:
                self.title += data.strip()
            else:
                text = data.strip()
                if text:
                    self.text_parts.append(text)

    def get_text(self) -> str:
        """Get extracted text."""
        return "\n".join(self.text_parts)

    def finalize(self):
        """Fix link text that was parsed."""
        # This is a simplified approach - in production, track text differently
        pass


class ScraperBackend:
    """
    Web scraping backend.
    Pure transformation: URL → page content
    """

    def __init__(self, timeout: int = 10, user_agent: str = None):
        """
        Initialize scraper backend.

        Args:
            timeout: Request timeout in seconds
            user_agent: Custom User-Agent header
        """
        self.timeout = timeout
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

    def fetch_page(
        self,
        url: str,
        **kwargs
    ) -> Tuple[bool, Optional[ScrapedPageContent], Optional[str]]:
        """
        Fetch and parse a web page.

        Args:
            url: Page URL
            **kwargs: Additional requests parameters

        Returns:
            (success: bool, content: Optional[ScrapedPageContent], error: Optional[str])
        """
        if not url or not url.strip():
            return False, None, "URL cannot be empty"

        try:
            headers = {"User-Agent": self.user_agent}
            response = requests.get(
                url,
                headers=headers,
                timeout=self.timeout,
                **kwargs
            )

            # Don't raise for 4xx/5xx - return with status code
            html_content = response.text

            # Extract content
            extractor = HtmlExtractor(base_url=url)
            try:
                extractor.feed(html_content)
            except Exception:
                # HTML parsing error - continue with partial data
                pass

            # Build result
            content = ScrapedPageContent(
                url=url,
                title=extractor.title,
                text=extractor.get_text(),
                html=html_content,
                links=extractor.links,
                images=extractor.images,
                metadata=extractor.metadata,
                status_code=response.status_code,
            )

            # Import time for timestamp
            import time
            content.timestamp = time.time()

            return True, content, None

        except requests.exceptions.RequestException as e:
            return False, None, f"Failed to fetch page: {str(e)}"
        except Exception as e:
            return False, None, f"Error processing page: {str(e)}"

    def extract_text(
        self,
        page_content: ScrapedPageContent
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Extract readable text from page content.

        Args:
            page_content: ScrapedPageContent object

        Returns:
            (success: bool, text: Optional[str], error: Optional[str])
        """
        try:
            return True, page_content.text, None
        except Exception as e:
            return False, None, str(e)

    def extract_links(
        self,
        page_content: ScrapedPageContent,
        internal_only: bool = False
    ) -> Tuple[bool, Optional[List[PageLink]], Optional[str]]:
        """
        Extract links from page content.

        Args:
            page_content: ScrapedPageContent object
            internal_only: Only return internal links

        Returns:
            (success: bool, links: Optional[List[PageLink]], error: Optional[str])
        """
        try:
            links = page_content.links
            if internal_only:
                links = [l for l in links if l.is_internal]

            return True, links, None
        except Exception as e:
            return False, None, str(e)

    def extract_images(
        self,
        page_content: ScrapedPageContent
    ) -> Tuple[bool, Optional[List[PageImage]], Optional[str]]:
        """
        Extract images from page content.

        Args:
            page_content: ScrapedPageContent object

        Returns:
            (success: bool, images: Optional[List[PageImage]], error: Optional[str])
        """
        try:
            return True, page_content.images, None
        except Exception as e:
            return False, None, str(e)

    def extract_metadata(
        self,
        page_content: ScrapedPageContent
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract metadata from page content.

        Args:
            page_content: ScrapedPageContent object

        Returns:
            (success: bool, metadata: Optional[Dict], error: Optional[str])
        """
        try:
            metadata = {
                "title": page_content.title,
                "url": page_content.url,
                "status_code": page_content.status_code,
                "content_length": len(page_content.html),
                "text_length": len(page_content.text),
                "links_count": len(page_content.links),
                "images_count": len(page_content.images),
                "page_metadata": page_content.metadata,
            }
            return True, metadata, None
        except Exception as e:
            return False, None, str(e)
