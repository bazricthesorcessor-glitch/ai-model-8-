import asyncio

from schemas import ArticleSummary
from web.graph_manager import GraphManager


def test_graph_manager_fallback_path():
    manager = GraphManager()

    async def fake_page(url):
        class Page:
            pass

        page = Page()
        page.title = "Example"
        page.url = url
        page.html = "<html><body>Example article text</body></html>"
        page.text = "Example article text"
        page.status = 200
        page.backend = "requests_fallback"
        return page

    manager.playwright.fetch_page = fake_page
    manager.ollama.generate = lambda **kwargs: {
        "success": True,
        "result": {"response": '{"title":"Example","summary":"Summary","key_points":["One"]}'},
        "error": None,
    }

    result = asyncio.run(manager._run_local_semantic_extract("https://example.com", "summarize", ArticleSummary))
    assert result["success"] is True
    assert result["result"]["title"] == "Example"
