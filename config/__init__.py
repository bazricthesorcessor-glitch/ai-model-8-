"""
Configuration module - centralizes all system settings.
No module imports. Brain and Executor read config, don't import each other.
"""

from .settings import (
    LLM_CONFIG,
    SAFETY_RULES,
    EXECUTION_CONFIG,
    TOOL_REGISTRY,
    LOGGING_CONFIG,
    INTENT_CONFIG,
    SCREEN_CONFIG,
    OS_CONFIG,
    WEB_CONFIG,
)
from .paths import Paths, path_of

__all__ = [
    "LLM_CONFIG",
    "SAFETY_RULES",
    "EXECUTION_CONFIG",
    "TOOL_REGISTRY",
    "LOGGING_CONFIG",
    "INTENT_CONFIG",
    "SCREEN_CONFIG",
    "OS_CONFIG",
    "WEB_CONFIG",
    "Paths",
    "path_of",
]
