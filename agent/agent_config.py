"""
Configuration for Elzyra's Hyprland desktop agent.
"""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from config import endpoint_of

# Ollama Configuration
OLLAMA_URL = endpoint_of("ollama")
OLLAMA_MODEL = "mildl"  # Change this to your Mildl model name
OLLAMA_TIMEOUT = 30  # seconds

# System paths
SOCKET_FILE = "~/.local/run/elzyra-agent.sock"
LOG_FILE = "~/.local/share/elzyra/agent.log"

# Audio settings
AUDIO_BACKEND = "pulseaudio"  # or "alsa", "pipewire"
DEFAULT_VOLUME_STEP = 5

# Window manager
WINDOW_MANAGER = "hyprland"

# Voice settings (optional)
VOICE_ENABLED = True
VOICE_MODEL_PATH = "~/.local/share/vosk/models/en-us"
VOICE_SAMPLE_RATE = 16000

# GPU detection
GPU_TYPE = "auto"  # "nvidia", "amd", "auto"

# Command timeout
COMMAND_TIMEOUT = 5  # seconds

# Features
FEATURES = {
    "window_management": True,
    "audio_control": True,
    "system_control": True,
    "monitoring": True,
    "voice_input": True,
}

# Workspace configuration
WORKSPACES = {
    "1": "work",
    "2": "media",
    "3": "chat",
    "4": "gaming",
    "5": "misc",
}
