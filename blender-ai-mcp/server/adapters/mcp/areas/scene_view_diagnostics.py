from __future__ import annotations

from typing import Literal

from fastmcp import Context

from server.adapters.mcp.context_utils import ctx_info
from server.adapters.mcp.contracts.scene import (
    SceneAssembledTargetScopeContract,
    SceneViewDiagnosticsPayloadContract,
    SceneViewDiagnosticsResponseContract,
    SceneViewDiagnosticsSummaryContract,
    SceneViewDiagnosticsTargetContract,
    SceneViewProjectionEvidenceContract,
    SceneViewQueryContract,
)
from server.adapters.mcp.router_helper import route_tool_call, route_tool_call_async
from server.adapters.mcp.session_capabilities import (
    describe_guided_flow_feedback,
    get_session_capability_state_async,
    record_guided_flow_spatial_check_completion,
    record_guided_flow_spatial_check_completion_async,
)
from server.infrastructure.di import get_scene_handler

from .scene_guided_runtime import (
    guided_scope_mismatch_message,
    guided_scope_requirement_error,
    hydrate_sync_route_session,
    view_diagnostics_can_complete_guided_check,
)


def route_scene_view_diagnostics(
    ctx: Context,
    *,
    target_object: str | None = None,
    target_objects: list[str] | None = None,
    collection_name: str | None = None,
    camera_name: str | None = None,
    focus_target: str | None = None,
    view_name: Literal["FRONT", "RIGHT", "TOP"] | None = None,
    orbit_horizontal: float = 0.0,
    orbit_vertical: float = 0.0,
    zoom_factor: float | None = None,
    persist_view: bool = False,
    get_scene_handler_fn=get_scene_handler,
    route_tool_call_fn=route_tool_call,
    guided_scope_requirement_error_fn=guided_scope_requirement_error,
    guided_scope_mismatch_message_fn=guided_scope_mismatch_message,
    view_diagnostics_can_complete_guided_check_fn=view_diagnostics_can_complete_guided_check,
    record_guided_flow_spatial_check_completion_fn=record_guided_flow_spatial_check_completion,
) -> SceneViewDiagnosticsResponseContract:
    def execute() -> SceneViewDiagnosticsResponseContract:
        if not any([target_object, target_objects, collection_name]):
            return SceneViewDiagnosticsResponseContract(
                error=guided_scope_requirement_error_fn("scene_view_diagnostics"),
            )

        handler = get_scene_handler_fn()
        try:
            scope = SceneAssembledTargetScopeContract.model_validate(
                handler.get_scope_graph(
                    target_object=target_object,
                    target_objects=target_objects,
                    collection_name=collection_name,
                )
            )
            raw_payload = handler.get_view_diagnostics(
                target_object=scope.primary_target or target_object,
                target_objects=list(scope.object_names or []),
                camera_name=camera_name,
                focus_target=focus_target,
                view_name=view_name,
                orbit_horizontal=orbit_horizontal,
                orbit_vertical=orbit_vertical,
                zoom_factor=zoom_factor,
                persist_view=persist_view,
            )
            target_contracts = [
                SceneViewDiagnosticsTargetContract.model_validate(
                    {
                        **item,
                        "projection": (
                            SceneViewProjectionEvidenceContract.model_validate(item["projection"])
                            if isinstance(item, dict) and isinstance(item.get("projection"), dict)
                            else item.get("projection")
                            if isinstance(item, dict)
                            else None
                        ),
                    }
                )
                for item in list(raw_payload.get("targets") or [])
                if isinstance(item, dict)
            ]
            payload = SceneViewDiagnosticsPayloadContract(
                view_query=SceneViewQueryContract.model_validate(raw_payload.get("view_query") or {}),
                scope=scope,
                summary=SceneViewDiagnosticsSummaryContract.model_validate(raw_payload.get("summary") or {}),
                targets=target_contracts,
                message=(
                    "View diagnostics report projection/framing/occlusion state for the requested scope only; "
                    "use measure/assert tools for truth-space verification."
                ),
            )
            mismatch_message = guided_scope_mismatch_message_fn(
                ctx,
                tool_name="scene_view_diagnostics",
                resolved_scope=payload.scope.model_dump(mode="json"),
            )
            if mismatch_message:
                payload.message = f"{payload.message} {mismatch_message}" if payload.message else mismatch_message
            if view_diagnostics_can_complete_guided_check_fn(payload):
                record_guided_flow_spatial_check_completion_fn(
                    ctx,
                    tool_name="scene_view_diagnostics",
                    resolved_scope=payload.scope.model_dump(mode="json"),
                )
            return SceneViewDiagnosticsResponseContract(payload=payload)
        except (RuntimeError, ValueError) as exc:
            return SceneViewDiagnosticsResponseContract(error=str(exc))

    result = route_tool_call_fn(
        tool_name="scene_view_diagnostics",
        params={
            "target_object": target_object,
            "target_objects": target_objects,
            "collection_name": collection_name,
            "camera_name": camera_name,
            "focus_target": focus_target,
            "view_name": view_name,
            "orbit_horizontal": orbit_horizontal,
            "orbit_vertical": orbit_vertical,
            "zoom_factor": zoom_factor,
            "persist_view": persist_view,
        },
        direct_executor=execute,
    )
    if isinstance(result, SceneViewDiagnosticsResponseContract):
        return result
    if isinstance(result, dict):
        return SceneViewDiagnosticsResponseContract.model_validate(result)
    return SceneViewDiagnosticsResponseContract(error=str(result))


