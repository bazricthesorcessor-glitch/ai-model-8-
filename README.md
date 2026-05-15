# Elzyra

Elzyra is a modular AI desktop operating system for Hyprland. Scout, Brain, Router, tools, UI primitives, Observer, Todo, and Memory are separate layers; tools stay small and composable.

Contact: elzyrra@gmail.com

## Features

### Window Management
- ✅ Maximize/minimize windows
- ✅ Close windows
- ✅ Split windows (left, right, up, down)
- ✅ Switch workspaces
- ✅ Move windows between workspaces
- ✅ Toggle fullscreen/floating

### Audio Control
- ✅ Set volume to percentage
- ✅ Increase/decrease volume
- ✅ Toggle mute
- ✅ Volume monitoring

### System Control
- ✅ Sleep/suspend
- ✅ Shutdown/reboot
- ✅ Lock screen
- ✅ System status monitoring

### System Monitoring
- ✅ Real-time CPU usage
- ✅ RAM usage
- ✅ GPU usage (NVIDIA/AMD)
- ✅ Current time/date
- ✅ Active video player detection
- ✅ Active window tracking

### Input Methods
- ✅ Text commands
- ✅ Voice input (STT)
- ✅ Socket-based daemon interface

## Requirements

- **OS**: Linux with Hyprland
- **Ollama**: Running locally with Mildl model
- **Browser**: Brave with a dedicated Elzyra profile
- **Python**: 3.8+
- **System tools**: pactl, hyprctl, systemctl, free, top
- **Optional**: nvidia-smi (for NVIDIA GPU) or rocm-smi (for AMD GPU)

## Quick Start

### 1. Install Dependencies
```bash
cd ~/ai\ model\ 8
pip3 install -r requirements.txt
```

### 2. Update Config
Edit the relevant config and set your Ollama model:
```python
OLLAMA_MODEL = "mildl"
```

### 3. Test Interactive Mode
```bash
python3 hyprland_ai_agent.py
```

Try: `maximize window`, `set volume to 75`, `what time is it`

### 4. Setup Daemon (Optional)
```bash
chmod +x setup.sh
./setup.sh
systemctl --user start elzyra-agent
systemctl --user enable elzyra-agent
```

### 5. Use CLI Client
```bash
chmod +x agent_cli.py
./agent_cli.py chat "maximize my window"
./agent_cli.py status
```

## Voice Input Setup

```bash
pip3 install vosk pyaudio
mkdir -p ~/.local/share/vosk/models
cd ~/.local/share/vosk/models
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
mv vosk-model-small-en-us-0.15 en-us
python3 voice_input.py
```

## Commands

### Window Management
```
maximize, minimize, close, split_window [left/right/up/down]
switch_workspace [1-10], move_to_workspace [1-10]
toggle_fullscreen, toggle_floating
```

### Audio
```
set_volume [0-100], increase_volume, decrease_volume, toggle_mute
```

### System
```
sleep, shutdown, reboot, lock_screen
```

### Info
```
get_time, get_cpu, get_ram, get_gpu, get_status, get_playing_video
```

## Troubleshooting

**Daemon won't start:**
```bash
rm -f ~/.local/run/elzyra-agent.sock
systemctl --user restart elzyra-agent
journalctl --user -u elzyra-agent -f
```

**Ollama not found:**
```bash
# Verify Ollama running
curl http://127.0.0.1:11434/api/tags
ollama serve
```

**Launch Elzyra Brave profile manually:**
```bash
brave --remote-debugging-port=9222 \
  --user-data-dir=$HOME/.local/share/elzyra/brave-profile
```

**Hyprctl fails:**
```bash
# Verify Hyprland session
echo $HYPRLAND_INSTANCE_SIGNATURE
hyprctl activewindow
```

## Files

- `hyprland_ai_agent.py` - Main agent with all commands
- `agent_daemon.py` - Background daemon service
- `agent_cli.py` - CLI client for daemon
- `voice_input.py` - Voice input handler
- `config.py` - Configuration
- `setup.sh` - Automated setup script
- `requirements.txt` - Python dependencies

## License

MIT
