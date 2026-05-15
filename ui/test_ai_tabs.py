#!/usr/bin/env python3
"""
Tests for Brave/CDP AI tab primitives.
"""

from ui.ai_tabs import AITabsManager


def test_focus_provider_reuses_existing_tab():
    manager = AITabsManager(cdp_base_url="http://cdp", tabs_url="http://cdp/json")
    calls = []

    def fake_http_get(url):
        calls.append(url)
        if url == "http://cdp/json":
            return (
                True,
                '[{"id":"tab-1","type":"page","url":"https://chat.openai.com/","title":"ChatGPT"}]',
                None,
            )
        if url == "http://cdp/json/activate/tab-1":
            return True, "Target activated", None
        return False, "", f"unexpected url {url}"

    manager._http_get = fake_http_get

    result = manager.focus_provider("chatgpt")

    assert result["success"] is True
    assert result["action"] == "focused"
    assert result["tab"]["id"] == "tab-1"
    assert calls == ["http://cdp/json", "http://cdp/json/activate/tab-1"]


def test_focus_provider_opens_tab_when_missing():
    manager = AITabsManager(cdp_base_url="http://cdp", tabs_url="http://cdp/json")
    calls = []

    def fake_http_get(url):
        calls.append(url)
        if url == "http://cdp/json":
            return True, "[]", None
        if url == "http://cdp/json/new/https%3A%2F%2Fclaude.ai":
            return (
                True,
                '{"id":"tab-2","type":"page","url":"https://claude.ai","title":"Claude"}',
                None,
            )
        return False, "", f"unexpected url {url}"

    manager._http_get = fake_http_get

    result = manager.focus_provider("claude")

    assert result["success"] is True
    assert result["action"] == "opened"
    assert result["tab_id"] == "tab-2"
    assert calls == [
        "http://cdp/json",
        "http://cdp/json/new/https%3A%2F%2Fclaude.ai",
    ]


def test_list_tabs_returns_clear_error_when_cdp_unavailable():
    manager = AITabsManager(cdp_base_url="http://cdp", tabs_url="http://cdp/json")
    manager._http_get = lambda url: (False, "", "Brave CDP unavailable")

    result = manager.list_tabs()

    assert result["success"] is False
    assert result["tabs"] == []
    assert "Brave CDP unavailable" in result["error"]


def run_all_tests():
    test_focus_provider_reuses_existing_tab()
    print("✓ focus_provider reuses existing tab")
    test_focus_provider_opens_tab_when_missing()
    print("✓ focus_provider opens missing tab")
    test_list_tabs_returns_clear_error_when_cdp_unavailable()
    print("✓ CDP unavailable returns clear error")


if __name__ == "__main__":
    run_all_tests()
