# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Goal-scoped reference image intake and lifecycle tools."""

from __future__ import annotations

import contextvars
import logging
import re
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from typing import Any, Literal, Mapping, Sequence, cast
from uuid import uuid4

from fastmcp import Context

from server.adapters.mcp.areas.reference_checkpoint_compare import (
    build_compare_response as _build_compare_response,
)
from server.adapters.mcp.areas.reference_checkpoint_compare import (
    run_checkpoint_compare as _run_checkpoint_compare_impl,
)
from server.adapters.mcp.areas.reference_compare_packets import (
    execute_compare_packets as _execute_compare_packets,
)
from server.adapters.mcp.areas.reference_compare_packets import (
    has_compare_uncertainty as _has_compare_uncertainty,
)
from server.adapters.mcp.areas.reference_compare_packets import (
    should_emit_compare_diagnostics as _should_emit_compare_diagnostics,
)
from server.adapters.mcp.areas.reference_current_view import (
    run_current_view_compare as _run_current_view_compare_impl,
)
from server.adapters.mcp.areas.reference_feedback import build_reference_orchestrator_feedback
from server.adapters.mcp.areas.reference_images_runtime import (
    _validate_local_reference_path,
)
from server.adapters.mcp.areas.reference_images_runtime import (
    handle_reference_images as _handle_reference_images,
)
from server.adapters.mcp.areas.reference_planner import (
    build_compare_packets as _build_compare_packets,
)
from server.adapters.mcp.areas.reference_planner import (
    build_correction_candidates as _planner_build_correction_candidates,
)
from server.adapters.mcp.areas.reference_planner import (
    build_refinement_handoff as _build_refinement_handoff,
)
from server.adapters.mcp.areas.reference_planner import (
    build_repair_planner_detail as _build_repair_planner_detail,
)
from server.adapters.mcp.areas.reference_planner import (
    build_repair_planner_summary as _build_repair_planner_summary,
)
from server.adapters.mcp.areas.reference_planner import (
    effective_candidate_budget as _effective_candidate_budget,
)
from server.adapters.mcp.areas.reference_planner import (
    effective_pair_budget as _effective_pair_budget,
)
from server.adapters.mcp.areas.reference_planner import (
    normalize_focus_key as _planner_normalize_focus_key,
)
from server.adapters.mcp.areas.reference_planner import (
    resolve_actionable_focus as _planner_resolve_actionable_focus,
)
from server.adapters.mcp.areas.reference_planner import (
    resolve_gate_blocker_focus as _planner_resolve_gate_blocker_focus,
)
from server.adapters.mcp.areas.reference_planner import (
    resolve_hybrid_budget_runtime as _resolve_hybrid_budget_runtime,
)
from server.adapters.mcp.areas.reference_planner import (
    select_refinement_route as _select_refinement_route,
)
from server.adapters.mcp.areas.reference_planner import (
    should_inspect_from_truth_signal as _planner_should_inspect_from_truth_signal,
)
from server.adapters.mcp.areas.reference_planner import (
    trim_correction_candidates as _planner_trim_correction_candidates,
)
from server.adapters.mcp.areas.reference_silhouette import (
    build_action_hints_from_silhouette as _build_action_hints_from_silhouette,
)
from server.adapters.mcp.areas.reference_silhouette import (
    build_silhouette_analysis_payload as _build_silhouette_analysis_payload,
)
from server.adapters.mcp.areas.reference_truth import (
    assembled_target_scope as _assembled_target_scope_impl,
)
from server.adapters.mcp.areas.reference_truth import (
    build_correction_truth_bundle as _build_correction_truth_bundle_impl,
)
from server.adapters.mcp.areas.reference_truth import (
    build_truth_followup as _build_truth_followup,
)
from server.adapters.mcp.areas.reference_truth import dedupe_names as _dedupe_names
from server.adapters.mcp.areas.reference_truth import (
    resolve_capture_scope as _resolve_capture_scope_impl,
)
from server.adapters.mcp.areas.reference_truth import trim_truth_bundle_to_budget as _truth_trim_truth_bundle_to_budget
from server.adapters.mcp.areas.reference_understanding import (
    refresh_reference_understanding_summary as _refresh_reference_understanding_summary_impl,
)
from server.adapters.mcp.areas.reference_view_diagnostics import (
    build_stage_view_diagnostics_hints as _build_stage_view_diagnostics_hints,
)
from server.adapters.mcp.areas.reference_view_diagnostics import (
    build_view_diagnostics_hints as _build_view_diagnostics_hints,
)
from server.adapters.mcp.context_utils import ctx_session_id, ctx_transport_type
from server.adapters.mcp.contracts.guided_flow import GuidedFlowStateContract
from server.adapters.mcp.contracts.quality_gates import GatePlanContract
from server.adapters.mcp.contracts.reference import (
    GuidedReferenceReadinessContract,
    ReferenceActionHintContract,
    ReferenceCompareCheckpointResponseContract,
    ReferenceCompareDiagnosticsContract,
    ReferenceCompareStageCheckpointResponseContract,
    ReferenceCorrectionCandidateContract,
    ReferenceHybridBudgetControlContract,
    ReferenceImageRecordContract,
    ReferenceImagesResponseContract,
    ReferenceIterateStageCheckpointResponseContract,
    ReferencePartSegmentationContract,
    ReferencePlannerTargetScopeContract,
    ReferenceRefinementHandoffContract,
    ReferenceRefinementRouteContract,
    ReferenceRepairPlannerDetailContract,
    ReferenceRepairPlannerSummaryContract,
    ReferenceSilhouetteAnalysisContract,
    ReferenceStrategyStateContract,
    ReferenceUnderstandingSummaryContract,
    ReferenceViewDiagnosticsHintContract,
)
from server.adapters.mcp.contracts.scene import (
    SceneAssembledTargetScopeContract,
    SceneCorrectionTruthBundleContract,
    SceneTruthFollowupContract,
)
from server.adapters.mcp.sampling.result_types import (
    to_vision_assistant_contract,
)
from server.adapters.mcp.session_capabilities import (
    GuidedReferenceReadinessState,
    SessionCapabilityState,
    advance_guided_flow_from_iteration_async,
    apply_visibility_for_session_state,
    build_guided_reference_readiness,
    build_guided_reference_readiness_payload,
    get_session_capability_state_async,
    ingest_quality_gate_proposal_async,
    set_session_capability_state_async,
)
from server.adapters.mcp.session_state import get_session_value_async, set_session_value_async
from server.adapters.mcp.transforms.quality_gate_verifier import verify_gate_plan_with_relation_graph
from server.adapters.mcp.visibility.tags import get_capability_tags
from server.adapters.mcp.vision import (
    CapturePresetProfile,
    build_reference_capture_images,
    capture_stage_images,
    run_vision_assist,
    select_reference_records_for_target,
)
from server.application.services.spatial_graph import get_spatial_graph_service
from server.infrastructure.debug_profiles import emit_debug_log
from server.infrastructure.di import get_collection_handler, get_scene_handler, get_vision_backend_resolver
from server.infrastructure.tmp_paths import get_viewport_output_paths

logger = logging.getLogger(__name__)

REFERENCE_PUBLIC_TOOL_NAMES = (
    "reference_images",
    "reference_compare_checkpoint",
    "reference_compare_current_view",
    "reference_compare_stage_checkpoint",
    "reference_iterate_stage_checkpoint",
)
_REFERENCE_CORRECTION_LOOP_STATE_KEY = "reference_correction_loop"
_REFERENCE_CORRECTION_STAGNATION_THRESHOLD = 2
_REFERENCE_COMPARE_EMIT_COMPACT_DETAIL: contextvars.ContextVar[bool] = contextvars.ContextVar(
    "reference_compare_emit_compact_detail",
    default=False,
)


def _normalize_focus_key(value: str) -> str:
    return _planner_normalize_focus_key(value)


def _resolve_actionable_focus(compare_result: ReferenceCompareStageCheckpointResponseContract) -> list[str]:
    return _planner_resolve_actionable_focus(compare_result)


def _resolve_gate_blocker_focus(compare_result: ReferenceCompareStageCheckpointResponseContract) -> list[str]:
    return _planner_resolve_gate_blocker_focus(compare_result)


def _should_inspect_from_truth_signal(
    correction_candidates: list[ReferenceCorrectionCandidateContract],
) -> bool:
    return _planner_should_inspect_from_truth_signal(correction_candidates)


def _trim_truth_bundle_to_budget(
    *,
    truth_bundle: SceneCorrectionTruthBundleContract,
    pair_budget: int,
    max_truth_chars: int,
) -> tuple[SceneCorrectionTruthBundleContract, bool]:
    return _truth_trim_truth_bundle_to_budget(
        truth_bundle=truth_bundle,
        pair_budget=pair_budget,
        max_truth_chars=max_truth_chars,
    )


def _build_correction_candidates(
    compare_result: ReferenceCompareStageCheckpointResponseContract,
) -> list[ReferenceCorrectionCandidateContract]:
    return _planner_build_correction_candidates(compare_result)


def _resolve_capture_scope(
    *,
    target_object: str | None,
    target_objects: list[str] | None,
    collection_name: str | None,
) -> tuple[str | None, list[str], str | None]:
    return _resolve_capture_scope_impl(
        target_object=target_object,
        target_objects=target_objects,
        collection_name=collection_name,
        get_collection_handler=get_collection_handler,
    )


_CREATURE_BROAD_FIRST_STEPS: frozenset[str] = frozenset(
    {"establish_spatial_context", "bootstrap_primary_workset", "create_primary_masses", "place_secondary_parts"}
)
_CREATURE_PRIMARY_MASS_ROLES: tuple[str, ...] = ("body_core", "head_mass", "tail_mass")


def _guided_role_to_objects(guided_part_registry: list[dict[str, Any]] | None) -> dict[str, list[str]]:
    role_to_objects: dict[str, list[str]] = {}
    for item in list(guided_part_registry or []):
        if not isinstance(item, dict):
            continue
        role = str(item.get("role") or "").strip().lower()
        object_name = str(item.get("object_name") or "").strip()
        if not role or not object_name:
            continue
        role_to_objects.setdefault(role, [])
        if object_name not in role_to_objects[role]:
            role_to_objects[role].append(object_name)
    return role_to_objects


def _resolved_active_scope_role_objects(
    *,
    role_to_objects: Mapping[str, Sequence[str]],
    active_scope_name_keys: Mapping[str, str],
    roles: Sequence[str],
) -> list[str]:
    resolved: list[str] = []
    for role in roles:
        for object_name in role_to_objects.get(role, ()):
            active_scope_name = active_scope_name_keys.get(object_name.lower())
            if active_scope_name and active_scope_name not in resolved:
                resolved.append(active_scope_name)
    return resolved


