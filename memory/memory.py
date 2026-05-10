"""
Persistent memory - logs actions to disk for debugging and replay.
Extracted from ai-exec.py log_command() functionality.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from config import LOGGING_CONFIG


def get_log_file() -> str:
    """Get the log file path for current month."""
    now = datetime.now()
    log_dir = LOGGING_CONFIG["log_dir"]
    log_file = os.path.join(log_dir, f"{now.strftime('%Y-%m')}.log")
    return log_file


def log_action(action: str, result: Dict[str, Any], executed: bool = True) -> Dict[str, Any]:
    """
    Log an action and its result to disk.
    Extracted from ai-exec.py log_command()
    """
    log_file = get_log_file()

    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "executed": executed,
        "result": str(result)[:LOGGING_CONFIG.get("max_log_size", 500)],
    }

    try:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
        return {"success": True, "log_file": log_file}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_action_log(limit: int = 100) -> List[Dict[str, Any]]:
    """Read recent actions from log file."""
    log_file = get_log_file()

    if not os.path.exists(log_file):
        return []

    actions = []
    try:
        with open(log_file, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    actions.append(entry)
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass

    return actions[-limit:] if len(actions) > limit else actions
