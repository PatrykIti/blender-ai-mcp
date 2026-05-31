# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Guided part-registry and flow-transition helpers."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Mapping, Sequence
from dataclasses import asdict, replace
from typing import Any, Callable

from fastmcp import Context

from server.adapters.mcp.contracts.guided_flow import GuidedFlowStateContract, GuidedTargetScopeContract
from server.adapters.mcp.contracts.quality_gates import GatePlanContract, completion_blockers_for_gate_plan
from server.adapters.mcp.contracts.scene import (
    SceneAssembledTargetScopeContract,
    SceneObjectRoleLiteral,
    SceneScopeObjectRoleContract,
)
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
from server.infrastructure.debug_profiles import emit_debug_log

_REFINEMENT_ENTRY_GATE_TYPES = {"shape_profile", "proportion_ratio", "opening_or_cut", "refinement_stage"}
_REFINEMENT_PREREQUISITE_GATE_TYPES = {"attachment_seam", "support_contact"}
_REFINEMENT_ENTRY_STATUSES = {"pending", "blocked", "failed"}
logger = logging.getLogger(__name__)

_GUIDED_ROLE_TO_SCENE_ROLE: dict[str, SceneObjectRoleLiteral] = {
    "anchor_core": "anchor_core",
    "primary_mass": "attached_mass",
    "body_core": "anchor_core",
    "head_mass": "attached_mass",
    "tail_mass": "attached_appendage",
    "snout_mass": "attached_appendage",
    "ear_pair": "accessory_feature",
    "eye_pair": "accessory_feature",
    "foreleg_pair": "attached_appendage",
    "hindleg_pair": "attached_appendage",
}


