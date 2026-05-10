#!/bin/bash
# Setup script for Hyprland AI Agent

set -e

echo "🚀 Setting up Hyprland AI Agent..."

# Check dependencies
echo "Checking dependencies..."

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Check for required system commands
for cmd in hyprctl pactl free; do
    if ! command -v $cmd &> /dev/null; then
        echo "⚠️  Warning: $cmd not found. Some features may not work."
    fi
done

# Create directories
echo "Creating directories..."
mkdir -p ~/.local/share/hyprland-agent
mkdir -p ~/.local/run

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Check Ollama connection
echo "Testing Ollama connection..."
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✅ Ollama is running"
else
    echo "❌ Cannot reach Ollama on localhost:11434"
    echo "   Make sure Ollama is installed and running: ollama serve"
    exit 1
fi

# Create systemd service file
echo "Creating systemd service..."
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

sudo tee /etc/systemd/user/hyprland-ai-agent.service > /dev/null <<EOF
[Unit]
Description=Hyprland AI Agent Daemon
After=network.target hyprland.desktop

[Service]
Type=simple
ExecStart=$SCRIPT_DIR/agent_daemon.py
Restart=on-failure
RestartSec=5

# Environment
Environment="DISPLAY=%i"
Environment="WAYLAND_DISPLAY=wayland-%i"

[Install]
WantedBy=default.target
EOF

# Reload systemd
systemctl --user daemon-reload

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update config.py with your model name if needed"
echo "2. Start daemon: systemctl --user start hyprland-ai-agent"
echo "3. Enable on boot: systemctl --user enable hyprland-ai-agent"
echo "4. Check status: systemctl --user status hyprland-ai-agent"
echo "5. Test: python3 hyprland_ai_agent.py"
echo ""
