"""
Action Parser - Parse LLM responses into valid action structures.

Converts LLM JSON responses into executable action format.
Handles errors gracefully with fallback logic.
"""

from typing import Dict, Any, Optional, List
import json


def parse_action_response(
    llm_response: str, tool_schemas: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Parse LLM response into action structure.

    Expected LLM response format:
    ```json
    {
        "steps": [
            {"tool_name": "web_search", "params": {"query": "..."}},
            {"tool_name": "fetch_page", "params": {"url": "..."}}
        ],
        "reasoning": "explanation of steps"
    }
    ```

    Args:
        llm_response: Raw LLM response text
        tool_schemas: Available tool schemas for validation (optional)

    Returns:
        Dict with keys:
            - steps: List of executable steps
            - reasoning: Explanation
            - context: Any additional context
    """
    try:
        # Try to extract JSON from response
        parsed = _extract_json(llm_response)

        if not parsed:
            # Fallback if no JSON found
            return _create_fallback_action(llm_response)

        # Validate and clean steps
        steps = parsed.get("steps", [])
        if not isinstance(steps, list):
            steps = [steps]

        # Validate each step
        validated_steps = []
        for step in steps:
            valid_step = _validate_step(step, tool_schemas)
            if valid_step:
                validated_steps.append(valid_step)

        if not validated_steps:
            return _create_fallback_action(llm_response)

        return {
            "steps": validated_steps,
            "reasoning": parsed.get("reasoning", ""),
            "context": {"llm_parsed": True},
        }

    except Exception as e:
        # Fallback on any parsing error
        return _create_fallback_action(llm_response, error=str(e))


def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract JSON object from text response.

    Handles LLM responses that include explanations around JSON.

    Args:
        text: Response text

    Returns:
        Parsed JSON dict or None
    """
    # Try direct JSON parsing first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON block in text
    start_idx = text.find("{")
    end_idx = text.rfind("}") + 1

    if start_idx != -1 and end_idx > start_idx:
        try:
            json_str = text[start_idx:end_idx]
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass

    # Try to find JSON in code blocks
    for prefix in ["```json", "```"]:
        if prefix in text:
            start = text.find(prefix) + len(prefix)
            end = text.find("```", start)
            if end > start:
                try:
                    return json.loads(text[start:end].strip())
                except json.JSONDecodeError:
                    pass

    return None


def _validate_step(
    step: Any, tool_schemas: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """
    Validate a single action step.

    Args:
        step: Step dict to validate
        tool_schemas: Available tool schemas (optional validation)

    Returns:
        Valid step dict or None
    """
    # Must be a dict
    if not isinstance(step, dict):
        return None

    # Must have tool_name
    tool_name = step.get("tool_name") or step.get("tool")
    if not tool_name or not isinstance(tool_name, str):
        return None

    # Get params (may be under "params" or "data" or "arguments")
    params = step.get("params") or step.get("data") or step.get("arguments") or {}

    if not isinstance(params, dict):
        return None

    # Build validated step
    valid_step = {
        "tool": tool_name,
        "data": params,  # Keep as "data" for backward compatibility
        "params": params,  # Also include as "params"
    }

    # Add optional fields
    if "stop_on_error" in step:
        valid_step["stop_on_error"] = bool(step["stop_on_error"])

    if "max_retries" in step:
        try:
            valid_step["max_retries"] = int(step["max_retries"])
        except (ValueError, TypeError):
            pass

    # Optional: validate against tool schemas
    if tool_schemas and tool_name not in tool_schemas:
        # Tool not found in available schemas
        return None

    return valid_step


def _create_fallback_action(
    response: str, error: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create fallback action when parsing fails.

    Uses internal LLM reasoning as fallback.

    Args:
        response: LLM response text
        error: Parsing error message

    Returns:
        Fallback action dict
    """
    return {
        "steps": [
            {
                "tool": "internal_reasoning",
                "data": {"query": response},
                "params": {"query": response},
            }
        ],
        "reasoning": "LLM response parsing failed; using internal reasoning",
        "context": {
            "llm_parsed": False,
            "fallback": True,
            "parse_error": error,
        },
    }


# ============================================================================
# UTILITY: Build LLM prompt with tool schemas
# ============================================================================


def build_action_prompt(
    user_query: str,
    tool_schemas: Dict[str, Any],
    tier_info: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Build prompt for LLM to generate action steps.

    Args:
        user_query: User's request
        tool_schemas: Available tool schemas
        tier_info: Knowledge tier routing information
        context: Execution context

    Returns:
        Formatted prompt string
    """
    context = context or {}

    prompt = f"""You are an AI assistant that helps execute user requests.

User Query: {user_query}
"""

    if tier_info:
        prompt += f"""
Knowledge Tier Selected: {tier_info.get('tier', 'unknown')}
Reasoning: {tier_info.get('reasoning', '')}
Fallback Chain: {' → '.join(tier_info.get('fallback_chain', []))}
"""

    prompt += f"""
Available Tools:
{json.dumps(tool_schemas, indent=2)}

Generate a sequence of action steps to fulfill the user's request.

Return VALID JSON with this structure:
{{
    "steps": [
        {{"tool_name": "<tool_name>", "params": {{"<param>": "<value>"}}}},
        ...
    ],
    "reasoning": "why these steps will fulfill the request"
}}

Important:
- Only use tools from the available list above
- Use tool_name exactly as shown in the schemas
- Include all required parameters for each tool
- Keep steps focused and minimal
- Return ONLY valid JSON, no other text
"""

    return prompt
