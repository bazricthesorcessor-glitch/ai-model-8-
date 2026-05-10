#!/usr/bin/env python3
"""
System Status Dashboard
Simple text-based dashboard for monitoring system and agent status
"""

import curses
import time
from datetime import datetime
import subprocess
import json
import socket
from pathlib import Path

SOCKET_FILE = Path.home() / '.local/run/hyprland-agent.sock'


def get_daemon_status() -> dict:
    """Check if daemon is running and get its status"""
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(str(SOCKET_FILE))
        sock.send(json.dumps({"command": "status"}).encode())
        response = sock.recv(4096).decode()
        sock.close()
        return json.loads(response)
    except:
        return {"status": "offline"}


def get_system_info() -> dict:
    """Get system information"""
    try:
        # CPU
        with open('/proc/loadavg') as f:
            loadavg = f.read().split()[:3]
            cpu = f"Load: {loadavg[0]}, {loadavg[1]}, {loadavg[2]}"

        # Memory
        mem_result = subprocess.run(['free', '-h'], capture_output=True, text=True)
        mem_lines = mem_result.stdout.split('\n')
        mem_line = mem_lines[1].split()
        memory = f"RAM: {mem_line[2]} / {mem_line[1]}"

        # Disk
        disk_result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
        disk_lines = disk_result.stdout.split('\n')
        disk_line = disk_lines[1].split()
        disk = f"Disk: {disk_line[2]} / {disk_line[1]} ({disk_line[4]})"

        # Uptime
        with open('/proc/uptime') as f:
            uptime_seconds = int(float(f.read().split()[0]))
            days = uptime_seconds // 86400
            hours = (uptime_seconds % 86400) // 3600
            uptime = f"Uptime: {days}d {hours}h"

        return {"cpu": cpu, "memory": memory, "disk": disk, "uptime": uptime}
    except Exception as e:
        return {"error": str(e)}


def draw_dashboard(stdscr):
    """Draw the dashboard"""
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(1)   # Non-blocking input

    # Colors
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # Title
        title = "🤖 Hyprland AI Agent Dashboard"
        stdscr.addstr(0, (width - len(title)) // 2, title, curses.color_pair(2) | curses.A_BOLD)

        # Time
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        stdscr.addstr(2, 2, f"Time: {now}", curses.color_pair(2))

        # Daemon Status
        daemon_status = get_daemon_status()
        line = 4
        if daemon_status.get("status") == "offline":
            stdscr.addstr(line, 2, "Daemon Status: OFFLINE", curses.color_pair(4))
        else:
            stdscr.addstr(line, 2, "Daemon Status: ONLINE", curses.color_pair(1))
            if "cpu" in daemon_status:
                line += 1
                stdscr.addstr(line, 4, f"CPU: {daemon_status.get('cpu', 'N/A')}")
            if "ram" in daemon_status:
                line += 1
                stdscr.addstr(line, 4, f"RAM: {daemon_status.get('ram', 'N/A')}")
            if "gpu" in daemon_status:
                line += 1
                stdscr.addstr(line, 4, f"GPU: {daemon_status.get('gpu', 'N/A')}")
            if "volume" in daemon_status:
                line += 1
                vol = daemon_status.get('volume', 0)
                stdscr.addstr(line, 4, f"Volume: {vol}%")

        # System Info
        line += 3
        stdscr.addstr(line, 2, "System Information:", curses.color_pair(3) | curses.A_BOLD)
        sys_info = get_system_info()

        if "error" not in sys_info:
            line += 1
            stdscr.addstr(line, 4, sys_info.get('cpu', ''))
            line += 1
            stdscr.addstr(line, 4, sys_info.get('memory', ''))
            line += 1
            stdscr.addstr(line, 4, sys_info.get('disk', ''))
            line += 1
            stdscr.addstr(line, 4, sys_info.get('uptime', ''))

        # Help
        line += 3
        stdscr.addstr(line, 2, "Commands (press 'q' to quit):", curses.color_pair(3) | curses.A_BOLD)
        line += 1
        stdscr.addstr(line, 4, "'s' for system status | 'm' for maximize | 'v' for volume control")
        line += 1
        stdscr.addstr(line, 4, "'w' for workspace info | 'r' to restart daemon | 'q' to quit")

        stdscr.refresh()

        # Handle input
        try:
            key = stdscr.getch()
            if key == ord('q'):
                break
            elif key == ord('s'):
                # Show detailed status
                pass
            elif key == ord('m'):
                # Maximize window
                subprocess.run(['./agent_cli.py', 'direct', 'maximize_window'])
            elif key == ord('v'):
                # Volume menu
                pass
            elif key == ord('r'):
                # Restart daemon
                subprocess.run(['systemctl', '--user', 'restart', 'hyprland-ai-agent'])
        except:
            pass

        time.sleep(1)


def main():
    """Start dashboard"""
    try:
        curses.wrapper(draw_dashboard)
    except KeyboardInterrupt:
        print("\nDashboard closed")


if __name__ == "__main__":
    main()
