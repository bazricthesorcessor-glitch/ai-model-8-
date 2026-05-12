#!/bin/bash
# Caelestia Quick Terminal Shortcuts
# Add this to your ~/.config/fish/config.fish or ~/.bashrc
#
# Usage:
#   yt              - Open YouTube
#   ss              - Take screenshot and copy
#   ss-chat         - Send screenshot to ChatGPT
#   bright-up       - Increase brightness
#   bright-down     - Decrease brightness
#   bright [0-100]  - Set brightness to %
#

# For Fish shell (~/.config/fish/config.fish):

alias yt='python /home/dmannu/ai-model-8/ui/quick_terminal.py youtube'
alias ss='python /home/dmannu/ai-model-8/ui/quick_terminal.py screenshot'
alias ss-chat='python /home/dmannu/ai-model-8/ui/quick_terminal.py screenshot-to-chatgpt'
alias bright-up='python /home/dmannu/ai-model-8/ui/quick_terminal.py brightness-up'
alias bright-down='python /home/dmannu/ai-model-8/ui/quick_terminal.py brightness-down'
function bright
    python /home/dmannu/ai-model-8/ui/quick_terminal.py brightness $argv[1]
end
alias bright-info='python /home/dmannu/ai-model-8/ui/quick_terminal.py brightness-info'

# For Bash (~/.bashrc):
#
# alias yt='python /home/dmannu/ai-model-8/ui/quick_terminal.py youtube'
# alias ss='python /home/dmannu/ai-model-8/ui/quick_terminal.py screenshot'
# alias ss-chat='python /home/dmannu/ai-model-8/ui/quick_terminal.py screenshot-to-chatgpt'
# alias bright-up='python /home/dmannu/ai-model-8/ui/quick_terminal.py brightness-up'
# alias bright-down='python /home/dmannu/ai-model-8/ui/quick_terminal.py brightness-down'
# bright() {
#     python /home/dmannu/ai-model-8/ui/quick_terminal.py brightness "$1"
# }
# alias bright-info='python /home/dmannu/ai-model-8/ui/quick_terminal.py brightness-info'
