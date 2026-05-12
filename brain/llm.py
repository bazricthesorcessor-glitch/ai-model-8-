"""
LLM integration - calls Groq API.
Reads config from config module only, no hardcoded values.
"""

import requests
from config import LLM_CONFIG


def get_llm_response(prompt_text: str, model: str = None) -> str:
    """
    Call Groq API model.

    Args:
        prompt_text: Prompt to send to LLM
        model: Model name (defaults to general model from config)

    Returns:
        LLM response text

    Raises:
        Exception: If API call fails
    """
    if model is None:
        model = LLM_CONFIG["general_model"]

    try:
        from groq import Groq
        from api import api as groq_api_key

        print(f"📡 Calling Groq API (llama-3.1-8b-instant)...")
        client = Groq(api_key=groq_api_key)

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": prompt_text
                }
            ],
            temperature=LLM_CONFIG["temperature"],
            top_p=LLM_CONFIG["top_p"],
            max_completion_tokens=2048,
        )

        response = completion.choices[0].message.content.strip()
        print(f"✓ Groq response received ({len(response)} chars)")
        return response

    except Exception as e:
        raise Exception(f"Groq API call failed: {str(e)}")


def get_code_llm_response(prompt_text: str) -> str:
    """
    Call code-specialized model (using Groq).
    Shortcut for code generation tasks.
    """
    return get_llm_response(prompt_text, model=LLM_CONFIG["code_model"])