def _early_creature_primary_mass_scope(
    *,
    flow_state: GuidedFlowStateContract,
    active_scope_name_keys: Mapping[str, str],
    active_scope_names: Sequence[str],
    role_to_objects: Mapping[str, Sequence[str]],
) -> ReferencePlannerTargetScopeContract | None:
    if (
        flow_state.domain_profile != "creature"
        or flow_state.current_step not in _CREATURE_BROAD_FIRST_STEPS
        or flow_state.active_target_scope is None
    ):
        return None

    active_scope = flow_state.active_target_scope
    primary_mass_objects = _resolved_active_scope_role_objects(
        role_to_objects=role_to_objects,
        active_scope_name_keys=active_scope_name_keys,
        roles=_CREATURE_PRIMARY_MASS_ROLES,
    )
    if len(primary_mass_objects) >= 2:
        primary_target = (
            active_scope.primary_target
            if active_scope.primary_target in primary_mass_objects
            else primary_mass_objects[0]
        )
        return ReferencePlannerTargetScopeContract(
            scope_kind="single_object" if len(primary_mass_objects) == 1 else "object_set",
            target_object=primary_target if len(primary_mass_objects) == 1 else primary_target,
            target_objects=primary_mass_objects,
            collection_name=None,
            local_region_hint="primary_mass_workset",
        )

    if active_scope.collection_name:
        return ReferencePlannerTargetScopeContract(
            scope_kind="collection",
            target_object=active_scope.primary_target,
            target_objects=list(active_scope_names),
            collection_name=active_scope.collection_name,
            local_region_hint="active_workset",
        )
    if active_scope_names:
        return ReferencePlannerTargetScopeContract(
            scope_kind="single_object" if len(active_scope_names) == 1 else "object_set",
            target_object=active_scope.primary_target
            or (active_scope_names[0] if len(active_scope_names) == 1 else None),
            target_objects=list(active_scope_names),
            collection_name=None,
            local_region_hint="active_workset",
        )
    return None


def resolve_active_compare_scope(
    *,
    guided_flow_state: dict[str, Any] | None,
    gate_plan: dict[str, Any] | None,
    guided_part_registry: list[dict[str, Any]] | None,
    last_guided_affected_objects: list[str] | None,
    target_object: str | None,
    target_objects: list[str] | None,
    collection_name: str | None,
    focus_pairs: list[str] | None = None,
) -> ReferencePlannerTargetScopeContract | None:
    """Resolve one runtime-owned compare scope when the client omits explicit targets."""

    if target_object or target_objects or collection_name:
        explicit_objects = _dedupe_names([*(target_objects or []), *([target_object] if target_object else [])])
        scope_kind: Literal["single_object", "object_set", "collection", "scene", "unknown"]
        if collection_name:
            scope_kind = "collection"
        elif len(explicit_objects) == 1:
            scope_kind = "single_object"
        elif explicit_objects:
            scope_kind = "object_set"
        else:
            scope_kind = "unknown"
        return ReferencePlannerTargetScopeContract(
            scope_kind=scope_kind,
            target_object=target_object or (explicit_objects[0] if len(explicit_objects) == 1 else None),
            target_objects=explicit_objects,
            collection_name=collection_name,
        )

    if not guided_flow_state:
        return None
    try:
        flow_state = GuidedFlowStateContract.model_validate(guided_flow_state)
    except Exception:
        return None

    active_scope = flow_state.active_target_scope
    if active_scope is None:
        return None

    active_scope_names = _dedupe_names(
        [
            *(list(active_scope.object_names or [])),
            *([active_scope.primary_target] if active_scope.primary_target else []),
        ]
    )
    active_scope_name_keys = {name.lower(): name for name in active_scope_names}
    role_to_objects = _guided_role_to_objects(guided_part_registry)

    early_creature_scope = _early_creature_primary_mass_scope(
        flow_state=flow_state,
        active_scope_name_keys=active_scope_name_keys,
        active_scope_names=active_scope_names,
        role_to_objects=role_to_objects,
    )
    if early_creature_scope is not None:
        return early_creature_scope

    blocker_target_objects: list[str] = []
    if gate_plan is not None:
        try:
            gate_plan_contract = GatePlanContract.model_validate(gate_plan)
        except Exception:
            gate_plan_contract = None
        if gate_plan_contract is not None:
            for blocker in list(gate_plan_contract.completion_blockers or []):
                blocker_target_objects.extend(
                    str(name).strip() for name in list(blocker.target_objects or []) if str(name).strip()
                )
                target_label = str(blocker.target_label or "").strip().lower()
                if target_label:
                    blocker_target_objects.extend(role_to_objects.get(target_label, []))

    resolved_blocker_objects = _dedupe_names(
        [
            active_scope_name_keys[name.lower()]
            for name in blocker_target_objects
            if name.lower() in active_scope_name_keys
        ]
    )
    if resolved_blocker_objects:
        return ReferencePlannerTargetScopeContract(
            scope_kind="single_object" if len(resolved_blocker_objects) == 1 else "object_set",
            target_object=resolved_blocker_objects[0] if len(resolved_blocker_objects) == 1 else None,
            target_objects=resolved_blocker_objects,
            collection_name=None,
            local_region_hint="gate_blocker_cluster",
        )

    focus_pair_objects: list[str] = []
    for focus_pair in list(focus_pairs or []):
        if not isinstance(focus_pair, str):
            continue
        for raw_name in re.split(r"\s*->\s*|\s*<->\s*", focus_pair):
            object_name = raw_name.strip()
            if object_name:
                focus_pair_objects.append(object_name)
    resolved_focus_pair_objects = _dedupe_names(
        [active_scope_name_keys[name.lower()] for name in focus_pair_objects if name.lower() in active_scope_name_keys]
    )
    if resolved_focus_pair_objects:
        return ReferencePlannerTargetScopeContract(
            scope_kind="single_object" if len(resolved_focus_pair_objects) == 1 else "object_set",
            target_object=resolved_focus_pair_objects[0] if len(resolved_focus_pair_objects) == 1 else None,
            target_objects=resolved_focus_pair_objects,
            collection_name=None,
            local_region_hint="focus_pair",
        )

    resolved_affected_objects = _dedupe_names(
        [
            active_scope_name_keys[name.lower()]
            for name in list(last_guided_affected_objects or [])
            if isinstance(name, str) and name.strip() and name.lower() in active_scope_name_keys
        ]
    )
    if resolved_affected_objects:
        return ReferencePlannerTargetScopeContract(
            scope_kind="single_object" if len(resolved_affected_objects) == 1 else "object_set",
            target_object=resolved_affected_objects[0] if len(resolved_affected_objects) == 1 else None,
            target_objects=resolved_affected_objects,
            collection_name=None,
            local_region_hint="last_mutation",
        )

    if active_scope.collection_name:
        return ReferencePlannerTargetScopeContract(
            scope_kind="collection",
            target_object=active_scope.primary_target,
            target_objects=active_scope_names,
            collection_name=active_scope.collection_name,
            local_region_hint="active_workset",
        )
    if active_scope_names:
        return ReferencePlannerTargetScopeContract(
            scope_kind="single_object" if len(active_scope_names) == 1 else "object_set",
            target_object=active_scope.primary_target
            or (active_scope_names[0] if len(active_scope_names) == 1 else None),
            target_objects=active_scope_names,
            collection_name=None,
            local_region_hint="active_workset",
        )
    return None


def _assembled_target_scope(
    *,
    target_object: str | None,
    target_objects: list[str] | None,
    collection_name: str | None,
) -> SceneAssembledTargetScopeContract:
    return _assembled_target_scope_impl(
        target_object=target_object,
        target_objects=target_objects,
        collection_name=collection_name,
        get_collection_handler=get_collection_handler,
        get_scene_handler=get_scene_handler,
        get_spatial_graph_service=get_spatial_graph_service,
    )


def _build_correction_truth_bundle(
    scene_handler,
    scope: SceneAssembledTargetScopeContract,
    *,
    goal_hint: str | None = None,
) -> tuple[SceneCorrectionTruthBundleContract, dict[str, Any]]:
    return _build_correction_truth_bundle_impl(
        scene_handler,
        scope,
        goal_hint=goal_hint,
        get_spatial_graph_service=get_spatial_graph_service,
    )


def _dedupe_preserving_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        normalized = value.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(normalized)
    return deduped


def _register_existing_tool(target, tool_name: str):
    tool = globals()[tool_name]
    fn = getattr(tool, "fn", tool)
    return target.tool(fn, name=tool_name, tags=set(get_capability_tags("reference")))


def register_reference_tools(target):
    return {tool_name: _register_existing_tool(target, tool_name) for tool_name in REFERENCE_PUBLIC_TOOL_NAMES}


def _safe_checkpoint_token(value: str | None) -> str:
    """Return a filesystem-safe token for checkpoint/bundle ids."""

    raw = str(value or "scene").strip()
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "_", raw).strip("._-")
    return normalized or "scene"


def _select_reference_records_for_scope(
    reference_records: Sequence[ReferenceImageRecordContract | dict[str, Any]],
    *,
    resolved_target_object: str | None,
    assembled_target_scope: SceneAssembledTargetScopeContract,
    target_view: str | None,
) -> tuple[ReferenceImageRecordContract, ...]:
    resolved_reference_records = [
        record
        if isinstance(record, ReferenceImageRecordContract)
        else ReferenceImageRecordContract.model_validate(record)
        for record in reference_records
    ]

    def _strict_scope_selection(scope_target: str) -> tuple[ReferenceImageRecordContract, ...]:
        selected: list[ReferenceImageRecordContract] = []
        seen_ids: set[str] = set()

        def _append(records: Sequence[ReferenceImageRecordContract]) -> None:
            for record in records:
                if record.reference_id in seen_ids:
                    continue
                seen_ids.add(record.reference_id)
                selected.append(record)

        if target_view is not None:
            targeted_view = tuple(
                record
                for record in resolved_reference_records
                if record.target_object == scope_target and record.target_view == target_view
            )
            _append(targeted_view)

            generic_view = tuple(
                record
                for record in resolved_reference_records
                if record.target_object is None and record.target_view == target_view
            )
            _append(generic_view)

        targeted = tuple(record for record in resolved_reference_records if record.target_object == scope_target)
        _append(targeted)

        generic = tuple(record for record in resolved_reference_records if record.target_object is None)
        _append(generic)
        return tuple(selected)

    scoped_targets = _dedupe_preserving_order(
        [
            *(assembled_target_scope.object_names or []),
            *([resolved_target_object] if resolved_target_object else []),
        ]
    )
    if not scoped_targets:
        return select_reference_records_for_target(
            resolved_reference_records,
            target_object=resolved_target_object,
            target_view=target_view,
        )

    ordered_records: list[ReferenceImageRecordContract] = []
    seen_reference_ids: set[str] = set()
    for scoped_target in scoped_targets:
        selected_records = _strict_scope_selection(scoped_target)
        for record in selected_records:
            if record.reference_id in seen_reference_ids:
                continue
            seen_reference_ids.add(record.reference_id)
            ordered_records.append(record)
    if ordered_records:
        return tuple(ordered_records)
    return select_reference_records_for_target(
        resolved_reference_records,
        target_object=resolved_target_object,
        target_view=target_view,
    )


def _compare_response(
    *,
    action: Literal["compare_checkpoint", "compare_current_view"],
    checkpoint_path: str,
    checkpoint_label: str | None,
    goal: str | None,
    target_object: str | None,
    target_view: str | None,
    reference_ids: list[str],
    reference_labels: list[str],
    view_diagnostics_hints: list[ReferenceViewDiagnosticsHintContract] | None = None,
    vision_assistant=None,
    message: str | None = None,
    error: str | None = None,
) -> ReferenceCompareCheckpointResponseContract:
    return _build_compare_response(
        action=action,
        checkpoint_path=checkpoint_path,
        checkpoint_label=checkpoint_label,
        goal=goal,
        target_object=target_object,
        target_view=target_view,
        reference_ids=reference_ids,
        reference_labels=reference_labels,
        view_diagnostics_hints=view_diagnostics_hints,
        vision_assistant=vision_assistant,
        message=message,
        error=error,
    )


