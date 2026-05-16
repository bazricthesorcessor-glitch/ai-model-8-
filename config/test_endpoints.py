#!/usr/bin/env python3
"""
Tests for Elzyra endpoint registry and app metadata.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    ALLOWED_WORKSPACES,
    APP_NAME,
    CONTACT_EMAIL,
    ENDPOINTS,
    endpoint_of,
)


def test_endpoint_registry_values():
    assert APP_NAME == "Elzyra"
    assert CONTACT_EMAIL == "elzyrra@gmail.com"
    assert endpoint_of("brave_cdp") == "http://127.0.0.1:9222"
    assert endpoint_of("brave_tabs") == "http://127.0.0.1:9222/json"
    assert endpoint_of("ollama") == "http://127.0.0.1:11434"
    assert endpoint_of("ollama_generate") == "http://127.0.0.1:11434/api/generate"
    assert ENDPOINTS["brave_cdp"] == endpoint_of("brave_cdp")
    assert ALLOWED_WORKSPACES == [7, 8, 9]


def test_unknown_endpoint_raises_clear_error():
    try:
        endpoint_of("missing")
    except ValueError as exc:
        assert "Endpoint not found" in str(exc)
        assert "brave_cdp" in str(exc)
    else:
        raise AssertionError("endpoint_of should reject unknown endpoint names")


def run_all_tests():
    test_endpoint_registry_values()
    print("✓ endpoint registry values")
    test_unknown_endpoint_raises_clear_error()
    print("✓ unknown endpoint error")


if __name__ == "__main__":
    run_all_tests()
