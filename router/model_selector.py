import requests
from groq import Groq

from config.settings import (
    LLM_CONFIG,
)

ROUTER_PROMPT = """
You are a routing AI.

Decide whether the task needs:
- FAST
- THINK

Rules:
- FAST = simple commands, short answers, casual chat, UI actions, googling, browsing, play songs, play something on youtube, etc
- THINK = coding, planning, debugging, architecture, deep reasoning

Respond ONLY:
FAST
or
THINK
"""

def select_model(user_input):
    """
    Select routing model with fallback strategy:
    1. Try groq
    2. On error, fallback to llama3.2:3b
    """

    # Strategy 1: Try Groq first
    try:
        from api import api as groq_api_key

        client = Groq(api_key=groq_api_key)

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": f"{ROUTER_PROMPT}\n\nTask:\n{user_input}"
                }
            ],
            temperature=0.1
        )

        result = response.choices[0].message.content.strip().upper()
        print("✓ Groq API started successfully")

        if "THINK" in result:
            return "groq"

        return "groq"

    except Exception as e:
        print(f"✗ Groq failed: {str(e)}")
        print("→ Falling back to llama3.2:3b")

        # Strategy 2: Fallback to llama3.2:3b via OLLAMA
        try:
            url = LLM_CONFIG["ollama_url"]
            payload = {
                "model": "llama3.2:3b",
                "prompt": f"{ROUTER_PROMPT}\n\nTask:\n{user_input}",
                "stream": False,
                "options": {
                    "temperature": 0.1
                }
            }

            response = requests.post(
                url,
                json=payload,
                timeout=LLM_CONFIG["timeout"]
            )

            data = response.json()
            result = data.get("response", "").strip().upper()
            print("✓ llama3.2:3b started successfully")

            if "THINK" in result:
                return "llama3.2:3b"

            return "llama3.2:3b"

        except Exception as e2:
            print(f"✗ llama3.2:3b also failed: {str(e2)}")
            print("→ Using llama3.2:3b as final fallback")
            return "llama3.2:3b"
