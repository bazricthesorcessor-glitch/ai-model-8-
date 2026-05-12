"""
JSON extraction utilities - robustly extract JSON from LLM responses.

LLMs often wrap JSON in markdown blocks or explanatory text:
    "Here is the plan:
    ```json
    [...]
    ```"

This module extracts the actual JSON, hiding that complexity.
"""

import json
import re
from typing import Any, Optional, Union


def extract_json_object(text: str) -> Optional[dict]:
    """
    Extract JSON object from text that may contain markdown or explanatory text.

    Handles formats like:
    - Bare JSON: {...}
    - Markdown blocks: ```json {...} ```
    - Wrapped in text: "Here's the JSON: {...}"

    Args:
        text: Text potentially containing JSON

    Returns:
        Parsed dict or None if no valid JSON found
    """
    if not text:
        return None

    # Try 1: Strip markdown code blocks
    json_match = re.search(r"```(?:json)?\s*(\{[^`]*\})\s*```", text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # Try 2: Find bare JSON object
    # Look for { ... } at various indentation levels
    brace_match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group(0))
        except json.JSONDecodeError:
            pass

    # Try 3: Try parsing the entire text (maybe it's valid JSON after stripping)
    try:
        stripped = text.strip()
        if stripped.startswith("{"):
            return json.loads(stripped)
    except json.JSONDecodeError:
        pass

    return None


def extract_json_array(text: str) -> Optional[list]:
    """
    Extract JSON array from text that may contain markdown or explanatory text.

    Handles formats like:
    - Bare JSON: [...]
    - Markdown blocks: ```json [...] ```
    - Wrapped in text: "Here are the items: [...]"

    Args:
        text: Text potentially containing JSON array

    Returns:
        Parsed list or None if no valid JSON array found
    """
    if not text:
        return None

    # Try 1: Strip markdown code blocks
    json_match = re.search(r"```(?:json)?\s*(\[[^\]`]*(?:\{[^{}]*\}[^\]`]*)*\])\s*```", text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # Try 2: Find bare JSON array
    bracket_match = re.search(r"\[[^\[\]]*(?:\{[^{}]*\}[^\[\]]*)*\]", text, re.DOTALL)
    if bracket_match:
        try:
            return json.loads(bracket_match.group(0))
        except json.JSONDecodeError:
            pass

    # Try 3: Try parsing the entire text
    try:
        stripped = text.strip()
        if stripped.startswith("["):
            return json.loads(stripped)
    except json.JSONDecodeError:
        pass

    return None


def extract_json(text: str) -> Optional[Union[dict, list]]:
    """
    Extract JSON (object or array) from text.

    Tries to parse as object first, then array.

    Args:
        text: Text potentially containing JSON

    Returns:
        Parsed JSON (dict or list) or None if not found
    """
    # Try object first
    obj = extract_json_object(text)
    if obj is not None:
        return obj

    # Try array
    arr = extract_json_array(text)
    if arr is not None:
        return arr

    return None
