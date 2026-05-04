from __future__ import annotations

import asyncio

from fastmcp import Context

from server.adapters.mcp.context_utils import ctx_info
from server.adapters.mcp.contracts.scene import SceneCustomPropertiesContract
from server.adapters.mcp.guided_contract import canonicalize_scene_clean_scene_arguments
from server.adapters.mcp.router_helper import route_tool_call
from server.adapters.mcp.session_capabilities import mark_guided_spatial_state_stale_async
from server.adapters.mcp.utils import parse_coordinate
from server.infrastructure.di import get_scene_handler

from .scene_guided_runtime import (
    hydrate_sync_route_session,
    legacy_route_report_result,
    report_has_successful_scene_clean_step,
    route_tool_call_report_for_context,
)


def route_scene_list_objects(
    ctx: Context,
    *,
    get_scene_handler_fn=get_scene_handler,
    route_tool_call_fn=route_tool_call,
    ctx_info_fn=ctx_info,
) -> str:
    def execute():
        handler = get_scene_handler_fn()
        try:
            result = handler.list_objects()
            ctx_info_fn(ctx, f"Listed {len(result)} objects")
            return str(result)
        except RuntimeError as exc:
            return str(exc)

    return route_tool_call_fn(tool_name="scene_list_objects", params={}, direct_executor=execute)


def route_scene_delete_object(
    name: str, ctx: Context, *, get_scene_handler_fn=get_scene_handler, route_tool_call_fn=route_tool_call
) -> str:
    return route_tool_call_fn(
        tool_name="scene_delete_object",
        params={"name": name},
        direct_executor=lambda: get_scene_handler_fn().delete_object(name),
    )


def route_scene_clean_scene(
    ctx: Context,
    *,
    keep_lights_and_cameras: bool | None = None,
    keep_lights: bool | None = None,
    keep_cameras: bool | None = None,
    get_scene_handler_fn=get_scene_handler,
    route_tool_call_fn=route_tool_call,
) -> str:
    canonical_arguments = canonicalize_scene_clean_scene_arguments(
        {
            key: value
            for key, value in {
                "keep_lights_and_cameras": keep_lights_and_cameras,
                "keep_lights": keep_lights,
                "keep_cameras": keep_cameras,
            }.items()
            if value is not None
        }
    )
    keep_lights_and_cameras_value = bool(canonical_arguments.get("keep_lights_and_cameras", True))
    return route_tool_call_fn(
        tool_name="scene_clean_scene",
        params={"keep_lights_and_cameras": keep_lights_and_cameras_value},
        direct_executor=lambda: get_scene_handler_fn().clean_scene(keep_lights_and_cameras_value),
    )


async def route_scene_clean_scene_async(
    ctx: Context,
    *,
    keep_lights_and_cameras: bool | None = None,
    keep_lights: bool | None = None,
    keep_cameras: bool | None = None,
    get_scene_handler_fn=get_scene_handler,
    hydrate_sync_route_session_fn=hydrate_sync_route_session,
    route_tool_call_report_for_context_fn=route_tool_call_report_for_context,
    legacy_route_report_result_fn=legacy_route_report_result,
    report_has_successful_scene_clean_step_fn=report_has_successful_scene_clean_step,
    mark_guided_spatial_state_stale_async_fn=mark_guided_spatial_state_stale_async,
    to_thread_fn=asyncio.to_thread,
) -> str:
    await hydrate_sync_route_session_fn(ctx)
    canonical_arguments = canonicalize_scene_clean_scene_arguments(
        {
            key: value
            for key, value in {
                "keep_lights_and_cameras": keep_lights_and_cameras,
                "keep_lights": keep_lights,
                "keep_cameras": keep_cameras,
            }.items()
            if value is not None
        }
    )
    keep_lights_and_cameras_value = bool(canonical_arguments.get("keep_lights_and_cameras", True))
    report = await to_thread_fn(
        route_tool_call_report_for_context_fn,
        ctx,
        tool_name="scene_clean_scene",
        params={"keep_lights_and_cameras": keep_lights_and_cameras_value},
        direct_executor=lambda: get_scene_handler_fn().clean_scene(keep_lights_and_cameras_value),
    )
    result = legacy_route_report_result_fn(report)
    if report_has_successful_scene_clean_step_fn(report):
        await mark_guided_spatial_state_stale_async_fn(
            ctx,
            tool_name="scene_clean_scene",
            reason="scene_clean_scene",
        )
    return str(result)


def route_scene_duplicate_object(
    ctx: Context,
    *,
    name: str,
    translation: str | list[float] | None = None,
    get_scene_handler_fn=get_scene_handler,
    route_tool_call_fn=route_tool_call,
    parse_coordinate_fn=parse_coordinate,
) -> str:
    def execute():
        handler = get_scene_handler_fn()
        try:
            parsed_translation = parse_coordinate_fn(translation)
            return str(handler.duplicate_object(name, parsed_translation))
        except (RuntimeError, ValueError) as exc:
            return str(exc)

    return route_tool_call_fn(
        tool_name="scene_duplicate_object",
        params={"name": name, "translation": translation},
        direct_executor=execute,
    )


def route_scene_set_active_object(
    ctx: Context,
    *,
    name: str,
    get_scene_handler_fn=get_scene_handler,
    route_tool_call_fn=route_tool_call,
) -> str:
    return route_tool_call_fn(
        tool_name="scene_set_active_object",
        params={"name": name},
        direct_executor=lambda: get_scene_handler_fn().set_active_object(name),
    )


