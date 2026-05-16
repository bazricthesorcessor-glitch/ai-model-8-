from web.scrape_service import SemanticScrapeService


def test_semantic_extract_caches_success():
    service = SemanticScrapeService()
    service.cache.clear()
    calls = {"count": 0}

    async def fake_run(url, prompt, schema=None):
        calls["count"] += 1
        return {"success": True, "result": {"url": url, "summary": prompt}, "error": None}

    service.graphs.run_semantic_extract = fake_run

    first = service.semantic_extract("https://example.com", "extract")
    second = service.semantic_extract("https://example.com", "extract")

    assert first["success"] is True
    assert second["success"] is True
    assert calls["count"] == 1