def _compact_compare_detail_allowed(
    *,
    preset_profile: CapturePresetProfile,
    error: str | None,
    compare_diagnostics: ReferenceCompareDiagnosticsContract | None,
    hard_failure: bool = False,
    emit_compact_detail: bool = False,
) -> bool:
    """Return True when compact output may include heavy truth/candidate/planner detail."""

    if emit_compact_detail or preset_profile != "compact" or error is not None or hard_failure:
        return True
    if compare_diagnostics is None:
        return False
    return bool(
        compare_diagnostics.synthesis_status == "error"
        or bool(compare_diagnostics.conflict_notes)
        or _has_compare_uncertainty(compare_diagnostics)
    )


def _gate_fields_have_hard_failure(gate_fields: Mapping[str, Any]) -> bool:
    """Return True when gate state has a concrete failed runtime assertion."""

    for field_name in ("gate_statuses", "completion_blockers"):
        for item in list(gate_fields.get(field_name) or []):
            if getattr(item, "status", None) == "failed":
                return True
    return False


def _gate_checkpoint_fields(active_gate_plan: dict[str, Any] | None) -> dict[str, Any]:
    """Project active gate plan details into strict checkpoint response fields."""

    if active_gate_plan is None:
        return {
            "gate_statuses": [],
            "completion_blockers": [],
            "next_gate_actions": [],
            "recommended_bounded_tools": [],
        }

    gate_plan = GatePlanContract.model_validate(active_gate_plan)
    recommended_tools: list[str] = []
    seen_tools: set[str] = set()
    for blocker in gate_plan.completion_blockers:
        for tool_name in blocker.recommended_bounded_tools:
            if tool_name in seen_tools:
                continue
            seen_tools.add(tool_name)
            recommended_tools.append(tool_name)

    next_actions: list[str] = []
    if gate_plan.completion_blockers:
        next_actions.append("resolve_quality_gate_blockers")
        if any(blocker.status == "stale" for blocker in gate_plan.completion_blockers):
            next_actions.append("refresh_gate_evidence")
        if any(
            blocker.gate_type in {"attachment_seam", "support_contact"} for blocker in gate_plan.completion_blockers
        ):
            next_actions.append("verify_or_repair_spatial_gate")

    return {
        "gate_statuses": gate_plan.gates,
        "completion_blockers": gate_plan.completion_blockers,
        "next_gate_actions": next_actions,
        "recommended_bounded_tools": recommended_tools,
    }


def _stage_compare_response(
    *,
    session_id: str | None = None,
    transport: str | None = None,
    guided_flow_state: dict[str, Any] | None = None,
    active_gate_plan: dict[str, Any] | None = None,
    checkpoint_id: str,
    checkpoint_label: str | None,
    goal: str | None,
    target_object: str | None,
    target_objects: list[str],
    collection_name: str | None,
    assembled_target_scope: SceneAssembledTargetScopeContract | None = None,
    target_view: str | None,
    preset_profile: CapturePresetProfile,
    preset_names: list[str],
    captures: list | tuple = (),
    reference_ids: list[str],
    reference_labels: list[str],
    guided_reference_readiness: GuidedReferenceReadinessContract | None = None,
    reference_understanding_summary: ReferenceUnderstandingSummaryContract | None = None,
    reference_understanding_gate_ids: list[str] | None = None,
    reference_strategy_state: dict[str, Any] | None = None,
    vision_assistant=None,
    truth_bundle: SceneCorrectionTruthBundleContract | None = None,
    truth_followup: SceneTruthFollowupContract | None = None,
    compare_diagnostics: ReferenceCompareDiagnosticsContract | None = None,
    correction_candidates: list[ReferenceCorrectionCandidateContract] | None = None,
    budget_control: ReferenceHybridBudgetControlContract | None = None,
    refinement_route: ReferenceRefinementRouteContract | None = None,
    refinement_handoff: ReferenceRefinementHandoffContract | None = None,
    planner_summary: ReferenceRepairPlannerSummaryContract | None = None,
    planner_detail: ReferenceRepairPlannerDetailContract | None = None,
    silhouette_analysis: ReferenceSilhouetteAnalysisContract | None = None,
    action_hints: list[ReferenceActionHintContract] | None = None,
    part_segmentation: ReferencePartSegmentationContract | None = None,
    view_diagnostics_hints: list[ReferenceViewDiagnosticsHintContract] | None = None,
    include_captures: bool = True,
    emit_compact_detail: bool = False,
    message: str | None = None,
    error: str | None = None,
) -> ReferenceCompareStageCheckpointResponseContract:
    emitted_captures = list(captures) if include_captures else []
    gate_fields = _gate_checkpoint_fields(active_gate_plan)
    heavy_detail_allowed = _compact_compare_detail_allowed(
        preset_profile=preset_profile,
        error=error,
        compare_diagnostics=compare_diagnostics,
        hard_failure=_gate_fields_have_hard_failure(gate_fields),
        emit_compact_detail=emit_compact_detail,
    )
    guided_flow_contract = (
        GuidedFlowStateContract.model_validate(guided_flow_state) if guided_flow_state is not None else None
    )
    active_gate_plan_contract = (
        GatePlanContract.model_validate(active_gate_plan) if active_gate_plan is not None else None
    )
    reference_strategy_contract = (
        ReferenceStrategyStateContract.model_validate(reference_strategy_state)
        if reference_strategy_state is not None
        else None
    )
    reference_orchestrator_feedback = build_reference_orchestrator_feedback(
        goal=goal,
        summary=reference_understanding_summary,
        strategy_state=reference_strategy_contract,
        guided_flow_state=guided_flow_contract,
        gate_plan=active_gate_plan_contract,
        guided_reference_readiness=guided_reference_readiness,
        compare_diagnostics=compare_diagnostics,
        budget_control=budget_control,
        planner_summary=planner_summary,
        correction_candidates=list(correction_candidates or []),
        next_gate_actions=list(gate_fields["next_gate_actions"] or []),
        recommended_bounded_tools=list(gate_fields["recommended_bounded_tools"] or []),
    )
    return ReferenceCompareStageCheckpointResponseContract(
        action="compare_stage_checkpoint",
        session_id=session_id,
        transport=transport,
        goal=goal,
        guided_flow_state=guided_flow_contract,
        active_gate_plan=active_gate_plan_contract,
        gate_statuses=gate_fields["gate_statuses"],
        completion_blockers=gate_fields["completion_blockers"],
        next_gate_actions=gate_fields["next_gate_actions"],
        recommended_bounded_tools=gate_fields["recommended_bounded_tools"],
        guided_reference_readiness=guided_reference_readiness,
        reference_understanding_summary=reference_understanding_summary,
        reference_understanding_gate_ids=list(reference_understanding_gate_ids or []),
        reference_orchestrator_feedback=reference_orchestrator_feedback,
        target_object=target_object,
        target_objects=target_objects,
        collection_name=collection_name,
        assembled_target_scope=assembled_target_scope,
        truth_bundle=truth_bundle if heavy_detail_allowed else None,
        truth_followup=truth_followup if heavy_detail_allowed else None,
        compare_diagnostics=compare_diagnostics,
        correction_candidates=list(correction_candidates or []) if heavy_detail_allowed else [],
        budget_control=budget_control,
        refinement_route=refinement_route,
        refinement_handoff=refinement_handoff,
        planner_summary=planner_summary,
        planner_detail=planner_detail if heavy_detail_allowed else None,
        silhouette_analysis=silhouette_analysis,
        action_hints=list(action_hints or []),
        part_segmentation=part_segmentation or _disabled_part_segmentation(),
        view_diagnostics_hints=view_diagnostics_hints,
        target_view=target_view,
        checkpoint_id=checkpoint_id,
        checkpoint_label=checkpoint_label,
        preset_profile=preset_profile,
        preset_names=preset_names,
        capture_count=len(captures),
        captures=emitted_captures,
        reference_count=len(reference_ids),
        reference_ids=reference_ids,
        reference_labels=reference_labels,
        vision_assistant=vision_assistant,
        message=message,
        error=error,
    )


