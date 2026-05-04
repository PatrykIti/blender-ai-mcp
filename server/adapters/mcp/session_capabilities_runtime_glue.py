# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Visibility, gate-projection, and runtime-glue helpers."""

from __future__ import annotations

import json
from dataclasses import replace
from typing import TYPE_CHECKING, Any, Callable, Mapping, Sequence, cast

from fastmcp import Context

from server.adapters.mcp.contracts.guided_flow import GuidedFlowStateContract
from server.adapters.mcp.contracts.quality_gates import (
    GateEvidenceRequirementContract,
    GateIntakeResultContract,
    GatePlanContract,
    GatePolicyWarningContract,
    GateProposalContract,
    GateSourceProvenanceContract,
    NormalizedQualityGateContract,
    gate_equivalence_key,
    mark_gate_plan_stale,
    normalize_gate_plan,
    refresh_gate_plan_status,
    without_proposal_source,
)
from server.adapters.mcp.session_capabilities_flow import (
    _GOAL_TIME_UNAVAILABLE_GATE_EVIDENCE_KINDS,
    _SPATIAL_STATE_DIRTY_FAMILIES,
    _SPATIAL_STATE_DIRTY_TOOL_NAMES,
    _apply_role_summary,
    _apply_spatial_refresh_gate,
    _build_role_summary,
    _flow_state_for_current_step,
)
from server.adapters.mcp.session_capabilities_state import (
    SESSION_LAST_ROUTER_DISPOSITION_KEY,
    SESSION_LAST_ROUTER_ERROR_KEY,
    SessionCapabilityState,
    get_session_capability_state,
    get_session_capability_state_async,
    set_session_capability_state,
    set_session_capability_state_async,
)
from server.adapters.mcp.session_state import set_session_value
from server.adapters.mcp.transforms.quality_gate_verifier import verify_gate_plan_with_relation_graph

if TYPE_CHECKING:
    from server.adapters.mcp.guided_mode import VisibilityDiagnostics


async def apply_visibility_for_session_state(
    ctx: Context,
    state: SessionCapabilityState,
) -> VisibilityDiagnostics:
    """Apply native session visibility rules for the current capability state."""

    from server.adapters.mcp.guided_mode import apply_session_visibility

    surface_profile = state.surface_profile or "legacy-flat"
    return await apply_session_visibility(
        ctx,
        surface_profile=surface_profile,
        phase=state.phase,
        guided_handoff=state.guided_handoff,
        guided_flow_state=state.guided_flow_state,
        gate_plan=state.gate_plan,
    )


def ingest_quality_gate_proposal_for_state(
    current: SessionCapabilityState,
    gate_proposal: dict[str, Any] | None,
) -> tuple[SessionCapabilityState, GateIntakeResultContract]:
    if gate_proposal is None:
        return current, GateIntakeResultContract(status="ignored", reason="no_gate_proposal")
    if not current.goal or current.guided_flow_state is None:
        return current, GateIntakeResultContract(status="ignored", reason="no_active_guided_goal")

    try:
        flow_state = GuidedFlowStateContract.model_validate(current.guided_flow_state)
        proposal = GateProposalContract.model_validate(gate_proposal)
        gate_plan = normalize_gate_plan(
            proposal,
            domain_profile=flow_state.domain_profile,
        )
        if proposal.source == "llm_goal":
            gate_plan = _apply_goal_time_gate_input_bounds(gate_plan)
        merged_gate_plan = _merge_gate_plan_for_proposal_source(
            current.gate_plan,
            gate_plan,
            proposal_source=proposal.source,
        )
    except Exception as exc:
        return current, GateIntakeResultContract(status="rejected", reason=str(exc))

    updated = replace(current, gate_plan=merged_gate_plan.model_dump(mode="json", exclude_none=True))
    return updated, GateIntakeResultContract(
        status="accepted",
        gate_plan=merged_gate_plan,
        policy_warnings=gate_plan.policy_warnings,
    )


