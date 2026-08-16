from __future__ import annotations

from typing import Any, Callable

from fastmcp import Context

from server.adapters.mcp.contracts.scene import (
    SceneBoundingBoxContract,
    SceneContextResponseContract,
    SceneHierarchyContract,
    SceneModeContract,
    SceneOriginInfoContract,
    SceneSelectionContract,
    SceneSnapshotDiffContract,
    SceneSnapshotStateContract,
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


def execute_scene_snapshot_state(
    *,
    ctx: Context,
    include_mesh_stats: bool,
    include_materials: bool,
    get_scene_handler: Callable[[], Any],
    info: Callable[[Context, str], None],
) -> SceneSnapshotStateContract:
    """Builds the snapshot-state contract from the current scene."""

    handler = get_scene_handler()
    try:
        contract = SceneSnapshotStateContract.model_validate(
            handler.snapshot_state(include_mesh_stats=include_mesh_stats, include_materials=include_materials)
        )
        snapshot = contract.snapshot
        snapshot_hash = contract.hash
        object_count = snapshot.get("object_count", 0) if isinstance(snapshot, dict) else 0
        info(ctx, f"Snapshot captured: {object_count} objects, hash={(snapshot_hash or '')[:8]}")
        return contract
    except RuntimeError as exc:
        return SceneSnapshotStateContract(error=str(exc))


def execute_scene_compare_snapshot(
    *,
    ctx: Context,
    baseline_snapshot: str,
    target_snapshot: str,
    ignore_minor_transforms: float,
    get_snapshot_diff_service: Callable[[], Any],
    info: Callable[[Context, str], None],
) -> SceneSnapshotDiffContract:
    """Builds the snapshot-diff contract for two serialized scene snapshots."""

    diff_service = get_snapshot_diff_service()
    try:
        result = SceneSnapshotDiffContract.model_validate(
            diff_service.compare_snapshots(
                baseline_snapshot=baseline_snapshot,
                target_snapshot=target_snapshot,
                ignore_minor_transforms=ignore_minor_transforms,
            )
        )
    except ValueError as exc:
        return SceneSnapshotDiffContract(error=str(exc))

    info(
        ctx,
        "Snapshot diff: "
        f"+{len(result.objects_added or [])} "
        f"-{len(result.objects_removed or [])} "
        f"~{len(result.objects_modified or [])}",
    )
    return result


def execute_scene_get_hierarchy(
    *,
    ctx: Context,
    object_name: str | None,
    include_transforms: bool,
    get_scene_handler: Callable[[], Any],
    info: Callable[[Context, str], None],
) -> SceneHierarchyContract:
    """Builds the structured hierarchy read contract."""

    handler = get_scene_handler()
    try:
        result = SceneHierarchyContract(payload=handler.get_hierarchy(object_name, include_transforms))
        info(ctx, f"Retrieved hierarchy for {object_name or 'full scene'}")
        return result
    except RuntimeError as exc:
        return SceneHierarchyContract(error=str(exc))


def execute_scene_get_bounding_box(
    *,
    ctx: Context,
    object_name: str,
    world_space: bool,
    get_scene_handler: Callable[[], Any],
    info: Callable[[Context, str], None],
) -> SceneBoundingBoxContract:
    """Builds the structured bounding-box read contract."""

    handler = get_scene_handler()
    try:
        result = SceneBoundingBoxContract(payload=handler.get_bounding_box(object_name, world_space))
        info(ctx, f"Retrieved bounding box for '{object_name}'")
        return result
    except RuntimeError as exc:
        return SceneBoundingBoxContract(error=str(exc))


def execute_scene_get_origin_info(
    *,
    ctx: Context,
    object_name: str,
    get_scene_handler: Callable[[], Any],
    info: Callable[[Context, str], None],
) -> SceneOriginInfoContract:
    """Builds the structured origin-info read contract."""

    handler = get_scene_handler()
    try:
        result = SceneOriginInfoContract(payload=handler.get_origin_info(object_name))
        info(ctx, f"Retrieved origin info for '{object_name}'")
        return result
    except RuntimeError as exc:
        return SceneOriginInfoContract(error=str(exc))
