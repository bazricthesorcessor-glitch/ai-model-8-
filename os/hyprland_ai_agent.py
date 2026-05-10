#!/usr/bin/env python3
"""
Hyprland AI Agent - Integrates Ollama AI with Hyprland desktop environment
Controls window management, audio, system, and provides system monitoring
"""

import json
import subprocess
import time
import os
from typing import Optional
import requests
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "mildl"  # Change to your model name
OLLAMA_ENDPOINT = f"{OLLAMA_URL}/api/generate"


@dataclass
class SystemState:
    """Current system state for context"""
    active_window: str = ""
    active_workspace: int = 0
    gpu_usage: str = ""
    cpu_usage: str = ""
    ram_usage: str = ""
    volume: int = 0
    current_time: str = ""
    playing_video: str = ""


class HyprlandControl:
    """Control Hyprland window manager"""

    @staticmethod
    def execute(cmd: str) -> str:
        """Execute hyprctl command"""
        try:
            result = subprocess.run(['hyprctl', *cmd.split()],
                                  capture_output=True, text=True, timeout=2)
            return result.stdout.strip()
        except Exception as e:
            logger.error(f"Hyprctl error: {e}")
            return f"Error: {e}"

    @staticmethod
    def maximize_window() -> str:
        """Maximize active window"""
        return HyprlandControl.execute("dispatch layoutmsg swapwithmaster")

    @staticmethod
    def minimize_window() -> str:
        """Minimize active window"""
        return HyprlandControl.execute("dispatch togglespecialworkspace minimized")

    @staticmethod
    def close_window() -> str:
        """Close active window"""
        return HyprlandControl.execute("dispatch killactive")

    @staticmethod
    def split_window(direction: str = "right") -> str:
        """Split window in given direction (left/right/up/down)"""
        return HyprlandControl.execute(f"dispatch layoutmsg {direction}")

    @staticmethod
    def switch_workspace(workspace: int) -> str:
        """Switch to workspace number"""
        return HyprlandControl.execute(f"dispatch workspace {workspace}")

    @staticmethod
    def get_active_window() -> str:
        """Get currently active window"""
        return HyprlandControl.execute("activewindow")

    @staticmethod
    def get_workspaces() -> str:
        """Get all workspaces"""
        return HyprlandControl.execute("workspaces")

    @staticmethod
    def move_window_to_workspace(workspace: int) -> str:
        """Move window to workspace"""
        return HyprlandControl.execute(f"dispatch movetoworkspace {workspace}")

    @staticmethod
    def toggle_fullscreen() -> str:
        """Toggle fullscreen for active window"""
        return HyprlandControl.execute("dispatch fullscreen 0")

    @staticmethod
    def toggle_floating() -> str:
        """Toggle floating mode"""
        return HyprlandControl.execute("dispatch togglefloating")

    @staticmethod
    def set_app_opacity(app_name: str, opacity: float) -> str:
        """Set app-specific opacity in config files (works for VS Code, Alacritty, Kitty, etc.)"""
        try:
            opacity = max(0.0, min(1.0, float(opacity)))
            percent = int(opacity * 100)

            app_name = app_name.lower().strip()

            # VS Code
            if 'code' in app_name or 'vscode' in app_name:
                config_path = Path.home() / '.config/Code/User/settings.json'
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        settings = json.load(f)
                    settings['window.opacity'] = opacity
                    with open(config_path, 'w') as f:
                        json.dump(settings, f, indent=2)
                    return f"VS Code opacity set to {percent}% in settings.json (restart VS Code to apply)"
                else:
                    return f"VS Code config not found at {config_path}"

            # Alacritty
            elif 'alacritty' in app_name:
                config_path = Path.home() / '.config/alacritty/alacritty.toml'
                if config_path.exists():
                    content = config_path.read_text()
                    # Simple TOML modification
                    if 'opacity =' in content:
                        content = content.replace(
                            content[content.find('opacity ='):content.find('\n', content.find('opacity ='))],
                            f'opacity = {opacity}'
                        )
                    else:
                        content += f'\n[window]\nopacity = {opacity}\n'
                    config_path.write_text(content)
                    return f"Alacritty opacity set to {percent}% in alacritty.toml (restart terminal to apply)"
                else:
                    return f"Alacritty config not found at {config_path}"

            # Kitty
            elif 'kitty' in app_name:
                config_path = Path.home() / '.config/kitty/kitty.conf'
                if config_path.exists():
                    content = config_path.read_text()
                    if 'background_opacity' in content:
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if line.startswith('background_opacity'):
                                lines[i] = f'background_opacity {opacity}'
                        content = '\n'.join(lines)
                    else:
                        content += f'\nbackground_opacity {opacity}\n'
                    config_path.write_text(content)
                    return f"Kitty opacity set to {percent}% in kitty.conf (restart terminal to apply)"
                else:
                    return f"Kitty config not found at {config_path}"

            else:
                return f"Unsupported app: {app_name}. Supported: code/vscode, alacritty, kitty"

        except Exception as e:
            return f"Error setting app opacity: {e}"

    @staticmethod
    def get_supported_opacity_apps() -> str:
        """List apps that support opacity configuration"""
        return """
Supported Apps for Opacity Configuration:
  • VS Code (vscode, code)
  • Alacritty (alacritty)
  • Kitty (kitty)

Usage: "set opacity of [app] to [percent]"
Example: "set opacity of alacritty to 70 percent"
         "set vscode opacity to 80"
"""


