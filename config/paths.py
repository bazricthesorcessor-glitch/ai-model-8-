"""
Path resolver system for config files and OS integration.

Why path_of() exists:
- Models understand semantic names ("shell", "hyprland") better than raw paths
- Centralizes path definitions in one place (easier to refactor)
- Enables runtime path resolution without parsing config files
- Type-safe access: models can introspect available paths
"""

from pathlib import Path

HOME = Path.home()


class Paths:
    """Central registry of all configuration file paths."""

    # Hyprland window manager
    hyprland = HOME / ".config/hypr/hyprland.conf"
    hyprland_dir = HOME / ".config/hypr"
    hyprland_variables = HOME / ".config/hypr/variables.conf"
    hyprland_keybinds = HOME / ".config/hypr/hyprland/keybinds.conf"

    # Caelestia shell configuration
    shell = HOME / ".config/caelestia/shell.json"
    caelestia_dir = HOME / ".config/caelestia"


def path_of(name: str) -> Path:
    """
    Get a path by semantic name.

    Args:
        name: semantic name ("shell", "hyprland", "hyprland_dir", etc)

    Returns:
        Path object expanded to user home

    Raises:
        ValueError: if name not found in path registry

    Examples:
        >>> path_of("shell")
        Path('/home/dmannu/.config/caelestia/shell.json')

        >>> path_of("hyprland")
        Path('/home/dmannu/.config/hypr/hyprland.conf')
    """
    mapping = {
        "shell": Paths.shell,
        "hyprland": Paths.hyprland,
        "hyprland_dir": Paths.hyprland_dir,
        "hyprland_variables": Paths.hyprland_variables,
        "hyprland_keybinds": Paths.hyprland_keybinds,
        "caelestia_dir": Paths.caelestia_dir,
    }

    if name not in mapping:
        available = ", ".join(sorted(mapping.keys()))
        raise ValueError(f"Path not found: '{name}'. Available: {available}")

    return mapping[name]
