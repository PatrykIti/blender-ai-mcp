# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Guided part-registry and flow-transition helpers."""

from __future__ import annotations

from collections.abc import Awaitable
from dataclasses import asdict, replace
from typing import Any, Callable

from fastmcp import Context

from server.adapters.mcp.contracts.guided_flow import GuidedFlowStateContract, GuidedTargetScopeContract
from server.adapters.mcp.session_capabilities_flow import (
    _GUIDED_FLOW_STOPPED_STEPS,
    _GUIDED_PRIMARY_REQUIRED_ROLES,
    _GUIDED_SCOPE_BINDING_TOOL_NAME,
    _GUIDED_SECONDARY_REQUIRED_ROLES,
    _SPATIAL_CONTEXT_TOOL_NAMES,
    _apply_role_summary,
    _apply_spatial_refresh_gate,
    _build_active_guided_target_scope_fingerprint,
    _build_guided_target_scope_fingerprint,
    _build_role_summary,
    _clear_spatial_refresh_gate,
    _flow_state_for_current_step,
    _is_bindable_guided_target_scope,
    _normalize_guided_target_scope,
    _resolve_guided_role_group,
)
from server.adapters.mcp.session_capabilities_runtime_glue import apply_visibility_for_session_state
from server.adapters.mcp.session_capabilities_state import (
    GuidedPartRegistryItem,
    SessionCapabilityState,
    get_session_capability_state,
    get_session_capability_state_async,
    set_session_capability_state,
    set_session_capability_state_async,
)
from server.adapters.mcp.session_phase import SessionPhase


