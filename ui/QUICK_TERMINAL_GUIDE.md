"""
Quick Terminal Utilities - Quick Reference Guide

One-command tools for common tasks:
- YouTube, ChatGPT, Screenshots
- Brightness control
- Screen capture to ChatGPT automation
"""

# ============================================================================
# COMMAND LINE USAGE
# ============================================================================

"""
QUICK COMMANDS:

1. YouTube:
   python ui/quick_terminal.py youtube
   
2. Screenshot (copy to clipboard):
   python ui/quick_terminal.py screenshot
   
3. Screenshot → ChatGPT (full workflow):
   python ui/quick_terminal.py screenshot-to-chatgpt
   
4. Brightness:
   python ui/quick_terminal.py brightness-up      # +10%
   python ui/quick_terminal.py brightness-down    # -10%
   python ui/quick_terminal.py brightness 75      # Set to 75%
   python ui/quick_terminal.py brightness-info    # Get current

5. ChatGPT:
   python ui/quick_terminal.py chatgpt            # Open ChatGPT
"""

# ============================================================================
# USING WITH ALIASES (FASTER)
# ============================================================================

"""
Add to ~/.config/fish/config.fish or ~/.bashrc:

# YouTube
alias yt='python /path/to/ai-model-8/ui/quick_terminal.py youtube'

# Screenshot
alias ss='python /path/to/ai-model-8/ui/quick_terminal.py screenshot'
alias ss-chat='python /path/to/ai-model-8/ui/quick_terminal.py screenshot-to-chatgpt'

# Brightness
alias bright-up='python /path/to/ai-model-8/ui/quick_terminal.py brightness-up'
alias bright-down='python /path/to/ai-model-8/ui/quick_terminal.py brightness-down'
alias bright-info='python /path/to/ai-model-8/ui/quick_terminal.py brightness-info'

Then use:
  yt              - Open YouTube
  ss              - Screenshot and copy
  ss-chat         - Send to ChatGPT
  bright-up       - Increase brightness
  bright-down     - Decrease brightness
"""

# ============================================================================
# PYTHON LIBRARY USAGE
# ============================================================================

"""
from ui.quick_terminal import QuickTerminal

qt = QuickTerminal()

# YouTube
qt.open_youtube()

# Screenshots
qt.screenshot_and_copy()
qt.send_screenshot_to_chatgpt()

# Brightness
qt.brightness_up()
qt.brightness_down()
qt.set_brightness(75)
qt.get_brightness()

# ChatGPT
qt.open_chatgpt()
"""

# ============================================================================
# FEATURES IN DETAIL
# ============================================================================

"""
1. YOUTUBE OPEN:
   - Detects if Firefox is running
   - If not: Starts Firefox with YouTube
   - If yes: Opens YouTube in new tab
   
2. SCREENSHOT & COPY:
   - Takes screenshot using gnome-screenshot, scrot, or ImageMagick
   - Automatically copies to clipboard using xclip or wl-copy
   - Saves to ~/.cache/caelestia/screenshots/
   
3. CHATGPT SCREENSHOT WORKFLOW:
   Step 1: Take screenshot
   Step 2: Copy to clipboard
   Step 3: Open/switch to ChatGPT (reuses tab if open)
   Step 4: Paste screenshot (Ctrl+V)
   Step 5: Optional auto-send
   
   Complete in ~5-10 seconds!
   
4. BRIGHTNESS CONTROL:
   - Uses brightnessctl for hardware control
   - Up/Down: ±10% (configurable)
   - Set: Any percentage 1-100%
   - Get: Read current brightness
"""

# ============================================================================
# WORKFLOWS
# ============================================================================