def _iterate_stage_response(
    *,
    session_id: str | None = None,
    transport: str | None = None,
    goal: str | None,
    guided_flow_state: dict[str, Any] | None = None,
    active_gate_plan: dict[str, Any] | None = None,
    target_object: str | None,
    target_objects: list[str],
    collection_name: str | None,
    target_view: str | None,
    checkpoint_id: str,
    checkpoint_label: str | None,
    iteration_index: int,
    loop_disposition: Literal["continue_build", "inspect_validate", "stop"],
    continue_recommended: bool,
    prior_checkpoint_id: str | None,
    prior_correction_focus: list[str],
    correction_focus: list[str],
    repeated_correction_focus: list[str],
    stagnation_count: int,
    compare_result: ReferenceCompareStageCheckpointResponseContract,
    guided_reference_readiness: GuidedReferenceReadinessContract | None = None,
    reference_understanding_summary: ReferenceUnderstandingSummaryContract | None = None,
    reference_understanding_gate_ids: list[str] | None = None,
    reference_strategy_state: dict[str, Any] | None = None,
    correction_candidates: list[ReferenceCorrectionCandidateContract] | None = None,
    budget_control: ReferenceHybridBudgetControlContract | None = None,
    refinement_route: ReferenceRefinementRouteContract | None = None,
    refinement_handoff: ReferenceRefinementHandoffContract | None = None,
    planner_summary: ReferenceRepairPlannerSummaryContract | None = None,
    planner_detail: ReferenceRepairPlannerDetailContract | None = None,
    silhouette_analysis: ReferenceSilhouetteAnalysisContract | None = None,
    action_hints: list[ReferenceActionHintContract] | None = None,
    part_segmentation: ReferencePartSegmentationContract | None = None,
    view_diagnostics_hints: list[ReferenceViewDiagnosticsHintContract] | None = None,
    stop_reason: str | None = None,
    message: str | None = None,
    error: str | None = None,
) -> ReferenceIterateStageCheckpointResponseContract:
    compact_compare_result = _compact_compare_result_for_iterate(compare_result)
    debug_payload_omitted = compact_compare_result is not compare_result
    resolved_gate_plan = active_gate_plan
    if resolved_gate_plan is None and compare_result.active_gate_plan is not None:
        resolved_gate_plan = compare_result.active_gate_plan.model_dump(mode="json")
    if resolved_gate_plan is not None:
        gate_fields = _gate_checkpoint_fields(resolved_gate_plan)
    else:
        gate_fields = {
            "gate_statuses": list(compare_result.gate_statuses or []),
            "completion_blockers": list(compare_result.completion_blockers or []),
            "next_gate_actions": list(compare_result.next_gate_actions or []),
            "recommended_bounded_tools": list(compare_result.recommended_bounded_tools or []),
        }
    guided_flow_contract = (
        GuidedFlowStateContract.model_validate(guided_flow_state) if guided_flow_state is not None else None
    )
    active_gate_plan_contract = (
        GatePlanContract.model_validate(resolved_gate_plan) if resolved_gate_plan is not None else None
    )
    reference_strategy_contract = (
        ReferenceStrategyStateContract.model_validate(reference_strategy_state)
        if reference_strategy_state is not None
        else None
    )
    resolved_correction_candidates = list(correction_candidates or compare_result.correction_candidates or [])
    reference_orchestrator_feedback = build_reference_orchestrator_feedback(
        goal=goal,
        summary=reference_understanding_summary or compare_result.reference_understanding_summary,
        strategy_state=reference_strategy_contract,
        guided_flow_state=guided_flow_contract,
        gate_plan=active_gate_plan_contract,
        guided_reference_readiness=guided_reference_readiness or compare_result.guided_reference_readiness,
        compare_diagnostics=compare_result.compare_diagnostics,
        budget_control=budget_control or compare_result.budget_control,
        planner_summary=planner_summary or compare_result.planner_summary,
        correction_candidates=resolved_correction_candidates,
        next_gate_actions=list(gate_fields["next_gate_actions"] or []),
        recommended_bounded_tools=list(gate_fields["recommended_bounded_tools"] or []),
        correction_focus=correction_focus,
        loop_disposition=loop_disposition,
    )
    heavy_detail_allowed = _compact_compare_detail_allowed(
        preset_profile=compare_result.preset_profile,
        error=error,
        compare_diagnostics=compare_result.compare_diagnostics,
        hard_failure=_gate_fields_have_hard_failure(gate_fields),
    )
    return ReferenceIterateStageCheckpointResponseContract(
        action="iterate_stage_checkpoint",
        session_id=session_id,
        transport=transport,
        goal=goal,
        guided_flow_state=guided_flow_contract,
        active_gate_plan=active_gate_plan_contract,
        gate_statuses=gate_fields["gate_statuses"],
        completion_blockers=gate_fields["completion_blockers"],
        next_gate_actions=gate_fields["next_gate_actions"],
        recommended_bounded_tools=gate_fields["recommended_bounded_tools"],
        guided_reference_readiness=guided_reference_readiness or compare_result.guided_reference_readiness,
        reference_understanding_summary=reference_understanding_summary
        or compare_result.reference_understanding_summary,
        reference_understanding_gate_ids=(
            list(reference_understanding_gate_ids or [])
            if reference_understanding_gate_ids is not None
            else list(compare_result.reference_understanding_gate_ids or [])
        ),
        reference_orchestrator_feedback=reference_orchestrator_feedback,
        target_object=target_object,
        target_objects=target_objects,
        collection_name=collection_name,
        assembled_target_scope=compare_result.assembled_target_scope,
        truth_bundle=compare_result.truth_bundle if heavy_detail_allowed else None,
        truth_followup=compare_result.truth_followup if heavy_detail_allowed else None,
        compare_diagnostics=compare_result.compare_diagnostics,
        correction_candidates=resolved_correction_candidates if heavy_detail_allowed else [],
        budget_control=budget_control or compare_result.budget_control,
        refinement_route=refinement_route or compare_result.refinement_route,
        refinement_handoff=refinement_handoff or compare_result.refinement_handoff,
        planner_summary=planner_summary or compare_result.planner_summary,
        planner_detail=(planner_detail or compare_result.planner_detail) if heavy_detail_allowed else None,
        silhouette_analysis=silhouette_analysis or compare_result.silhouette_analysis,
        action_hints=list(action_hints or compare_result.action_hints or []),
        part_segmentation=part_segmentation or compare_result.part_segmentation or _disabled_part_segmentation(),
        view_diagnostics_hints=view_diagnostics_hints or compare_result.view_diagnostics_hints,
        target_view=target_view,
        checkpoint_id=checkpoint_id,
        checkpoint_label=checkpoint_label,
        iteration_index=iteration_index,
        loop_disposition=loop_disposition,
        continue_recommended=continue_recommended,
        prior_checkpoint_id=prior_checkpoint_id,
        prior_correction_focus=prior_correction_focus,
        correction_focus=correction_focus,
        repeated_correction_focus=repeated_correction_focus,
        stagnation_count=stagnation_count,
        stop_reason=stop_reason,
        compare_result=compact_compare_result,
        debug_payload_omitted=debug_payload_omitted,
        message=message,
        error=error,
    )


def _compact_compare_result_for_iterate(
    compare_result: ReferenceCompareStageCheckpointResponseContract,
) -> ReferenceCompareStageCheckpointResponseContract:
    """Return a slim compare_result copy for normal compact iterate responses."""

    if compare_result.preset_profile != "compact":
        return compare_result
    return compare_result.model_copy(
        update={
            "truth_bundle": None,
            "truth_followup": None,
            "compare_diagnostics": None,
            "correction_candidates": [],
            "silhouette_analysis": None,
            "action_hints": [],
            "planner_detail": None,
            "part_segmentation": _disabled_part_segmentation(),
            "captures": [],
            "message": (
                "Compact iterate response omitted nested debug compare payload details; use rich/debug delivery for full data."
            ),
        }
    )


def _should_hold_guided_build_loop_in_build(
    guided_flow_state: dict[str, Any] | None,
) -> bool:
    if guided_flow_state is None:
        return False

    if hasattr(guided_flow_state, "model_dump"):
        try:
            guided_flow_state = guided_flow_state.model_dump(mode="json")
        except Exception:
            return False

    if not isinstance(guided_flow_state, dict):
        return False

    current_step = str(guided_flow_state.get("current_step") or "").strip().lower()
    missing_roles = [str(role).strip() for role in guided_flow_state.get("missing_roles") or [] if str(role).strip()]
    return current_step in {"create_primary_masses", "place_secondary_parts"} and bool(missing_roles)


_REFINEMENT_CONTINUE_BUILD_GATE_TYPES: frozenset[str] = frozenset(
    {"shape_profile", "proportion_ratio", "opening_or_cut", "refinement_stage"}
)


def _completion_blocker_gate_type(blocker: Any) -> str:
    if isinstance(blocker, dict):
        return str(blocker.get("gate_type") or "").strip()
    return str(getattr(blocker, "gate_type", "") or "").strip()


def _should_continue_refinement_build(
    guided_flow_state: dict[str, Any] | None,
    completion_blockers: list[Any] | None,
) -> bool:
    if guided_flow_state is None:
        return False

    if hasattr(guided_flow_state, "model_dump"):
        try:
            guided_flow_state = guided_flow_state.model_dump(mode="json")
        except Exception:
            return False

    if not isinstance(guided_flow_state, dict):
        return False

    current_step = str(guided_flow_state.get("current_step") or "").strip().lower()
    if current_step != "refine_low_poly_forms":
        return False

    blockers = list(completion_blockers or [])
    if not blockers:
        return False

    blocker_types = {_completion_blocker_gate_type(blocker) for blocker in blockers}
    blocker_types.discard("")
    return bool(blocker_types) and blocker_types.issubset(_REFINEMENT_CONTINUE_BUILD_GATE_TYPES)


def _guided_stage_reference_error(readiness: GuidedReferenceReadinessState) -> str:
    """Return one deterministic fail-fast error for staged guided reference flows."""

    if readiness.blocking_reason == "active_goal_required":
        return "Set an active goal with router_set_goal(...) before calling staged compare/iterate tools."
    if readiness.blocking_reason == "goal_input_pending":
        return "Finish the pending router goal questions before calling staged compare/iterate tools."
    if readiness.blocking_reason == "pending_references_detected":
        return "Reference session is not ready yet because pending references still need adoption or review."
    if readiness.blocking_reason == "reference_images_required":
        return "Attach at least one reference image with reference_images(action='attach', ...) before staging compare/iterate."
    return (
        "Reference session is not ready for staged compare/iterate yet. Check router_get_status() for the next action."
    )


def _scene_scope_looks_like_existing_build(
    *,
    target_object: str | None,
    target_objects: list[str] | None,
    collection_name: str | None,
) -> bool:
    """Return True when the requested stage scope already appears to exist in Blender."""

    requested_names = _dedupe_names([*(target_objects or []), *([target_object] if target_object else [])])
    if requested_names:
        try:
            scene_objects = get_scene_handler().list_objects()
        except Exception:
            scene_objects = []
        existing_names = {
            str(item.get("name")).strip()
            for item in scene_objects
            if isinstance(item, dict) and str(item.get("name") or "").strip()
        }
        if any(name in existing_names for name in requested_names):
            return True

    if collection_name:
        try:
            collection_payload = get_collection_handler().list_objects(
                collection_name=collection_name,
                recursive=True,
                include_hidden=False,
            )
        except Exception:
            return False
        collection_objects = [
            str(item.get("name")).strip()
            for item in collection_payload.get("objects", [])
            if isinstance(item, dict) and str(item.get("name") or "").strip()
        ]
        if collection_objects:
            return True

    return False


def _guided_stage_reference_recovery_error(
    readiness: GuidedReferenceReadinessState,
    *,
    target_object: str | None,
    target_objects: list[str] | None,
    collection_name: str | None,
) -> str:
    """Return a fail-fast error with a reconnect/reset hint when scene scope already exists."""

    base_error = _guided_stage_reference_error(readiness)
    if readiness.blocking_reason != "active_goal_required":
        return base_error
    if not _scene_scope_looks_like_existing_build(
        target_object=target_object,
        target_objects=target_objects,
        collection_name=collection_name,
    ):
        return base_error
    return (
        f"{base_error} The requested Blender objects/collection already exist, so the scene may still be intact "
        "while the guided MCP session state was reset or reconnected. Re-run router_set_goal(...), then restore "
        "reference_images(...) only if guided_reference_readiness still reports them missing."
    )


def _guided_checkpoint_scope_error(
    guided_flow_state: dict[str, Any] | None,
    requested_scope: SceneAssembledTargetScopeContract,
) -> str | None:
    """Return an actionable error when a checkpoint narrows away from the active workset."""

    if not guided_flow_state:
        return None
    try:
        flow_state = GuidedFlowStateContract.model_validate(guided_flow_state)
    except Exception:
        return None
    if flow_state.current_step not in {"checkpoint_iterate", "inspect_validate"}:
        return None
    active_scope = flow_state.active_target_scope
    if active_scope is None:
        return None

    active_collection = str(active_scope.collection_name or "").strip()
    requested_collection = str(requested_scope.collection_name or "").strip()
    if active_collection and requested_collection == active_collection:
        return None

    active_objects = {name.lower() for name in active_scope.object_names if name.strip()}
    requested_objects = {name.lower() for name in requested_scope.object_names if name.strip()}
    if active_scope.primary_target:
        active_objects.add(active_scope.primary_target.lower())
    if requested_scope.primary_target:
        requested_objects.add(requested_scope.primary_target.lower())

    if len(active_objects) <= 1:
        return None
    if active_objects and active_objects.issubset(requested_objects):
        return None

    expected = (
        f"collection_name={active_collection!r}"
        if active_collection
        else f"target_objects={list(active_scope.object_names)!r}"
    )
    return (
        "Checkpoint target scope does not cover the active guided workset. "
        f"Use {expected} so required seams remain visible; do not narrow to a single safe object while the "
        "assembled workset is still active."
    )


def _is_recoverable_stage_compare_setup_error(
    compare_result: ReferenceCompareStageCheckpointResponseContract,
) -> bool:
    """Return True for setup/precondition errors that should not advance the guided loop."""

    if not compare_result.error:
        return False

    readiness = compare_result.guided_reference_readiness
    if readiness is not None and readiness.status == "blocked":
        return True

    error_text = compare_result.error.strip()
    recoverable_prefixes = (
        "Checkpoint target scope does not cover the active guided workset.",
        "No matching reference images are attached for the requested target_object/target_view.",
        "Reference session is not ready for staged compare/iterate yet.",
    )
    return any(error_text.startswith(prefix) for prefix in recoverable_prefixes)