def _merge_gate_plan_for_proposal_source(
    existing_gate_plan: dict[str, Any] | None,
    incoming_gate_plan: GatePlanContract,
    *,
    proposal_source: str,
) -> GatePlanContract:
    """Replace only the active source slice while preserving the rest of the session gate plan."""

    if existing_gate_plan is None:
        return incoming_gate_plan

    existing_plan = GatePlanContract.model_validate(existing_gate_plan)
    retained_gates: list[NormalizedQualityGateContract] = []
    removed_gate_ids: set[str] = set()
    for gate in existing_plan.gates:
        if proposal_source not in gate.proposal_sources:
            retained_gates.append(gate)
            continue
        retained_gate = without_proposal_source(gate, proposal_source)
        if retained_gate is None:
            removed_gate_ids.add(gate.gate_id)
            continue
        retained_gates.append(retained_gate)
    incoming_source_gates = [gate for gate in incoming_gate_plan.gates if proposal_source in gate.proposal_sources]
    incoming_source_gate_ids = {gate.gate_id for gate in incoming_source_gates}
    merged_gates = list(retained_gates)
    incoming_gate_id_map: dict[str, str] = {}
    for incoming_gate in incoming_source_gates:
        equivalent_index = _find_equivalent_gate_index(merged_gates, incoming_gate)
        if equivalent_index is None:
            merged_gates.append(incoming_gate)
            incoming_gate_id_map[incoming_gate.gate_id] = incoming_gate.gate_id
            continue
        merged_gate = _merge_equivalent_gates(merged_gates[equivalent_index], incoming_gate)
        merged_gates[equivalent_index] = merged_gate
        incoming_gate_id_map[incoming_gate.gate_id] = merged_gate.gate_id
    retained_warnings = [
        warning
        for warning in existing_plan.policy_warnings
        if warning.gate_id is None or warning.gate_id not in removed_gate_ids
    ]
    incoming_source_warnings = [
        _remap_gate_policy_warning(warning, gate_id_map=incoming_gate_id_map)
        for warning in incoming_gate_plan.policy_warnings
        if warning.gate_id is None or warning.gate_id in incoming_source_gate_ids
    ]

    return refresh_gate_plan_status(
        existing_plan.model_copy(
            update={
                "plan_id": incoming_gate_plan.plan_id,
                "proposal_id": incoming_gate_plan.proposal_id,
                "gates": merged_gates,
                "policy_warnings": [*retained_warnings, *incoming_source_warnings],
            }
        )
    )


def _find_equivalent_gate_index(
    gates: list[NormalizedQualityGateContract],
    candidate: NormalizedQualityGateContract,
) -> int | None:
    candidate_key = gate_equivalence_key(candidate)
    for index, gate in enumerate(gates):
        if gate_equivalence_key(gate) == candidate_key:
            return index
    return None


def _merge_equivalent_gates(
    existing: NormalizedQualityGateContract,
    incoming: NormalizedQualityGateContract,
) -> NormalizedQualityGateContract:
    return existing.model_copy(
        update={
            "target_label": existing.target_label or incoming.target_label,
            "target_objects": _merge_unique_strings(existing.target_objects, incoming.target_objects),
            "required": existing.required or incoming.required,
            "priority": _higher_gate_priority(existing.priority, incoming.priority),
            "allowed_correction_families": cast(
                Any,
                _merge_unique_strings(existing.allowed_correction_families, incoming.allowed_correction_families),
            ),
            "recommended_bounded_tools": _merge_unique_strings(
                existing.recommended_bounded_tools,
                incoming.recommended_bounded_tools,
            ),
            "proposal_sources": cast(Any, _merge_unique_strings(existing.proposal_sources, incoming.proposal_sources)),
            "source_provenance": _merge_source_provenance(existing, incoming),
            "evidence_requirements": _merge_evidence_requirements(existing, incoming),
            "allow_embedded_intersection": existing.allow_embedded_intersection or incoming.allow_embedded_intersection,
            "allow_alignment_drift": existing.allow_alignment_drift or incoming.allow_alignment_drift,
            "rationale": existing.rationale or incoming.rationale,
        }
    )


def _merge_source_provenance(
    existing: NormalizedQualityGateContract,
    incoming: NormalizedQualityGateContract,
) -> list[GateSourceProvenanceContract]:
    merged: list[GateSourceProvenanceContract] = []
    seen: set[str] = set()
    for provenance in [*existing.source_provenance, *incoming.source_provenance]:
        payload = provenance.model_dump(mode="json", exclude_none=True)
        dedupe_key = json.dumps(payload, sort_keys=True)
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        merged.append(provenance)
    return merged


