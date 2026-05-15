#!/bin/bash
# Installation & Configuration Checklist for Elzyra

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  Elzyra - Installation Checklist                              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

CHECKS_PASSED=0
CHECKS_FAILED=0
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
OLLAMA_URL="$(PYTHONPATH="$PROJECT_DIR" python3 -c 'from config import endpoint_of; print(endpoint_of("ollama"))')"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_command() {
    local cmd=$1
    local name=$2
    if command -v $cmd &> /dev/null; then
        echo -e "${GREEN}✓${NC} $name installed"
        ((CHECKS_PASSED+=1))
    else
        echo -e "${RED}✗${NC} $name NOT found"
        ((CHECKS_FAILED+=1))
    fi
}

check_file() {
    local file=$1
    local name=$2
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $name exists"
        ((CHECKS_PASSED+=1))
    else
        echo -e "${RED}✗${NC} $name NOT found: $file"
        ((CHECKS_FAILED+=1))
    fi
}

check_service() {
    local service=$1
    if systemctl --user is-enabled "$service" &> /dev/null; then
        echo -e "${GREEN}✓${NC} $service enabled"
        ((CHECKS_PASSED+=1))
    else
        echo -e "${YELLOW}!${NC} $service not enabled (optional)"
    fi
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SYSTEM REQUIREMENTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
check_command "python3" "Python 3"
check_command "hyprctl" "Hyprland"
check_command "pactl" "PulseAudio (audio control)"
check_command "systemctl" "Systemd"
check_command "brave" "Brave browser"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "AGENT FILES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
check_file "$PROJECT_DIR/os/hyprland_ai_agent.py" "Main agent"
check_file "$PROJECT_DIR/agent/agent_daemon.py" "Daemon"
check_file "$PROJECT_DIR/agent/agent_cli.py" "CLI client"
check_file "$PROJECT_DIR/agent/agent_config.py" "Agent configuration"
check_file "$PROJECT_DIR/requirements.txt" "Dependencies"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PYTHON DEPENDENCIES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check requests
if python3 -c "import requests" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} requests installed"
    ((CHECKS_PASSED+=1))
else
    echo -e "${RED}✗${NC} requests NOT installed (required)"
    ((CHECKS_FAILED+=1))
fi

# Check vosk (optional)
if python3 -c "import vosk" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} vosk installed (voice input available)"
    ((CHECKS_PASSED+=1))
else
    echo -e "${YELLOW}!${NC} vosk not installed (optional for voice input)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "OLLAMA & MODELS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check Ollama
if curl -s "$OLLAMA_URL/api/tags" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Ollama is running"
    ((CHECKS_PASSED+=1))

    # Check for mildl model
    MODELS=$(curl -s "$OLLAMA_URL/api/tags" | python3 -c "import sys, json; data=json.load(sys.stdin); print(' '.join([m['name'].split(':')[0] for m in data.get('models', [])]))" 2>/dev/null || echo "")
    if echo "$MODELS" | grep -q "mildl"; then
        echo -e "${GREEN}✓${NC} Mildl model available"
        ((CHECKS_PASSED+=1))
    else
        echo -e "${YELLOW}!${NC} Mildl model not found. Available: $MODELS"
        echo "   Run: ollama pull mildl"
    fi
else
    echo -e "${RED}✗${NC} Ollama NOT running"
    echo "   Start with: ollama serve"
    ((CHECKS_FAILED+=1))
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "GPU DETECTION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v nvidia-smi &> /dev/null; then
    echo -e "${GREEN}✓${NC} NVIDIA GPU detected"
    nvidia-smi --query-gpu=name --format=csv,noheader | head -1 | sed 's/^/   /'
    ((CHECKS_PASSED+=1))
elif command -v rocm-smi &> /dev/null; then
    echo -e "${GREEN}✓${NC} AMD GPU detected"
    ((CHECKS_PASSED+=1))
else
    echo -e "${YELLOW}!${NC} No GPU detected (fallback to CPU)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "DIRECTORIES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

mkdir -p ~/.local/share/elzyra/brave-profile
echo -e "${GREEN}✓${NC} Created ~/.local/share/elzyra/brave-profile"

mkdir -p ~/.local/run
echo -e "${GREEN}✓${NC} Created ~/.local/run"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "DAEMON STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if systemctl --user is-active elzyra-agent &> /dev/null; then
    echo -e "${GREEN}✓${NC} Daemon is running"
    ((CHECKS_PASSED+=1))
else
    echo -e "${YELLOW}!${NC} Daemon not running (it's ok, start manually)"
fi

check_service "elzyra-agent"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo -e "Checks passed: ${GREEN}$CHECKS_PASSED${NC}"
echo -e "Checks failed: ${RED}$CHECKS_FAILED${NC}"

echo ""
if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All systems ready!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Test interactive mode:"
    echo "     python3 $PROJECT_DIR/os/hyprland_ai_agent.py"
    echo ""
    echo "  2. Start daemon:"
    echo "     systemctl --user start elzyra-agent"
    echo ""
    echo "  3. Use CLI client:"
    echo "     python3 $PROJECT_DIR/agent/agent_cli.py chat 'maximize window'"
else
    echo -e "${RED}✗ Please fix the failed checks above${NC}"
    echo ""
    if ! curl -s "$OLLAMA_URL" &>/dev/null; then
        echo "URGENT: Start Ollama:"
        echo "  ollama serve"
    fi
    if [ ! -f ~/.venv/bin/activate ]; then
        echo "URGENT: Install Python dependencies:"
        echo "  pip3 install -r $PROJECT_DIR/requirements.txt"
    fi
fi

echo ""