def _trim_correction_candidates(
    candidates: list[ReferenceCorrectionCandidateContract],
    *,
    candidate_budget: int,
) -> tuple[list[ReferenceCorrectionCandidateContract], bool]:
    return _planner_trim_correction_candidates(
        candidates,
        candidate_budget=candidate_budget,
    )


def _disabled_part_segmentation() -> ReferencePartSegmentationContract:
    return ReferencePartSegmentationContract(
        status="disabled",
        provider_name=None,
        advisory_only=True,
        parts=[],
        notes=[
            "Optional part segmentation remains disabled by default.",
            "The sidecar path is advisory-only and separate from vision_contract_profile routing.",
        ],
    )


def _configured_part_segmentation() -> ReferencePartSegmentationContract:
    from server.infrastructure.di import get_vision_backend_resolver

    resolver = get_vision_backend_resolver()
    runtime_config = getattr(resolver, "runtime_config", None)
    sidecar = getattr(runtime_config, "active_segmentation_sidecar", None) if runtime_config is not None else None
    if sidecar is None or not getattr(sidecar, "enabled", False):
        return _disabled_part_segmentation()
    return ReferencePartSegmentationContract(
        status="unavailable",
        provider_name=getattr(sidecar, "provider_name", None),
        advisory_only=True,
        parts=[],
        notes=[
            "Optional part segmentation sidecar is enabled on the runtime config.",
            "No compare-time sidecar result was collected for this staged compare run.",
            "The sidecar path is advisory-only and separate from vision_contract_profile routing.",
        ],
    )


def _gate_slug(value: str | None) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", str(value or "").strip().lower()).strip("_")
    return normalized or "unknown"


def _guided_domain_profile(guided_flow_state: dict[str, Any] | None) -> str | None:
    if guided_flow_state is None:
        return None
    try:
        return str(GuidedFlowStateContract.model_validate(guided_flow_state).domain_profile)
    except Exception:
        return None


def _reference_checkpoint_gate_proposal(
    *,
    session: SessionCapabilityState,
    truth_bundle: SceneCorrectionTruthBundleContract,
) -> dict[str, Any] | None:
    """Build checkpoint-owned quality gates from deterministic creature seam truth."""

    if _guided_domain_profile(session.guided_flow_state) != "creature":
        return None

    gates: list[dict[str, Any]] = []
    seen_pairs: set[tuple[str, str]] = set()
    if truth_bundle.summary.pairing_strategy == "required_creature_seams":
        for check in truth_bundle.checks:
            semantics = check.attachment_semantics
            if semantics is None or not semantics.required_seam:
                continue
            part_object = str(semantics.part_object or check.from_object).strip()
            anchor_object = str(semantics.anchor_object or check.to_object).strip()
            if not part_object or not anchor_object:
                continue
            pair_key = (part_object, anchor_object)
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)
            seam_kind = str(semantics.seam_kind)
            gates.append(
                {
                    "gate_id": (
                        f"creature_{_gate_slug(seam_kind)}_"
                        f"{_gate_slug(part_object)}_to_{_gate_slug(anchor_object)}_seam"
                    ),
                    "gate_type": "attachment_seam",
                    "label": f"{seam_kind.replace('_', '/')} seam is seated",
                    "target_kind": "object_pair",
                    "target_objects": [part_object, anchor_object],
                    "allow_embedded_intersection": semantics.relation_kind == "embedded_attachment",
                    "allowed_correction_families": ["attachment_alignment", "inspect_validate"],
                }
            )

    if not gates and session.gate_plan is not None:
        return None
    return {
        "proposal_id": "reference_checkpoint_creature_completion_gates",
        "source": "reference_checkpoint",
        "gates": gates,
    }


async def refresh_reference_understanding_summary_async(
    ctx: Context,
    *,
    session: SessionCapabilityState | None = None,
) -> SessionCapabilityState:
    """Refresh session-scoped reference understanding from active references when possible."""

    return await _refresh_reference_understanding_summary_impl(
        ctx,
        session=session,
        get_session_capability_state_async=get_session_capability_state_async,
        set_session_capability_state_async=set_session_capability_state_async,
        apply_visibility_for_session_state=apply_visibility_for_session_state,
        build_reference_capture_images=build_reference_capture_images,
        get_vision_backend_resolver=get_vision_backend_resolver,
        ingest_quality_gate_proposal_async=ingest_quality_gate_proposal_async,
    )


def _repeated_focus(current: list[str], prior: list[str]) -> list[str]:
    prior_keys = {_normalize_focus_key(item) for item in prior if _normalize_focus_key(item)}
    repeated: list[str] = []
    for item in current:
        normalized = _normalize_focus_key(item)
        if normalized and normalized in prior_keys:
            repeated.append(item)
    return repeated


async def _run_checkpoint_compare(
    ctx: Context,
    *,
    checkpoint: Path,
    checkpoint_label: str | None,
    target_object: str | None,
    target_view: str | None,
    goal_override: str | None,
    prompt_hint: str | None,
    response_action: Literal["compare_checkpoint", "compare_current_view"],
) -> ReferenceCompareCheckpointResponseContract:
    """Shared bounded checkpoint compare path."""

    return await _run_checkpoint_compare_impl(
        ctx,
        checkpoint=checkpoint,
        checkpoint_label=checkpoint_label,
        target_object=target_object,
        target_view=target_view,
        goal_override=goal_override,
        prompt_hint=prompt_hint,
        response_action=response_action,
        build_compare_response=_compare_response,
        get_session_capability_state_async=get_session_capability_state_async,
        select_reference_records_for_target=select_reference_records_for_target,
        build_reference_capture_images=build_reference_capture_images,
        run_vision_assist=run_vision_assist,
        get_vision_backend_resolver=get_vision_backend_resolver,
        to_vision_assistant_contract=to_vision_assistant_contract,
    )


def _effective_reference_understanding_gate_ids_from_session(session: SessionCapabilityState) -> list[str]:
    if session.reference_understanding_gate_ids is not None:
        return list(session.reference_understanding_gate_ids)
    if session.gate_plan is None:
        return []
    gate_plan = GatePlanContract.model_validate(session.gate_plan)
    return [gate.gate_id for gate in gate_plan.gates if "reference_understanding" in gate.proposal_sources]


