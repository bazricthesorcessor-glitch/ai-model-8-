"""
LLM integration - calls models by role.
Supports role-based model selection: router_model, coding_model, deep_thinking_model, etc.
"""

import requests
from config import LLM_CONFIG


def get_llm_response(prompt_text: str, role: str = "router_model") -> str:
    """
    Call LLM using role-based model selection.

    Args:
        prompt_text: Prompt to send to LLM
        role: Model role from config (router_model, coding_model, deep_thinking_model, etc)

    Returns:
        LLM response text

    Raises:
        Exception: If API call fails or role not found
    """
    # Validate role exists in config
    if role not in LLM_CONFIG:
        available_roles = [k for k in LLM_CONFIG.keys() if k.endswith("_model")]
        raise ValueError(f"Unknown role '{role}'. Available: {available_roles}")

    model_name = LLM_CONFIG[role]

    try:
        # For now, assume all models are served via Ollama
        # This is a compatibility layer that can be extended later
        url = LLM_CONFIG["ollama_url"]

        payload = {
            "model": model_name,
            "prompt": prompt_text,
            "stream": False,
        }

        response = requests.post(url, json=payload, timeout=LLM_CONFIG["timeout"])
        response.raise_for_status()

        data = response.json()
        result = data.get("response", "").strip()

        print(f"📡 LLM response received ({len(result)} chars) via {role}")
        return result

    except Exception as e:
        raise Exception(f"LLM call failed ({role}): {str(e)}")


def get_coding_response(prompt_text: str) -> str:
    """Shortcut for code generation using coding_model role."""
    return get_llm_response(prompt_text, role="coding_model")


def get_thinking_response(prompt_text: str) -> str:
    """Shortcut for deep reasoning using deep_thinking_model role."""
    return get_llm_response(prompt_text, role="deep_thinking_model")


def get_fast_response(prompt_text: str) -> str:
    """Shortcut for fast execution using fast_executor_model role."""
    return get_llm_response(prompt_text, role="fast_executor_model")
