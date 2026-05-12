"""
Router Services Configuration - Infrastructure metadata only.
Defines what services exist, their timeouts, and recovery behavior.
NO cognitive logic. NO brain imports.
"""

from typing import Dict, Any


SERVICES = {
    # Core execution services
    "executor": {
        "timeout": 30,
        "restartable": True,
        "max_retries": 3,
        "healthcheck": "ping",
    },

    # Query makers - context generators
    "query_maker1": {
        "timeout": 15,
        "restartable": True,
        "max_retries": 2,
    },

    "query_maker2": {
        "timeout": 15,
        "restartable": True,
        "max_retries": 2,
    },

    # Specialist models
    "vision_memory": {
        "timeout": 20,
        "restartable": True,
        "max_retries": 2,
    },

    "fast_executor": {
        "timeout": 10,
        "restartable": True,
        "max_retries": 2,
    },

    "coder": {
        "timeout": 120,
        "restartable": True,
        "max_retries": 1,
    },

    "thinker": {
        "timeout": 180,
        "restartable": True,
        "max_retries": 1,
    },

    # System services
    "browser_tools": {
        "timeout": 30,
        "restartable": True,
        "max_retries": 2,
    },

    "os_tools": {
        "timeout": 30,
        "restartable": True,
        "max_retries": 2,
    },
}


def get_service_config(service_name: str) -> Dict[str, Any]:
    """Get configuration for a service."""
    return SERVICES.get(service_name, {})


def is_restartable(service_name: str) -> bool:
    """Check if service supports restart on failure."""
    return SERVICES.get(service_name, {}).get("restartable", False)


def get_timeout(service_name: str) -> int:
    """Get timeout in seconds for service."""
    return SERVICES.get(service_name, {}).get("timeout", 30)


def get_max_retries(service_name: str) -> int:
    """Get max retry count for service."""
    return SERVICES.get(service_name, {}).get("max_retries", 3)
