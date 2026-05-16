#!/usr/bin/env python3
"""
Tests for Brave/CDP AI tab primitives.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.ai_tabs import AITabsManager


class FakeWindow:
    def __init__(self, title, workspace, class_name="brave-browser"):
        self.title = title
        self.workspace = workspace
        self.class_name = class_name


class FakeWorkspace:
    def __init__(self, workspace_id):
        self.id = workspace_id


class FakeHyprland:
    def __init__(self, windows=None, active_workspace=1, workspaces=None):
        self.windows = windows or []
        self.active_workspace = active_workspace
        self.workspaces = workspaces or [FakeWorkspace(i) for i in range(1, 11)]
        self.calls = []

    def list_windows(self):
        self.calls.append(("list_windows", None))
        return True, self.windows, None

    def get_workspaces(self):
        self.calls.append(("get_workspaces", None))
        return True, self.workspaces, None

    def get_active_workspace_id(self):
        self.calls.append(("get_active_workspace_id", None))
        return True, self.active_workspace, None

    def switch_workspace(self, workspace_id):
        self.calls.append(("switch_workspace", workspace_id))
        self.active_workspace = workspace_id
        return True, "ok", None


def test_focus_provider_reuses_existing_tab_in_allowed_workspace():
    hyprland = FakeHyprland(
        windows=[FakeWindow(title="ChatGPT", workspace=8)],
        active_workspace=1,
    )
    manager = AITabsManager(
        cdp_base_url="http://cdp",
        tabs_url="http://cdp/json",
        hyprland_manager=hyprland,
    )
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
    assert result["workspace"] == 8
    assert ("switch_workspace", 8) in hyprland.calls
    assert calls == ["http://cdp/json", "http://cdp/json/activate/tab-1"]


def test_focus_provider_opens_new_tab_when_match_is_outside_allowed_workspace():
    hyprland = FakeHyprland(
        windows=[FakeWindow(title="ChatGPT", workspace=3)],
        active_workspace=1,
    )
    manager = AITabsManager(
        cdp_base_url="http://cdp",
        tabs_url="http://cdp/json",
        hyprland_manager=hyprland,
    )
    manager._find_brave_binary = lambda: "/usr/bin/brave"
    manager._spawn_brave_window = lambda workspace, enable_cdp: {
        "success": True,
        "workspace": workspace,
        "workspace_name": f"workspace_{workspace}",
    }

    calls = []

    def fake_http_get(url):
        calls.append(url)
        if url == "http://cdp/json":
            return (
                True,
                '[{"id":"tab-1","type":"page","url":"https://chat.openai.com/","title":"ChatGPT"}]',
                None,
            )
        if url == "http://cdp/json/new/https%3A%2F%2Fchat.openai.com":
            return (
                True,
                '{"id":"tab-2","type":"page","url":"https://chat.openai.com","title":"ChatGPT"}',
                None,
            )
        return False, "", f"unexpected url {url}"

    manager._http_get = fake_http_get

    result = manager.focus_provider("chatgpt")

    assert result["success"] is True
    assert result["action"] == "opened"
    assert result["workspace"] == 7
    assert ("switch_workspace", 7) in hyprland.calls
    assert calls[0] == "http://cdp/json"
    assert calls[-1] == "http://cdp/json/new/https%3A%2F%2Fchat.openai.com"


def test_list_tabs_returns_clear_error_when_cdp_unavailable():
    manager = AITabsManager(cdp_base_url="http://cdp", tabs_url="http://cdp/json")
    manager._http_get = lambda url: (False, "", "Brave CDP unavailable")

    result = manager.list_tabs()

    assert result["success"] is False
    assert result["tabs"] == []
    assert "Brave CDP unavailable" in result["error"]


def run_all_tests():
    test_focus_provider_reuses_existing_tab_in_allowed_workspace()
    print("✓ focus_provider reuses existing tab in allowed workspace")
    test_focus_provider_opens_new_tab_when_match_is_outside_allowed_workspace()
    print("✓ focus_provider opens a new tab when existing match is outside allowed workspace")
    test_list_tabs_returns_clear_error_when_cdp_unavailable()
    print("✓ CDP unavailable returns clear error")


if __name__ == "__main__":
    run_all_tests()