def _merge_evidence_requirements(
    existing: NormalizedQualityGateContract,
    incoming: NormalizedQualityGateContract,
) -> list[GateEvidenceRequirementContract]:
    merged: list[GateEvidenceRequirementContract] = []
    by_kind: dict[str, int] = {}
    for requirement in [*existing.evidence_requirements, *incoming.evidence_requirements]:
        evidence_kind = str(requirement.evidence_kind)
        if evidence_kind not in by_kind:
            by_kind[evidence_kind] = len(merged)
            merged.append(requirement)
            continue
        current = merged[by_kind[evidence_kind]]
        merged[by_kind[evidence_kind]] = current.model_copy(
            update={
                "required": current.required or requirement.required,
                "reason": current.reason or requirement.reason,
            }
        )
    return merged


def _merge_unique_strings(existing: Sequence[str], incoming: Sequence[str]) -> list[str]:
    merged: list[str] = []
    seen: set[str] = set()
    for item in [*existing, *incoming]:
        normalized = str(item).strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        merged.append(normalized)
    return merged


def _higher_gate_priority(existing: str, incoming: str) -> str:
    priority_rank = {"high": 0, "normal": 1, "low": 2}
    existing_rank = priority_rank.get(existing, 1)
    incoming_rank = priority_rank.get(incoming, 1)
    return existing if existing_rank <= incoming_rank else incoming


def _remap_gate_policy_warning(
    warning: GatePolicyWarningContract,
    *,
    gate_id_map: dict[str, str],
) -> GatePolicyWarningContract:
    if warning.gate_id is None:
        return warning
    remapped_gate_id = gate_id_map.get(warning.gate_id, warning.gate_id)
    if remapped_gate_id == warning.gate_id:
        return warning
    return warning.model_copy(update={"gate_id": remapped_gate_id})


def ingest_quality_gate_proposal(
    ctx: Context,
    gate_proposal: dict[str, Any] | None,
) -> GateIntakeResultContract:
    """Normalize and persist one optional guided quality-gate proposal."""

    current = get_session_capability_state(ctx)
    updated, result = ingest_quality_gate_proposal_for_state(current, gate_proposal)
    if result.status == "accepted":
        set_session_capability_state(ctx, updated)
    return result


async def ingest_quality_gate_proposal_async(
    ctx: Context,
    gate_proposal: dict[str, Any] | None,
) -> GateIntakeResultContract:
    """Async variant of guided quality-gate proposal intake."""

    current = await get_session_capability_state_async(ctx)
    updated, result = ingest_quality_gate_proposal_for_state(current, gate_proposal)
    if result.status == "accepted":
        await set_session_capability_state_async(ctx, updated)
    return result


def _apply_goal_time_gate_input_bounds(gate_plan: GatePlanContract) -> GatePlanContract:
    """Drop gates that require unavailable reference/perception evidence at goal intake time."""

    warnings = list(gate_plan.policy_warnings)
    retained_gates = []
    for gate in gate_plan.gates:
        unavailable_required = sorted(
            requirement.evidence_kind
            for requirement in gate.evidence_requirements
            if requirement.required and requirement.evidence_kind in _GOAL_TIME_UNAVAILABLE_GATE_EVIDENCE_KINDS
        )
        if not unavailable_required:
            retained_gates.append(gate)
            continue
        warnings.append(
            GatePolicyWarningContract(
                code="unavailable_required_evidence",
                message=(
                    "Goal-time gate intake cannot require unavailable reference/perception evidence "
                    f"({', '.join(unavailable_required)}); drop or relax the gate until the runtime source exists."
                ),
                action="dropped",
                gate_id=gate.gate_id,
                gate_label=gate.label,
                field="evidence_requirements",
            )
        )

    if len(retained_gates) == len(gate_plan.gates):
        return gate_plan
    return refresh_gate_plan_status(gate_plan.model_copy(update={"gates": retained_gates, "policy_warnings": warnings}))


