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
from .app import (
    APP_NAME,
    APP_SLUG,
    LEGACY_APP_NAME,
    CONTACT_EMAIL,
    LOCAL_SHARE_DIR,
    CACHE_DIR,
    LOG_DIR,
    BRAVE_PROFILE_DIR,
    ensure_runtime_dirs,
)
from .endpoints import ENDPOINTS, endpoint_of

__all__ = [
    "APP_NAME",
    "APP_SLUG",
    "LEGACY_APP_NAME",
    "CONTACT_EMAIL",
    "LOCAL_SHARE_DIR",
    "CACHE_DIR",
    "LOG_DIR",
    "BRAVE_PROFILE_DIR",
    "ensure_runtime_dirs",
    "ENDPOINTS",
    "endpoint_of",
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
