from __future__ import annotations

from typing import Any, Callable

from fastmcp import Context

from server.adapters.mcp.contracts.scene import (
    SceneContextResponseContract,
    SceneModeContract,
    SceneSelectionContract,
)


def execute_scene_context(
    *,
    ctx: Context,
    action: str,
    read_mode: Callable[[Context], dict[str, Any]],
    read_selection: Callable[[Context], dict[str, Any]],
) -> SceneContextResponseContract:
    """Builds the structured scene_context response from injected read helpers."""

    if action == "mode":
        return SceneContextResponseContract(
            action="mode",
            payload=SceneModeContract.model_validate(read_mode(ctx)),
        )
    if action == "selection":
        return SceneContextResponseContract(
            action="selection",
            payload=SceneSelectionContract.model_validate(read_selection(ctx)),
        )
    return SceneContextResponseContract(
        action="mode",
        error=f"Unknown action '{action}'. Valid actions: mode, selection",
    )


def get_scene_mode(
    *,
    ctx: Context,
    get_scene_handler: Callable[[], Any],
) -> dict[str, Any]:
    """Reports the current Blender interaction mode and selection summary."""

    handler = get_scene_handler()
    try:
        return handler.get_mode()
    except RuntimeError as exc:
        return {"error": str(exc)}


def list_scene_selection(
    *,
    ctx: Context,
    get_scene_handler: Callable[[], Any],
) -> dict[str, Any]:
    """Lists the current selection summary in Object or Edit Mode."""

    handler = get_scene_handler()
    try:
        return handler.list_selection()
    except RuntimeError as exc:
        return {"error": str(exc)}
