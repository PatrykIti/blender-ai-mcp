from __future__ import annotations

import base64
from datetime import datetime
from typing import Any, Literal

from fastmcp import Context
from fastmcp.utilities.types import Image

from server.adapters.mcp.router_helper import route_tool_call
from server.adapters.mcp.tasks.task_bridge import is_background_task_context, run_rpc_background_job
from server.infrastructure.di import get_scene_handler
from server.infrastructure.tmp_paths import get_viewport_output_paths


def format_viewport_output(
    b64_data: str,
    *,
    width: int,
    height: int,
    shading: str,
    output_mode: str | None,
) -> Image | str:
    mode_val = (output_mode or "IMAGE").upper()

    if mode_val == "IMAGE":
        image_bytes = base64.b64decode(b64_data)
        return Image(data=image_bytes, format="jpeg")

    if mode_val == "BASE64":
        return b64_data

    if mode_val in {"FILE", "MARKDOWN"}:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"viewport_{timestamp}.jpg"
        internal_file, internal_latest, external_file, external_latest = get_viewport_output_paths(filename)
        image_bytes = base64.b64decode(b64_data)
        internal_file.write_bytes(image_bytes)
        internal_latest.write_bytes(image_bytes)

        header = (
            f"Viewport render saved.\n\n"
            f"Timestamped file: {external_file}\n"
            f"Latest file: {external_latest}\n\n"
            f"Resolution: {width}x{height}, shading: {shading}."
        )

        if mode_val == "FILE":
            return header

        data_url = f"data:image/jpeg;base64,{b64_data}"
        return (
            f"Viewport render saved to: {external_latest}\n\n"
            f"**Preview ({width}x{height}, {shading} mode):**\n\n"
            f"![Viewport]({data_url})\n\n"
            f"*Note: If you cannot see the image above, open the file at: {external_latest}*"
        )

    return f"Invalid output_mode '{mode_val}'. Allowed values are: IMAGE, BASE64, FILE, MARKDOWN."


async def route_scene_get_viewport(
    ctx: Context,
    *,
    width: int,
    height: int,
    shading: str,
    camera_name: str | None,
    focus_target: str | None,
    view_name: str | None,
    orbit_horizontal: float,
    orbit_vertical: float,
    zoom_factor: float | None,
    persist_view: bool,
    output_mode: Literal["IMAGE", "BASE64", "FILE", "MARKDOWN"],
    get_scene_handler_fn=get_scene_handler,
    is_background_task_context_fn=is_background_task_context,
    run_rpc_background_job_fn=run_rpc_background_job,
    route_tool_call_fn=route_tool_call,
    format_viewport_output_fn=format_viewport_output,
) -> Image | str:
    if is_background_task_context_fn(ctx):

        def _foreground_rpc() -> str:
            handler = get_scene_handler_fn()
            return handler.get_viewport(
                width,
                height,
                shading,
                camera_name,
                focus_target,
                view_name,
                orbit_horizontal,
                orbit_vertical,
                zoom_factor,
                persist_view,
            )

        def _format_result(payload: Any) -> Image | str:
            if not isinstance(payload, str):
                raise RuntimeError("Background viewport job returned an invalid payload")
            return format_viewport_output_fn(
                payload,
                width=width,
                height=height,
                shading=shading,
                output_mode=output_mode,
            )

        return await run_rpc_background_job_fn(
            ctx,
            tool_name="scene_get_viewport",
            rpc_cmd="scene.get_viewport",
            rpc_args={
                "width": width,
                "height": height,
                "shading": shading,
                "camera_name": camera_name,
                "focus_target": focus_target,
                "view_name": view_name,
                "orbit_horizontal": orbit_horizontal,
                "orbit_vertical": orbit_vertical,
                "zoom_factor": zoom_factor,
                "persist_view": persist_view,
            },
            foreground_executor=_foreground_rpc,
            result_formatter=_format_result,
            start_message="Launching viewport capture in Blender",
            completion_message="Viewport capture completed",
        )

    def execute():
        handler = get_scene_handler_fn()
        try:
            b64_data = handler.get_viewport(
                width,
                height,
                shading,
                camera_name,
                focus_target,
                view_name,
                orbit_horizontal,
                orbit_vertical,
                zoom_factor,
                persist_view,
            )
        except RuntimeError as exc:
            return str(exc)
        return format_viewport_output_fn(
            b64_data,
            width=width,
            height=height,
            shading=shading,
            output_mode=output_mode,
        )

    return route_tool_call_fn(
        tool_name="scene_get_viewport",
        params={
            "width": width,
            "height": height,
            "shading": shading,
            "camera_name": camera_name,
            "focus_target": focus_target,
            "view_name": view_name,
            "orbit_horizontal": orbit_horizontal,
            "orbit_vertical": orbit_vertical,
            "zoom_factor": zoom_factor,
            "persist_view": persist_view,
            "output_mode": output_mode,
        },
        direct_executor=execute,
    )
