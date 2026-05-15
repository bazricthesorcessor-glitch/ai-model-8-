#!/usr/bin/env python3
"""
Elzyra Hyprland desktop agent daemon.
Runs as a background service with socket-based command interface
"""

import socket
import json
import threading
import logging
import time
import importlib.util
import sys
from pathlib import Path

try:
    from .agent_config import LOG_FILE, SOCKET_FILE as CONFIG_SOCKET_FILE
except ImportError:
    from agent_config import LOG_FILE, SOCKET_FILE as CONFIG_SOCKET_FILE


def _load_agent_impl():
    """Load the Hyprland implementation from the repo's os/ directory."""
    impl_path = Path(__file__).resolve().parents[1] / "os" / "hyprland_ai_agent.py"
    spec = importlib.util.spec_from_file_location("elzyra_hyprland_agent", impl_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load agent implementation from {impl_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_agent_impl = _load_agent_impl()
OllamaAgent = _agent_impl.OllamaAgent
SystemMonitor = _agent_impl.SystemMonitor


def _logging_handlers():
    """Build logging handlers, falling back to stderr if log dir is unavailable."""
    log_path = Path(LOG_FILE).expanduser()
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        return [logging.FileHandler(log_path), logging.StreamHandler()]
    except OSError:
        return [logging.StreamHandler()]


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=_logging_handlers(),
)
logger = logging.getLogger(__name__)

SOCKET_FILE = Path(CONFIG_SOCKET_FILE).expanduser()


class AgentDaemon:
    """Background daemon for AI agent"""

    def __init__(self):
        self.agent = OllamaAgent()
        self.socket_file = SOCKET_FILE
        self.running = True

        # Create socket directory
        self.socket_file.parent.mkdir(parents=True, exist_ok=True)

        # Remove old socket file if exists
        if self.socket_file.exists():
            self.socket_file.unlink()

        logger.info("Elzyra Hyprland desktop agent daemon initialized")

    def start(self):
        """Start daemon"""
        logger.info(f"Starting daemon on {self.socket_file}")

        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(str(self.socket_file))
        server.listen(1)

        try:
            while self.running:
                try:
                    connection, _ = server.accept()
                    # Handle connection in thread
                    thread = threading.Thread(target=self.handle_client, args=(connection,))
                    thread.daemon = True
                    thread.start()
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    logger.error(f"Accept error: {e}")
                    time.sleep(1)
        finally:
            server.close()
            if self.socket_file.exists():
                self.socket_file.unlink()
            logger.info("Daemon stopped")

    def handle_client(self, connection):
        """Handle client connection"""
        try:
            data = connection.recv(1024).decode('utf-8')
            if not data:
                return

            request = json.loads(data)
            response = self.process_request(request)

            connection.send(json.dumps(response).encode('utf-8'))
        except json.JSONDecodeError:
            connection.send(json.dumps({"error": "Invalid JSON"}).encode('utf-8'))
        except Exception as e:
            logger.error(f"Client error: {e}")
            connection.send(json.dumps({"error": str(e)}).encode('utf-8'))
        finally:
            connection.close()

    def process_request(self, request: dict) -> dict:
        """Process incoming request"""
        command = request.get('command', '')
        text = request.get('text', '')

        if command == 'chat':
            # Send to AI
            response = self.agent.send_message(text)
            if response['status'] == 'success':
                result = self.agent.parse_and_execute(response['response'])
                return {"status": "success", "result": result}
            return {"status": "error", "error": response['response']}

        elif command == 'status':
            state = SystemMonitor.get_system_state()
            return {
                "status": "success",
                "cpu": state.cpu_usage,
                "ram": state.ram_usage,
                "gpu": state.gpu_usage,
                "volume": state.volume,
                "time": state.current_time,
                "playing": state.playing_video
            }

        elif command == 'direct':
            # Direct command execution
            action = request.get('action', '')
            params = request.get('params', {})
            result = self.agent.execute_command(action, params)
            return {"status": "success", "result": result}

        else:
            return {"status": "error", "error": f"Unknown command: {command}"}


def main():
    """Start daemon"""
    daemon = AgentDaemon()
    daemon.start()


if __name__ == "__main__":
    main()
