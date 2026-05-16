"""
Application identity and runtime paths for Elzyra.
"""

from pathlib import Path


APP_NAME = "Elzyra"
APP_SLUG = "elzyra"
LEGACY_APP_NAME = "Avril"
CONTACT_EMAIL = "elzyrra@gmail.com"

LOCAL_SHARE_DIR = Path.home() / ".local" / "share" / APP_SLUG
CACHE_DIR = Path.home() / ".cache" / APP_SLUG
LOG_DIR = LOCAL_SHARE_DIR / "logs"


def ensure_runtime_dirs() -> None:
    """Create Elzyra runtime directories used by local services."""
    for path in (LOCAL_SHARE_DIR, CACHE_DIR, LOG_DIR):
        path.mkdir(parents=True, exist_ok=True)