class AudioControl:
    """Control system audio"""

    @staticmethod
    def set_volume(percent: int) -> str:
        """Set volume to percentage (0-100)"""
        try:
            percent = max(0, min(100, percent))
            subprocess.run(['pactl', 'set-sink-volume', '@DEFAULT_SINK@', f'{percent}%'],
                         timeout=2)
            return f"Volume set to {percent}%"
        except Exception as e:
            return f"Error setting volume: {e}"

    @staticmethod
    def increase_volume(step: int = 5) -> str:
        """Increase volume by step"""
        try:
            subprocess.run(['pactl', 'set-sink-volume', '@DEFAULT_SINK@', f'+{step}%'],
                         timeout=2)
            vol = AudioControl.get_volume()
            return f"Volume increased to {vol}%"
        except Exception as e:
            return f"Error: {e}"

    @staticmethod
    def decrease_volume(step: int = 5) -> str:
        """Decrease volume by step"""
        try:
            subprocess.run(['pactl', 'set-sink-volume', '@DEFAULT_SINK@', f'-{step}%'],
                         timeout=2)
            vol = AudioControl.get_volume()
            return f"Volume decreased to {vol}%"
        except Exception as e:
            return f"Error: {e}"

    @staticmethod
    def toggle_mute() -> str:
        """Toggle mute"""
        try:
            subprocess.run(['pactl', 'set-sink-mute', '@DEFAULT_SINK@', 'toggle'],
                         timeout=2)
            return "Mute toggled"
        except Exception as e:
            return f"Error: {e}"

    @staticmethod
    def get_volume() -> int:
        """Get current volume"""
        try:
            result = subprocess.run(['pactl', 'get-sink-volume', '@DEFAULT_SINK@'],
                                  capture_output=True, text=True, timeout=2)
            # Parse: "Volume: front-left: 65536 / 100% / 0.00 dB"
            if 'Volume:' in result.stdout:
                parts = result.stdout.split('/')
                volume = int(''.join(filter(str.isdigit, parts[1])))
                return volume
        except Exception as e:
            logger.error(f"Volume error: {e}")
        return 0


class SystemControl:
    """Control system functions"""

    @staticmethod
    def sleep() -> str:
        """Put system to sleep"""
        try:
            subprocess.run(['systemctl', 'suspend'], timeout=2)
            return "System sleeping"
        except Exception as e:
            return f"Error: {e}"

    @staticmethod
    def shutdown() -> str:
        """Shutdown system"""
        try:
            subprocess.run(['systemctl', 'poweroff'], timeout=2)
            return "System shutting down"
        except Exception as e:
            return f"Error: {e}"

    @staticmethod
    def reboot() -> str:
        """Reboot system"""
        try:
            subprocess.run(['systemctl', 'reboot'], timeout=2)
            return "System rebooting"
        except Exception as e:
            return f"Error: {e}"

    @staticmethod
    def lock_screen() -> str:
        """Lock screen"""
        try:
            subprocess.run(['loginctl', 'lock-session'], timeout=2)
            return "Screen locked"
        except Exception as e:
            return f"Error: {e}"


