"""
Settings configuration - extracted from ai-exec.py
All system configuration centralized here.
"""

import os
from datetime import datetime


OLLAMA_ENDPOINTS = {
    "generate": "/api/generate",
}



# ===== SCREEN CONFIGURATION =====
SCREEN_CONFIG = {
    "width": 1920,
    "height": 1200,
    "refresh_rate": 60,
    "dpi": 96,
}

# ===== LLM CONFIGURATION =====
LLM_CONFIG = {
    "router_model": "llama3.2:3b",
    "general_model": "llama3.2:3b",
    "thinking_model" : "gemma4:26b",
    "code_model": "llama3.2:3b",
    "ollama_url": "http://localhost:11434/api/generate",
    "temperature": 0.3,
    "top_p": 0.9,
    "timeout": 120,
}

# ===== SAFETY RULES =====
SAFETY_RULES = {
    "forbidden_patterns": [
        "rm -rf /",
        "rm -rf ~",
        "dd if=",
        "mkfs",
        "> /dev/sd",
        "chmod 777 /",
        "chmod -R 777",
        "curl * | bash",
        "curl * | sh",
        "wget * | sh",
        "wget * | bash",
        ":(){ :|:& };:",
        "mv /* ",
        "pacman -Syu --noconfirm",
    ],
    "requires_confirmation": [
        "sudo rm",
        "sudo pacman -R",
        "systemctl stop",
        "systemctl disable",
        "git push --force",
        "docker rm",
        "docker system prune",
    ],
    "warning_patterns": [
        "| sh",
        "| bash",
        "| fish",
    ],
}

# ===== INTENT DETECTION =====
INTENT_CONFIG = {
    "greetings": ["hi", "hello", "hey", "sup", "yo", "greetings"],
    "conversational_keywords": [
        "what is",
        "who is",
        "explain",
        "tell me about",
        "how does",
        "why",
    ],
}

# ===== EXECUTION CONFIGURATION =====
EXECUTION_CONFIG = {
    "require_approval": True,
    "shell": "/usr/bin/fish",  # CachyOS default
    "timeout": 300,
    "max_retries": 3,
    "dry_run_enabled": True,
}

# ===== LOGGING CONFIGURATION =====
LOG_DIR = os.path.expanduser("~/.ai-exec-logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING_CONFIG = {
    "log_dir": LOG_DIR,
    "log_file_pattern": "{log_dir}/{year}-{month}.log",
    "max_log_size": 500,  # Truncate output to this many chars
}

# ===== TOOL REGISTRY =====
# Tools are definitions only - no execution logic here
TOOL_REGISTRY = {
    "run_command": {
        "platform": "cli",
        "description": "Execute shell command",
        "params": {"command": str, "shell": str},
        "handler": "executor.execute_command",
    },
    "click_button": {
        "platform": "gui",
        "description": "Click UI element",
        "params": {"selector": str, "x": int, "y": int},
        "handler": "executor.click_button",
    },
    "type_text": {
        "platform": "gui",
        "description": "Type text in focused element",
        "params": {"text": str, "delay": float},
        "handler": "executor.type_text",
    },
    "read_screen": {
        "platform": "vision",
        "description": "Capture and analyze screen",
        "params": {"region": dict},
        "handler": "vision.capture_screen",
    },
    "web_search": {
        "platform": "web",
        "description": "Search the web using APIs",
        "params": {"query": str, "num_results": int, "provider": str},
        "handler": "web.search",
    },
    "fetch_page": {
        "platform": "web",
        "description": "Fetch and extract page content",
        "params": {"url": str, "extract_links": bool, "extract_images": bool},
        "handler": "web.fetch_page",
    },
    "extract_text": {
        "platform": "web",
        "description": "Extract text from a page",
        "params": {"url": str},
        "handler": "web.extract_text",
    },
    "extract_links": {
        "platform": "web",
        "description": "Extract links from a page",
        "params": {"url": str, "internal_only": bool},
        "handler": "web.extract_links",
    },
    "browser_navigate": {
        "platform": "web",
        "description": "Navigate to URL in browser",
        "params": {"url": str},
        "handler": "web.navigate",
    },
    "browser_click": {
        "platform": "web",
        "description": "Click element in browser",
        "params": {"selector": str, "by_type": str},
        "handler": "web.click",
    },
    "browser_type": {
        "platform": "web",
        "description": "Type text in browser field",
        "params": {"selector": str, "text": str, "by_type": str},
        "handler": "web.type_text",
    },
}