def route_scene_set_mode(
    ctx: Context,
    *,
    mode: str,
    get_scene_handler_fn=get_scene_handler,
    route_tool_call_fn=route_tool_call,
) -> str:
    def execute():
        handler = get_scene_handler_fn()
        try:
            return handler.set_mode(mode)
        except ValueError as exc:
            return f"Validation error: {str(exc)}"
        except RuntimeError as exc:
            return str(exc)

    return route_tool_call_fn(tool_name="scene_set_mode", params={"mode": mode}, direct_executor=execute)


def route_scene_rename_object(
    ctx: Context,
    *,
    old_name: str,
    new_name: str,
    get_scene_handler_fn=get_scene_handler,
    route_tool_call_fn=route_tool_call,
) -> str:
    def execute():
        handler = get_scene_handler_fn()
        try:
            return handler.rename_object(old_name, new_name)
        except RuntimeError as exc:
            return str(exc)

    return route_tool_call_fn(
        tool_name="scene_rename_object",
        params={"old_name": old_name, "new_name": new_name},
        direct_executor=execute,
    )


def route_scene_hide_object(
    ctx: Context,
    *,
    object_name: str,
    hide: bool = True,
    hide_render: bool = False,
    get_scene_handler_fn=get_scene_handler,
    route_tool_call_fn=route_tool_call,
) -> str:
    def execute():
        handler = get_scene_handler_fn()
        try:
            return handler.hide_object(object_name, hide, hide_render)
        except RuntimeError as exc:
            return str(exc)

    return route_tool_call_fn(
        tool_name="scene_hide_object",
        params={"object_name": object_name, "hide": hide, "hide_render": hide_render},
        direct_executor=execute,
    )


def route_scene_show_all_objects(
    ctx: Context,
    *,
    include_render: bool = False,
    get_scene_handler_fn=get_scene_handler,
    route_tool_call_fn=route_tool_call,
) -> str:
    def execute():
        handler = get_scene_handler_fn()
        try:
            return handler.show_all_objects(include_render)
        except RuntimeError as exc:
            return str(exc)

    return route_tool_call_fn(
        tool_name="scene_show_all_objects",
        params={"include_render": include_render},
        direct_executor=execute,
    )


def route_scene_isolate_object(
    ctx: Context,
    *,
    object_name: str | list[str],
    get_scene_handler_fn=get_scene_handler,
    route_tool_call_fn=route_tool_call,
) -> str:
    def execute():
        handler = get_scene_handler_fn()
        try:
            names = [object_name] if isinstance(object_name, str) else list(object_name)
            return handler.isolate_object(names)
        except RuntimeError as exc:
            return str(exc)

    return route_tool_call_fn(
        tool_name="scene_isolate_object",
        params={"object_name": object_name},
        direct_executor=execute,
    )


def route_scene_camera_orbit(
    ctx: Context,
    *,
    angle_horizontal: float = 0.0,
    angle_vertical: float = 0.0,
    target_object: str | None = None,
    target_point: str | list[float] | None = None,
    get_scene_handler_fn=get_scene_handler,
    route_tool_call_fn=route_tool_call,
    parse_coordinate_fn=parse_coordinate,
) -> str:
    def execute():
        handler = get_scene_handler_fn()
        try:
            parsed_point = parse_coordinate_fn(target_point)
            return handler.camera_orbit(angle_horizontal, angle_vertical, target_object, parsed_point)
        except RuntimeError as exc:
            return str(exc)

    return route_tool_call_fn(
        tool_name="scene_camera_orbit",
        params={
            "angle_horizontal": angle_horizontal,
            "angle_vertical": angle_vertical,
            "target_object": target_object,
            "target_point": target_point,
        },
        direct_executor=execute,
    )


def route_scene_camera_focus(
    ctx: Context,
    *,
    object_name: str,
    zoom_factor: float = 1.0,
    get_scene_handler_fn=get_scene_handler,
    route_tool_call_fn=route_tool_call,
) -> str:
    def execute():
        handler = get_scene_handler_fn()
        try:
            return handler.camera_focus(object_name, zoom_factor)
        except RuntimeError as exc:
            return str(exc)

    return route_tool_call_fn(
        tool_name="scene_camera_focus",
        params={"object_name": object_name, "zoom_factor": zoom_factor},
        direct_executor=execute,
    )


def route_scene_get_custom_properties(
    ctx: Context,
    *,
    object_name: str,
    get_scene_handler_fn=get_scene_handler,
    route_tool_call_fn=route_tool_call,
    ctx_info_fn=ctx_info,
) -> SceneCustomPropertiesContract | str:
    def execute():
        handler = get_scene_handler_fn()
        try:
            result = SceneCustomPropertiesContract.model_validate(handler.get_custom_properties(object_name))
            ctx_info_fn(ctx, f"Retrieved {result.property_count} custom properties from '{object_name}'")
            return result
        except RuntimeError as exc:
            return SceneCustomPropertiesContract(error=str(exc), object_name=object_name)

    return route_tool_call_fn(
        tool_name="scene_get_custom_properties",
        params={"object_name": object_name},
        direct_executor=execute,
    )


def route_scene_set_custom_property(
    ctx: Context,
    *,
    object_name: str,
    property_name: str,
    property_value: str | int | float | bool,
    delete: bool = False,
    get_scene_handler_fn=get_scene_handler,
    route_tool_call_fn=route_tool_call,
) -> str:
    def execute():
        handler = get_scene_handler_fn()
        try:
            return handler.set_custom_property(object_name, property_name, property_value, delete)
        except RuntimeError as exc:
            return str(exc)

    return route_tool_call_fn(
        tool_name="scene_set_custom_property",
        params={
            "object_name": object_name,
            "property_name": property_name,
            "property_value": property_value,
            "delete": delete,
        },
        direct_executor=execute,
    )