def _dedupe_guided_names(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        normalized = str(value or "").strip()
        if not normalized:
            continue
        key = normalized.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(normalized)
    return deduped


def _scene_role_for_guided_registration(
    *,
    guided_role: str,
    role_group: str | None,
    is_primary: bool,
) -> SceneObjectRoleLiteral:
    if is_primary:
        return "anchor_core"
    normalized_role = guided_role.strip().lower()
    mapped_role = _GUIDED_ROLE_TO_SCENE_ROLE.get(normalized_role)
    if mapped_role is not None:
        return mapped_role
    normalized_group = str(role_group or "").strip().lower()
    if normalized_group == "primary_masses":
        return "attached_mass"
    if normalized_group in {"secondary_parts", "attachment_alignment"}:
        return "attached_appendage"
    return "scene_member"


def _coerce_guided_target_scope(
    active_target_scope: GuidedTargetScopeContract | Mapping[str, Any] | None,
) -> GuidedTargetScopeContract | None:
    if active_target_scope is None:
        return None
    if isinstance(active_target_scope, GuidedTargetScopeContract):
        return active_target_scope
    try:
        return GuidedTargetScopeContract.model_validate(active_target_scope)
    except Exception:
        return None


def _active_scope_from_flow_state_dict(flow_state: dict[str, Any] | None) -> GuidedTargetScopeContract | None:
    if flow_state is None:
        return None
    try:
        return GuidedFlowStateContract.model_validate(flow_state).active_target_scope
    except Exception:
        return None


def build_guided_registry_compare_scope(
    *,
    guided_part_registry: Sequence[Mapping[str, Any]] | None,
    active_target_scope: GuidedTargetScopeContract | Mapping[str, Any] | None = None,
) -> SceneAssembledTargetScopeContract | None:
    """Project guided part registrations into the scene-scope graph contract."""

    registry_by_name: dict[str, dict[str, str | None]] = {}
    registry_order: list[str] = []
    for item in list(guided_part_registry or []):
        if not isinstance(item, Mapping):
            continue
        object_name = str(item.get("object_name") or "").strip()
        role = str(item.get("role") or "").strip().lower()
        if not object_name or not role:
            continue
        key = object_name.lower()
        if key not in registry_by_name:
            registry_order.append(object_name)
        registry_by_name[key] = {
            "object_name": object_name,
            "role": role,
            "role_group": str(item.get("role_group") or "").strip().lower() or None,
        }

    if not registry_by_name:
        return None

    active_scope = _coerce_guided_target_scope(active_target_scope)
    active_object_names = (
        _dedupe_guided_names(
            [
                *(list(active_scope.object_names or [])),
                *([active_scope.primary_target] if active_scope.primary_target else []),
            ]
        )
        if active_scope is not None
        else []
    )
    object_names = active_object_names or _dedupe_guided_names(registry_order)
    if not object_names:
        return None

    primary_target = (
        active_scope.primary_target
        if active_scope is not None and active_scope.primary_target in object_names
        else None
    )
    object_name_keys = {name.lower() for name in object_names}
    if primary_target is None:
        primary_target = next(
            (
                item["object_name"] or object_names[0]
                for key, item in registry_by_name.items()
                if key in object_name_keys
                if item.get("role") in {"body_core", "anchor_core"}
            ),
            object_names[0],
        )

    object_roles: list[SceneScopeObjectRoleContract] = []
    for object_name in object_names:
        registry_item = registry_by_name.get(object_name.lower())
        is_primary = object_name == primary_target
        if registry_item is None:
            object_roles.append(
                SceneScopeObjectRoleContract(
                    object_name=object_name,
                    role="scene_member",
                    is_primary=is_primary,
                    signals=["active_target_scope"],
                )
            )
            continue
        guided_role = str(registry_item["role"] or "")
        role_group = registry_item.get("role_group")
        signals = ["guided_part_registry", f"guided_role:{guided_role}"]
        if role_group:
            signals.append(f"guided_role_group:{role_group}")
        object_roles.append(
            SceneScopeObjectRoleContract(
                object_name=object_name,
                role=_scene_role_for_guided_registration(
                    guided_role=guided_role,
                    role_group=role_group,
                    is_primary=is_primary,
                ),
                is_primary=is_primary,
                signals=signals,
            )
        )

    scope_kind = (
        active_scope.scope_kind
        if active_scope is not None
        else ("single_object" if len(object_names) == 1 else "object_set")
    )
    if scope_kind == "single_object" and len(object_names) > 1:
        scope_kind = "object_set"
    return SceneAssembledTargetScopeContract(
        scope_kind=scope_kind,
        primary_target=primary_target,
        object_names=object_names,
        object_count=len(object_names),
        collection_name=active_scope.collection_name if active_scope is not None else None,
        object_roles=object_roles,
    )


def resolve_guided_mark_id_map(
    *,
    guided_part_registry: Sequence[Mapping[str, Any]] | None,
    active_target_scope: GuidedTargetScopeContract | Mapping[str, Any] | None = None,
    prior_mark_id_map: Mapping[str, int] | None = None,
) -> dict[str, int]:
    """Return append-only stable Set-of-Mark ids for the active guided object set."""

    scope = build_guided_registry_compare_scope(
        guided_part_registry=guided_part_registry,
        active_target_scope=active_target_scope,
    )
    if scope is None:
        return {}

    scoped_names = _dedupe_guided_names(list(scope.object_names or []))
    scoped_keys = {name.lower(): name for name in scoped_names}
    stable_map: dict[str, int] = {}
    used_ids: set[int] = set()
    for raw_name, raw_id in dict(prior_mark_id_map or {}).items():
        object_name = scoped_keys.get(str(raw_name or "").strip().lower())
        if object_name is None or not isinstance(raw_id, int) or isinstance(raw_id, bool) or raw_id <= 0:
            continue
        if raw_id in used_ids:
            continue
        stable_map[object_name] = raw_id
        used_ids.add(raw_id)

    next_id = max(used_ids, default=0) + 1
    for object_name in scoped_names:
        if object_name in stable_map:
            continue
        while next_id in used_ids:
            next_id += 1
        stable_map[object_name] = next_id
        used_ids.add(next_id)
        next_id += 1
    return stable_map


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
    gate_plan: dict[str, Any] | None = None,
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
            contract.current_step = (
                "refine_low_poly_forms"
                if _can_enter_refinement_stage(contract, gate_plan=gate_plan)
                else "checkpoint_iterate"
            )
            contract.blocked_families = []
            _flow_state_for_current_step(contract, part_registry=part_registry)
            if contract.current_step == "checkpoint_iterate":
                _apply_spatial_refresh_gate(contract, part_registry=part_registry, force=True)

    role_summary = _build_role_summary(
        domain_profile=contract.domain_profile,
        current_step=contract.current_step,
        part_registry=part_registry,
        completed_role_hints=contract.completed_roles,
    )
    _apply_role_summary(contract, role_summary)
    return contract.model_dump(mode="json")


def _can_enter_refinement_stage(
    contract: GuidedFlowStateContract,
    *,
    gate_plan: dict[str, Any] | None,
) -> bool:
    """Return True when normalized gate state proves refinement is the next bounded lane."""

    if contract.domain_profile != "creature":
        return False
    if contract.spatial_state_stale or contract.spatial_refresh_required:
        return False
    if gate_plan is None:
        return False

    try:
        plan = GatePlanContract.model_validate(gate_plan)
        blockers = list(plan.completion_blockers) or completion_blockers_for_gate_plan(plan)
    except Exception:
        return False

    if not blockers:
        return False
    if any(blocker.status == "stale" for blocker in blockers):
        return False
    if any(blocker.gate_type in _REFINEMENT_PREREQUISITE_GATE_TYPES for blocker in blockers):
        return False
    return any(
        blocker.gate_type in _REFINEMENT_ENTRY_GATE_TYPES and blocker.status in _REFINEMENT_ENTRY_STATUSES
        for blocker in blockers
    )


def _has_buildable_required_part_blockers(
    contract: GuidedFlowStateContract,
    *,
    gate_plan: dict[str, Any] | None,
) -> bool:
    if contract.current_step not in {"create_primary_masses", "place_secondary_parts"}:
        return False
    if gate_plan is None:
        return False

    try:
        plan = GatePlanContract.model_validate(gate_plan)
        blockers = list(plan.completion_blockers) or completion_blockers_for_gate_plan(plan)
    except Exception:
        return False

    if not blockers:
        return False

    buildable_required_part_present = False
    for blocker in blockers:
        if blocker.gate_type != "required_part":
            return False
        if blocker.recommended_bounded_tools:
            buildable_required_part_present = True
    return buildable_required_part_present


def _maybe_expand_active_target_scope_dict(
    flow_state: dict[str, Any],
    *,
    object_name: str,
) -> dict[str, Any]:
    contract = GuidedFlowStateContract.model_validate(flow_state)
    active_scope = contract.active_target_scope
    normalized_object_name = str(object_name or "").strip()
    if active_scope is None or not normalized_object_name:
        return contract.model_dump(mode="json")

    object_names = [str(name).strip() for name in list(active_scope.object_names or []) if str(name).strip()]
    seen_names = {name.lower() for name in object_names}
    if normalized_object_name.lower() in seen_names:
        return contract.model_dump(mode="json")

    widened_scope = {
        "scope_kind": active_scope.scope_kind,
        "primary_target": active_scope.primary_target or normalized_object_name,
        "object_names": [*object_names, normalized_object_name],
        "object_count": len(object_names) + 1,
        "collection_name": active_scope.collection_name,
    }
    normalized_scope = _normalize_guided_target_scope(widened_scope)
    if normalized_scope is None:
        return contract.model_dump(mode="json")

    contract.active_target_scope = GuidedTargetScopeContract.model_validate(normalized_scope)
    contract.spatial_scope_fingerprint = _build_guided_target_scope_fingerprint(normalized_scope)
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
    updated_flow_state = _maybe_expand_active_target_scope_dict(
        updated_flow_state,
        object_name=normalized_object_name,
    )
    updated_flow_state = _maybe_advance_guided_flow_from_part_registry_dict(
        updated_flow_state,
        part_registry=updated_registry,
        gate_plan=current.gate_plan,
    )
    updated_mark_id_map = resolve_guided_mark_id_map(
        guided_part_registry=updated_registry,
        active_target_scope=_active_scope_from_flow_state_dict(updated_flow_state),
        prior_mark_id_map=current.guided_mark_id_map,
    )
    state = replace(
        current,
        guided_flow_state=updated_flow_state,
        guided_part_registry=updated_registry,
        guided_mark_id_map=updated_mark_id_map or None,
    )
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
    updated_flow_state = _maybe_expand_active_target_scope_dict(
        updated_flow_state,
        object_name=normalized_object_name,
    )
    updated_flow_state = _maybe_advance_guided_flow_from_part_registry_dict(
        updated_flow_state,
        part_registry=updated_registry,
        gate_plan=current.gate_plan,
    )
    updated_mark_id_map = resolve_guided_mark_id_map(
        guided_part_registry=updated_registry,
        active_target_scope=_active_scope_from_flow_state_dict(updated_flow_state),
        prior_mark_id_map=current.guided_mark_id_map,
    )
    state = replace(
        current,
        guided_flow_state=updated_flow_state,
        guided_part_registry=updated_registry,
        guided_mark_id_map=updated_mark_id_map or None,
    )
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
    updated_mark_id_map = dict(current.guided_mark_id_map or {})
    if normalized_old_name in updated_mark_id_map:
        updated_mark_id_map[normalized_new_name] = updated_mark_id_map.pop(normalized_old_name)
    updated_mark_id_map = resolve_guided_mark_id_map(
        guided_part_registry=updated_registry,
        active_target_scope=_active_scope_from_flow_state_dict(updated_flow_state),
        prior_mark_id_map=updated_mark_id_map,
    )
    state = replace(
        current,
        guided_flow_state=updated_flow_state,
        guided_part_registry=updated_registry,
        guided_mark_id_map=updated_mark_id_map or None,
    )
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
    updated_mark_id_map = dict(current.guided_mark_id_map or {})
    if normalized_old_name in updated_mark_id_map:
        updated_mark_id_map[normalized_new_name] = updated_mark_id_map.pop(normalized_old_name)
    updated_mark_id_map = resolve_guided_mark_id_map(
        guided_part_registry=updated_registry,
        active_target_scope=_active_scope_from_flow_state_dict(updated_flow_state),
        prior_mark_id_map=updated_mark_id_map,
    )
    state = replace(
        current,
        guided_flow_state=updated_flow_state,
        guided_part_registry=updated_registry,
        guided_mark_id_map=updated_mark_id_map or None,
    )
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
    updated_mark_id_map = resolve_guided_mark_id_map(
        guided_part_registry=updated_registry or None,
        active_target_scope=_active_scope_from_flow_state_dict(updated_flow_state),
        prior_mark_id_map=current.guided_mark_id_map,
    )
    state = replace(
        current,
        guided_flow_state=updated_flow_state,
        guided_part_registry=updated_registry or None,
        guided_mark_id_map=updated_mark_id_map or None,
    )
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
    updated_mark_id_map = resolve_guided_mark_id_map(
        guided_part_registry=updated_registry or None,
        active_target_scope=_active_scope_from_flow_state_dict(updated_flow_state),
        prior_mark_id_map=current.guided_mark_id_map,
    )
    state = replace(
        current,
        guided_flow_state=updated_flow_state,
        guided_part_registry=updated_registry or None,
        guided_mark_id_map=updated_mark_id_map or None,
    )
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
    previous_flow = GuidedFlowStateContract.model_validate(current.guided_flow_state)

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
    updated_flow = GuidedFlowStateContract.model_validate(updated_flow_state)
    emit_debug_log(
        "guided_flow",
        logger,
        "spatial_check_completed tool=%s previous_step=%s current_step=%s spatial_refresh_required=%s pending_checks=%d",
        tool_name,
        previous_flow.current_step,
        updated_flow.current_step,
        updated_flow.spatial_refresh_required,
        len([check for check in updated_flow.required_checks if check.status != "completed"]),
    )
    return state


def _advance_guided_flow_for_iteration_dict(
    flow_state: dict[str, Any],
    *,
    loop_disposition: str,
    part_registry: list[dict[str, Any]] | None = None,
    gate_plan: dict[str, Any] | None = None,
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
        if current_role_summary["missing_roles"] or _has_buildable_required_part_blockers(
            contract,
            gate_plan=gate_plan,
        ):
            _flow_state_for_current_step(contract, part_registry=part_registry)
            contract.blocked_families = []
            if contract.spatial_state_stale:
                _apply_spatial_refresh_gate(contract, part_registry=part_registry, force=True)
            return contract.model_dump(mode="json")

    if loop_disposition == "continue_build" and current_step == "refine_low_poly_forms":
        _flow_state_for_current_step(contract, part_registry=part_registry)
        contract.blocked_families = []
        if contract.spatial_state_stale:
            _apply_spatial_refresh_gate(contract, part_registry=part_registry, force=True)
        return contract.model_dump(mode="json")

    if current_step not in contract.completed_steps and current_step not in _GUIDED_FLOW_STOPPED_STEPS:
        contract.completed_steps.append(current_step)

    if (
        loop_disposition == "continue_build"
        and current_step in {"place_secondary_parts", "checkpoint_iterate"}
        and _can_enter_refinement_stage(contract, gate_plan=gate_plan)
    ):
        contract.current_step = "refine_low_poly_forms"
        contract.blocked_families = []
    elif loop_disposition == "inspect_validate":
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
    previous_flow = GuidedFlowStateContract.model_validate(current.guided_flow_state)

    updated_flow_state = _advance_guided_flow_for_iteration_dict(
        current.guided_flow_state,
        loop_disposition=loop_disposition,
        part_registry=current.guided_part_registry,
        gate_plan=current.gate_plan,
    )
    next_phase = current.phase
    if loop_disposition == "inspect_validate":
        next_phase = SessionPhase.INSPECT_VALIDATE
    elif current.phase == SessionPhase.INSPECT_VALIDATE and loop_disposition != "inspect_validate":
        next_phase = SessionPhase.BUILD
    state = replace(current, phase=next_phase, guided_flow_state=updated_flow_state)
    await set_session_capability_state_async(ctx, state)
    updated_flow = GuidedFlowStateContract.model_validate(updated_flow_state)
    emit_debug_log(
        "guided_flow",
        logger,
        "iteration_advance disposition=%s previous_step=%s current_step=%s phase=%s blocked_families=%s",
        loop_disposition,
        previous_flow.current_step,
        updated_flow.current_step,
        next_phase.value,
        updated_flow.blocked_families,
    )
    return state
