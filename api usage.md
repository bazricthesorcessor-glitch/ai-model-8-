````md
# AVRIL GROQ API SETUP

==================================================
1. INSTALL REQUIRED PACKAGES
==================================================

```bash
pip install groq
````

Optional:

```bash
pip install python-dotenv
```

==================================================
2. CREATE api.py
================
==================================================
3. IMPORT API ANYWHERE
======================

```python
from api import api
```

Now `api` contains the selected Groq API key.

==================================================
4. BASIC GROQ CONNECTION
========================

```python
from groq import Groq
from api import api

client = Groq(api_key=api)
```

==================================================
5. BASIC MODEL REQUEST
======================

```python
response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "user",
            "content": "Hello"
        }
    ]
)

print(response.choices[0].message.content)
```

==================================================
6. AVRIL MODEL STACK
====================

| Model         | Purpose              |
| ------------- | -------------------- |
| Llama 4 Scout | Vision + Memory      |
| Llama 3.1 8B  | Fast UI Executor     |
| Qwen3 32B     | Coding + Engineering |
| GPT-OSS 120B  | Deep Thinking        |

==================================================
7. MODEL NAMES
==============

```python
VISION_MODEL = "meta-llama/llama-4-scout"

EXECUTOR_MODEL = "llama-3.1-8b-instant"

CODING_MODEL = "qwen/qwen3-32b"

THINKING_MODEL = "openai/gpt-oss-120b"
```

==================================================
8. EXAMPLE MODEL USAGE
======================

# Vision

```python
model=VISION_MODEL
```

Used for:

* OCR
* screenshots
* UI understanding
* memory/context

---

# Fast UI Executor

```python
model=EXECUTOR_MODEL
```

Used for:

* browser control
* opening apps
* songs/videos
* fast actions

---

# Coding

```python
model=CODING_MODEL
```

Used for:

* coding
* debugging
* engineering

---

# Deep Thinking

```python
model=THINKING_MODEL
```

Used for:

* planning
* architecture
* deep reasoning

==================================================
9. SUGGESTED STRUCTURE
======================

```text
project/
│
├── api.py
├── main.py
├── brain.py
├── router.py
│
├── core/
│   ├── model_selector.py
│   └── groq_client.py
│
├── config/
│   └── models.py
│
└── memory/
```

==================================================
10. IMPORTANT NOTES
===================

* Do NOT hardcode API keys in multiple files
* Keep all keys only inside `api.py`
* Never upload real keys publicly
* Add `api.py` to `.gitignore`

Example `.gitignore`:

```text
api.py
__pycache__/
```

==================================================
11. DESIGN PHILOSOPHY
=====================

Instead of:

* one giant model

Use:

* specialized AI roles

Benefits:

* faster
* more stable
* easier upgrades
* lower latency
* better reasoning separation

```
```
