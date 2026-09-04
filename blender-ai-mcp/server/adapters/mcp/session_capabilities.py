# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Stable facade for adaptive FastMCP session-capability helpers."""

from __future__ import annotations

import asyncio
from typing import Any

from fastmcp import Context

from server.adapters.mcp.session_capabilities_bootstrap import (
    bootstrap_guided_empty_scene_primary_workset_async,
    build_guided_reference_readiness,
    build_guided_reference_readiness_payload,
    clear_session_goal_state,
    clear_session_goal_state_async,
    infer_phase_from_router_status,
    merge_resolved_params_with_session_answers,
    merge_resolved_params_with_session_answers_async,
    replace_session_pending_reference_images,
    replace_session_pending_reference_images_async,
    replace_session_reference_images,
    replace_session_reference_images_async,
    router_result_has_ready_guided_reference_goal,
    session_has_ready_guided_reference_goal,
    update_session_from_router_goal,
    update_session_from_router_goal_async,
)
from server.adapters.mcp.session_capabilities_flow import (
    describe_guided_flow_feedback,
    describe_guided_scope_mismatch,
    resolve_guided_role_group_for_domain,
)
from server.adapters.mcp.session_capabilities_registry import (
    advance_guided_flow_from_iteration_async,
    remove_guided_part_registrations,
    remove_guided_part_registrations_async,
)
from server.adapters.mcp.session_capabilities_runtime_glue import (
    apply_visibility_for_session_state,
    ingest_quality_gate_proposal,
    ingest_quality_gate_proposal_async,
    ingest_quality_gate_proposal_for_state,
    is_guided_spatial_state_dirtying_operation,
    mark_guided_spatial_state_stale_async,
    record_router_execution_outcome,
    update_quality_gate_plan_from_relation_graph_async,
)
from server.adapters.mcp.session_capabilities_state import (
    GuidedPartRegistryItem,
    GuidedReferenceReadinessState,
    SessionCapabilityState,
    get_session_capability_state,
    get_session_capability_state_async,
    set_session_capability_state,
    set_session_capability_state_async,
)

__all__ = [
    "GuidedPartRegistryItem",
    "GuidedReferenceReadinessState",
    "SessionCapabilityState",
    "apply_visibility_for_session_state",
    "advance_guided_flow_from_iteration_async",
    "bootstrap_guided_empty_scene_primary_workset_async",
    "build_guided_reference_readiness",
    "build_guided_reference_readiness_payload",
    "clear_session_goal_state",
    "clear_session_goal_state_async",
    "describe_guided_flow_feedback",
    "describe_guided_scope_mismatch",
    "get_session_capability_state",
    "get_session_capability_state_async",
    "infer_phase_from_router_status",
    "ingest_quality_gate_proposal",
    "ingest_quality_gate_proposal_async",
    "ingest_quality_gate_proposal_for_state",
    "is_guided_spatial_state_dirtying_operation",
    "mark_guided_spatial_state_stale",
    "mark_guided_spatial_state_stale_async",
    "merge_resolved_params_with_session_answers",
    "merge_resolved_params_with_session_answers_async",
    "record_guided_flow_spatial_check_completion",
    "record_guided_flow_spatial_check_completion_async",
    "record_router_execution_outcome",
    "refresh_visibility_for_session_state",
    "register_guided_part_role",
    "register_guided_part_role_async",
    "remove_guided_part_registrations",
    "remove_guided_part_registrations_async",
    "rename_guided_part_registration",
    "rename_guided_part_registration_async",
    "replace_session_pending_reference_images",
    "replace_session_pending_reference_images_async",
    "replace_session_reference_images",
    "replace_session_reference_images_async",
    "require_existing_scene_object_name",
    "resolve_guided_role_group_for_domain",
    "router_result_has_ready_guided_reference_goal",
    "session_has_ready_guided_reference_goal",
    "set_session_capability_state",
    "set_session_capability_state_async",
    "update_quality_gate_plan_from_relation_graph",
    "update_quality_gate_plan_from_relation_graph_async",
    "update_session_from_router_goal",
    "update_session_from_router_goal_async",
]


def _scene_object_names() -> set[str]:
    from server.infrastructure.di import get_scene_handler

    objects = get_scene_handler().list_objects()
    names: set[str] = set()
    for item in objects:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        if isinstance(name, str) and name.strip():
            names.add(name.strip())
    return names


def _normalize_guided_object_name(object_name: str) -> str:
    normalized_object_name = str(object_name or "").strip()
    if not normalized_object_name:
        raise ValueError("guided_register_part(...) requires a non-empty `object_name`.")
    return normalized_object_name


