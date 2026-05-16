#!/bin/bash
# Setup script for Elzyra desktop agent

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
OLLAMA_URL="$(PYTHONPATH="$PROJECT_DIR" python3 -c 'from config import endpoint_of; print(endpoint_of("ollama"))')"

echo "Setting up Elzyra desktop agent..."

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
mkdir -p ~/.local/share/elzyra
mkdir -p ~/.local/run

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r "$PROJECT_DIR/requirements.txt"

echo "Installing Playwright Chromium..."
python3 -m playwright install chromium

# Check Ollama connection
echo "Testing Ollama connection..."
if curl -s "$OLLAMA_URL/api/tags" > /dev/null; then
    echo "Ollama is running"
else
    echo "Cannot reach Ollama on $OLLAMA_URL"
    echo "   Make sure Ollama is installed and running: ollama serve"
    exit 1
fi

# Create systemd service file
echo "Creating systemd service..."

sudo tee /etc/systemd/user/elzyra-agent.service > /dev/null <<EOF
[Unit]
Description=Elzyra Desktop Agent Daemon
After=network.target hyprland.desktop

[Service]
Type=simple
WorkingDirectory=$PROJECT_DIR
Environment="PYTHONPATH=$PROJECT_DIR"
ExecStart=/usr/bin/env python3 $PROJECT_DIR/agent/agent_daemon.py
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
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update config.py with your model name if needed"
echo "2. Start daemon: systemctl --user start elzyra-agent"
echo "3. Enable on boot: systemctl --user enable elzyra-agent"
echo "4. Check status: systemctl --user status elzyra-agent"
echo "5. Test: python3 hyprland_ai_agent.py"
echo ""