def _spatial_state_version_from_flow_state(flow_state: dict[str, Any] | None) -> int | None:
    if flow_state is None:
        return None
    try:
        contract = GuidedFlowStateContract.model_validate(flow_state)
    except Exception:
        return None
    return contract.spatial_state_version


def _scope_fingerprint_from_flow_state(flow_state: dict[str, Any] | None) -> str | None:
    if flow_state is None:
        return None
    try:
        contract = GuidedFlowStateContract.model_validate(flow_state)
    except Exception:
        return None
    return contract.spatial_scope_fingerprint


def update_quality_gate_plan_from_relation_graph(
    ctx: Context,
    relation_graph_payload: dict[str, Any],
    *,
    refresh_visibility: Callable[[Context, SessionCapabilityState], None] | None = None,
) -> SessionCapabilityState:
    """Apply scene relation graph truth to the active session gate plan."""

    current = get_session_capability_state(ctx)
    if current.gate_plan is None:
        return current

    updated_gate_plan = verify_gate_plan_with_relation_graph(
        current.gate_plan,
        relation_graph_payload,
        spatial_state_version=_spatial_state_version_from_flow_state(current.guided_flow_state),
        scope_fingerprint=_scope_fingerprint_from_flow_state(current.guided_flow_state),
        guided_part_registry=cast(list[Mapping[str, Any]] | None, current.guided_part_registry),
    )
    state = replace(current, gate_plan=updated_gate_plan.model_dump(mode="json", exclude_none=True))
    set_session_capability_state(ctx, state)
    if refresh_visibility is not None:
        refresh_visibility(ctx, state)
    return state


async def update_quality_gate_plan_from_relation_graph_async(
    ctx: Context,
    relation_graph_payload: dict[str, Any],
) -> SessionCapabilityState:
    """Async variant of quality-gate relation graph verification."""

    current = await get_session_capability_state_async(ctx)
    if current.gate_plan is None:
        return current

    updated_gate_plan = verify_gate_plan_with_relation_graph(
        current.gate_plan,
        relation_graph_payload,
        spatial_state_version=_spatial_state_version_from_flow_state(current.guided_flow_state),
        scope_fingerprint=_scope_fingerprint_from_flow_state(current.guided_flow_state),
        guided_part_registry=cast(list[Mapping[str, Any]] | None, current.guided_part_registry),
    )
    state = replace(current, gate_plan=updated_gate_plan.model_dump(mode="json", exclude_none=True))
    await set_session_capability_state_async(ctx, state)
    await apply_visibility_for_session_state(ctx, state)
    return state


def record_router_execution_outcome(
    ctx: Context,
    *,
    router_disposition: str,
    error: str | None = None,
) -> SessionCapabilityState:
    """Persist the last router execution outcome for diagnostics surfaces."""

    set_session_value(ctx, SESSION_LAST_ROUTER_DISPOSITION_KEY, router_disposition)
    set_session_value(ctx, SESSION_LAST_ROUTER_ERROR_KEY, error)

    current = get_session_capability_state(ctx)
    if current.last_router_disposition == router_disposition and current.last_router_error == error:
        return current
    return replace(current, last_router_disposition=router_disposition, last_router_error=error)


