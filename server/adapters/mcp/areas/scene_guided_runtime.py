from __future__ import annotations

from collections.abc import Callable
from typing import Any

from fastmcp import Context

from server.adapters.mcp.contracts.scene import SceneViewDiagnosticsPayloadContract
from server.adapters.mcp.router_helper import route_tool_call_report
from server.adapters.mcp.session_capabilities import (
    describe_guided_scope_mismatch,
    get_session_capability_state,
    get_session_capability_state_async,
    set_session_capability_state_async,
)


def guided_scope_requirement_error(tool_name: str) -> str:
    return (
        f"Provide target_object, target_objects, or collection_name for {tool_name}. "
        "On llm-guided, the active spatial gate requires explicit scope instead of an implicit whole-scene check."
    )


def should_require_explicit_guided_scope(ctx: Context) -> bool:
    try:
        session = get_session_capability_state(ctx)
    except Exception:
        return False

    flow_state = session.guided_flow_state or {}
    if not flow_state:
        return False
    current_step = str(flow_state.get("current_step") or "").strip().lower()
    spatial_refresh_required = bool(flow_state.get("spatial_refresh_required"))
    return current_step == "establish_spatial_context" or spatial_refresh_required


def guided_scope_mismatch_message(
    ctx: Context,
    *,
    tool_name: str,
    resolved_scope: dict[str, Any] | None,
) -> str | None:
    try:
        session = get_session_capability_state(ctx)
    except Exception:
        return None
    return describe_guided_scope_mismatch(
        session.guided_flow_state,
        tool_name=tool_name,
        resolved_scope=resolved_scope,
    )


def view_diagnostics_can_complete_guided_check(payload: SceneViewDiagnosticsPayloadContract) -> bool:
    if not payload.view_query.available:
        return False
    if any(target.projection_status != "unavailable" for target in payload.targets):
        return True
    return payload.summary.target_count > 0 and payload.summary.unavailable_count == 0


def legacy_route_report_result(report: Any) -> Any:
    if report.error is None and len(report.steps) == 1:
        result = report.steps[0].result
        if not isinstance(result, str):
            return result
    return report.to_legacy_text()


def report_has_successful_scene_clean_step(report: Any) -> bool:
    if getattr(report, "error", None) is not None:
        return False

    for step in getattr(report, "steps", ()) or ():
        if getattr(step, "tool_name", None) != "scene_clean_scene":
            continue
        if getattr(step, "error", None) is not None:
            continue
        result = getattr(step, "result", None)
        if isinstance(result, str) and result.strip().lower().startswith("scene cleaned"):
            return True
    return False


async def hydrate_sync_route_session(ctx: Context) -> None:
    state = await get_session_capability_state_async(ctx)
    await set_session_capability_state_async(ctx, state)


def route_tool_call_report_for_context(
    ctx: Context,
    *,
    tool_name: str,
    params: dict[str, Any],
    direct_executor: Callable[[], Any],
) -> Any:
    token = None
    current_context = None
    try:
        from fastmcp.server.context import _current_context  # type: ignore

        current_context = _current_context
        token = current_context.set(ctx)
    except Exception:
        current_context = None
        token = None
    try:
        return route_tool_call_report(tool_name=tool_name, params=params, direct_executor=direct_executor)
    finally:
        if current_context is not None and token is not None:
            current_context.reset(token)