async def _run_stage_checkpoint_compare(
    ctx: Context,
    *,
    checkpoint_id: str,
    checkpoint_label: str | None,
    target_object: str | None,
    target_objects: list[str] | None,
    collection_name: str | None,
    target_view: str | None,
    preset_profile: CapturePresetProfile,
    goal_override: str | None,
    prompt_hint: str | None,
    emit_compact_detail: bool = False,
) -> ReferenceCompareStageCheckpointResponseContract:
    """Capture one deterministic stage view-set, then compare it against references."""

    session = await get_session_capability_state_async(ctx)
    session_id = ctx_session_id(ctx)
    transport = ctx_transport_type(ctx)
    readiness = build_guided_reference_readiness(session)
    readiness_contract = GuidedReferenceReadinessContract.model_validate(
        build_guided_reference_readiness_payload(session)
    )
    reference_understanding_summary = (
        ReferenceUnderstandingSummaryContract.model_validate(session.reference_understanding_summary)
        if session.reference_understanding_summary is not None
        else None
    )
    reference_understanding_gate_ids = _effective_reference_understanding_gate_ids_from_session(session)
    reference_strategy_state = session.reference_strategy_state
    goal = session.goal
    emit_debug_log(
        "reference",
        logger,
        "stage_compare_start checkpoint_id=%s preset_profile=%s goal_present=%s reference_count=%d",
        checkpoint_id,
        preset_profile,
        goal is not None,
        len(session.reference_images or []),
    )
    if not readiness.compare_ready or goal is None:
        emit_debug_log(
            "reference",
            logger,
            "stage_compare_blocked checkpoint_id=%s readiness_status=%s next_action=%s",
            checkpoint_id,
            readiness.status,
            readiness.next_action,
            level=logging.WARNING,
        )
        return _stage_compare_response(
            session_id=session_id,
            transport=transport,
            guided_flow_state=session.guided_flow_state,
            active_gate_plan=session.gate_plan,
            checkpoint_id=checkpoint_id,
            checkpoint_label=checkpoint_label,
            goal=goal,
            target_object=target_object,
            target_objects=list(target_objects or []),
            collection_name=collection_name,
            assembled_target_scope=None,
            target_view=target_view,
            preset_profile=preset_profile,
            preset_names=[],
            reference_ids=[],
            reference_labels=[],
            guided_reference_readiness=readiness_contract,
            reference_understanding_summary=reference_understanding_summary,
            reference_understanding_gate_ids=reference_understanding_gate_ids,
            reference_strategy_state=reference_strategy_state,
            error=_guided_stage_reference_recovery_error(
                readiness,
                target_object=target_object,
                target_objects=target_objects,
                collection_name=collection_name,
            ),
        )

    prior_loop_state = await get_session_value_async(ctx, _REFERENCE_CORRECTION_LOOP_STATE_KEY, None)
    prior_focus_pairs = (
        list(prior_loop_state.get("last_focus_pairs") or [])
        if isinstance(prior_loop_state, dict)
        and prior_loop_state.get("goal") == goal
        and prior_loop_state.get("preset_profile") == preset_profile
        and not target_object
        and not target_objects
        and not collection_name
        else []
    )
    runtime_scope = resolve_active_compare_scope(
        guided_flow_state=session.guided_flow_state,
        gate_plan=session.gate_plan,
        guided_part_registry=session.guided_part_registry,
        last_guided_affected_objects=session.last_guided_affected_objects,
        target_object=target_object,
        target_objects=target_objects,
        collection_name=collection_name,
        focus_pairs=prior_focus_pairs,
    )
    runtime_scope_selected = (
        runtime_scope is not None and not target_object and not target_objects and not collection_name
    )

    try:
        resolved_target_object, resolved_target_objects, resolved_collection_name = _resolve_capture_scope(
            target_object=runtime_scope.target_object if runtime_scope is not None else target_object,
            target_objects=runtime_scope.target_objects if runtime_scope is not None else target_objects,
            collection_name=runtime_scope.collection_name if runtime_scope is not None else collection_name,
        )
    except RuntimeError as exc:
        return _stage_compare_response(
            session_id=session_id,
            transport=transport,
            guided_flow_state=session.guided_flow_state,
            active_gate_plan=session.gate_plan,
            checkpoint_id=checkpoint_id,
            checkpoint_label=checkpoint_label,
            goal=goal,
            target_object=target_object,
            target_objects=list(target_objects or []),
            collection_name=collection_name,
            assembled_target_scope=None,
            target_view=target_view,
            preset_profile=preset_profile,
            preset_names=[],
            reference_ids=[],
            reference_labels=[],
            guided_reference_readiness=readiness_contract,
            reference_understanding_summary=reference_understanding_summary,
            reference_understanding_gate_ids=reference_understanding_gate_ids,
            reference_strategy_state=reference_strategy_state,
            error=str(exc),
        )
    assembled_target_scope = _assembled_target_scope(
        target_object=resolved_target_object,
        target_objects=resolved_target_objects,
        collection_name=resolved_collection_name,
    )
    capture_target_object = resolved_target_object or assembled_target_scope.primary_target
    scope_error = (
        None
        if runtime_scope_selected
        else _guided_checkpoint_scope_error(session.guided_flow_state, assembled_target_scope)
    )
    if scope_error:
        return _stage_compare_response(
            session_id=session_id,
            transport=transport,
            guided_flow_state=session.guided_flow_state,
            active_gate_plan=session.gate_plan,
            checkpoint_id=checkpoint_id,
            checkpoint_label=checkpoint_label,
            goal=goal,
            target_object=resolved_target_object,
            target_objects=resolved_target_objects,
            collection_name=resolved_collection_name,
            assembled_target_scope=assembled_target_scope,
            target_view=target_view,
            preset_profile=preset_profile,
            preset_names=[],
            reference_ids=[],
            reference_labels=[],
            guided_reference_readiness=readiness_contract,
            reference_understanding_summary=reference_understanding_summary,
            reference_understanding_gate_ids=reference_understanding_gate_ids,
            reference_strategy_state=reference_strategy_state,
            error=scope_error,
        )

    references = list(session.reference_images or [])
    selected_reference_records = _select_reference_records_for_scope(
        references,
        resolved_target_object=resolved_target_object,
        assembled_target_scope=assembled_target_scope,
        target_view=target_view,
    )
    if not selected_reference_records:
        emit_debug_log(
            "reference",
            logger,
            "stage_compare_no_matching_references checkpoint_id=%s target_object=%s target_count=%d",
            checkpoint_id,
            resolved_target_object,
            len(resolved_target_objects),
            level=logging.WARNING,
        )
        return _stage_compare_response(
            session_id=session_id,
            transport=transport,
            guided_flow_state=session.guided_flow_state,
            active_gate_plan=session.gate_plan,
            checkpoint_id=checkpoint_id,
            checkpoint_label=checkpoint_label,
            goal=goal,
            target_object=resolved_target_object,
            target_objects=resolved_target_objects,
            collection_name=resolved_collection_name,
            assembled_target_scope=assembled_target_scope,
            target_view=target_view,
            preset_profile=preset_profile,
            preset_names=[],
            reference_ids=[],
            reference_labels=[],
            guided_reference_readiness=readiness_contract,
            reference_understanding_summary=reference_understanding_summary,
            reference_understanding_gate_ids=reference_understanding_gate_ids,
            reference_strategy_state=reference_strategy_state,
            error="No matching reference images are attached for the requested target_object/target_view.",
        )

    scene_handler = get_scene_handler()

    try:
        captures = capture_stage_images(
            scene_handler,
            bundle_id=checkpoint_id,
            stage="after",
            target_object=capture_target_object,
            target_objects=resolved_target_objects,
            preset_profile=preset_profile,
        )
    except RuntimeError as exc:
        emit_debug_log(
            "reference",
            logger,
            "stage_compare_capture_error checkpoint_id=%s error=%s",
            checkpoint_id,
            exc,
            level=logging.WARNING,
        )
        return _stage_compare_response(
            session_id=session_id,
            transport=transport,
            guided_flow_state=session.guided_flow_state,
            active_gate_plan=session.gate_plan,
            checkpoint_id=checkpoint_id,
            checkpoint_label=checkpoint_label,
            goal=goal,
            target_object=resolved_target_object,
            target_objects=resolved_target_objects,
            collection_name=resolved_collection_name,
            assembled_target_scope=assembled_target_scope,
            target_view=target_view,
            preset_profile=preset_profile,
            preset_names=[],
            reference_ids=[item.reference_id for item in selected_reference_records],
            reference_labels=[item.label or item.reference_id for item in selected_reference_records],
            guided_reference_readiness=readiness_contract,
            reference_understanding_summary=reference_understanding_summary,
            reference_understanding_gate_ids=reference_understanding_gate_ids,
            reference_strategy_state=reference_strategy_state,
            error=str(exc),
        )

    view_diagnostics_hints = _build_stage_view_diagnostics_hints(
        scene_handler=scene_handler,
        captures=captures,
        preset_profile=preset_profile,
        target_object=capture_target_object,
        target_objects=resolved_target_objects,
        collection_name=resolved_collection_name,
        target_view=target_view,
    )

    resolver = get_vision_backend_resolver()
    runtime_config = getattr(resolver, "runtime_config", None)
    segmentation_sidecar_config = (
        getattr(runtime_config, "active_segmentation_sidecar", None) if runtime_config is not None else None
    )
    runtime_budget = _resolve_hybrid_budget_runtime(resolver)
    runtime_max_tokens = runtime_budget.max_tokens
    runtime_max_images = runtime_budget.max_images
    runtime_max_input_chars = runtime_budget.max_input_chars
    runtime_model_name = runtime_budget.model_name
    truth_bundle, _truth_relation_graph = _build_correction_truth_bundle(
        scene_handler,
        assembled_target_scope,
        goal_hint=goal,
    )
    pair_budget = _effective_pair_budget(
        max_tokens=runtime_max_tokens,
        model_name=runtime_model_name,
    )
    if truth_bundle.summary.pairing_strategy == "required_creature_seams":
        required_creature_pair_count = sum(
            1
            for check in truth_bundle.checks
            if check.attachment_semantics is not None and check.attachment_semantics.required_seam
        )
        pair_budget = max(
            pair_budget,
            min(required_creature_pair_count or truth_bundle.summary.pair_count, 6),
        )
        truth_char_share = 1.0
        truth_char_floor = 6000
    else:
        truth_char_share = 0.5
        truth_char_floor = 1800
    max_truth_chars = min(
        int(runtime_max_input_chars * truth_char_share),
        max(truth_char_floor, runtime_max_tokens * 12),
    )
    budgeted_truth_bundle, scope_trimmed = _trim_truth_bundle_to_budget(
        truth_bundle=truth_bundle,
        pair_budget=pair_budget,
        max_truth_chars=max_truth_chars,
    )
    truth_followup = _build_truth_followup(budgeted_truth_bundle)
    checkpoint_gate_proposal = _reference_checkpoint_gate_proposal(
        session=session,
        truth_bundle=truth_bundle,
    )
    if checkpoint_gate_proposal is not None:
        gate_intake = await ingest_quality_gate_proposal_async(ctx, checkpoint_gate_proposal)
        if gate_intake.status == "accepted":
            session = await get_session_capability_state_async(ctx)
    silhouette_analysis = _build_silhouette_analysis_payload(
        selected_reference_records=selected_reference_records,
        captures=captures,
        target_view=target_view,
    )
    action_hints = _build_action_hints_from_silhouette(
        silhouette_analysis,
        target_object=resolved_target_object or assembled_target_scope.primary_target,
    )
    compare_diagnostics = _build_compare_packets(
        target_view=target_view,
        captures=captures,
        reference_records=selected_reference_records,
        assembled_target_scope=assembled_target_scope,
        truth_followup=truth_followup,
        max_images_per_packet=runtime_max_images,
        prefer_target_scope_clusters=(runtime_scope.local_region_hint == "primary_mass_workset")
        if runtime_scope is not None
        else False,
    )
    packet_execution = await _execute_compare_packets(
        ctx=ctx,
        compare_diagnostics=compare_diagnostics,
        captures=captures,
        reference_records=selected_reference_records,
        truth_bundle=budgeted_truth_bundle,
        goal=goal,
        prompt_hint=prompt_hint,
        checkpoint_label=checkpoint_label,
        checkpoint_id=checkpoint_id,
        preset_profile=preset_profile,
        target_view=target_view,
        resolved_collection_name=resolved_collection_name,
        resolved_target_object=resolved_target_object,
        resolved_target_objects=resolved_target_objects,
        assembled_target_scope=assembled_target_scope,
        segmentation_sidecar_config=segmentation_sidecar_config,
        resolver=resolver,
        run_vision_assist_fn=run_vision_assist,
        to_vision_assistant_contract_fn=to_vision_assistant_contract,
    )
    compare_diagnostics = packet_execution.compare_diagnostics
    vision_assistant = packet_execution.vision_assistant
    part_segmentation = packet_execution.part_segmentation
    if part_segmentation is None:
        part_segmentation = _configured_part_segmentation()
    runtime_budget = _resolve_hybrid_budget_runtime(resolver)
    runtime_max_tokens = runtime_budget.max_tokens
    runtime_max_images = runtime_budget.max_images
    runtime_max_input_chars = runtime_budget.max_input_chars
    runtime_model_name = runtime_budget.model_name
    full_correction_candidates = _build_correction_candidates(
        ReferenceCompareStageCheckpointResponseContract(
            action="compare_stage_checkpoint",
            goal=goal,
            guided_reference_readiness=readiness_contract,
            reference_understanding_summary=reference_understanding_summary,
            reference_understanding_gate_ids=reference_understanding_gate_ids,
            target_object=resolved_target_object,
            target_objects=resolved_target_objects,
            collection_name=resolved_collection_name,
            assembled_target_scope=assembled_target_scope,
            truth_bundle=budgeted_truth_bundle,
            truth_followup=truth_followup,
            compare_diagnostics=compare_diagnostics,
            target_view=target_view,
            view_diagnostics_hints=view_diagnostics_hints,
            checkpoint_id=checkpoint_id,
            checkpoint_label=checkpoint_label,
            preset_profile=preset_profile,
            preset_names=[capture.preset_name or capture.label for capture in captures],
            capture_count=len(captures),
            captures=list(captures),
            reference_count=len(selected_reference_records),
            reference_ids=[item.reference_id for item in selected_reference_records],
            reference_labels=[item.label or item.reference_id for item in selected_reference_records],
            vision_assistant=vision_assistant,
            silhouette_analysis=silhouette_analysis,
            action_hints=action_hints,
            part_segmentation=part_segmentation,
        )
    )
    candidate_budget = _effective_candidate_budget(
        pair_budget=pair_budget,
        max_tokens=runtime_max_tokens,
        model_name=runtime_model_name,
    )
    correction_candidates, candidate_detail_trimmed = _trim_correction_candidates(
        full_correction_candidates,
        candidate_budget=candidate_budget,
    )
    compact_capture_trimmed = preset_profile == "compact" and bool(captures)
    planner_detail_trimmed = preset_profile == "compact"
    compact_detail_trimmed = candidate_detail_trimmed or compact_capture_trimmed or planner_detail_trimmed
    model_aware_trimming_applied = scope_trimmed or candidate_detail_trimmed
    budget_control = ReferenceHybridBudgetControlContract(
        model_name=runtime_model_name,
        max_input_chars=runtime_max_input_chars,
        max_output_tokens=runtime_max_tokens,
        max_images=runtime_max_images,
        configured_max_input_chars=runtime_budget.configured_max_input_chars,
        configured_max_output_tokens=runtime_budget.configured_max_tokens,
        configured_max_images=runtime_budget.configured_max_images,
        effective_max_input_chars=runtime_budget.max_input_chars,
        effective_max_output_tokens=runtime_budget.max_tokens,
        effective_max_images=runtime_budget.max_images,
        fail_safe_max_input_chars=runtime_budget.fail_safe_max_input_chars,
        fail_safe_max_output_tokens=runtime_budget.fail_safe_max_tokens,
        fail_safe_max_images=runtime_budget.fail_safe_max_images,
        budget_clipped=runtime_budget.budget_clipped,
        budget_clip_fields=list(runtime_budget.budget_clip_fields),
        original_pair_count=truth_bundle.summary.pair_count,
        emitted_pair_count=budgeted_truth_bundle.summary.pair_count,
        original_candidate_count=len(full_correction_candidates),
        emitted_candidate_count=len(correction_candidates),
        trimming_applied=scope_trimmed or compact_detail_trimmed,
        scope_trimmed=scope_trimmed,
        detail_trimmed=compact_detail_trimmed,
        trim_reason=(
            "model_aware_budget_control"
            if scope_trimmed or candidate_detail_trimmed
            else "compact_checkpoint_payload"
            if compact_capture_trimmed or planner_detail_trimmed
            else None
        ),
        selected_focus_pairs=list(truth_followup.focus_pairs or []),
    )
    if model_aware_trimming_applied:
        compare_diagnostics.budget_notes.append(
            "Model-aware budget control trimmed staged compare evidence before final projection."
        )
    if runtime_budget.budget_clipped:
        clipped_fields = ", ".join(runtime_budget.budget_clip_fields)
        compare_diagnostics.budget_notes.append(
            f"Configured vision budget exceeded fail-safe caps; effective limits were clipped for {clipped_fields}."
        )
    if compare_diagnostics.synthesis_required and compare_diagnostics.synthesis_status == "success":
        compare_diagnostics.conflict_notes = _dedupe_preserving_order(compare_diagnostics.conflict_notes)
    candidate_packet_refs_present = any(
        candidate.vision_evidence is not None and bool(candidate.vision_evidence.packet_evidence_refs)
        for candidate in correction_candidates
    )
    emitted_compare_diagnostics = (
        compare_diagnostics
        if candidate_packet_refs_present
        or _should_emit_compare_diagnostics(
            compare_diagnostics=compare_diagnostics,
            preset_profile=preset_profile,
            model_aware_trimming_applied=model_aware_trimming_applied or runtime_budget.budget_clipped,
        )
        else None
    )
    staged_compare_contract = ReferenceCompareStageCheckpointResponseContract(
        action="compare_stage_checkpoint",
        goal=goal,
        guided_reference_readiness=readiness_contract,
        reference_understanding_summary=reference_understanding_summary,
        reference_understanding_gate_ids=reference_understanding_gate_ids,
        target_object=resolved_target_object,
        target_objects=resolved_target_objects,
        collection_name=resolved_collection_name,
        assembled_target_scope=assembled_target_scope,
        truth_bundle=budgeted_truth_bundle,
        truth_followup=truth_followup,
        compare_diagnostics=emitted_compare_diagnostics,
        correction_candidates=correction_candidates,
        budget_control=budget_control,
        view_diagnostics_hints=view_diagnostics_hints,
        target_view=target_view,
        checkpoint_id=checkpoint_id,
        checkpoint_label=checkpoint_label,
        preset_profile=preset_profile,
        preset_names=[capture.preset_name or capture.label for capture in captures],
        capture_count=len(captures),
        captures=list(captures),
        reference_count=len(selected_reference_records),
        reference_ids=[item.reference_id for item in selected_reference_records],
        reference_labels=[item.label or item.reference_id for item in selected_reference_records],
        vision_assistant=vision_assistant,
        silhouette_analysis=silhouette_analysis,
        action_hints=action_hints,
        part_segmentation=part_segmentation,
    )
    active_gate_plan = session.gate_plan
    if session.gate_plan is not None:
        gate_relation_graph = get_spatial_graph_service().build_relation_graph(
            reader=scene_handler,
            scope_graph=assembled_target_scope.model_dump(mode="json"),
            goal_hint=goal,
            include_truth_payloads=False,
            include_guided_pairs=True,
        )
        flow_state = (
            GuidedFlowStateContract.model_validate(session.guided_flow_state)
            if session.guided_flow_state is not None
            else None
        )
        updated_gate_plan = verify_gate_plan_with_relation_graph(
            session.gate_plan,
            gate_relation_graph,
            spatial_state_version=None if flow_state is None else flow_state.spatial_state_version,
            scope_fingerprint=None if flow_state is None else flow_state.spatial_scope_fingerprint,
            guided_part_registry=cast(list[Mapping[str, Any]] | None, session.guided_part_registry),
        )
        session = replace(session, gate_plan=updated_gate_plan.model_dump(mode="json", exclude_none=True))
        await set_session_capability_state_async(ctx, session)
        await apply_visibility_for_session_state(ctx, session)
        active_gate_plan = session.gate_plan

    refinement_route = _select_refinement_route(
        staged_compare_contract,
        active_gate_plan=active_gate_plan,
    )
    refinement_handoff = _build_refinement_handoff(staged_compare_contract, refinement_route)
    planner_summary = _build_repair_planner_summary(
        staged_compare_contract,
        route=refinement_route,
        handoff=refinement_handoff,
    )
    planner_detail = (
        _build_repair_planner_detail(
            staged_compare_contract,
            summary=planner_summary,
            route=refinement_route,
            handoff=refinement_handoff,
            detail_trimmed=scope_trimmed or candidate_detail_trimmed,
        )
        if preset_profile == "rich"
        else None
    )

    response = _stage_compare_response(
        session_id=session_id,
        transport=transport,
        guided_flow_state=session.guided_flow_state,
        active_gate_plan=active_gate_plan,
        checkpoint_id=checkpoint_id,
        checkpoint_label=checkpoint_label,
        goal=goal,
        target_object=resolved_target_object,
        target_objects=resolved_target_objects,
        collection_name=resolved_collection_name,
        assembled_target_scope=assembled_target_scope,
        target_view=target_view,
        preset_profile=preset_profile,
        preset_names=[capture.preset_name or capture.label for capture in captures],
        captures=captures,
        reference_ids=[item.reference_id for item in selected_reference_records],
        reference_labels=[item.label or item.reference_id for item in selected_reference_records],
        guided_reference_readiness=readiness_contract,
        reference_understanding_summary=reference_understanding_summary,
        reference_understanding_gate_ids=reference_understanding_gate_ids,
        reference_strategy_state=reference_strategy_state,
        vision_assistant=vision_assistant,
        truth_bundle=budgeted_truth_bundle,
        truth_followup=truth_followup,
        compare_diagnostics=emitted_compare_diagnostics,
        correction_candidates=correction_candidates,
        budget_control=budget_control,
        refinement_route=refinement_route,
        refinement_handoff=refinement_handoff,
        planner_summary=planner_summary,
        planner_detail=planner_detail,
        silhouette_analysis=silhouette_analysis,
        action_hints=action_hints,
        part_segmentation=part_segmentation,
        view_diagnostics_hints=view_diagnostics_hints,
        include_captures=preset_profile != "compact",
        emit_compact_detail=emit_compact_detail,
        message=(
            f"Captured and compared stage checkpoint '{checkpoint_label or checkpoint_id}' across "
            f"{compare_diagnostics.packet_count} packet(s) using {len(captures)} deterministic view(s)."
            if vision_assistant is not None and vision_assistant.status == "success"
            else "Stage checkpoint capture executed but packeted vision assistance did not complete successfully."
        ),
        error=(
            vision_assistant.rejection_reason
            if vision_assistant is not None and vision_assistant.status != "success"
            else None
        ),
    )
    emit_debug_log(
        "reference",
        logger,
        "stage_compare_finish checkpoint_id=%s packet_count=%d capture_count=%d reference_count=%d vision_status=%s compare_error=%s",
        checkpoint_id,
        compare_diagnostics.packet_count,
        len(captures),
        len(selected_reference_records),
        vision_assistant.status if vision_assistant is not None else None,
        response.error,
    )
    return response


