"""
Workspace registry for Elzyra-controlled UI boundaries.

Elzyra uses the normal shared Brave session. Isolation comes from Hyprland
workspace boundaries, not from a dedicated browser profile.
"""

from __future__ import annotations

from typing import Iterable, Optional


ALLOWED_WORKSPACES = [7, 8, 9]

WORKSPACE_REGISTRY = {
    7: "elzyrra_primary",
    8: "elzyrra_browser",
    9: "elzyrra_execution",
}


def is_allowed_workspace(workspace_id: int) -> bool:
    """Return True when the workspace belongs to Elzyra's boundary."""
    return workspace_id in ALLOWED_WORKSPACES


def get_workspace_name(workspace_id: int) -> str:
    """Return a stable human-readable name for a workspace."""
    return WORKSPACE_REGISTRY.get(workspace_id, f"workspace_{workspace_id}")


def get_workspace_priority_order(
    known_workspaces: Optional[Iterable[int]] = None,
) -> list[int]:
    """
    Return the workspace selection order for Elzyra.

    Primary order is 7 -> 8 -> 9. If those are occupied, expand from 9
    downward into other free workspaces first, then check higher-numbered
    workspaces as a last resort.
    """
    if known_workspaces is None:
        universe = list(range(1, 11))
    else:
        universe = sorted({int(workspace) for workspace in known_workspaces if int(workspace) > 0})

    minimum_allowed = min(ALLOWED_WORKSPACES)
    maximum_allowed = max(ALLOWED_WORKSPACES)

    lower_fallback = sorted(
        [workspace for workspace in universe if workspace < minimum_allowed],
        reverse=True,
    )
    higher_fallback = sorted(
        [workspace for workspace in universe if workspace > maximum_allowed],
        reverse=True,
    )

    primary = [workspace for workspace in ALLOWED_WORKSPACES if workspace in universe]
    return primary + lower_fallback + higher_fallback


def get_available_workspace(
    occupied_workspaces: Optional[Iterable[int]] = None,
    known_workspaces: Optional[Iterable[int]] = None,
) -> Optional[int]:
    """Return the first available workspace according to Elzyra policy."""
    occupied = {int(workspace) for workspace in (occupied_workspaces or [])}

    for workspace in get_workspace_priority_order(known_workspaces):
        if workspace not in occupied:
            return workspace

    return None