"""
WORKFLOW 1: Quick YouTube
  Terminal: yt
  Result: YouTube opens in Firefox
  
WORKFLOW 2: Share screenshot on ChatGPT
  Terminal: ss-chat
  Automated:
    1. Screens hots current screen
    2. Copies image to clipboard
    3. Opens ChatGPT (reuses existing window)
    4. Pastes image in chat
    5. Prompts to send or not
  Result: Screenshot in ChatGPT within 10 seconds
  
WORKFLOW 3: Adjust brightness
  Terminal: bright-up
  Result: Brightness increases by 10%
  
  Terminal: bright 50
  Result: Brightness set to 50%
  
  Terminal: bright-info
  Result: Shows current brightness: 45%
         Current: 45 / Max: 100
"""

# ============================================================================
# DEPENDENCIES
# ============================================================================

"""
REQUIRED:
  - brightnessctl: sudo pacman -S brightnessctl
  - xclip or wl-copy: 
    - X11: sudo pacman -S xclip
    - Wayland: sudo pacman -S wl-clipboard
  - Screenshot tool (at least one):
    - gnome-screenshot: sudo pacman -S gnome-screenshot
    - scrot: sudo pacman -S scrot
    - ImageMagick: sudo pacman -S imagemagick

OPTIONAL:
  - xdotool: For better window detection (sudo pacman -S xdotool)
  - Firefox or Chrome (for browser automation)

ALL DEPENDENCIES:
  sudo pacman -S brightnessctl xclip gnome-screenshot xdotool firefox
"""

# ============================================================================
# SETUP
# ============================================================================

"""
1. Install dependencies:
   sudo pacman -S brightnessctl xclip gnome-screenshot xdotool firefox

2. Add shortcuts to shell config:
   
   Fish (~/.config/fish/config.fish):
   ====================================
   alias yt='python /home/dmannu/ai-model-8/ui/quick_terminal.py youtube'
   alias ss='python /home/dmannu/ai-model-8/ui/quick_terminal.py screenshot'
   alias ss-chat='python /home/dmannu/ai-model-8/ui/quick_terminal.py screenshot-to-chatgpt'
   alias bright-up='python /home/dmannu/ai-model-8/ui/quick_terminal.py brightness-up'
   alias bright-down='python /home/dmannu/ai-model-8/ui/quick_terminal.py brightness-down'
   
   Bash (~/.bashrc):
   =================
   alias yt='python /home/dmannu/ai-model-8/ui/quick_terminal.py youtube'
   alias ss='python /home/dmannu/ai-model-8/ui/quick_terminal.py screenshot'
   alias ss-chat='python /home/dmannu/ai-model-8/ui/quick_terminal.py screenshot-to-chatgpt'
   alias bright-up='python /home/dmannu/ai-model-8/ui/quick_terminal.py brightness-up'
   alias bright-down='python /home/dmannu/ai-model-8/ui/quick_terminal.py brightness-down'

3. Reload shell config:
   source ~/.config/fish/config.fish
   # or
   source ~/.bashrc

4. Test:
   yt                    # Should open YouTube
   bright-info           # Should show brightness
"""

# ============================================================================
# EXAMPLES
# ============================================================================

"""
EXAMPLE 1: Quick YouTube
  $ yt
  [→] Opening YouTube...
  [*] Firefox already running, opening YouTube in new tab...
  {"success": true, "action": "open_youtube", "url": "https://youtube.com"}

EXAMPLE 2: Screenshot Workflow
  $ ss
  [→] Taking screenshot...
  [→] Copying image to clipboard...
  [✓] Image copied to clipboard
  {"success": true, "action": "screenshot_and_copy", "path": "..."}

EXAMPLE 3: ChatGPT Screenshot
  $ ss-chat
  ============================================================
  SCREENSHOT → CHATGPT WORKFLOW
  ============================================================
  
  [1/4] Taking screenshot...
  [✓] Screenshot saved: /home/user/.cache/caelestia/screenshots/...
  
  [2/4] Copying to clipboard...
  [✓] Image copied to clipboard
  
  [3/4] Opening ChatGPT...
  [✓] ChatGPT tab found and activated
  
  [4/4] Pasting screenshot...
  [*] Finding message input area...
  [*] Pasting image (Ctrl+V)...
  [✓] Image pasted in ChatGPT
  
  [Optional] Auto-sending message...
  [?] Send message now? (y/n): y
  [*] Sending message...
  [✓] Message sent!
  
  ============================================================
  ✓ WORKFLOW COMPLETE
  ============================================================

EXAMPLE 4: Brightness Control
  $ bright-info
  Current brightness: 45%
  Current: 45 / Max: 100
  
  $ bright-up
  [→] Brightness up (10%)...
  [✓] Brightness increased
  
  $ bright 75
  [→] Setting brightness to 75%...
  [✓] Brightness set to 75%
"""