async def reference_images(
    ctx: Context,
    action: str,
    source_path: str | None = None,
    reference_id: str | None = None,
    label: str | None = None,
    notes: str | None = None,
    target_object: str | None = None,
    target_view: str | None = None,
) -> ReferenceImagesResponseContract:
    """Manage goal-scoped reference images for later vision/capture interpretation."""

    return await _handle_reference_images(
        ctx,
        action=action,
        source_path=source_path,
        images=None,
        source_paths=None,
        reference_id=reference_id,
        label=label,
        notes=notes,
        target_object=target_object,
        target_view=target_view,
        refresh_reference_understanding=lambda context, session: refresh_reference_understanding_summary_async(
            context,
            session=session,
        ),
    )


async def reference_compare_checkpoint(
    ctx: Context,
    checkpoint_path: str,
    checkpoint_label: str | None = None,
    target_object: str | None = None,
    target_view: str | None = None,
    goal_override: str | None = None,
    prompt_hint: str | None = None,
) -> ReferenceCompareCheckpointResponseContract:
    """Compare one current checkpoint image against the active goal and attached references."""

    try:
        checkpoint = _validate_local_reference_path(checkpoint_path)
    except ValueError as exc:
        return _compare_response(
            action="compare_checkpoint",
            checkpoint_path=checkpoint_path,
            checkpoint_label=checkpoint_label,
            goal=goal_override,
            target_object=target_object,
            target_view=target_view,
            reference_ids=[],
            reference_labels=[],
            error=str(exc),
        )

    return await _run_checkpoint_compare(
        ctx,
        checkpoint=checkpoint,
        checkpoint_label=checkpoint_label,
        target_object=target_object,
        target_view=target_view,
        goal_override=goal_override,
        prompt_hint=prompt_hint,
        response_action="compare_checkpoint",
    )


async def reference_compare_current_view(
    ctx: Context,
    checkpoint_label: str | None = None,
    target_object: str | None = None,
    target_view: str | None = None,
    goal_override: str | None = None,
    prompt_hint: str | None = None,
    width: int = 1280,
    height: int = 960,
    shading: str = "SOLID",
    camera_name: str | None = None,
    focus_target: str | None = None,
    view_name: str | None = None,
    orbit_horizontal: float = 0.0,
    orbit_vertical: float = 0.0,
    zoom_factor: float | None = None,
    persist_view: bool = False,
) -> ReferenceCompareCheckpointResponseContract:
    """Capture one current viewport/camera checkpoint and compare it against attached references."""

    return await _run_current_view_compare_impl(
        ctx,
        checkpoint_label=checkpoint_label,
        target_object=target_object,
        target_view=target_view,
        goal_override=goal_override,
        prompt_hint=prompt_hint,
        width=width,
        height=height,
        shading=shading,
        camera_name=camera_name,
        focus_target=focus_target,
        view_name=view_name,
        orbit_horizontal=orbit_horizontal,
        orbit_vertical=orbit_vertical,
        zoom_factor=zoom_factor,
        persist_view=persist_view,
        build_compare_response=_compare_response,
        get_session_capability_state_async=get_session_capability_state_async,
        get_scene_handler=get_scene_handler,
        get_viewport_output_paths=get_viewport_output_paths,
        build_view_diagnostics_hints=_build_view_diagnostics_hints,
        run_checkpoint_compare=_run_checkpoint_compare,
        now=lambda: datetime.now(),
        new_uuid=lambda: uuid4(),
    )