# ===== WEB MODULE CONFIGURATION =====
WEB_CONFIG = {
    "backend": "mock",  # Options: mock, api, scraper, browser
    "search_provider": "serpapi",  # Options: serpapi, google, bing, duckduckgo, brave, mock
    "browser_type": "chrome",  # Options: chrome, firefox, edge, safari, mock
    "browser_headless": True,  # Run browser in headless mode
    "browser_timeout": 10,  # Browser operation timeout in seconds
    "scraper_timeout": 10,  # Web scraping timeout
    "request_headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    },
    # API keys (use environment variables in production)
    "api_keys": {
        "serpapi": None,  # Use SERPAPI_KEY env var
        "google": None,  # Use GOOGLE_SEARCH_API_KEY env var
        "bing": None,  # Use BING_SEARCH_API_KEY env var
        "brave": None,  # Use BRAVE_SEARCH_API_KEY env var
    },
}

# ===== OS/HYPRLAND CONFIGURATION =====
# ACTUAL configuration locations for Hyprland and Caelestia desktop environment
# See ACTUAL_HYPRLAND_ANALYSIS.md for detailed explanation
OS_CONFIG = {
    # ===== USER-EDITABLE CONFIGS (Hyprland) =====
    "hyprland_config_dir": os.path.expanduser("~/.config/hypr"),
    "hyprland_main_config": os.path.expanduser("~/.config/hypr/hyprland.conf"),

    # User-editable Hyprland configs (MODIFY THESE)
    "hyprland_variables": os.path.expanduser("~/.config/hypr/variables.conf"),
    "hyprland_keybinds": os.path.expanduser("~/.config/hypr/hyprland/keybinds.conf"),
    "hyprland_overrides": os.path.expanduser("~/.config/hypr/hypr-user.conf"),

    # Hyprland modular configs
    "hyprland_modules_dir": os.path.expanduser("~/.config/hypr/hyprland"),
    "hyprland_modules": {
        "animations": os.path.expanduser("~/.config/hypr/hyprland/animations.conf"),
        "decoration": os.path.expanduser("~/.config/hypr/hyprland/decoration.conf"),
        "env": os.path.expanduser("~/.config/hypr/hyprland/env.conf"),
        "execs": os.path.expanduser("~/.config/hypr/hyprland/execs.conf"),
        "general": os.path.expanduser("~/.config/hypr/hyprland/general.conf"),
        "gestures": os.path.expanduser("~/.config/hypr/hyprland/gestures.conf"),
        "group": os.path.expanduser("~/.config/hypr/hyprland/group.conf"),
        "input": os.path.expanduser("~/.config/hypr/hyprland/input.conf"),
        "keybinds": os.path.expanduser("~/.config/hypr/hyprland/keybinds.conf"),
        "misc": os.path.expanduser("~/.config/hypr/hyprland/misc.conf"),
        "rules": os.path.expanduser("~/.config/hypr/hyprland/rules.conf"),
    },

    # ===== CAELESTIA SHELL CONFIG (MODIFY THIS) =====
    "caelestia_config_dir": os.path.expanduser("~/.config/caelestia"),
    "shell_config_file": os.path.expanduser("~/.config/caelestia/shell.json"),
    "caelestia_hypr_user": os.path.expanduser("~/.config/caelestia/hypr-user.conf"),

    # ===== CORE CAELESTIA (READ-ONLY - system files) =====
    "caelestia_base_dir": os.path.expanduser("~/.local/share/caelestia/hypr"),
    "caelestia_base_configs": {
        "variables": os.path.expanduser("~/.local/share/caelestia/hypr/variables.conf"),
        "keybinds": os.path.expanduser("~/.local/share/caelestia/hypr/hyprland/keybinds.conf"),
        "animations": os.path.expanduser("~/.local/share/caelestia/hypr/hyprland/animations.conf"),
    },

    # ===== SCRIPTS & UTILITIES =====
    "scripts_dir": os.path.expanduser("~/.config/hypr/scripts"),

    # ===== WINDOW MANAGER SETTINGS =====
    "hyprctl_available": True,
    "default_shell": "/usr/bin/fish",
    "hyprland_instance_env": "HYPRLAND_INSTANCE_SIGNATURE",
    "reload_command": "hyprctl reload",
}

