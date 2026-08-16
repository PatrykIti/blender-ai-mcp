from __future__ import annotations

from typing import Any, Callable

from fastmcp import Context

from server.adapters.mcp.contracts.scene import SceneInspectResponseContract


def execute_scene_inspect(
    *,
    ctx: Context,
    action: str,
    object_name: str | None,
    detailed: bool,
    include_disabled: bool,
    material_filter: str | None,
    include_empty_slots: bool,
    include_bones: bool,
    modifier_name: str | None,
    include_node_tree: bool,
    inspect_object: Callable[[Context, str], dict[str, Any]],
    inspect_topology: Callable[[Context, str, bool], dict[str, Any]],
    inspect_modifiers: Callable[[Context, str | None, bool], dict[str, Any]],
    inspect_materials: Callable[[Context, str | None, bool], dict[str, Any]],
    inspect_constraints: Callable[[Context, str, bool], dict[str, Any]],
    inspect_modifier_data: Callable[[Context, str, str | None, bool], dict[str, Any]],
    inspect_render: Callable[[Context], dict[str, Any]],
    inspect_color_management: Callable[[Context], dict[str, Any]],
    inspect_world: Callable[[Context], dict[str, Any]],
) -> SceneInspectResponseContract:
    """Build the structured scene_inspect response from injected action handlers."""

    if action == "object":
        if object_name is None:
            return SceneInspectResponseContract(
                action="object",
                error="Error: 'object' action requires 'object_name' parameter.",
            )
        return SceneInspectResponseContract(action="object", payload=inspect_object(ctx, object_name))
    if action == "topology":
        if object_name is None:
            return SceneInspectResponseContract(
                action="topology",
                error="Error: 'topology' action requires 'object_name' parameter.",
            )
        return SceneInspectResponseContract(
            action="topology",
            payload=inspect_topology(ctx, object_name, detailed),
        )
    if action == "modifiers":
        return SceneInspectResponseContract(
            action="modifiers",
            payload=inspect_modifiers(ctx, object_name, include_disabled),
        )
    if action == "materials":
        return SceneInspectResponseContract(
            action="materials",
            payload=inspect_materials(ctx, material_filter, include_empty_slots),
        )
    if action == "constraints":
        if object_name is None:
            return SceneInspectResponseContract(
                action="constraints",
                error="Error: 'constraints' action requires 'object_name' parameter.",
            )
        return SceneInspectResponseContract(
            action="constraints",
            payload=inspect_constraints(ctx, object_name, include_bones),
        )
    if action == "modifier_data":
        if object_name is None:
            return SceneInspectResponseContract(
                action="modifier_data",
                error="Error: 'modifier_data' action requires 'object_name' parameter.",
            )
        return SceneInspectResponseContract(
            action="modifier_data",
            payload=inspect_modifier_data(ctx, object_name, modifier_name, include_node_tree),
        )
    if action == "render":
        return SceneInspectResponseContract(action="render", payload=inspect_render(ctx))
    if action == "color_management":
        return SceneInspectResponseContract(
            action="color_management",
            payload=inspect_color_management(ctx),
        )
    if action == "world":
        return SceneInspectResponseContract(action="world", payload=inspect_world(ctx))
    return SceneInspectResponseContract(
        action="object",
        error=(
            f"Unknown action '{action}'. Valid actions: object, topology, modifiers, "
            "materials, constraints, modifier_data, render, color_management, world"
        ),
    )


def inspect_scene_object(
    *,
    ctx: Context,
    name: str,
    get_scene_handler: Callable[[], Any],
) -> dict[str, Any]:
    handler = get_scene_handler()
    try:
        return handler.inspect_object(name)
    except RuntimeError as exc:
        return {"error": str(exc)}


def inspect_scene_render_settings(
    *,
    ctx: Context,
    get_scene_handler: Callable[[], Any],
) -> dict[str, Any]:
    handler = get_scene_handler()
    try:
        return handler.inspect_render_settings()
    except RuntimeError as exc:
        return {"error": str(exc)}


def inspect_scene_color_management(
    *,
    ctx: Context,
    get_scene_handler: Callable[[], Any],
) -> dict[str, Any]:
    handler = get_scene_handler()
    try:
        return handler.inspect_color_management()
    except RuntimeError as exc:
        return {"error": str(exc)}


def inspect_scene_world(
    *,
    ctx: Context,
    get_scene_handler: Callable[[], Any],
) -> dict[str, Any]:
    handler = get_scene_handler()
    try:
        return handler.inspect_world()
    except RuntimeError as exc:
        return {"error": str(exc)}


def inspect_scene_material_slots(
    *,
    ctx: Context,
    material_filter: str | None,
    include_empty_slots: bool,
    get_scene_handler: Callable[[], Any],
    info: Callable[[Context, str], None],
) -> dict[str, Any]:
    handler = get_scene_handler()
    try:
        result = handler.inspect_material_slots(
            material_filter=material_filter,
            include_empty_slots=include_empty_slots,
        )
        info(
            ctx,
            f"Material slot audit: {result.get('total_slots', 0)} slots "
            f"({result.get('assigned_slots', 0)} assigned, {result.get('empty_slots', 0)} empty)",
        )
        return result
    except RuntimeError as exc:
        return {"error": str(exc)}


def inspect_scene_mesh_topology(
    *,
    ctx: Context,
    object_name: str,
    detailed: bool,
    get_scene_handler: Callable[[], Any],
) -> dict[str, Any]:
    handler = get_scene_handler()
    try:
        return handler.inspect_mesh_topology(object_name, detailed)
    except RuntimeError as exc:
        return {"error": str(exc)}


def inspect_scene_modifiers(
    *,
    ctx: Context,
    object_name: str | None,
    include_disabled: bool,
    get_scene_handler: Callable[[], Any],
    info: Callable[[Context, str], None],
) -> dict[str, Any]:
    handler = get_scene_handler()
    try:
        result = handler.inspect_modifiers(object_name, include_disabled)
        info(
            ctx,
            f"Inspected modifiers: {result.get('modifier_count', 0)} on {result.get('object_count', 0)} objects",
        )
        return result
    except RuntimeError as exc:
        return {"error": str(exc)}


def inspect_scene_constraints(
    *,
    ctx: Context,
    object_name: str,
    include_bones: bool,
    get_scene_handler: Callable[[], Any],
) -> dict[str, Any]:
    handler = get_scene_handler()
    try:
        return handler.get_constraints(object_name, include_bones)
    except RuntimeError as exc:
        return {"error": str(exc)}


def inspect_scene_modifier_data(
    *,
    ctx: Context,
    object_name: str,
    modifier_name: str | None,
    include_node_tree: bool,
    modeling_get_modifier_data: Callable[[Context, str, str | None, bool], dict[str, Any]],
) -> dict[str, Any]:
    return modeling_get_modifier_data(ctx, object_name, modifier_name, include_node_tree)
