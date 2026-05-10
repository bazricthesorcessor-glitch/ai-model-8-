"""
LLM integration - calls Ollama via HTTP.
Reads config from config module only, no hardcoded values.
"""

import requests
from config import LLM_CONFIG


def get_llm_response(prompt_text: str, model: str = None) -> str:
    """
    Call local Ollama model via HTTP API.
    Extracted from ai-exec.py get_local_llm_response()

    Args:
        prompt_text: Prompt to send to LLM
        model: Model name (defaults to general model from config)

    Returns:
        LLM response text

    Raises:
        requests.RequestException: If HTTP call fails
        KeyError: If response doesn't have expected format
    """
    if model is None:
        model = LLM_CONFIG["general_model"]

    try:
        response = requests.post(
            LLM_CONFIG["ollama_url"],
            json={
                "model": model,
                "prompt": prompt_text,
                "stream": False,
                "options": {
                    "temperature": LLM_CONFIG["temperature"],
                    "top_p": LLM_CONFIG["top_p"],
                },
            },
            timeout=LLM_CONFIG["timeout"],
        )
        response.raise_for_status()
        data = response.json()
        return data["response"].strip()

    except requests.exceptions.ConnectionError:
        raise Exception(
            f"Cannot connect to Ollama at {LLM_CONFIG['ollama_url']}. "
            "Make sure Ollama is running: ollama serve"
        )
    except requests.exceptions.Timeout:
        raise Exception(f"Ollama request timed out after {LLM_CONFIG['timeout']}s")
    except KeyError:
        raise Exception("Unexpected Ollama response format")


def get_code_llm_response(prompt_text: str) -> str:
    """
    Call code-specialized model (Qwen).
    Shortcut for code generation tasks.
    """
    return get_llm_response(prompt_text, model=LLM_CONFIG["code_model"])