# ============================================================================
# ADVANCED USAGE
# ============================================================================

"""
CUSTOM SCREENSHOT REGIONS:
  from ui.quick_terminal import QuickTerminal
  
  qt = QuickTerminal()
  # Take screenshot of region (x=100, y=100, width=500, height=500)
  qt.screenshot_and_copy(region=(100, 100, 500, 500))

AUTO-SEND IN CHATGPT (Programmatic):
  from ui.quick_terminal import QuickTerminal
  
  qt = QuickTerminal()
  result = qt.send_screenshot_to_chatgpt()
  # User will be prompted to confirm send

BRIGHTNESS CHANGES (Programmatic):
  from ui.quick_terminal import QuickTerminal
  
  qt = QuickTerminal()
  qt.brightness_up(0.2)        # Increase by 20%
  qt.brightness_down(0.15)     # Decrease by 15%
  qt.set_brightness(85)        # Set to 85%
  brightness = qt.get_brightness()
  print(f"Brightness: {brightness['percent']}%")
"""

# ============================================================================
# TROUBLESHOOTING
# ============================================================================

"""
"No screenshot tool available":
  Install one:
  - gnome-screenshot: sudo pacman -S gnome-screenshot
  - scrot: sudo pacman -S scrot
  - ImageMagick: sudo pacman -S imagemagick

"No clipboard tool available":
  Install one:
  - X11: sudo pacman -S xclip
  - Wayland: sudo pacman -S wl-clipboard

"Firefox window not found":
  - Make sure Firefox is installed
  - Install xdotool for better window detection
  - sudo pacman -S xdotool

"ChatGPT tab not found, always opens new tab":
  - This is expected if ChatGPT wasn't open before
  - Subsequent uses will reuse the tab

"Image paste not working in ChatGPT":
  - Make sure you have an active ChatGPT session
  - Manually click in the message input box before running
  - Some browsers may require additional setup
"""

# ============================================================================
# KEYBOARD SHORTCUTS REFERENCE
# ============================================================================

"""
With aliases set up, just type:

  yt              Open YouTube
  ss              Screenshot (copy to clipboard)
  ss-chat         Screenshot to ChatGPT (full workflow)
  bright-up       Increase brightness by 10%
  bright-down     Decrease brightness by 10%
  bright-info     Show current brightness
  
With numbers:
  bright 50       Set brightness to 50%
  bright 75       Set brightness to 75%
  bright 100      Set brightness to 100%
"""

# ============================================================================
# SPEED COMPARISON
# ============================================================================

"""
Traditional way (Manual steps):
  1. Open screenshot tool      (1 sec)
  2. Take screenshot           (2 sec)
  3. Copy image to clipboard   (2 sec)
  4. Open Firefox              (2 sec)
  5. Navigate to ChatGPT       (3 sec)
  6. Click message box         (1 sec)
  7. Paste image (Ctrl+V)      (1 sec)
  8. Send message              (1 sec)
  Total: ~13 seconds

With Quick Terminal:
  $ ss-chat
  (Automatic workflow runs)
  Total: ~8-10 seconds
  + Prompts you to confirm send

Automation advantage: 3-5 seconds faster + less prone to error
"""

print(__doc__)
