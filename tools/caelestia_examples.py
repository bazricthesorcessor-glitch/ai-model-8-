"""
Caelestia Integration Examples

Practical examples of using Caelestia shell commands in AI workflows.
"""

from tools.caelestia import CaelestiaShell, ToastType, ResizeConfig, MediaAction


def example_notification_workflow():
    """Example: Clear notifications and toggle DND"""
    shell = CaelestiaShell()

    # User entering focus mode
    shell.clear_notifications()
    shell.enable_dnd()
    shell.send_toast(
        "Focus Mode",
        "Notifications disabled, notifications cleared",
        ToastType.SUCCESS,
        "emblem-ok"
    )


def example_night_mode_workflow():
    """Example: Set up night mode"""
    shell = CaelestiaShell()

    # Set dark wallpaper
    shell.set_wallpaper(
        "/home/dmannu/Pictures/Wallpapers/Dark/night.jpg",
        smart_scheme=True
    )

    # Reduce brightness
    shell.set_brightness(20)

    # Enable DND
    shell.enable_dnd()

    # Send notification
    shell.send_toast(
        "Night Mode",
        "Dark wallpaper, brightness reduced",
        ToastType.INFO,
        "weather-clear-night"
    )


def example_gaming_workflow():
    """Example: Set up gaming mode"""
    shell = CaelestiaShell()

    # Enable game mode (auto-disables notifications)
    shell.enable_game_mode()

    # Prevent sleep during gaming
    shell.enable_idle_inhibitor()

    # Max brightness
    shell.set_brightness(100)

    # Pause music if playing
    shell.pause_media()

    # Notify user
    shell.send_toast(
        "Gaming Mode",
        "System optimized for gaming",
        ToastType.SUCCESS,
        "application-games"
    )


def example_media_control():
    """Example: Control media playback"""
    shell = CaelestiaShell()

    # Check active player
    player = shell.get_active_player()
    print(f"Currently playing: {player}")

    # Control playback
    shell.pause_media()
    shell.next_track()
    shell.toggle_media()

    # Notify
    shell.send_toast(
        "Media Control",
        "Track changed",
        ToastType.INFO,
        "media-skip-forward"
    )


def example_screen_capture_workflow():
    """Example: Take screenshot or record"""
    shell = CaelestiaShell()

    # Take full screenshot
    shell.screenshot()

    shell.send_toast(
        "Screenshot",
        "Full screen captured",
        ToastType.SUCCESS,
        "image-x-generic"
    )

    # Or record with audio
    # shell.start_recording(region=True, audio=True)


def example_window_management():
    """Example: Resize and manage windows"""
    shell = CaelestiaShell()

    # Resize active window to HD
    config = ResizeConfig(
        pattern="active",
        match_type="titleContains",
        width=1920,
        height=1080,
        actions=["float", "center"]
    )
    shell.resize_window(config)

    # PIP mode
    config_pip = ResizeConfig(
        pattern="pip",
        match_type="titleContains",
        width=400,
        height=300,
        actions=["float"]
    )
    shell.resize_window(config_pip)


def example_brightness_by_time():
    """Example: Adjust brightness based on time"""
    import datetime
    shell = CaelestiaShell()

    hour = datetime.datetime.now().hour

    if 6 <= hour < 18:  # Daytime
        shell.set_brightness(100)
        shell.disable_dnd()
    elif 18 <= hour < 21:  # Evening
        shell.set_brightness(75)
    else:  # Night
        shell.set_brightness(20)
        shell.enable_dnd()


def example_status_check():
    """Example: Check system status"""
    shell = CaelestiaShell()

    status = {
        "dnd_enabled": shell.is_dnd_enabled(),
        "game_mode": shell.is_game_mode_enabled(),
        "screen_locked": shell.is_screen_locked(),
        "brightness": shell.get_brightness(),
        "active_player": shell.get_active_player(),
    }

    print("System Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")


def example_ai_executor_integration():
    """Example: How to integrate into executor module"""

    # In executor/executor.py:
    from tools.caelestia import CaelestiaShell

    shell = CaelestiaShell()

    def execute_system_action(action: str, params: dict) -> dict:
        """Execute system control actions"""

        if action == "clear_notifications":
            success = shell.clear_notifications()
            return {"success": success, "action": action}

        elif action == "set_wallpaper":
            success = shell.set_wallpaper(params["path"])
            return {"success": success, "path": params["path"]}

        elif action == "lock_screen":
            success = shell.lock_screen()
            return {"success": success, "locked": True}

        elif action == "enable_game_mode":
            success = shell.enable_game_mode()
            return {"success": success, "game_mode": True}

        elif action == "set_brightness":
            success = shell.set_brightness(params["level"])
            return {"success": success, "brightness": params["level"]}

        elif action == "send_notification":
            success = shell.send_toast(
                title=params["title"],
                message=params["message"],
                icon=params.get("icon", "dialog-information")
            )
            return {"success": success, "notification": params}

        return {"success": False, "error": "Unknown action"}


def example_ai_brain_integration():
    """Example: How to use in brain module for decision making"""

    # In brain/brain.py:
    from tools.caelestia import CaelestiaShell
    from router import Message, Response

    shell = CaelestiaShell()

    def analyze_intent(message: Message) -> Response:
        """Analyze user intent and decide on actions"""

        intent = message.data.get("intent")

        if intent == "focus":
            # Decide: enable focus mode
            actions = [
                {
                    "type": "clear_notifications",
                    "description": "Clear all notifications"
                },
                {
                    "type": "enable_dnd",
                    "description": "Enable Do Not Disturb"
                },
                {
                    "type": "send_notification",
                    "title": "Focus Mode",
                    "message": "Notifications disabled",
                    "icon": "emblem-ok"
                }
            ]
            return Response(
                success=True,
                data={"intent": intent, "actions": actions}
            )

        elif intent == "night_mode":
            actions = [
                {"type": "set_brightness", "level": 20},
                {"type": "enable_dnd"},
                {
                    "type": "send_notification",
                    "title": "Night Mode",
                    "message": "System in night mode",
                    "icon": "weather-clear-night"
                }
            ]
            return Response(
                success=True,
                data={"intent": intent, "actions": actions}
            )

        return Response(
            success=False,
            error=f"Unknown intent: {intent}"
        )


if __name__ == "__main__":
    # Run examples
    print("=== Notification Workflow ===")
    example_notification_workflow()

    print("\n=== System Status ===")
    example_status_check()

    print("\n=== Media Control ===")
    example_media_control()
