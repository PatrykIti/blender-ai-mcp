from __future__ import annotations

from typing import Any, Literal

from fastmcp import Context

from server.adapters.mcp.contracts.scene import SceneConfigureResponseContract, SceneCreateResponseContract


def execute_scene_create(
    *,
    ctx: Context,
    action: Literal["light", "camera", "empty"],
    location: Any,
    rotation: Any,
    name: str | None,
    light_type: str,
    energy: float,
    color: Any,
    lens: float,
    clip_start: float | None,
    clip_end: float | None,
    empty_type: str,
    size: float,
    parse_coordinate: Any,
    create_light: Any,
    create_camera: Any,
    create_empty: Any,
) -> SceneCreateResponseContract:
    """Build the grouped scene_create response using injected action helpers."""

    if action == "light":
        try:
            parsed_color = parse_coordinate(color) or [1.0, 1.0, 1.0]
            parsed_location = parse_coordinate(location) or [0.0, 0.0, 5.0]
            created_name = create_light(ctx, light_type, energy, parsed_color, parsed_location, name)
            return SceneCreateResponseContract(
                action="light",
                payload={
                    "object_name": created_name,
                    "object_type": "LIGHT",
                    "light_type": light_type,
                    "energy": energy,
                    "color": parsed_color,
                    "location": parsed_location,
                },
            )
        except (RuntimeError, ValueError) as exc:
            return SceneCreateResponseContract(action="light", error=str(exc))
    if action == "camera":
        try:
            parsed_camera_location = parse_coordinate(location) or None
            parsed_camera_rotation = parse_coordinate(rotation) or None
            if parsed_camera_location is None or parsed_camera_rotation is None:
                return SceneCreateResponseContract(
                    action="camera",
                    error="Invalid location or rotation coordinate payload.",
                )
            created_name = create_camera(
                ctx,
                parsed_camera_location,
                parsed_camera_rotation,
                lens,
                clip_start,
                clip_end,
                name,
            )
            return SceneCreateResponseContract(
                action="camera",
                payload={
                    "object_name": created_name,
                    "object_type": "CAMERA",
                    "location": parsed_camera_location,
                    "rotation": parsed_camera_rotation,
                    "lens": lens,
                    "clip_start": clip_start,
                    "clip_end": clip_end,
                },
            )
        except (RuntimeError, ValueError) as exc:
            return SceneCreateResponseContract(action="camera", error=str(exc))
    if action == "empty":
        try:
            parsed_location = parse_coordinate(location) or [0.0, 0.0, 0.0]
            created_name = create_empty(ctx, empty_type, size, parsed_location, name)
            return SceneCreateResponseContract(
                action="empty",
                payload={
                    "object_name": created_name,
                    "object_type": "EMPTY",
                    "empty_type": empty_type,
                    "size": size,
                    "location": parsed_location,
                },
            )
        except (RuntimeError, ValueError) as exc:
            return SceneCreateResponseContract(action="empty", error=str(exc))
    return SceneCreateResponseContract(
        action="light",
        error=f"Unknown action '{action}'. Valid actions: light, camera, empty",
    )


def execute_scene_create_light(
    *, ctx: Context, handler_getter: Any, type: str, energy: float, color: Any, location: Any, name: str | None
) -> str:
    """Create a light through the scene handler while preserving parse/error semantics."""

    handler = handler_getter()
    return handler.create_light(type, energy, color, location, name)


def execute_scene_create_camera(
    *,
    ctx: Context,
    handler_getter: Any,
    location: Any,
    rotation: Any,
    lens: float,
    clip_start: float | None,
    clip_end: float | None,
    name: str | None,
) -> str:
    """Create a camera through the scene handler."""

    handler = handler_getter()
    return handler.create_camera(location, rotation, lens, clip_start, clip_end, name)


def execute_scene_create_empty(
    *,
    ctx: Context,
    handler_getter: Any,
    type: str,
    size: float,
    location: Any,
    name: str | None,
) -> str:
    """Create an empty through the scene handler."""

    handler = handler_getter()
    return handler.create_empty(type, size, location, name)


def execute_scene_configure(
    *,
    ctx: Context,
    action: Literal["render", "color_management", "world"],
    settings: dict[str, Any],
    configure_render: Any,
    configure_color_management: Any,
    configure_world: Any,
) -> SceneConfigureResponseContract:
    """Build the grouped scene_configure response using injected action helpers."""

    if not isinstance(settings, dict):
        return SceneConfigureResponseContract(action=action, error="'settings' must be an object/dict.")

    try:
        if action == "render":
            return SceneConfigureResponseContract(
                action="render",
                payload=configure_render(ctx, settings),
            )
        if action == "color_management":
            return SceneConfigureResponseContract(
                action="color_management",
                payload=configure_color_management(ctx, settings),
            )
        if action == "world":
            return SceneConfigureResponseContract(
                action="world",
                payload=configure_world(ctx, settings),
            )
        return SceneConfigureResponseContract(
            action="render",
            error=f"Unknown action '{action}'. Valid actions: render, color_management, world",
        )
    except (RuntimeError, ValueError) as exc:
        return SceneConfigureResponseContract(action=action, error=str(exc))


def execute_scene_configure_render_settings(
    *, ctx: Context, settings: dict[str, Any], handler_getter: Any
) -> dict[str, Any]:
    """Apply grouped render settings through the scene handler."""

    return handler_getter().configure_render_settings(settings)


def execute_scene_configure_color_management(
    *, ctx: Context, settings: dict[str, Any], handler_getter: Any
) -> dict[str, Any]:
    """Apply grouped color-management settings through the scene handler."""

    return handler_getter().configure_color_management(settings)


def execute_scene_configure_world(*, ctx: Context, settings: dict[str, Any], handler_getter: Any) -> dict[str, Any]:
    """Apply grouped world settings through the scene handler."""

    return handler_getter().configure_world(settings)
