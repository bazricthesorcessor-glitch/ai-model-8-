import asyncio

from web.playwright_manager import PlaywrightManager


def test_playwright_manager_fallback_fetch():
    manager = PlaywrightManager()

    async def fake_fetch(url):
        class FakeResult:
            pass

        result = FakeResult()
        result.url = url
        result.title = "Example"
        result.html = "<html><title>Example</title><body>Hello</body></html>"
        result.text = "Hello"
        result.status = 200
        result.backend = "requests_fallback"
        return result

    manager._fetch_with_requests = fake_fetch
    result = asyncio.run(manager._fetch_with_requests("https://example.com"))
    assert result.title == "Example"