class SystemMonitor:
    """Monitor system status"""

    @staticmethod
    def get_cpu_usage() -> str:
        """Get CPU usage percentage"""
        try:
            result = subprocess.run(['top', '-bn1'],
                                  capture_output=True, text=True, timeout=2)
            for line in result.stdout.split('\n'):
                if 'Cpu(s)' in line:
                    # Parse: "Cpu(s):  5.2%us,  1.8%sy,  0.0%ni, 92.9%id"
                    return line.split(':')[1].strip()
        except Exception as e:
            logger.error(f"CPU error: {e}")
        return "N/A"

    @staticmethod
    def get_ram_usage() -> str:
        """Get RAM usage"""
        try:
            result = subprocess.run(['free', '-h'],
                                  capture_output=True, text=True, timeout=2)
            lines = result.stdout.split('\n')
            if len(lines) > 1:
                mem_line = lines[1].split()
                used = mem_line[2]
                total = mem_line[1]
                return f"{used} / {total}"
        except Exception as e:
            logger.error(f"RAM error: {e}")
        return "N/A"

    @staticmethod
    def get_gpu_usage() -> str:
        """Get GPU usage (nvidia-smi or rocm-smi)"""
        try:
            # Try NVIDIA first
            result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,utilization.memory',
                                   '--format=csv,noheader,nounits'],
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                return f"GPU: {result.stdout.strip()}%"

            # Try AMD ROCm
            result = subprocess.run(['rocm-smi', '--showuse'],
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            logger.error(f"GPU error: {e}")
        return "N/A"

    @staticmethod
    def get_time() -> str:
        """Get current time and date"""
        return subprocess.run(['date'], capture_output=True, text=True).stdout.strip()

    @staticmethod
    def get_playing_video() -> str:
        """Get currently playing video (mpv, vlc, etc)"""
        try:
            # Check mpv
            result = subprocess.run(['pgrep', '-f', 'mpv'],
                                  capture_output=True, text=True, timeout=1)
            if result.stdout.strip():
                return "MPV player is active"

            # Check vlc
            result = subprocess.run(['pgrep', 'vlc'],
                                  capture_output=True, text=True, timeout=1)
            if result.stdout.strip():
                return "VLC player is active"
        except Exception as e:
            logger.error(f"Player check error: {e}")
        return "No video player active"

    @staticmethod
    def get_system_state() -> SystemState:
        """Get complete system state"""
        state = SystemState()
        state.active_window = HyprlandControl.get_active_window()
        state.gpu_usage = SystemMonitor.get_gpu_usage()
        state.cpu_usage = SystemMonitor.get_cpu_usage()
        state.ram_usage = SystemMonitor.get_ram_usage()
        state.volume = AudioControl.get_volume()
        state.current_time = SystemMonitor.get_time()
        state.playing_video = SystemMonitor.get_playing_video()
        return state


class OllamaAgent:
    """Interface with Ollama AI"""

    def __init__(self, model: str = OLLAMA_MODEL):
        self.model = model
        self.conversation_history = []

    def get_system_context(self) -> str:
        """Get formatted system state for AI context"""
        state = SystemMonitor.get_system_state()
        return f"""
CURRENT SYSTEM STATE:
- Time: {state.current_time}
- CPU: {state.cpu_usage}
- RAM: {state.ram_usage}
- GPU: {state.gpu_usage}
- Volume: {state.volume}%
- Active Window: {state.active_window}
- Playing: {state.playing_video}

AVAILABLE COMMANDS:
Window: maximize, minimize, close, split_window [left/right/up/down], switch_workspace [1-10], toggle_fullscreen, toggle_floating
Audio: set_volume [0-100], increase_volume, decrease_volume, toggle_mute
System: sleep, shutdown, reboot, lock_screen
Info: get_time, get_cpu, get_ram, get_gpu, get_playing_video, get_status

Respond with JSON format:
{{"action": "command_name", "params": {{...}}, "explanation": "what you did"}}
"""

    def send_message(self, user_input: str) -> dict:
        """Send message to Ollama and get response"""
        try:
            # Build context-aware prompt
            system_context = self.get_system_context()
            prompt = f"{system_context}\n\nUser: {user_input}\n\nRespond with the command JSON."

            response = requests.post(
                OLLAMA_ENDPOINT,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(f"Ollama response: {result['response']}")
                return {"status": "success", "response": result['response']}
            else:
                return {"status": "error", "response": f"HTTP {response.status_code}"}

        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama. Is it running on localhost:11434?")
            return {"status": "error", "response": "Cannot connect to Ollama"}
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return {"status": "error", "response": str(e)}

    def parse_and_execute(self, response_text: str) -> str:
        """Parse AI response and execute commands"""
        try:
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1

            if json_start == -1 or json_end == 0:
                return f"Could not parse response: {response_text}"

            json_str = response_text[json_start:json_end]
            command_json = json.loads(json_str)

            action = command_json.get('action', '').lower()
            params = command_json.get('params', {})

            # Execute command
            result = self.execute_command(action, params)
            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            return f"Error parsing response: {e}"
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return f"Execution error: {e}"

    def execute_command(self, action: str, params: dict) -> str:
        """Execute command based on action"""

        # Window commands
        if action == "maximize":
            return HyprlandControl.maximize_window()
        elif action == "minimize":
            return HyprlandControl.minimize_window()
        elif action == "close":
            return HyprlandControl.close_window()
        elif action == "split_window":
            direction = params.get('direction', 'right')
            return HyprlandControl.split_window(direction)
        elif action == "switch_workspace":
            workspace = params.get('workspace', 1)
            return HyprlandControl.switch_workspace(workspace)
        elif action == "move_to_workspace":
            workspace = params.get('workspace', 1)
            return HyprlandControl.move_window_to_workspace(workspace)
        elif action == "toggle_fullscreen":
            return HyprlandControl.toggle_fullscreen()
        elif action == "toggle_floating":
            return HyprlandControl.toggle_floating()
        elif action == "set_opacity":
            opacity = params.get('opacity', 1.0)
            return HyprlandControl.set_opacity(opacity)
        elif action == "increase_opacity":
            step = params.get('step', 0.1)
            return HyprlandControl.increase_opacity(step)
        elif action == "decrease_opacity":
            step = params.get('step', 0.1)
            return HyprlandControl.decrease_opacity(step)

        # Audio commands
        elif action == "set_volume":
            volume = params.get('volume', 50)
            return AudioControl.set_volume(volume)
        elif action == "increase_volume":
            step = params.get('step', 5)
            return AudioControl.increase_volume(step)
        elif action == "decrease_volume":
            step = params.get('step', 5)
            return AudioControl.decrease_volume(step)
        elif action == "toggle_mute":
            return AudioControl.toggle_mute()

        # System commands
        elif action == "sleep":
            return SystemControl.sleep()
        elif action == "shutdown":
            return SystemControl.shutdown()
        elif action == "reboot":
            return SystemControl.reboot()
        elif action == "lock_screen":
            return SystemControl.lock_screen()

        # Info commands
        elif action == "get_status":
            state = SystemMonitor.get_system_state()
            return f"Status: CPU {state.cpu_usage} | RAM {state.ram_usage} | GPU {state.gpu_usage}"
        elif action == "get_time":
            return SystemMonitor.get_time()
        elif action == "get_gpu":
            return SystemMonitor.get_gpu_usage()
        elif action == "get_cpu":
            return SystemMonitor.get_cpu_usage()
        elif action == "get_ram":
            return SystemMonitor.get_ram_usage()

        # Hyprland info commands
        elif action == "get_active_window":
            return HyprlandControl.get_active_window()
        elif action == "get_workspaces":
            return HyprlandControl.get_workspaces()
        elif action == "get_playing_video":
            return SystemMonitor.get_playing_video()

        else:
            return f"Unknown action: {action}"


def main():
    """Main agent loop"""
    agent = OllamaAgent()

    print("🤖 Hyprland AI Agent Started")
    print("Commands: 'status' for system state, 'quit' to exit")
    print("Example: 'maximize window', 'set volume to 50', 'what time is it'")
    print("-" * 50)

    while True:
        try:
            user_input = input("\n> ").strip()

            if not user_input:
                continue

            if user_input.lower() == 'quit':
                print("Goodbye!")
                break

            if user_input.lower() == 'status':
                state = SystemMonitor.get_system_state()
                print(f"📊 System Status:")
                print(f"   CPU: {state.cpu_usage}")
                print(f"   RAM: {state.ram_usage}")
                print(f"   GPU: {state.gpu_usage}")
                print(f"   Volume: {state.volume}%")
                print(f"   Time: {state.current_time}")
                print(f"   Playing: {state.playing_video}")
                continue

            # Send to Ollama
            print("🤔 Thinking...")
            response = agent.send_message(user_input)

            if response['status'] == 'success':
                result = agent.parse_and_execute(response['response'])
                print(f"✅ {result}")
            else:
                print(f"❌ {response['response']}")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            logger.error(f"Main loop error: {e}")
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