def require_existing_scene_object_name(object_name: str) -> str:
    normalized_object_name = _normalize_guided_object_name(object_name)

    try:
        object_names = _scene_object_names()
    except Exception as exc:
        raise ValueError(
            f"guided_register_part(...) could not validate object '{normalized_object_name}' against the Blender scene: {exc}"
        ) from exc

    if normalized_object_name not in object_names:
        raise ValueError(
            f"guided_register_part(...) requires an existing Blender object named '{normalized_object_name}'."
        )
    return normalized_object_name


def refresh_visibility_for_session_state(
    ctx: Context,
    state: SessionCapabilityState,
) -> None:
    """Best-effort sync wrapper for applying session visibility after sync tool calls."""

    if state.guided_flow_state is None:
        return
    if not all(
        callable(getattr(ctx, method_name, None))
        for method_name in ("reset_visibility", "enable_components", "disable_components")
    ):
        return

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        asyncio.run(apply_visibility_for_session_state(ctx, state))
        return

    # Do not schedule background visibility writes on an active FastMCP request
    # loop. Async call sites must await apply_visibility_for_session_state(...)
    # directly so request-path semantics stay deterministic.
    return


def update_quality_gate_plan_from_relation_graph(
    ctx: Context,
    relation_graph_payload: dict[str, Any],
) -> SessionCapabilityState:
    from server.adapters.mcp.session_capabilities_runtime_glue import update_quality_gate_plan_from_relation_graph

    return update_quality_gate_plan_from_relation_graph(
        ctx,
        relation_graph_payload,
        refresh_visibility=refresh_visibility_for_session_state,
    )


def mark_guided_spatial_state_stale(
    ctx: Context,
    *,
    tool_name: str,
    family: str | None = None,
    reason: str | None = None,
    affected_objects: list[str] | None = None,
) -> SessionCapabilityState:
    from server.adapters.mcp.session_capabilities_runtime_glue import mark_guided_spatial_state_stale

    return mark_guided_spatial_state_stale(
        ctx,
        tool_name=tool_name,
        family=family,
        reason=reason,
        affected_objects=affected_objects,
        refresh_visibility=refresh_visibility_for_session_state,
    )


def register_guided_part_role(
    ctx: Context,
    *,
    object_name: str,
    role: str,
    role_group: str | None = None,
) -> SessionCapabilityState:
    from server.adapters.mcp.session_capabilities_registry import register_guided_part_role

    return register_guided_part_role(
        ctx,
        object_name=_normalize_guided_object_name(object_name),
        role=role,
        role_group=role_group,
        refresh_visibility=refresh_visibility_for_session_state,
    )


def rename_guided_part_registration(
    ctx: Context,
    *,
    old_name: str,
    new_name: str,
) -> SessionCapabilityState:
    from server.adapters.mcp.session_capabilities_registry import rename_guided_part_registration

    return rename_guided_part_registration(
        ctx,
        old_name=old_name,
        new_name=require_existing_scene_object_name(new_name),
    )


async def rename_guided_part_registration_async(
    ctx: Context,
    *,
    old_name: str,
    new_name: str,
) -> SessionCapabilityState:
    from server.adapters.mcp.session_capabilities_registry import rename_guided_part_registration_async

    normalized_new_name = await asyncio.to_thread(require_existing_scene_object_name, new_name)
    return await rename_guided_part_registration_async(
        ctx,
        old_name=old_name,
        new_name=normalized_new_name,
    )


async def register_guided_part_role_async(
    ctx: Context,
    *,
    object_name: str,
    role: str,
    role_group: str | None = None,
) -> SessionCapabilityState:
    from server.adapters.mcp.session_capabilities_registry import register_guided_part_role_async

    return await register_guided_part_role_async(
        ctx,
        object_name=_normalize_guided_object_name(object_name),
        role=role,
        role_group=role_group,
        apply_visibility=apply_visibility_for_session_state,
    )


def record_guided_flow_spatial_check_completion(
    ctx: Context,
    *,
    tool_name: str,
    resolved_scope: dict[str, Any] | None = None,
) -> SessionCapabilityState:
    from server.adapters.mcp.session_capabilities_registry import record_guided_flow_spatial_check_completion

    return record_guided_flow_spatial_check_completion(
        ctx,
        tool_name=tool_name,
        resolved_scope=resolved_scope,
        refresh_visibility=refresh_visibility_for_session_state,
    )


async def record_guided_flow_spatial_check_completion_async(
    ctx: Context,
    *,
    tool_name: str,
    resolved_scope: dict[str, Any] | None = None,
) -> SessionCapabilityState:
    from server.adapters.mcp.session_capabilities_registry import record_guided_flow_spatial_check_completion_async

    return await record_guided_flow_spatial_check_completion_async(
        ctx,
        tool_name=tool_name,
        resolved_scope=resolved_scope,
        apply_visibility=apply_visibility_for_session_state,
    )
