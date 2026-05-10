#!/bin/bash
# Hyprland Configuration Snippet for AI Agent
# Add these bindings to ~/.config/hypr/hyprland.conf

cat > /tmp/hyprland_ai_config.conf << 'EOF'
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║         Hyprland AI Agent Integration - Add to hyprland.conf              ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

$AI_SCRIPT = ~/ai\ model\ 8/hyprland_ai_agent.py
$AI_CLI = ~/ai\ model\ 8/agent_cli.py
$TERM = kitty

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AI Agent Quick Access
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Super+A: Open AI Agent in floating terminal
bind = SUPER, A, exec, $TERM -o remember_window_size=no -o initial_window_width=80c -o initial_window_height=24c python3 $AI_SCRIPT

# Super+Shift+A: Show system dashboard
bind = SUPER SHIFT, A, exec, python3 ~/ai\ model\ 8/dashboard.py

# Super+Ctrl+A: Restart daemon
bind = SUPER CTRL, A, exec, systemctl --user restart hyprland-ai-agent

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Quick Commands via AI (No Terminal)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Volume Control
bind = , XF86AudioRaiseVolume, exec, python3 $AI_CLI direct increase_volume step=5
bind = , XF86AudioLowerVolume, exec, python3 $AI_CLI direct decrease_volume step=5
bind = , XF86AudioMute, exec, python3 $AI_CLI direct toggle_mute

# Window Management
bind = SUPER, F, exec, python3 $AI_CLI direct toggle_fullscreen
bind = SUPER, V, exec, python3 $AI_CLI direct toggle_floating
bind = SUPER, M, exec, python3 $AI_CLI direct maximize_window
bind = SUPER, N, exec, python3 $AI_CLI direct minimize_window

# Workspace Quick Switch
bind = SUPER, 1, exec, python3 $AI_CLI direct switch_workspace workspace=1
bind = SUPER, 2, exec, python3 $AI_CLI direct switch_workspace workspace=2
bind = SUPER, 3, exec, python3 $AI_CLI direct switch_workspace workspace=3
bind = SUPER, 4, exec, python3 $AI_CLI direct switch_workspace workspace=4
bind = SUPER, 5, exec, python3 $AI_CLI direct switch_workspace workspace=5

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Advanced Bindings (with modifiers)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Split windows
bind = SUPER SHIFT, L, exec, python3 $AI_CLI direct split_window direction=right
bind = SUPER SHIFT, H, exec, python3 $AI_CLI direct split_window direction=left
bind = SUPER SHIFT, K, exec, python3 $AI_CLI direct split_window direction=up
bind = SUPER SHIFT, J, exec, python3 $AI_CLI direct split_window direction=down

# Move window to workspace
bind = SUPER CTRL, 1, exec, python3 $AI_CLI direct move_to_workspace workspace=1
bind = SUPER CTRL, 2, exec, python3 $AI_CLI direct move_to_workspace workspace=2
bind = SUPER CTRL, 3, exec, python3 $AI_CLI direct move_to_workspace workspace=3
bind = SUPER CTRL, 4, exec, python3 $AI_CLI direct move_to_workspace workspace=4
bind = SUPER CTRL, 5, exec, python3 $AI_CLI direct move_to_workspace workspace=5

# System Control
bind = SUPER SHIFT, L, exec, python3 $AI_CLI direct lock_screen
bind = , XF86Sleep, exec, python3 $AI_CLI direct sleep

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  End of AI Agent Configuration                                            ║
# ║  To use: Copy this section into your ~/.config/hypr/hyprland.conf        ║
# ║  Then reload Hyprland: Super+Shift+R                                      ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
EOF

echo "✅ Configuration saved to /tmp/hyprland_ai_config.conf"
echo ""
echo "To add to your Hyprland config:"
echo "  cat /tmp/hyprland_ai_config.conf >> ~/.config/hypr/hyprland.conf"
echo ""
echo "Then reload Hyprland with Super+Shift+R"