async def reference_compare_stage_checkpoint(
    ctx: Context,
    target_object: str | None = None,
    target_objects: list[str] | None = None,
    collection_name: str | None = None,
    checkpoint_label: str | None = None,
    target_view: str | None = None,
    goal_override: str | None = None,
    prompt_hint: str | None = None,
    preset_profile: CapturePresetProfile = "compact",
) -> ReferenceCompareStageCheckpointResponseContract:
    """Capture deterministic stage views and run packeted reference compare.

    The public tool name stays stable while the server may split the compare into
    bounded view/scope packets. Rich delivery, multi-packet synthesis,
    model-aware budget pressure, and packet uncertainty can expose additive
    top-level compare_diagnostics with packet ids, pass status, support evidence,
    conflict notes, and budget_control details.
    """

    checkpoint_target = _safe_checkpoint_token(collection_name or target_object or "scene")
    checkpoint_id = f"stage_checkpoint_{checkpoint_target}_{uuid4().hex[:8]}"
    return await _run_stage_checkpoint_compare(
        ctx,
        checkpoint_id=checkpoint_id,
        checkpoint_label=checkpoint_label,
        target_object=target_object,
        target_objects=target_objects,
        collection_name=collection_name,
        target_view=target_view,
        preset_profile=preset_profile,
        goal_override=goal_override,
        prompt_hint=prompt_hint,
        emit_compact_detail=_REFERENCE_COMPARE_EMIT_COMPACT_DETAIL.get(),
    )


async def reference_iterate_stage_checkpoint(
    ctx: Context,
    target_object: str | None = None,
    target_objects: list[str] | None = None,
    collection_name: str | None = None,
    checkpoint_label: str | None = None,
    target_view: str | None = None,
    goal_override: str | None = None,
    prompt_hint: str | None = None,
    preset_profile: CapturePresetProfile = "compact",
) -> ReferenceIterateStageCheckpointResponseContract:
    """Run one session-aware packeted reference-compare iteration.

    Returns loop_disposition and compact reference_orchestrator_feedback for the
    next safe step. Top-level compare_diagnostics remains the public access path
    for rich delivery, multi-packet synthesis, model-budget pressure, or packet
    uncertainty even when the nested compact compare_result is slimmed.
    """

    token = _REFERENCE_COMPARE_EMIT_COMPACT_DETAIL.set(True)
    try:
        compare_result = await reference_compare_stage_checkpoint(
            ctx,
            target_object=target_object,
            target_objects=target_objects,
            collection_name=collection_name,
            checkpoint_label=checkpoint_label,
            target_view=target_view,
            goal_override=goal_override,
            prompt_hint=prompt_hint,
            preset_profile=preset_profile,
        )
    finally:
        _REFERENCE_COMPARE_EMIT_COMPACT_DETAIL.reset(token)
    session = await get_session_capability_state_async(ctx)
    hold_in_build = _should_hold_guided_build_loop_in_build(session.guided_flow_state)
    readiness = compare_result.guided_reference_readiness
    goal = compare_result.goal
    correction_focus = _resolve_actionable_focus(compare_result)
    if not correction_focus:
        correction_focus = _resolve_gate_blocker_focus(compare_result)
    action_hints = list(compare_result.action_hints or [])
    gate_blockers_present = bool(compare_result.completion_blockers)
    refinement_build_continue = _should_continue_refinement_build(
        session.guided_flow_state,
        list(compare_result.completion_blockers or []),
    )
    continue_recommended = bool(correction_focus or action_hints or gate_blockers_present)
    inspect_from_truth_signal = _should_inspect_from_truth_signal(compare_result.correction_candidates)
    inspect_from_gate_blockers = gate_blockers_present and not refinement_build_continue
    loop_disposition: Literal["continue_build", "inspect_validate", "stop"] = (
        "inspect_validate"
        if inspect_from_truth_signal or inspect_from_gate_blockers
        else ("continue_build" if continue_recommended else "stop")
    )
    stop_reason = (
        None if continue_recommended else "No actionable correction guidance was returned for this checkpoint."
    )

    if compare_result.error or goal is None:
        truth_only_handoff = bool(goal is not None and correction_focus and inspect_from_truth_signal)
        recoverable_setup_error = (
            goal is not None and not truth_only_handoff and _is_recoverable_stage_compare_setup_error(compare_result)
        )
        if recoverable_setup_error or goal is None:
            advanced_state = await get_session_capability_state_async(ctx)
        else:
            advanced_state = await advance_guided_flow_from_iteration_async(
                ctx,
                loop_disposition="inspect_validate" if truth_only_handoff else "stop",
            )
            await apply_visibility_for_session_state(ctx, advanced_state)
        error_loop_disposition: Literal["continue_build", "inspect_validate", "stop"] = (
            "continue_build" if recoverable_setup_error else ("inspect_validate" if truth_only_handoff else "stop")
        )
        error_continue_recommended = error_loop_disposition != "stop"
        response = _iterate_stage_response(
            session_id=compare_result.session_id,
            transport=compare_result.transport,
            goal=goal,
            guided_flow_state=advanced_state.guided_flow_state,
            active_gate_plan=advanced_state.gate_plan,
            target_object=target_object,
            target_objects=list(target_objects or []),
            collection_name=collection_name,
            target_view=target_view,
            checkpoint_id=compare_result.checkpoint_id,
            checkpoint_label=checkpoint_label,
            iteration_index=1,
            loop_disposition=error_loop_disposition,
            continue_recommended=error_continue_recommended,
            prior_checkpoint_id=None,
            prior_correction_focus=[],
            correction_focus=correction_focus,
            repeated_correction_focus=[],
            stagnation_count=0,
            compare_result=compare_result,
            guided_reference_readiness=readiness,
            reference_strategy_state=advanced_state.reference_strategy_state,
            correction_candidates=compare_result.correction_candidates,
            budget_control=compare_result.budget_control,
            refinement_route=compare_result.refinement_route,
            refinement_handoff=compare_result.refinement_handoff,
            stop_reason=compare_result.error or stop_reason,
            message=(
                "Vision compare did not complete successfully, but deterministic truth findings are available. "
                "Stop free-form modeling and switch to inspect/measure/assert before another large change."
                if truth_only_handoff
                else (
                    "Stage iteration setup is incomplete; fix the referenced precondition and rerun the same checkpoint."
                    if recoverable_setup_error
                    else "Stage iteration did not complete successfully."
                )
            ),
            error=compare_result.error,
        )
        emit_debug_log(
            "reference",
            logger,
            "stage_iterate_finish checkpoint_id=%s loop_disposition=%s continue_recommended=%s error=%s",
            compare_result.checkpoint_id,
            error_loop_disposition,
            error_continue_recommended,
            compare_result.error,
            level=logging.WARNING if compare_result.error else logging.INFO,
        )
        return response

    prior_state = await get_session_value_async(ctx, _REFERENCE_CORRECTION_LOOP_STATE_KEY, None)
    if not isinstance(prior_state, dict):
        prior_state = None

    same_loop = (
        prior_state is not None
        and prior_state.get("goal") == goal
        and prior_state.get("target_object") == target_object
        and list(prior_state.get("target_objects") or []) == list(compare_result.target_objects or [])
        and prior_state.get("collection_name") == collection_name
        and prior_state.get("target_view") == target_view
        and prior_state.get("preset_profile") == preset_profile
    )
    prior_checkpoint_id = (
        str(prior_state.get("last_checkpoint_id")) if same_loop and prior_state.get("last_checkpoint_id") else None
    )
    prior_correction_focus = list(prior_state.get("last_correction_focus") or []) if same_loop else []
    iteration_index = int(prior_state.get("iteration_index") or 0) + 1 if same_loop else 1
    repeated_correction_focus = _repeated_focus(correction_focus, prior_correction_focus)
    prior_stagnation_count = int(prior_state.get("stagnation_count") or 0) if same_loop else 0
    stagnation_count = prior_stagnation_count + 1 if repeated_correction_focus and correction_focus else 0

    if continue_recommended and stagnation_count >= _REFERENCE_CORRECTION_STAGNATION_THRESHOLD:
        loop_disposition = "inspect_validate"

    if hold_in_build and loop_disposition != "continue_build":
        loop_disposition = "continue_build"
        stop_reason = None

    await set_session_value_async(
        ctx,
        _REFERENCE_CORRECTION_LOOP_STATE_KEY,
        {
            "goal": goal,
            "target_object": target_object,
            "target_objects": list(compare_result.target_objects or []),
            "collection_name": collection_name,
            "target_view": target_view,
            "preset_profile": preset_profile,
            "last_checkpoint_id": compare_result.checkpoint_id,
            "last_checkpoint_label": checkpoint_label,
            "last_correction_focus": correction_focus,
            "last_focus_pairs": list(
                compare_result.truth_followup.focus_pairs if compare_result.truth_followup else []
            ),
            "iteration_index": iteration_index,
            "stagnation_count": stagnation_count,
        },
    )

    if loop_disposition == "inspect_validate":
        if inspect_from_truth_signal:
            message = (
                "Deterministic truth findings remain high-priority. "
                "Stop free-form modeling and switch to inspect/measure/assert now."
            )
        elif inspect_from_gate_blockers:
            message = (
                "Quality gate blockers remain unresolved. "
                "Stop free-form modeling and switch to inspect/measure/assert or bounded repair tools now."
            )
        else:
            message = (
                "Repeated correction focus persists across stage iterations. "
                "Stop free-form modeling and switch to inspect/measure/assert now."
            )
    elif loop_disposition == "continue_build":
        if hold_in_build:
            message = (
                "Guided governor is holding the session in the current build stage until the required role/workset "
                "slice is complete. Continue the bounded build loop on the active workset before escalating to "
                "inspect/measure/assert."
            )
        elif refinement_build_continue:
            message = (
                "Refinement-stage profile blockers remain active. Continue the bounded mesh/profile lane on the "
                "current workset before escalating to inspect/measure/assert."
            )
        elif correction_focus:
            message = "Continue the guided build loop using correction_focus first."
        else:
            message = "Continue the guided build loop using typed action_hints from silhouette analysis."
    else:
        message = "No further correction loop action is recommended for this checkpoint."

    advanced_state = await advance_guided_flow_from_iteration_async(
        ctx,
        loop_disposition=loop_disposition,
    )
    await apply_visibility_for_session_state(ctx, advanced_state)

    response = _iterate_stage_response(
        session_id=compare_result.session_id,
        transport=compare_result.transport,
        goal=goal,
        guided_flow_state=advanced_state.guided_flow_state,
        active_gate_plan=advanced_state.gate_plan,
        target_object=target_object,
        target_objects=list(compare_result.target_objects or []),
        collection_name=collection_name,
        target_view=target_view,
        checkpoint_id=compare_result.checkpoint_id,
        checkpoint_label=checkpoint_label,
        iteration_index=iteration_index,
        loop_disposition=loop_disposition,
        continue_recommended=continue_recommended,
        prior_checkpoint_id=prior_checkpoint_id,
        prior_correction_focus=prior_correction_focus,
        correction_focus=correction_focus,
        repeated_correction_focus=repeated_correction_focus,
        stagnation_count=stagnation_count,
        compare_result=compare_result,
        guided_reference_readiness=readiness,
        reference_strategy_state=advanced_state.reference_strategy_state,
        correction_candidates=compare_result.correction_candidates,
        budget_control=compare_result.budget_control,
        refinement_route=compare_result.refinement_route,
        refinement_handoff=compare_result.refinement_handoff,
        stop_reason=stop_reason,
        message=message,
    )
    emit_debug_log(
        "reference",
        logger,
        "stage_iterate_finish checkpoint_id=%s loop_disposition=%s continue_recommended=%s correction_focus=%d blockers=%d stagnation_count=%d",
        compare_result.checkpoint_id,
        loop_disposition,
        continue_recommended,
        len(correction_focus),
        len(compare_result.completion_blockers or []),
        stagnation_count,
    )
    return response
