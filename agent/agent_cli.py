#!/usr/bin/env python3
"""
Client for Hyprland AI Agent Daemon
Sends commands to the background daemon
"""

import socket
import json
import sys
from pathlib import Path

SOCKET_FILE = Path.home() / '.local/run/hyprland-agent.sock'


def send_command(command: str, **kwargs) -> dict:
    """Send command to daemon"""
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(str(SOCKET_FILE))

        request = {"command": command}
        request.update(kwargs)

        sock.send(json.dumps(request).encode('utf-8'))
        response = sock.recv(4096).decode('utf-8')
        sock.close()

        return json.loads(response)
    except FileNotFoundError:
        return {"error": "Daemon not running. Start with: systemctl --user start hyprland-ai-agent"}
    except Exception as e:
        return {"error": str(e)}


def main():
    """CLI interface"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  agent-cli chat 'your command'     - Chat with AI")
        print("  agent-cli status                  - Get system status")
        print("  agent-cli direct <action> [json]  - Execute direct action")
        print("")
        print("Examples:")
        print("  agent-cli chat 'maximize window'")
        print("  agent-cli chat 'what is my cpu usage'")
        print("  agent-cli status")
        print("  agent-cli direct set_volume volume=75")
        sys.exit(1)

    command = sys.argv[1]

    if command == "chat":
        text = " ".join(sys.argv[2:])
        print(f"Sending: {text}")
        response = send_command("chat", text=text)

    elif command == "status":
        response = send_command("status")

    elif command == "direct":
        action = sys.argv[2]
        params = {}
        for arg in sys.argv[3:]:
            if '=' in arg:
                k, v = arg.split('=', 1)
                try:
                    params[k] = int(v)
                except ValueError:
                    params[k] = v
        response = send_command("direct", action=action, params=params)

    else:
        response = {"error": f"Unknown command: {command}"}

    # Pretty print response
    print(json.dumps(response, indent=2))


if __name__ == "__main__":
    main()