def _update_guided_flow_role_summary_dict(
    flow_state: dict[str, Any],
    *,
    part_registry: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    contract = GuidedFlowStateContract.model_validate(flow_state)
    role_summary = _build_role_summary(
        domain_profile=contract.domain_profile,
        current_step=contract.current_step,
        part_registry=part_registry,
        completed_role_hints=contract.completed_roles,
    )
    _apply_role_summary(contract, role_summary)
    return contract.model_dump(mode="json")


def _maybe_advance_guided_flow_from_part_registry_dict(
    flow_state: dict[str, Any],
    *,
    part_registry: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    contract = GuidedFlowStateContract.model_validate(flow_state)
    current_role_summary = _build_role_summary(
        domain_profile=contract.domain_profile,
        current_step=contract.current_step,
        part_registry=part_registry,
        completed_role_hints=contract.completed_roles,
    )
    completed_roles = set(current_role_summary["completed_roles"])

    if contract.current_step in {"bootstrap_primary_workset", "create_primary_masses"}:
        required_roles = _GUIDED_PRIMARY_REQUIRED_ROLES[contract.domain_profile]
        if all(role in completed_roles for role in required_roles):
            if (
                contract.current_step == "bootstrap_primary_workset"
                and "bootstrap_primary_workset" not in contract.completed_steps
            ):
                contract.completed_steps.append("bootstrap_primary_workset")
            if "create_primary_masses" not in contract.completed_steps:
                contract.completed_steps.append("create_primary_masses")
            contract.current_step = "place_secondary_parts"
            contract.blocked_families = []
            _flow_state_for_current_step(contract, part_registry=part_registry)
            _apply_spatial_refresh_gate(contract, part_registry=part_registry, force=True)
    elif contract.current_step == "place_secondary_parts":
        required_roles = _GUIDED_SECONDARY_REQUIRED_ROLES[contract.domain_profile]
        if all(role in completed_roles for role in required_roles):
            if "place_secondary_parts" not in contract.completed_steps:
                contract.completed_steps.append("place_secondary_parts")
            contract.current_step = "checkpoint_iterate"
            contract.blocked_families = []
            _flow_state_for_current_step(contract, part_registry=part_registry)
            _apply_spatial_refresh_gate(contract, part_registry=part_registry, force=True)

    role_summary = _build_role_summary(
        domain_profile=contract.domain_profile,
        current_step=contract.current_step,
        part_registry=part_registry,
        completed_role_hints=contract.completed_roles,
    )
    _apply_role_summary(contract, role_summary)
    return contract.model_dump(mode="json")


async def register_guided_part_role_async(
    ctx: Context,
    *,
    object_name: str,
    role: str,
    role_group: str | None = None,
    apply_visibility: Callable[[Context, SessionCapabilityState], Awaitable[object]] | None = None,
) -> SessionCapabilityState:
    """Register or update one guided part role for the active guided session."""

    current = await get_session_capability_state_async(ctx)
    if current.guided_flow_state is None:
        raise ValueError("guided_register_part(...) requires an active guided flow session.")

    flow_state = GuidedFlowStateContract.model_validate(current.guided_flow_state)
    resolved_role = role.strip()
    if not resolved_role:
        raise ValueError("guided_register_part(...) requires a non-empty `role`.")
    resolved_role_group = _resolve_guided_role_group(
        domain_profile=flow_state.domain_profile,
        role=resolved_role,
        role_group=role_group,
    )
    normalized_object_name = str(object_name).strip()
    updated_registry = [
        item
        for item in list(current.guided_part_registry or [])
        if isinstance(item, dict) and item.get("object_name") != normalized_object_name
    ]
    updated_registry.append(
        asdict(
            GuidedPartRegistryItem(
                object_name=normalized_object_name,
                role=resolved_role,
                role_group=resolved_role_group,
                status="registered",
                created_in_step=flow_state.current_step,
            )
        )
    )
    updated_flow_state = _update_guided_flow_role_summary_dict(
        current.guided_flow_state,
        part_registry=updated_registry,
    )
    updated_flow_state = _maybe_advance_guided_flow_from_part_registry_dict(
        updated_flow_state,
        part_registry=updated_registry,
    )
    state = replace(current, guided_flow_state=updated_flow_state, guided_part_registry=updated_registry)
    await set_session_capability_state_async(ctx, state)
    if apply_visibility is None:
        await apply_visibility_for_session_state(ctx, state)
    else:
        await apply_visibility(ctx, state)
    return state


def register_guided_part_role(
    ctx: Context,
    *,
    object_name: str,
    role: str,
    role_group: str | None = None,
    refresh_visibility: Callable[[Context, SessionCapabilityState], None] | None = None,
) -> SessionCapabilityState:
    """Sync variant of guided part-role registration for synchronous tool wrappers."""

    current = get_session_capability_state(ctx)
    if current.guided_flow_state is None:
        raise ValueError("guided_register_part(...) requires an active guided flow session.")

    flow_state = GuidedFlowStateContract.model_validate(current.guided_flow_state)
    resolved_role = role.strip()
    if not resolved_role:
        raise ValueError("guided_register_part(...) requires a non-empty `role`.")
    resolved_role_group = _resolve_guided_role_group(
        domain_profile=flow_state.domain_profile,
        role=resolved_role,
        role_group=role_group,
    )
    normalized_object_name = str(object_name).strip()
    updated_registry = [
        item
        for item in list(current.guided_part_registry or [])
        if isinstance(item, dict) and item.get("object_name") != normalized_object_name
    ]
    updated_registry.append(
        asdict(
            GuidedPartRegistryItem(
                object_name=normalized_object_name,
                role=resolved_role,
                role_group=resolved_role_group,
                status="registered",
                created_in_step=flow_state.current_step,
            )
        )
    )
    updated_flow_state = _update_guided_flow_role_summary_dict(
        current.guided_flow_state,
        part_registry=updated_registry,
    )
    updated_flow_state = _maybe_advance_guided_flow_from_part_registry_dict(
        updated_flow_state,
        part_registry=updated_registry,
    )
    state = replace(current, guided_flow_state=updated_flow_state, guided_part_registry=updated_registry)
    set_session_capability_state(ctx, state)
    if refresh_visibility is not None:
        refresh_visibility(ctx, state)
    return state


def rename_guided_part_registration(
    ctx: Context,
    *,
    old_name: str,
    new_name: str,
) -> SessionCapabilityState:
    """Keep guided part registration aligned with one successful scene object rename."""

    current = get_session_capability_state(ctx)
    if current.guided_part_registry is None:
        return current

    normalized_old_name = str(old_name or "").strip()
    normalized_new_name = str(new_name or "").strip()
    if not normalized_old_name or normalized_old_name == normalized_new_name:
        return current

    changed = False
    updated_registry: list[dict[str, Any]] = []
    for item in list(current.guided_part_registry or []):
        if not isinstance(item, dict):
            continue
        updated_item = dict(item)
        if updated_item.get("object_name") == normalized_old_name:
            updated_item["object_name"] = normalized_new_name
            changed = True
        updated_registry.append(updated_item)

    if not changed:
        return current

    updated_flow_state = (
        _update_guided_flow_role_summary_dict(current.guided_flow_state, part_registry=updated_registry)
        if current.guided_flow_state is not None
        else None
    )
    state = replace(current, guided_flow_state=updated_flow_state, guided_part_registry=updated_registry)
    set_session_capability_state(ctx, state)
    return state


async def rename_guided_part_registration_async(
    ctx: Context,
    *,
    old_name: str,
    new_name: str,
) -> SessionCapabilityState:
    """Async variant of guided part registration rename for native FastMCP requests."""

    current = await get_session_capability_state_async(ctx)
    if current.guided_part_registry is None:
        return current

    normalized_old_name = str(old_name or "").strip()
    normalized_new_name = str(new_name or "").strip()
    if not normalized_old_name or normalized_old_name == normalized_new_name:
        return current

    changed = False
    updated_registry: list[dict[str, Any]] = []
    for item in list(current.guided_part_registry or []):
        if not isinstance(item, dict):
            continue
        updated_item = dict(item)
        if updated_item.get("object_name") == normalized_old_name:
            updated_item["object_name"] = normalized_new_name
            changed = True
        updated_registry.append(updated_item)

    if not changed:
        return current

    updated_flow_state = (
        _update_guided_flow_role_summary_dict(current.guided_flow_state, part_registry=updated_registry)
        if current.guided_flow_state is not None
        else None
    )
    state = replace(current, guided_flow_state=updated_flow_state, guided_part_registry=updated_registry)
    await set_session_capability_state_async(ctx, state)
    return state


def remove_guided_part_registrations(
    ctx: Context,
    *,
    object_names: list[str],
) -> SessionCapabilityState:
    """Remove guided part registrations for objects whose topology/identity changed materially."""

    current = get_session_capability_state(ctx)
    if current.guided_part_registry is None:
        return current

    names_to_remove = {str(name).strip() for name in object_names if str(name).strip()}
    if not names_to_remove:
        return current

    updated_registry = [
        dict(item)
        for item in list(current.guided_part_registry or [])
        if isinstance(item, dict) and str(item.get("object_name") or "").strip() not in names_to_remove
    ]
    if len(updated_registry) == len(list(current.guided_part_registry or [])):
        return current

    updated_flow_state = None
    if current.guided_flow_state is not None:
        contract = GuidedFlowStateContract.model_validate(current.guided_flow_state)
        contract.completed_roles = []
        contract.role_counts = {}
        contract.role_cardinality = {}
        contract.role_objects = {}
        updated_flow_state = _update_guided_flow_role_summary_dict(
            contract.model_dump(mode="json"),
            part_registry=updated_registry or None,
        )
    state = replace(current, guided_flow_state=updated_flow_state, guided_part_registry=updated_registry or None)
    set_session_capability_state(ctx, state)
    return state


async def remove_guided_part_registrations_async(
    ctx: Context,
    *,
    object_names: list[str],
) -> SessionCapabilityState:
    """Async variant of guided part registration removal for native FastMCP requests."""

    current = await get_session_capability_state_async(ctx)
    if current.guided_part_registry is None:
        return current

    names_to_remove = {str(name).strip() for name in object_names if str(name).strip()}
    if not names_to_remove:
        return current

    updated_registry = [
        dict(item)
        for item in list(current.guided_part_registry or [])
        if isinstance(item, dict) and str(item.get("object_name") or "").strip() not in names_to_remove
    ]
    if len(updated_registry) == len(list(current.guided_part_registry or [])):
        return current

    updated_flow_state = None
    if current.guided_flow_state is not None:
        contract = GuidedFlowStateContract.model_validate(current.guided_flow_state)
        contract.completed_roles = []
        contract.role_counts = {}
        contract.role_cardinality = {}
        contract.role_objects = {}
        updated_flow_state = _update_guided_flow_role_summary_dict(
            contract.model_dump(mode="json"),
            part_registry=updated_registry or None,
        )
    state = replace(current, guided_flow_state=updated_flow_state, guided_part_registry=updated_registry or None)
    await set_session_capability_state_async(ctx, state)
    return state


def _mark_guided_flow_check_completed_dict(
    flow_state: dict[str, Any],
    *,
    tool_name: str,
    resolved_scope: dict[str, Any] | None = None,
    part_registry: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    contract = GuidedFlowStateContract.model_validate(flow_state)
    normalized_scope = _normalize_guided_target_scope(resolved_scope)
    resolved_scope_fingerprint = _build_guided_target_scope_fingerprint(normalized_scope)
    changed = False

    if normalized_scope is None:
        for check in contract.required_checks:
            if check.tool_name == tool_name and check.status != "completed":
                check.status = "completed"
                changed = True

        if (
            changed
            and contract.required_checks
            and all(check.status == "completed" for check in contract.required_checks)
        ):
            if contract.spatial_refresh_required:
                _clear_spatial_refresh_gate(contract, part_registry=part_registry)
            elif contract.current_step == "establish_spatial_context":
                if "establish_spatial_context" not in contract.completed_steps:
                    contract.completed_steps.append("establish_spatial_context")
                contract.current_step = "create_primary_masses"
                contract.last_spatial_check_version = contract.spatial_state_version
                contract.spatial_state_stale = False
                contract.blocked_families = []
                _flow_state_for_current_step(contract, part_registry=part_registry)
        return contract.model_dump(mode="json")

    if tool_name == _GUIDED_SCOPE_BINDING_TOOL_NAME:
        should_bind = contract.active_target_scope is None
        if should_bind and _is_bindable_guided_target_scope(normalized_scope):
            contract.active_target_scope = GuidedTargetScopeContract.model_validate(normalized_scope)
            contract.spatial_scope_fingerprint = resolved_scope_fingerprint

    if contract.active_target_scope is None:
        return contract.model_dump(mode="json")
    if contract.spatial_refresh_required and tool_name != _GUIDED_SCOPE_BINDING_TOOL_NAME:
        scope_check = next(
            (check for check in contract.required_checks if check.tool_name == _GUIDED_SCOPE_BINDING_TOOL_NAME),
            None,
        )
        if scope_check is not None and scope_check.status != "completed":
            return contract.model_dump(mode="json")

    active_scope_fingerprint = _build_active_guided_target_scope_fingerprint(contract)
    if active_scope_fingerprint is None:
        return contract.model_dump(mode="json")
    contract.spatial_scope_fingerprint = active_scope_fingerprint

    if resolved_scope_fingerprint is None or resolved_scope_fingerprint != active_scope_fingerprint:
        return contract.model_dump(mode="json")

    for check in contract.required_checks:
        if check.tool_name == tool_name and check.status != "completed":
            check.status = "completed"
            changed = True

    if changed and contract.required_checks and all(check.status == "completed" for check in contract.required_checks):
        if contract.spatial_refresh_required:
            _clear_spatial_refresh_gate(contract, part_registry=part_registry)
        elif contract.current_step == "establish_spatial_context":
            if "establish_spatial_context" not in contract.completed_steps:
                contract.completed_steps.append("establish_spatial_context")
            contract.current_step = "create_primary_masses"
            contract.last_spatial_check_version = contract.spatial_state_version
            contract.spatial_state_stale = False
            contract.blocked_families = []
            _flow_state_for_current_step(contract, part_registry=part_registry)

    return contract.model_dump(mode="json")


def record_guided_flow_spatial_check_completion(
    ctx: Context,
    *,
    tool_name: str,
    resolved_scope: dict[str, Any] | None = None,
    refresh_visibility: Callable[[Context, SessionCapabilityState], None] | None = None,
) -> SessionCapabilityState:
    """Mark one spatial-context check as completed and advance the flow when ready."""

    if tool_name not in _SPATIAL_CONTEXT_TOOL_NAMES:
        return get_session_capability_state(ctx)

    current = get_session_capability_state(ctx)
    if current.guided_flow_state is None:
        return current

    updated_flow_state = _mark_guided_flow_check_completed_dict(
        current.guided_flow_state,
        tool_name=tool_name,
        resolved_scope=resolved_scope,
        part_registry=current.guided_part_registry,
    )
    state = replace(current, guided_flow_state=updated_flow_state)
    set_session_capability_state(ctx, state)
    if refresh_visibility is not None:
        refresh_visibility(ctx, state)
    return state


async def record_guided_flow_spatial_check_completion_async(
    ctx: Context,
    *,
    tool_name: str,
    resolved_scope: dict[str, Any] | None = None,
    apply_visibility: Callable[[Context, SessionCapabilityState], Awaitable[object]] | None = None,
) -> SessionCapabilityState:
    """Async variant of spatial-check completion recording."""

    if tool_name not in _SPATIAL_CONTEXT_TOOL_NAMES:
        return await get_session_capability_state_async(ctx)

    current = await get_session_capability_state_async(ctx)
    if current.guided_flow_state is None:
        return current

    updated_flow_state = _mark_guided_flow_check_completed_dict(
        current.guided_flow_state,
        tool_name=tool_name,
        resolved_scope=resolved_scope,
        part_registry=current.guided_part_registry,
    )
    state = replace(current, guided_flow_state=updated_flow_state)
    await set_session_capability_state_async(ctx, state)
    if apply_visibility is None:
        await apply_visibility_for_session_state(ctx, state)
    else:
        await apply_visibility(ctx, state)
    return state


def _advance_guided_flow_for_iteration_dict(
    flow_state: dict[str, Any],
    *,
    loop_disposition: str,
    part_registry: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    contract = GuidedFlowStateContract.model_validate(flow_state)
    current_step = contract.current_step
    if loop_disposition == "continue_build" and current_step in {"create_primary_masses", "place_secondary_parts"}:
        current_role_summary = _build_role_summary(
            domain_profile=contract.domain_profile,
            current_step=current_step,
            part_registry=part_registry,
            completed_role_hints=contract.completed_roles,
        )
        if current_role_summary["missing_roles"]:
            _flow_state_for_current_step(contract, part_registry=part_registry)
            contract.blocked_families = []
            if contract.spatial_state_stale:
                _apply_spatial_refresh_gate(contract, part_registry=part_registry, force=True)
            return contract.model_dump(mode="json")

    if current_step not in contract.completed_steps and current_step not in _GUIDED_FLOW_STOPPED_STEPS:
        contract.completed_steps.append(current_step)

    if loop_disposition == "inspect_validate":
        contract.current_step = "inspect_validate"
        contract.blocked_families = ["late_refinement", "finish"]
    elif loop_disposition == "stop":
        contract.current_step = "finish_or_stop"
        contract.blocked_families = []
    else:
        contract.current_step = (
            "place_secondary_parts" if current_step == "create_primary_masses" else "checkpoint_iterate"
        )
        contract.blocked_families = []
    _flow_state_for_current_step(contract, part_registry=part_registry)
    if contract.spatial_state_stale:
        _apply_spatial_refresh_gate(contract, part_registry=part_registry, force=True)
    return contract.model_dump(mode="json")


async def advance_guided_flow_from_iteration_async(
    ctx: Context,
    *,
    loop_disposition: str,
) -> SessionCapabilityState:
    """Advance the guided flow state from a compare/iterate loop result."""

    current = await get_session_capability_state_async(ctx)
    if current.guided_flow_state is None:
        return current

    updated_flow_state = _advance_guided_flow_for_iteration_dict(
        current.guided_flow_state,
        loop_disposition=loop_disposition,
        part_registry=current.guided_part_registry,
    )
    next_phase = current.phase
    if loop_disposition == "inspect_validate":
        next_phase = SessionPhase.INSPECT_VALIDATE
    elif current.phase == SessionPhase.INSPECT_VALIDATE and loop_disposition != "inspect_validate":
        next_phase = SessionPhase.BUILD
    state = replace(current, phase=next_phase, guided_flow_state=updated_flow_state)
    await set_session_capability_state_async(ctx, state)
    return state
