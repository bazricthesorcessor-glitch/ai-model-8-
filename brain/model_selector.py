import requests

from config.settings import (
    GEMMA_API,
    LLM_CONFIG,
    OLLAMA_ENDPOINTS,
)

ROUTER_PROMPT = """
You are a routing AI.

Decide whether the task needs:
- FAST
- THINK

Rules:
- FAST = simple commands, short answers, casual chat, UI actions,googling , browsing , play songs , play something on youtube ,etc
- THINK = coding, planning, debugging, architecture, deep reasoning

Respond ONLY:
FAST
or
THINK
"""

def select_model(user_input):

    url = GEMMA_API + OLLAMA_ENDPOINTS["generate"]

    payload = {
        "model": LLM_CONFIG["router_model"],
        "prompt": f"{ROUTER_PROMPT}\n\nTask:\n{user_input}",
        "stream": False,
        "options": {
            "temperature": 0.1
        }
    }

   try:
    response = requests.post(
        url,
        json=payload,
        timeout=LLM_CONFIG["timeout"]
    )

    data = response.json()

except Exception:
    return LLM_CONFIG["general_model"]

    data = response.json()

    result = data.get("response", "").strip().upper()

    if "THINK" in result:
        return LLM_CONFIG["thinking_model"]

    return LLM_CONFIG["general_model"]