async def route_scene_view_diagnostics_async(
    ctx: Context,
    *,
    target_object: str | None = None,
    target_objects: list[str] | None = None,
    collection_name: str | None = None,
    camera_name: str | None = None,
    focus_target: str | None = None,
    view_name: Literal["FRONT", "RIGHT", "TOP"] | None = None,
    orbit_horizontal: float = 0.0,
    orbit_vertical: float = 0.0,
    zoom_factor: float | None = None,
    persist_view: bool = False,
    get_scene_handler_fn=get_scene_handler,
    route_tool_call_async_fn=route_tool_call_async,
    hydrate_sync_route_session_fn=hydrate_sync_route_session,
    guided_scope_requirement_error_fn=guided_scope_requirement_error,
    guided_scope_mismatch_message_fn=guided_scope_mismatch_message,
    view_diagnostics_can_complete_guided_check_fn=view_diagnostics_can_complete_guided_check,
    get_session_capability_state_async_fn=get_session_capability_state_async,
    record_guided_flow_spatial_check_completion_async_fn=record_guided_flow_spatial_check_completion_async,
    describe_guided_flow_feedback_fn=describe_guided_flow_feedback,
    ctx_info_fn=ctx_info,
) -> SceneViewDiagnosticsResponseContract:
    await hydrate_sync_route_session_fn(ctx)

    def execute() -> SceneViewDiagnosticsResponseContract:
        if not any([target_object, target_objects, collection_name]):
            return SceneViewDiagnosticsResponseContract(
                error=guided_scope_requirement_error_fn("scene_view_diagnostics"),
            )

        handler = get_scene_handler_fn()
        try:
            scope = SceneAssembledTargetScopeContract.model_validate(
                handler.get_scope_graph(
                    target_object=target_object,
                    target_objects=target_objects,
                    collection_name=collection_name,
                )
            )
            raw_payload = handler.get_view_diagnostics(
                target_object=scope.primary_target or target_object,
                target_objects=list(scope.object_names or []),
                camera_name=camera_name,
                focus_target=focus_target,
                view_name=view_name,
                orbit_horizontal=orbit_horizontal,
                orbit_vertical=orbit_vertical,
                zoom_factor=zoom_factor,
                persist_view=persist_view,
            )
            target_contracts = [
                SceneViewDiagnosticsTargetContract.model_validate(
                    {
                        **item,
                        "projection": (
                            SceneViewProjectionEvidenceContract.model_validate(item["projection"])
                            if isinstance(item, dict) and isinstance(item.get("projection"), dict)
                            else item.get("projection")
                            if isinstance(item, dict)
                            else None
                        ),
                    }
                )
                for item in list(raw_payload.get("targets") or [])
                if isinstance(item, dict)
            ]
            payload = SceneViewDiagnosticsPayloadContract(
                view_query=SceneViewQueryContract.model_validate(raw_payload.get("view_query") or {}),
                scope=scope,
                summary=SceneViewDiagnosticsSummaryContract.model_validate(raw_payload.get("summary") or {}),
                targets=target_contracts,
                message=(
                    "View diagnostics report projection/framing/occlusion state for the requested scope only; "
                    "use measure/assert tools for truth-space verification."
                ),
            )
            mismatch_message = guided_scope_mismatch_message_fn(
                ctx,
                tool_name="scene_view_diagnostics",
                resolved_scope=payload.scope.model_dump(mode="json"),
            )
            if mismatch_message:
                payload.message = f"{payload.message} {mismatch_message}" if payload.message else mismatch_message
            return SceneViewDiagnosticsResponseContract(payload=payload)
        except (RuntimeError, ValueError) as exc:
            return SceneViewDiagnosticsResponseContract(error=str(exc))

    result = await route_tool_call_async_fn(
        ctx,
        tool_name="scene_view_diagnostics",
        params={
            "target_object": target_object,
            "target_objects": target_objects,
            "collection_name": collection_name,
            "camera_name": camera_name,
            "focus_target": focus_target,
            "view_name": view_name,
            "orbit_horizontal": orbit_horizontal,
            "orbit_vertical": orbit_vertical,
            "zoom_factor": zoom_factor,
            "persist_view": persist_view,
        },
        direct_executor=execute,
    )
    if isinstance(result, SceneViewDiagnosticsResponseContract):
        contract = result
    elif isinstance(result, dict):
        contract = SceneViewDiagnosticsResponseContract.model_validate(result)
    else:
        contract = SceneViewDiagnosticsResponseContract(error=str(result))

    if contract.payload is not None and view_diagnostics_can_complete_guided_check_fn(contract.payload):
        previous_state = await get_session_capability_state_async_fn(ctx)
        await record_guided_flow_spatial_check_completion_async_fn(
            ctx,
            tool_name="scene_view_diagnostics",
            resolved_scope=contract.payload.scope.model_dump(mode="json"),
        )
        feedback = describe_guided_flow_feedback_fn(previous_state, await get_session_capability_state_async_fn(ctx))
        if feedback:
            contract.payload.message = (
                f"{contract.payload.message} {feedback}" if contract.payload.message else feedback
            )
            ctx_info_fn(ctx, feedback)
    return contract