def _mark_guided_spatial_state_stale_dict(
    flow_state: dict[str, Any],
    *,
    tool_name: str,
    reason: str,
    part_registry: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    contract = GuidedFlowStateContract.model_validate(flow_state)

    if (
        tool_name != "scene_clean_scene"
        and contract.active_target_scope is None
        and contract.last_spatial_check_version is None
    ):
        return contract.model_dump(mode="json")

    contract.spatial_state_version += 1
    contract.spatial_state_stale = True
    contract.last_spatial_mutation_reason = reason

    if tool_name == "scene_clean_scene":
        contract.current_step = "bootstrap_primary_workset"
        contract.completed_steps = [
            step
            for step in contract.completed_steps
            if step in {"understand_goal", "establish_reference_context", "bootstrap_primary_workset"}
        ]
        contract.completed_roles = []
        contract.role_counts = {}
        contract.role_cardinality = {}
        contract.role_objects = {}
        contract.active_target_scope = None
        contract.spatial_scope_fingerprint = None
        contract.last_spatial_check_version = None
        contract.spatial_refresh_required = False
        contract.spatial_state_stale = False
        contract.required_checks = []
        contract.blocked_families = []
        _flow_state_for_current_step(contract, part_registry=part_registry)
        return contract.model_dump(mode="json")

    _apply_spatial_refresh_gate(contract, part_registry=part_registry)
    role_summary = _build_role_summary(
        domain_profile=contract.domain_profile,
        current_step=contract.current_step,
        part_registry=part_registry,
        completed_role_hints=contract.completed_roles,
    )
    _apply_role_summary(contract, role_summary)
    return contract.model_dump(mode="json")


def is_guided_spatial_state_dirtying_operation(
    *,
    tool_name: str,
    family: str | None = None,
) -> bool:
    """Return True when a successful tool operation invalidates guided spatial facts."""

    dirty_family = family in _SPATIAL_STATE_DIRTY_FAMILIES if isinstance(family, str) else False
    return tool_name in _SPATIAL_STATE_DIRTY_TOOL_NAMES or dirty_family


def mark_guided_spatial_state_stale(
    ctx: Context,
    *,
    tool_name: str,
    family: str | None = None,
    reason: str | None = None,
    affected_objects: list[str] | None = None,
    refresh_visibility: Callable[[Context, SessionCapabilityState], None] | None = None,
) -> SessionCapabilityState:
    """Mark the active guided flow's spatial facts stale after one scene mutation."""

    if not is_guided_spatial_state_dirtying_operation(tool_name=tool_name, family=family):
        return get_session_capability_state(ctx)

    current = get_session_capability_state(ctx)
    if current.guided_flow_state is None:
        return current

    updated_registry = None if tool_name == "scene_clean_scene" else current.guided_part_registry
    updated_flow_state = _mark_guided_spatial_state_stale_dict(
        current.guided_flow_state,
        tool_name=tool_name,
        reason=reason or tool_name,
        part_registry=updated_registry,
    )
    updated_gate_plan = (
        mark_gate_plan_stale(
            current.gate_plan,
            reason=reason or tool_name,
            spatial_state_version=_spatial_state_version_from_flow_state(updated_flow_state),
            affected_objects=affected_objects,
            guided_part_registry=cast(list[Mapping[str, Any]] | None, current.guided_part_registry),
        ).model_dump(mode="json", exclude_none=True)
        if current.gate_plan is not None
        else None
    )
    state = replace(
        current,
        guided_flow_state=updated_flow_state,
        gate_plan=updated_gate_plan,
        guided_part_registry=updated_registry,
    )
    set_session_capability_state(ctx, state)
    if refresh_visibility is not None:
        refresh_visibility(ctx, state)
    return state


async def mark_guided_spatial_state_stale_async(
    ctx: Context,
    *,
    tool_name: str,
    family: str | None = None,
    reason: str | None = None,
    affected_objects: list[str] | None = None,
) -> SessionCapabilityState:
    """Async variant of guided spatial dirty-state recording for native FastMCP requests."""

    if not is_guided_spatial_state_dirtying_operation(tool_name=tool_name, family=family):
        return await get_session_capability_state_async(ctx)

    current = await get_session_capability_state_async(ctx)
    if current.guided_flow_state is None:
        return current

    updated_registry = None if tool_name == "scene_clean_scene" else current.guided_part_registry
    updated_flow_state = _mark_guided_spatial_state_stale_dict(
        current.guided_flow_state,
        tool_name=tool_name,
        reason=reason or tool_name,
        part_registry=updated_registry,
    )
    updated_gate_plan = (
        mark_gate_plan_stale(
            current.gate_plan,
            reason=reason or tool_name,
            spatial_state_version=_spatial_state_version_from_flow_state(updated_flow_state),
            affected_objects=affected_objects,
            guided_part_registry=cast(list[Mapping[str, Any]] | None, current.guided_part_registry),
        ).model_dump(mode="json", exclude_none=True)
        if current.gate_plan is not None
        else None
    )
    state = replace(
        current,
        guided_flow_state=updated_flow_state,
        gate_plan=updated_gate_plan,
        guided_part_registry=updated_registry,
    )
    await set_session_capability_state_async(ctx, state)
    await apply_visibility_for_session_state(ctx, state)
    return state
