from web.cache import WebCache


def test_cache_round_trip():
    cache = WebCache(ttl_seconds=60, max_entries=10)
    cache.clear()
    cache.set("alpha", {"ok": True})
    assert cache.get("alpha") == {"ok": True}

