"""
Brain core logic - intent detection, safety checking, action generation.
Extracted from ai-exec.py and refactored for modularity.
"""

from config import SAFETY_RULES, INTENT_CONFIG


def is_conversational(text: str) -> bool:
    """
    Check if user wants a conversation vs a command.
    Extracted from ai-exec.py is_conversational()
    """
    text_lower = text.lower().strip()

    # Greetings
    if text_lower in INTENT_CONFIG["greetings"]:
        return True

    # Questions
    if any(kw in text_lower for kw in INTENT_CONFIG["conversational_keywords"]):
        return True

    # Ends with question mark
    if text.endswith("?"):
        return True

    return False


def check_safety(command: str) -> tuple:
    """
    Check if command is safe to execute.
    Returns (is_safe: bool, severity: 'safe'|'warning'|'blocked', reason: str)
    Extracted from ai-exec.py check_safety()
    """
    forbidden = SAFETY_RULES["forbidden_patterns"]
    confirmation = SAFETY_RULES["requires_confirmation"]

    # Check forbidden patterns (absolute block)
    for pattern in forbidden:
        if pattern in command:
            return False, "blocked", f"Matches forbidden pattern: '{pattern}'"

    # Check patterns requiring confirmation
    for pattern in confirmation:
        if pattern in command:
            return True, "warning", f"Potentially destructive: '{pattern}'"

    # Generic sudo check
    if command.startswith("sudo") and not any(
        x in command for x in ["pacman", "systemctl", "nano", "chmod"]
    ):
        return True, "warning", "Generic sudo command - review carefully"

    # Shell pipe check
    for warning_pattern in SAFETY_RULES["warning_patterns"]:
        if warning_pattern in command:
            return True, "warning", "Piping into a shell interpreter"

    return True, "safe", "Passed all safety checks"


def analyze_intent(user_input: str) -> dict:
    """
    Analyze user input to determine intent type.

    Returns:
        dict with:
            - intent: "conversational" or "command"
            - raw_input: original user input
            - is_question: bool
    """
    if not user_input or not user_input.strip():
        return {"intent": "invalid", "raw_input": user_input}

    is_conv = is_conversational(user_input)

    return {
        "intent": "conversational" if is_conv else "command",
        "raw_input": user_input,
        "is_question": user_input.endswith("?"),
    }


def generate_action(user_input, context=None, model=None) -> dict:
    """
    Generate a structured action from user input using LLM and tool schemas.

    Flow:
    1. Route query to appropriate knowledge tier
    2. Get available tool schemas from registry
    3. Call LLM with formatted prompt and tool list
    4. Parse LLM response into action steps
    5. Return executable action

    Args:
        user_input: User's request
        context: Prior execution context

    Returns:
        dict with:
            - action: "execute", "record_state", etc.
            - platform: "cli", "gui", "vision", etc.
            - mode: "visible", "headless", "hybrid"
            - steps: list of execution steps
            - context: execution context including tier info
    """
    from tools.knowledge_router import route_query
    from tools import REGISTRY
    from brain.llm import get_llm_response
    from brain.action_parser import parse_action_response, build_action_prompt

    context = context or {}

    try:
        # Step 1: Route query to knowledge tier
        tier_info = route_query(user_input, context)
        context["knowledge_tier"] = tier_info

        # Step 2: Get tool schemas from registry
        tool_schemas = REGISTRY.export_schemas()

        # Step 3: Build prompt with tool schemas and tier info
        prompt = build_action_prompt(user_input, tool_schemas, tier_info, context)

        # Step 4: Call LLM to generate action
        llm_response = get_llm_response(prompt, model=model)

        # Step 5: Parse LLM response into action steps
        action_result = parse_action_response(llm_response, tool_schemas)

        # Step 6: Determine platform and mode based on first tool
        steps = action_result.get("steps", [])
        platform = "cli"  # Default
        mode = "headless"  # Default

        if steps:
            first_tool_name = steps[0].get("tool", "")
            first_tool = REGISTRY.get(first_tool_name)
            if first_tool:
                platform = first_tool.platform

            # Use visible mode for important operations
            if platform in ["gui", "web"]:
                mode = "visible"

        return {
            "action": "execute",
            "platform": platform,
            "mode": mode,
            "steps": steps,
            "context": context,
        }

    except Exception as e:
        # Fallback if anything fails
        return {
            "action": "execute",
            "platform": "cli",
            "mode": "visible",
            "steps": [
                {
                    "tool": "internal_reasoning",
                    "data": {"query": user_input},
                    "params": {"query": user_input},
                }
            ],
            "context": {
                **context,
                "error": str(e),
                "fallback": True,
            },
        }
