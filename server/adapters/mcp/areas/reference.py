# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Goal-scoped reference image intake and lifecycle tools."""

from __future__ import annotations

import base64
import mimetypes
import re
import shutil
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal, Mapping, cast
from uuid import uuid4

from fastmcp import Context

from server.adapters.mcp.context_utils import ctx_info, ctx_session_id, ctx_transport_type
from server.adapters.mcp.contracts.guided_flow import GuidedFlowStateContract
from server.adapters.mcp.contracts.quality_gates import (
    GatePlanContract,
    GateProposalContract,
    refresh_gate_plan_status,
    without_proposal_source,
)
from server.adapters.mcp.contracts.reference import (
    GuidedReferenceReadinessContract,
    ReferenceActionHintContract,
    ReferenceCompareCheckpointResponseContract,
    ReferenceCompareStageCheckpointResponseContract,
    ReferenceCorrectionCandidateContract,
    ReferenceCorrectionTruthEvidenceContract,
    ReferenceCorrectionVisionEvidenceContract,
    ReferenceHybridBudgetControlContract,
    ReferenceImageRecordContract,
    ReferenceImagesResponseContract,
    ReferenceIterateStageCheckpointResponseContract,
    ReferencePartSegmentationContract,
    ReferencePlannerBlockerContract,
    ReferencePlannerEvidenceSourceContract,
    ReferencePlannerSourceLiteral,
    ReferencePlannerTargetScopeContract,
    ReferenceRefinementHandoffContract,
    ReferenceRefinementRouteContract,
    ReferenceRefinementToolCandidateContract,
    ReferenceRepairPlannerDetailContract,
    ReferenceRepairPlannerSummaryContract,
    ReferenceSilhouetteAnalysisContract,
    ReferenceUnderstandingSummaryContract,
    ReferenceViewDiagnosticsHintContract,
)
from server.adapters.mcp.contracts.scene import (
    SceneAssembledTargetScopeContract,
    SceneAssertionPayloadContract,
    SceneAttachmentSemanticsContract,
    SceneCorrectionTruthBundleContract,
    SceneCorrectionTruthPairContract,
    SceneCorrectionTruthSummaryContract,
    SceneRelationKindLiteral,
    SceneRelationVerdictLiteral,
    SceneRepairMacroCandidateContract,
    SceneSupportSemanticsContract,
    SceneSymmetrySemanticsContract,
    SceneTruthFollowupContract,
    SceneTruthFollowupItemContract,
)
from server.adapters.mcp.contracts.vision import VisionCaptureImageContract
from server.adapters.mcp.guided_contract import canonicalize_reference_images_arguments
from server.adapters.mcp.sampling.result_types import to_vision_assistant_contract
from server.adapters.mcp.session_capabilities import (
    GuidedReferenceReadinessState,
    SessionCapabilityState,
    advance_guided_flow_from_iteration_async,
    apply_visibility_for_session_state,
    build_guided_reference_readiness,
    build_guided_reference_readiness_payload,
    get_session_capability_state_async,
    ingest_quality_gate_proposal_async,
    replace_session_pending_reference_images_async,
    replace_session_reference_images_async,
    session_has_ready_guided_reference_goal,
    set_session_capability_state_async,
)
from server.adapters.mcp.session_state import get_session_value_async, set_session_value_async
from server.adapters.mcp.transforms.quality_gate_verifier import verify_gate_plan_with_relation_graph
from server.adapters.mcp.visibility.tags import get_capability_tags
from server.adapters.mcp.vision import (
    CapturePresetProfile,
    CapturePresetSpec,
    VisionBackendUnavailableError,
    VisionImageInput,
    VisionRequest,
    build_reference_capture_images,
    build_vision_request_from_stage_captures,
    capture_stage_images,
    resolve_capture_preset_specs,
    run_vision_assist,
    select_reference_records_for_target,
)
from server.adapters.mcp.vision.runner import VISION_ASSIST_POLICY
from server.adapters.mcp.vision.silhouette import build_silhouette_analysis
from server.application.services.spatial_graph import get_spatial_graph_service
from server.infrastructure.di import get_collection_handler, get_scene_handler, get_vision_backend_resolver
from server.infrastructure.tmp_paths import get_reference_image_storage_path, get_viewport_output_paths

REFERENCE_PUBLIC_TOOL_NAMES = (
    "reference_images",
    "reference_compare_checkpoint",
    "reference_compare_current_view",
    "reference_compare_stage_checkpoint",
    "reference_iterate_stage_checkpoint",
)
_ALLOWED_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
_REFERENCE_CORRECTION_LOOP_STATE_KEY = "reference_correction_loop"
_REFERENCE_CORRECTION_STAGNATION_THRESHOLD = 2
_ANCHOR_ROLE_HINTS: tuple[tuple[str, int], ...] = (
    ("body", 50),
    ("torso", 45),
    ("trunk", 45),
    ("head", 40),
    ("skull", 35),
    ("core", 30),
    ("root", 25),
    ("base", 20),
)
_ACCESSORY_ROLE_HINTS: tuple[str, ...] = (
    "ear",
    "eye",
    "nose",
    "snout",
    "paw",
    "foot",
    "tail",
    "horn",
    "antler",
    "whisker",
)
_HEAD_ROLE_HINTS: tuple[str, ...] = ("head", "skull", "face")
_BODY_ROLE_HINTS: tuple[str, ...] = ("body", "torso", "trunk", "chest", "abdomen", "pelvis", "hip")
_SNOUT_ROLE_HINTS: tuple[str, ...] = ("snout", "muzzle")
_NOSE_ROLE_HINTS: tuple[str, ...] = ("nose", "nostril")
_EYE_ROLE_HINTS: tuple[str, ...] = ("eye",)
_FACE_ATTACHMENT_HINTS: tuple[str, ...] = ("ear", "eye", "nose", "snout", "whisker")
_TAIL_ROLE_HINTS: tuple[str, ...] = ("tail",)
_ROOF_ROLE_HINTS: tuple[str, ...] = ("roof",)
_BUILDING_MASS_HINTS: tuple[str, ...] = ("wall", "facade", "volume", "shell")
_LIMB_ROLE_HINTS: tuple[str, ...] = (
    "limb",
    "leg",
    "arm",
    "paw",
    "foot",
    "hand",
    "hoof",
    "thigh",
    "shin",
    "calf",
    "foreleg",
    "hindleg",
    "forelimb",
    "hindlimb",
    "forearm",
    "lowerarm",
    "upperarm",
    "lowerleg",
    "upperleg",
)
_DISTAL_LIMB_HINTS: tuple[str, ...] = ("paw", "foot", "hand", "hoof", "shin", "calf", "forearm", "lowerarm", "lowerleg")
_PROXIMAL_LIMB_HINTS: tuple[str, ...] = ("upperarm", "upperleg", "thigh", "arm", "leg", "forelimb", "hindlimb")
_LOW_POLY_HINTS: tuple[str, ...] = ("low poly", "low-poly", "blockout")
_HARD_SURFACE_HINTS: tuple[str, ...] = (
    "housing",
    "panel",
    "button",
    "electronics",
    "electronic",
    "device",
    "pcb",
    "circuit",
    "connector",
    "wall",
    "roof",
    "window",
    "door",
    "building",
    "architecture",
    "tower",
)
_GARMENT_HINTS: tuple[str, ...] = (
    "shirt",
    "sleeve",
    "hood",
    "jacket",
    "coat",
    "dress",
    "skirt",
    "pants",
    "trousers",
    "fabric",
    "cloth",
    "cape",
)
_ANATOMY_HINTS: tuple[str, ...] = (
    "organ",
    "heart",
    "lung",
    "liver",
    "kidney",
    "artery",
    "vein",
    "tumor",
    "anatomy",
    "biological",
)
_ORGANIC_HINTS: tuple[str, ...] = (
    "animal",
    "creature",
    "character",
    "squirrel",
    "rabbit",
    "owl",
    "fox",
    "bird",
    "face",
    "snout",
    "ear",
    "tail",
    "limb",
    "muscle",
    "organic",
)
_SCULPT_RECOMMENDED_TOOLS: tuple[str, ...] = (
    "sculpt_deform_region",
    "sculpt_smooth_region",
    "sculpt_inflate_region",
    "sculpt_pinch_region",
    "sculpt_crease_region",
)

_CreatureRelationKind = Literal["embedded_attachment", "seated_attachment", "segment_attachment"]
_CreatureSeamKind = Literal[
    "face_head", "nose_snout", "head_body", "tail_body", "limb_body", "limb_segment", "roof_wall"
]


@dataclass(frozen=True)
class _PlannedCreatureSeam:
    part_object: str
    anchor_object: str
    relation_kind: _CreatureRelationKind
    seam_kind: _CreatureSeamKind


@dataclass(frozen=True)
class _PlannedTruthPair:
    from_object: str
    to_object: str
    seam: _PlannedCreatureSeam | None = None


def _register_existing_tool(target, tool_name: str):
    tool = globals()[tool_name]
    fn = getattr(tool, "fn", tool)
    return target.tool(fn, name=tool_name, tags=set(get_capability_tags("reference")))


def register_reference_tools(target):
    return {tool_name: _register_existing_tool(target, tool_name) for tool_name in REFERENCE_PUBLIC_TOOL_NAMES}


def _sorted_references(references: list[dict]) -> list[dict]:
    return sorted(references, key=lambda item: str(item.get("added_at") or ""))


def _merge_visible_references(*reference_groups: list[dict]) -> list[dict]:
    """Return one stable visible view across active and staged reference stores."""

    merged: list[dict] = []
    seen_reference_ids: set[str] = set()

    for group in reference_groups:
        for item in group:
            reference_id = item.get("reference_id")
            if isinstance(reference_id, str) and reference_id:
                if reference_id in seen_reference_ids:
                    continue
                seen_reference_ids.add(reference_id)
            merged.append(item)

    return merged


def _delete_reference_files(references: list[dict]) -> None:
    """Best-effort cleanup for stored reference files without double-unlinking."""

    deleted_paths: set[str] = set()
    for item in references:
        stored_path = item.get("stored_path")
        if not isinstance(stored_path, str) or stored_path in deleted_paths:
            continue
        deleted_paths.add(stored_path)
        try:
            Path(stored_path).unlink(missing_ok=True)
        except Exception:
            pass


def _as_response(
    *,
    action: Literal["attach", "list", "remove", "clear"],
    goal: str | None,
    references: list[dict],
    removed_reference_id: str | None = None,
    message: str | None = None,
    error: str | None = None,
) -> ReferenceImagesResponseContract:
    return ReferenceImagesResponseContract(
        action=action,
        goal=goal,
        reference_count=len(references),
        references=[ReferenceImageRecordContract.model_validate(item) for item in references],
        removed_reference_id=removed_reference_id,
        message=message,
        error=error,
    )


def _validate_local_reference_path(source_path: str) -> Path:
    path = Path(source_path).expanduser().resolve()
    if not path.exists() or not path.is_file():
        raise ValueError(f"Reference image path does not exist: {source_path}")
    if path.suffix.lower() not in _ALLOWED_IMAGE_SUFFIXES:
        raise ValueError("Reference image must be one of: .png, .jpg, .jpeg, .webp")
    return path


def _copy_reference_image(source_path: Path) -> tuple[str, str]:
    filename = f"ref_{uuid4().hex[:10]}{source_path.suffix.lower()}"
    internal_path, host_visible_path = get_reference_image_storage_path(filename)
    shutil.copy2(source_path, internal_path)
    return str(internal_path), host_visible_path


def _safe_checkpoint_token(value: str | None) -> str:
    """Return a filesystem-safe token for checkpoint/bundle ids."""

    raw = str(value or "scene").strip()
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "_", raw).strip("._-")
    return normalized or "scene"


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
    return ReferenceCompareCheckpointResponseContract(
        action=action,
        goal=goal,
        target_object=target_object,
        target_view=target_view,
        checkpoint_path=checkpoint_path,
        checkpoint_label=checkpoint_label,
        reference_count=len(reference_ids),
        reference_ids=reference_ids,
        reference_labels=reference_labels,
        view_diagnostics_hints=view_diagnostics_hints,
        vision_assistant=vision_assistant,
        message=message,
        error=error,
    )


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
    vision_assistant=None,
    truth_bundle: SceneCorrectionTruthBundleContract | None = None,
    truth_followup: SceneTruthFollowupContract | None = None,
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
    message: str | None = None,
    error: str | None = None,
) -> ReferenceCompareStageCheckpointResponseContract:
    emitted_captures = list(captures) if include_captures else []
    gate_fields = _gate_checkpoint_fields(active_gate_plan)
    return ReferenceCompareStageCheckpointResponseContract(
        action="compare_stage_checkpoint",
        session_id=session_id,
        transport=transport,
        goal=goal,
        guided_flow_state=(
            GuidedFlowStateContract.model_validate(guided_flow_state) if guided_flow_state is not None else None
        ),
        active_gate_plan=GatePlanContract.model_validate(active_gate_plan) if active_gate_plan is not None else None,
        gate_statuses=gate_fields["gate_statuses"],
        completion_blockers=gate_fields["completion_blockers"],
        next_gate_actions=gate_fields["next_gate_actions"],
        recommended_bounded_tools=gate_fields["recommended_bounded_tools"],
        guided_reference_readiness=guided_reference_readiness,
        reference_understanding_summary=reference_understanding_summary,
        reference_understanding_gate_ids=list(reference_understanding_gate_ids or []),
        target_object=target_object,
        target_objects=target_objects,
        collection_name=collection_name,
        assembled_target_scope=assembled_target_scope,
        truth_bundle=truth_bundle,
        truth_followup=truth_followup,
        correction_candidates=list(correction_candidates or []),
        budget_control=budget_control,
        refinement_route=refinement_route,
        refinement_handoff=refinement_handoff,
        planner_summary=planner_summary,
        planner_detail=planner_detail,
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
    return ReferenceIterateStageCheckpointResponseContract(
        action="iterate_stage_checkpoint",
        session_id=session_id,
        transport=transport,
        goal=goal,
        guided_flow_state=(
            GuidedFlowStateContract.model_validate(guided_flow_state) if guided_flow_state is not None else None
        ),
        active_gate_plan=GatePlanContract.model_validate(resolved_gate_plan)
        if resolved_gate_plan is not None
        else None,
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
        target_object=target_object,
        target_objects=target_objects,
        collection_name=collection_name,
        assembled_target_scope=compare_result.assembled_target_scope,
        truth_bundle=compare_result.truth_bundle,
        truth_followup=compare_result.truth_followup,
        correction_candidates=list(correction_candidates or compare_result.correction_candidates or []),
        budget_control=budget_control or compare_result.budget_control,
        refinement_route=refinement_route or compare_result.refinement_route,
        refinement_handoff=refinement_handoff or compare_result.refinement_handoff,
        planner_summary=planner_summary or compare_result.planner_summary,
        planner_detail=planner_detail or compare_result.planner_detail,
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


def _normalized_focus_key(value: str) -> str:
    return " ".join(value.strip().lower().split())


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


def _resolve_actionable_focus(compare_result: ReferenceCompareStageCheckpointResponseContract) -> list[str]:
    candidate_summaries = list(compare_result.correction_candidates or [])
    if candidate_summaries:
        deduped_candidates: list[str] = []
        seen_candidates: set[str] = set()
        for candidate in candidate_summaries:
            normalized = _normalized_focus_key(candidate.summary)
            if not normalized or normalized in seen_candidates:
                continue
            seen_candidates.add(normalized)
            deduped_candidates.append(candidate.summary)
        if deduped_candidates:
            return deduped_candidates[:3]

    vision_result = compare_result.vision_assistant.result if compare_result.vision_assistant else None
    if vision_result is None:
        return []

    ordered = list(vision_result.correction_focus or [])
    if not ordered:
        ordered.extend(vision_result.shape_mismatches or [])
        ordered.extend(vision_result.proportion_mismatches or [])
        ordered.extend(vision_result.next_corrections or [])

    deduped: list[str] = []
    seen: set[str] = set()
    for item in ordered:
        normalized = _normalized_focus_key(item)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(item)
    return deduped[:3]


def _resolve_gate_blocker_focus(compare_result: ReferenceCompareStageCheckpointResponseContract) -> list[str]:
    blockers = list(compare_result.completion_blockers or [])
    if not blockers:
        return []

    deduped: list[str] = []
    seen: set[str] = set()
    for blocker in blockers:
        item = (blocker.message or blocker.label or blocker.target_label or blocker.gate_id).strip()
        normalized = _normalized_focus_key(item)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(item)
    return deduped[:3]


def _should_inspect_from_truth_signal(
    correction_candidates: list[ReferenceCorrectionCandidateContract],
) -> bool:
    if not correction_candidates:
        return False

    for candidate in correction_candidates:
        if candidate.priority != "high":
            continue
        truth_evidence = candidate.truth_evidence
        if truth_evidence is None:
            continue
        if any(
            kind in {"contact_failure", "overlap", "attachment", "support", "symmetry", "measurement_error"}
            for kind in truth_evidence.item_kinds
        ):
            return True
    return False


def _contains_any(text: str, hints: tuple[str, ...]) -> bool:
    normalized = text.lower()
    return any(hint in normalized for hint in hints)


def _refinement_context_text(compare_result: ReferenceCompareStageCheckpointResponseContract) -> str:
    parts = [
        str(compare_result.goal or ""),
        str(compare_result.target_object or ""),
        str(compare_result.collection_name or ""),
        *list(compare_result.target_objects or []),
    ]
    return " | ".join(part for part in parts if part)


def _classify_refinement_domain(
    compare_result: ReferenceCompareStageCheckpointResponseContract,
) -> Literal["assembly", "hard_surface", "soft_surface", "organic_form", "garment", "anatomy", "generic_form"]:
    context_text = _refinement_context_text(compare_result)
    truth_followup = compare_result.truth_followup
    if truth_followup is not None and (truth_followup.focus_pairs or truth_followup.macro_candidates):
        return "assembly"
    if _contains_any(context_text, _GARMENT_HINTS):
        return "garment"
    if _contains_any(context_text, _ANATOMY_HINTS):
        return "anatomy"
    if _contains_any(context_text, _HARD_SURFACE_HINTS):
        return "hard_surface"
    if _contains_any(context_text, _ORGANIC_HINTS):
        return "organic_form"
    return "generic_form"


_STRUCTURAL_RELATION_BLOCKER_KINDS: frozenset[str] = frozenset(
    {"contact_failure", "gap", "overlap", "attachment", "support", "symmetry", "measurement_error"}
)
_PROPORTION_BLOCKING_HINT_TYPES: frozenset[str] = frozenset({"rebalance_proportion"})


def _planner_target_scope(
    compare_result: ReferenceCompareStageCheckpointResponseContract,
    *,
    local_region_hint: str | None = None,
) -> ReferencePlannerTargetScopeContract | None:
    assembled_scope = compare_result.assembled_target_scope
    if assembled_scope is not None:
        return ReferencePlannerTargetScopeContract(
            scope_kind=assembled_scope.scope_kind,
            target_object=compare_result.target_object or assembled_scope.primary_target,
            target_objects=list(assembled_scope.object_names or []),
            collection_name=assembled_scope.collection_name,
            local_region_hint=local_region_hint,
        )

    target_objects = _dedupe_names(
        [
            *(compare_result.target_objects or []),
            *([compare_result.target_object] if compare_result.target_object else []),
        ]
    )
    if target_objects or compare_result.collection_name:
        scope_kind: Literal["single_object", "object_set", "collection", "scene", "unknown"]
        if compare_result.collection_name:
            scope_kind = "collection"
        elif len(target_objects) == 1:
            scope_kind = "single_object"
        else:
            scope_kind = "object_set"
        return ReferencePlannerTargetScopeContract(
            scope_kind=scope_kind,
            target_object=compare_result.target_object or (target_objects[0] if len(target_objects) == 1 else None),
            target_objects=target_objects,
            collection_name=compare_result.collection_name,
            local_region_hint=local_region_hint,
        )

    return None


def _candidate_ids_with_structural_relation_blockers(
    candidates: list[ReferenceCorrectionCandidateContract],
) -> list[str]:
    candidate_ids: list[str] = []
    for candidate in candidates:
        truth_evidence = candidate.truth_evidence
        if truth_evidence is None:
            continue
        if any(kind in _STRUCTURAL_RELATION_BLOCKER_KINDS for kind in truth_evidence.item_kinds):
            candidate_ids.append(candidate.candidate_id)
    return candidate_ids


def _relation_planner_blockers(
    candidates: list[ReferenceCorrectionCandidateContract],
) -> list[ReferencePlannerBlockerContract]:
    candidate_ids = _candidate_ids_with_structural_relation_blockers(candidates)
    if not candidate_ids:
        return []
    return [
        ReferencePlannerBlockerContract(
            blocker_id="relation_structural_failure",
            category="relation",
            severity="blocking",
            reason=(
                "Unresolved attachment/contact/support/symmetry/gap/overlap truth evidence still dominates, "
                "so sculpt-region handoff is blocked until the structural relation is repaired or re-inspected."
            ),
            candidate_ids=candidate_ids,
            recommended_tool="scene_relation_graph",
        )
    ]


def _view_planner_blockers(
    compare_result: ReferenceCompareStageCheckpointResponseContract,
    *,
    require_view_evidence: bool,
) -> list[ReferencePlannerBlockerContract]:
    hints = compare_result.view_diagnostics_hints
    if hints is None:
        if not require_view_evidence:
            return []
        target_scope = _planner_target_scope(compare_result)
        target_object = (
            target_scope.target_object
            if target_scope is not None and target_scope.target_object
            else compare_result.target_object
        )
        arguments_hint: dict[str, object] = {}
        if target_object:
            arguments_hint["target_object"] = target_object
        return [
            ReferencePlannerBlockerContract(
                blocker_id="view_diagnostics_required",
                category="view",
                severity="blocking",
                reason=(
                    "Staged compare did not carry typed view-diagnostics evidence. Run scene_view_diagnostics(...) "
                    "for the intended local target before treating sculpt-region handoff as ready."
                ),
                recommended_tool="scene_view_diagnostics",
                arguments_hint=arguments_hint or None,
            )
        ]

    blockers: list[ReferencePlannerBlockerContract] = []
    for index, hint in enumerate(hints, start=1):
        blockers.append(
            ReferencePlannerBlockerContract(
                blocker_id=f"view_{hint.trigger}_{index}",
                category="view",
                severity="blocking",
                reason=hint.reason,
                recommended_tool=hint.recommended_tool,
                arguments_hint=hint.arguments_hint,
            )
        )
    return blockers


def _proportion_planner_blockers(
    compare_result: ReferenceCompareStageCheckpointResponseContract,
    *,
    low_poly_intent: bool,
) -> list[ReferencePlannerBlockerContract]:
    blockers: list[ReferencePlannerBlockerContract] = []
    proportion_hint_ids = [
        hint.hint_id
        for hint in list(compare_result.action_hints or [])
        if hint.hint_type in _PROPORTION_BLOCKING_HINT_TYPES
    ]
    if proportion_hint_ids:
        blockers.append(
            ReferencePlannerBlockerContract(
                blocker_id="proportion_nonlocal_drift",
                category="proportion",
                severity="blocking",
                reason=(
                    "Deterministic silhouette/proportion metrics still indicate a non-local proportion issue, "
                    "so macro or mesh/modeling correction is safer than local sculpt."
                ),
                candidate_ids=proportion_hint_ids,
                recommended_tool="scene_assert_proportion",
            )
        )
    if low_poly_intent:
        blockers.append(
            ReferencePlannerBlockerContract(
                blocker_id="low_poly_blockout_not_local_sculpt",
                category="proportion",
                severity="warning",
                reason=(
                    "The active goal is a low-poly/blockout refinement. Preserve plane and silhouette control with "
                    "mesh/modeling edits before using local sculpt smoothing."
                ),
            )
        )
    return blockers


def _local_form_reason(compare_result: ReferenceCompareStageCheckpointResponseContract) -> str | None:
    for candidate in list(compare_result.correction_candidates or []):
        vision_evidence = candidate.vision_evidence
        if vision_evidence is None:
            continue
        for item in [
            *list(vision_evidence.correction_focus or []),
            *list(vision_evidence.shape_mismatches or []),
            *list(vision_evidence.next_corrections or []),
        ]:
            text = str(item or "").strip()
            if text:
                return text
    if compare_result.silhouette_analysis is not None and compare_result.silhouette_analysis.status == "available":
        return "Silhouette metrics point to bounded local-form refinement."
    return None


def _planner_source_signals(
    *,
    candidates: list[ReferenceCorrectionCandidateContract],
    compare_result: ReferenceCompareStageCheckpointResponseContract,
) -> list[ReferencePlannerSourceLiteral]:
    signals: list[ReferencePlannerSourceLiteral] = ["scope", "naming"]
    if any(candidate.truth_evidence is not None for candidate in candidates):
        signals.extend(["truth", "relation"])
    if any(
        candidate.truth_evidence is not None and bool(candidate.truth_evidence.macro_candidates)
        for candidate in candidates
    ):
        signals.append("macro")
    if any(candidate.vision_evidence is not None for candidate in candidates):
        signals.append("vision")
    if compare_result.view_diagnostics_hints is not None:
        signals.append("view")
    if compare_result.silhouette_analysis is not None:
        signals.append("silhouette")
    if compare_result.budget_control is not None:
        signals.append("budget")
    return list(dict.fromkeys(signals))


def _planner_provenance(
    compare_result: ReferenceCompareStageCheckpointResponseContract,
    *,
    candidates: list[ReferenceCorrectionCandidateContract],
    source_signals: list[ReferencePlannerSourceLiteral],
) -> list[ReferencePlannerEvidenceSourceContract]:
    candidate_ids = [candidate.candidate_id for candidate in candidates]
    provenance: list[ReferencePlannerEvidenceSourceContract] = []
    if "scope" in source_signals:
        target_scope = _planner_target_scope(compare_result)
        scope_summary = (
            f"{target_scope.scope_kind} scope with {len(target_scope.target_objects)} object(s)"
            if target_scope is not None
            else "No explicit target scope was available."
        )
        provenance.append(
            ReferencePlannerEvidenceSourceContract(
                source_id="scope",
                source_class="scope",
                summary=scope_summary,
                tool_name="scene_scope_graph",
            )
        )
    if "truth" in source_signals or "relation" in source_signals:
        provenance.append(
            ReferencePlannerEvidenceSourceContract(
                source_id="truth_followup",
                source_class="truth",
                summary="Truth follow-up and relation evidence were used before vision-only correction hints.",
                candidate_ids=[
                    candidate.candidate_id for candidate in candidates if candidate.truth_evidence is not None
                ],
                tool_name="scene_relation_graph",
            )
        )
    if "macro" in source_signals:
        provenance.append(
            ReferencePlannerEvidenceSourceContract(
                source_id="macro_candidates",
                source_class="macro",
                summary="Macro repair candidates are available for unresolved structural relations.",
                candidate_ids=[
                    candidate.candidate_id
                    for candidate in candidates
                    if candidate.truth_evidence is not None and candidate.truth_evidence.macro_candidates
                ],
            )
        )
    if "vision" in source_signals:
        provenance.append(
            ReferencePlannerEvidenceSourceContract(
                source_id="vision_candidates",
                source_class="vision",
                summary="Vision mismatch text is advisory and can prioritize local-form attention.",
                candidate_ids=[
                    candidate.candidate_id for candidate in candidates if candidate.vision_evidence is not None
                ],
            )
        )
    if "view" in source_signals:
        provenance.append(
            ReferencePlannerEvidenceSourceContract(
                source_id="view_diagnostics_hints",
                source_class="view",
                summary="View diagnostics hints constrain whether a local target is visible and framed enough.",
                tool_name="scene_view_diagnostics",
            )
        )
    if "silhouette" in source_signals:
        provenance.append(
            ReferencePlannerEvidenceSourceContract(
                source_id="silhouette_analysis",
                source_class="silhouette",
                summary="Deterministic silhouette metrics can recommend inspection, proportion, or local-form work.",
                candidate_ids=candidate_ids,
            )
        )
    if "budget" in source_signals:
        provenance.append(
            ReferencePlannerEvidenceSourceContract(
                source_id="budget_control",
                source_class="budget",
                summary="Model-aware budget control bounded the emitted evidence and planner detail.",
            )
        )
    return provenance


def _support_tools_from_blockers(
    blockers: list[ReferencePlannerBlockerContract],
) -> list[ReferenceRefinementToolCandidateContract]:
    tools: list[ReferenceRefinementToolCandidateContract] = []
    seen: set[str] = set()
    for blocker in blockers:
        tool_name = blocker.recommended_tool
        if not tool_name or tool_name in seen:
            continue
        seen.add(tool_name)
        tools.append(
            ReferenceRefinementToolCandidateContract(
                tool_name=tool_name,
                reason=blocker.reason,
                priority="high" if blocker.severity == "blocking" else "normal",
                arguments_hint=blocker.arguments_hint,
            )
        )
    return tools


def _select_refinement_route(
    compare_result: ReferenceCompareStageCheckpointResponseContract,
) -> ReferenceRefinementRouteContract:
    candidates = list(compare_result.correction_candidates or [])
    domain = _classify_refinement_domain(compare_result)
    target_scope = _planner_target_scope(compare_result)
    if not candidates:
        return ReferenceRefinementRouteContract(
            domain_classification=domain,
            selected_family="inspect_only",
            reason="No ranked correction candidates are available for deterministic refinement routing.",
            source_signals=[],
            candidate_ids=[],
            target_scope=target_scope,
            detail_available=False,
        )

    candidate_ids = [candidate.candidate_id for candidate in candidates]
    has_macro = any(
        candidate.truth_evidence is not None and bool(candidate.truth_evidence.macro_candidates)
        for candidate in candidates
    )
    has_vision_only = any(candidate.candidate_kind == "vision_only" for candidate in candidates)
    low_poly_intent = _contains_any(_refinement_context_text(compare_result), _LOW_POLY_HINTS)
    source_signals = _planner_source_signals(candidates=candidates, compare_result=compare_result)
    relation_blockers = _relation_planner_blockers(candidates)
    proportion_blockers = _proportion_planner_blockers(compare_result, low_poly_intent=low_poly_intent)

    if relation_blockers or has_macro or domain == "assembly":
        return ReferenceRefinementRouteContract(
            domain_classification=domain,
            selected_family="macro",
            reason="Assembly-oriented truth/macro signals dominate, so bounded macro repair remains the primary refinement family.",
            source_signals=source_signals,
            candidate_ids=candidate_ids,
            target_scope=target_scope,
            blockers=relation_blockers,
            detail_available=True,
        )

    view_hint_blockers = _view_planner_blockers(compare_result, require_view_evidence=False)
    if view_hint_blockers:
        return ReferenceRefinementRouteContract(
            domain_classification=domain,
            selected_family="inspect_only",
            reason=(
                "Typed view diagnostics reported visibility or framing blockers, so inspect/view correction must "
                "happen before local-form or sculpt-region refinement."
            ),
            source_signals=source_signals,
            candidate_ids=candidate_ids,
            target_scope=target_scope,
            blockers=view_hint_blockers,
            detail_available=True,
        )

    blocking_proportion = [blocker for blocker in proportion_blockers if blocker.severity == "blocking"]
    if blocking_proportion:
        return ReferenceRefinementRouteContract(
            domain_classification=domain,
            selected_family="modeling_mesh",
            reason=(
                "Non-local proportion drift remains, so bounded modeling/mesh or macro correction is safer than "
                "a local sculpt-region handoff."
            ),
            source_signals=source_signals,
            candidate_ids=candidate_ids,
            target_scope=target_scope,
            blockers=proportion_blockers,
            detail_available=True,
        )

    if domain in {"garment", "anatomy", "organic_form"} and has_vision_only and not low_poly_intent:
        view_evidence_blockers = _view_planner_blockers(compare_result, require_view_evidence=True)
        if view_evidence_blockers:
            return ReferenceRefinementRouteContract(
                domain_classification=domain,
                selected_family="inspect_only",
                reason=(
                    "Organic/local-form evidence is present, but staged view evidence is missing or blocking; "
                    "run view diagnostics before recommending sculpt-region tools."
                ),
                source_signals=source_signals,
                candidate_ids=candidate_ids,
                target_scope=target_scope,
                blockers=view_evidence_blockers,
                detail_available=True,
            )
        return ReferenceRefinementRouteContract(
            domain_classification=domain,
            selected_family="sculpt_region",
            reason="Local soft/organic-form refinement dominates without strong assembly signals, so deterministic sculpt-region tools are the preferred family.",
            source_signals=source_signals,
            candidate_ids=candidate_ids,
            target_scope=_planner_target_scope(compare_result, local_region_hint=_local_form_reason(compare_result)),
            detail_available=True,
        )

    if domain in {"hard_surface", "generic_form", "soft_surface"} or low_poly_intent:
        return ReferenceRefinementRouteContract(
            domain_classification=domain,
            selected_family="modeling_mesh",
            reason="Current signals do not justify sculpt; bounded modeling/mesh refinement remains the safer default family.",
            source_signals=source_signals,
            candidate_ids=candidate_ids,
            target_scope=target_scope,
            blockers=proportion_blockers,
            detail_available=True,
        )

    return ReferenceRefinementRouteContract(
        domain_classification=domain,
        selected_family="modeling_mesh",
        reason="Falling back to bounded modeling/mesh refinement because no stronger deterministic family gate was met.",
        source_signals=source_signals,
        candidate_ids=candidate_ids,
        target_scope=target_scope,
        detail_available=True,
    )


def _build_refinement_handoff(
    compare_result: ReferenceCompareStageCheckpointResponseContract,
    route: ReferenceRefinementRouteContract,
) -> ReferenceRefinementHandoffContract:
    blockers = list(route.blockers or [])
    target_scope = route.target_scope or _planner_target_scope(compare_result)
    if route.selected_family != "sculpt_region":
        state: Literal["ready", "blocked", "suppressed"] = "blocked" if blockers else "suppressed"
        message = (
            "Sculpt-region handoff is blocked by the listed preconditions; follow the support tools before sculpting."
            if blockers
            else "Continue with the selected bounded refinement family; no sculpt handoff is recommended."
        )
        return ReferenceRefinementHandoffContract(
            selected_family=route.selected_family,
            state=state,
            message=message,
            target_object=target_scope.target_object if target_scope is not None else compare_result.target_object,
            target_scope=target_scope,
            local_reason=target_scope.local_region_hint if target_scope is not None else None,
            blockers=blockers,
            eligible_tool_names=list(_SCULPT_RECOMMENDED_TOOLS),
            recommended_tools=[],
        )

    target_object = target_scope.target_object if target_scope is not None else compare_result.target_object
    arguments_hint = cast(dict[str, object] | None, {"object_name": target_object} if target_object else None)
    return ReferenceRefinementHandoffContract(
        selected_family="sculpt_region",
        state="ready",
        message=(
            "A deterministic sculpt-region path is recommended for the next refinement step. "
            "Keep the scope narrow and use only bounded sculpt-region tools."
        ),
        target_object=target_object,
        target_scope=target_scope,
        local_reason=target_scope.local_region_hint if target_scope is not None else _local_form_reason(compare_result),
        blockers=[],
        eligible_tool_names=list(_SCULPT_RECOMMENDED_TOOLS),
        visibility_unlock_recommended=False,
        recommended_tools=[
            ReferenceRefinementToolCandidateContract(
                tool_name=tool_name,
                reason="Deterministic local-form refinement is a better fit than more assembly-oriented mesh/modeling edits.",
                priority=(
                    "high"
                    if tool_name in {"sculpt_deform_region", "sculpt_smooth_region", "sculpt_crease_region"}
                    else "normal"
                ),
                arguments_hint=arguments_hint,
            )
            for tool_name in _SCULPT_RECOMMENDED_TOOLS
        ],
    )


def _build_repair_planner_summary(
    compare_result: ReferenceCompareStageCheckpointResponseContract,
    *,
    route: ReferenceRefinementRouteContract,
    handoff: ReferenceRefinementHandoffContract,
) -> ReferenceRepairPlannerSummaryContract:
    candidates = list(compare_result.correction_candidates or [])
    provenance = _planner_provenance(
        compare_result,
        candidates=candidates,
        source_signals=list(route.source_signals or []),
    )
    blockers = list(route.blockers or handoff.blockers or [])
    return ReferenceRepairPlannerSummaryContract(
        selected_family=route.selected_family,
        target_scope=route.target_scope or handoff.target_scope,
        rationale=route.reason,
        provenance=provenance,
        blockers=blockers,
        detail_available=route.detail_available,
        required_support_tools=_support_tools_from_blockers(blockers),
    )


def _build_repair_planner_detail(
    compare_result: ReferenceCompareStageCheckpointResponseContract,
    *,
    summary: ReferenceRepairPlannerSummaryContract,
    route: ReferenceRefinementRouteContract,
    handoff: ReferenceRefinementHandoffContract,
    detail_trimmed: bool,
) -> ReferenceRepairPlannerDetailContract:
    notes: list[str] = []
    if detail_trimmed:
        notes.append("Planner detail reflects trimmed staged compare evidence after budget control was applied.")
    if handoff.selected_family == "sculpt_region" and handoff.visibility_unlock_recommended is False:
        notes.append("Sculpt handoff is recommendation-only and does not unlock guided sculpt visibility by itself.")
    return ReferenceRepairPlannerDetailContract(
        summary=summary,
        route=route,
        handoff=handoff,
        candidate_ids=list(route.candidate_ids or []),
        notes=notes,
        detail_trimmed=detail_trimmed,
    )


def _model_budget_bias(model_name: str | None) -> int:
    normalized = str(model_name or "").lower()
    if re.search(r"(^|[-_./:])(2b|3b|4b|mini)($|[-_./:])", normalized):
        return -1
    if any(token in normalized for token in ("27b", "70b", "72b", "grok")):
        return 1
    return 0


def _effective_pair_budget(*, max_tokens: int, model_name: str | None) -> int:
    if max_tokens <= 256:
        base = 2
    elif max_tokens <= 400:
        base = 3
    elif max_tokens <= 600:
        base = 4
    elif max_tokens <= 1000:
        base = 5
    else:
        base = 6
    return max(2, min(8, base + _model_budget_bias(model_name)))


def _effective_candidate_budget(*, pair_budget: int, max_tokens: int, model_name: str | None) -> int:
    base = pair_budget + 1
    if max_tokens <= 256:
        base = min(base, 3)
    elif max_tokens <= 400:
        base = min(base, 4)
    else:
        base = min(base, 6 + _model_budget_bias(model_name))
    return max(2, base)


def _resolve_hybrid_budget_runtime(resolver: Any) -> tuple[int, int, str | None]:
    runtime_config = getattr(resolver, "runtime_config", None)
    if runtime_config is None:
        return VISION_ASSIST_POLICY.max_tokens, 8, None
    return (
        int(getattr(runtime_config, "max_tokens", VISION_ASSIST_POLICY.max_tokens)),
        int(getattr(runtime_config, "max_images", 8)),
        cast(str | None, getattr(runtime_config, "active_model_name", None)),
    )


def _truth_summary_chars(bundle: SceneCorrectionTruthBundleContract) -> int:
    return len(bundle.model_dump_json())


def _check_priority_score(check: SceneCorrectionTruthPairContract) -> tuple[int, int, int, int, int, str]:
    overlap_score = 3 if check.overlap is not None and bool(check.overlap.get("overlaps")) else 0
    contact_score = 3 if check.contact_assertion is not None and not check.contact_assertion.passed else 0
    gap_score = 2 if check.gap is not None and str(check.gap.get("relation") or "").lower() == "separated" else 0
    alignment_score = 1 if check.alignment is not None and not bool(check.alignment.get("is_aligned")) else 0
    error_score = 4 if check.error else 0
    semantics = check.attachment_semantics
    support_semantics = check.support_semantics
    symmetry_semantics = check.symmetry_semantics
    required_score = 4 if semantics is not None and semantics.required_seam else 0
    verdict_score = 0
    seam_score = 0
    if semantics is not None:
        if semantics.attachment_verdict == "intersecting":
            verdict_score = 3
        elif semantics.attachment_verdict == "floating_gap":
            verdict_score = 2
        elif semantics.attachment_verdict == "misaligned_attachment":
            verdict_score = 1
        seam_score = {
            "head_body": 6,
            "tail_body": 5,
            "roof_wall": 5,
            "limb_segment": 4,
            "limb_body": 3,
            "face_head": 2,
            "nose_snout": 1,
        }.get(semantics.seam_kind, 0)
    if support_semantics is not None and support_semantics.verdict != "supported":
        verdict_score = max(verdict_score, 2)
        seam_score = max(seam_score, 4)
    if symmetry_semantics is not None and symmetry_semantics.verdict != "symmetric":
        verdict_score = max(verdict_score, 2)
        seam_score = max(seam_score, 4)
    pair_label = _pair_label(check.from_object, check.to_object)
    return (
        required_score + verdict_score + error_score + overlap_score + contact_score + gap_score + alignment_score,
        seam_score,
        overlap_score,
        contact_score,
        gap_score + alignment_score,
        pair_label,
    )


def _rebuild_truth_summary(
    *,
    pairing_strategy: Literal["none", "primary_to_others", "required_creature_seams", "guided_spatial_pairs"],
    checks: list[SceneCorrectionTruthPairContract],
) -> SceneCorrectionTruthSummaryContract:
    return SceneCorrectionTruthSummaryContract(
        pairing_strategy=pairing_strategy,
        pair_count=len(checks),
        evaluated_pairs=sum(1 for item in checks if item.error is None),
        contact_failures=sum(
            1 for item in checks if item.contact_assertion is not None and not item.contact_assertion.passed
        ),
        overlap_pairs=sum(1 for item in checks if item.overlap is not None and bool(item.overlap.get("overlaps"))),
        separated_pairs=sum(
            1 for item in checks if item.gap is not None and str(item.gap.get("relation") or "").lower() == "separated"
        ),
        misaligned_pairs=sum(
            1 for item in checks if item.alignment is not None and not bool(item.alignment.get("is_aligned"))
        ),
    )


def _trim_truth_bundle_to_budget(
    *,
    truth_bundle: SceneCorrectionTruthBundleContract,
    pair_budget: int,
    max_truth_chars: int,
) -> tuple[SceneCorrectionTruthBundleContract, bool]:
    def _compact_gap_payload(payload: dict[str, Any] | None) -> dict[str, Any] | None:
        if payload is None:
            return None
        return {
            key: payload.get(key)
            for key in ("relation", "gap", "axis_gap", "measurement_basis", "bbox_relation")
            if payload.get(key) is not None
        }

    def _compact_alignment_payload(payload: dict[str, Any] | None) -> dict[str, Any] | None:
        if payload is None:
            return None
        return {
            key: payload.get(key) for key in ("is_aligned", "aligned_axes", "deltas") if payload.get(key) is not None
        }

    def _compact_overlap_payload(payload: dict[str, Any] | None) -> dict[str, Any] | None:
        if payload is None:
            return None
        return {
            key: payload.get(key)
            for key in (
                "overlaps",
                "relation",
                "measurement_basis",
                "bbox_touching",
                "surface_gap",
                "overlap_dimensions",
            )
            if payload.get(key) is not None
        }

    def _compact_contact_assertion(
        payload: SceneAssertionPayloadContract | None,
    ) -> SceneAssertionPayloadContract | None:
        if payload is None:
            return None
        details = payload.details or {}
        compact_details = {
            key: details.get(key)
            for key in ("measurement_basis", "bbox_relation", "overlap_rejected")
            if details.get(key) is not None
        }
        return SceneAssertionPayloadContract(
            assertion=payload.assertion,
            passed=payload.passed,
            subject=payload.subject,
            target=payload.target,
            expected=payload.expected,
            actual=payload.actual,
            details=compact_details or None,
        )

    def _compact_truth_bundle_details(bundle: SceneCorrectionTruthBundleContract) -> SceneCorrectionTruthBundleContract:
        compact_checks = [
            SceneCorrectionTruthPairContract(
                from_object=item.from_object,
                to_object=item.to_object,
                relation_pair_id=item.relation_pair_id,
                relation_kinds=list(item.relation_kinds or []),
                relation_verdicts=list(item.relation_verdicts or []),
                gap=_compact_gap_payload(item.gap),
                alignment=_compact_alignment_payload(item.alignment),
                overlap=_compact_overlap_payload(item.overlap),
                contact_assertion=_compact_contact_assertion(item.contact_assertion),
                attachment_semantics=item.attachment_semantics,
                support_semantics=item.support_semantics,
                symmetry_semantics=item.symmetry_semantics,
                error=item.error,
            )
            for item in list(bundle.checks or [])
        ]
        return SceneCorrectionTruthBundleContract(
            scope=bundle.scope,
            summary=_rebuild_truth_summary(
                pairing_strategy=bundle.summary.pairing_strategy,
                checks=compact_checks,
            ),
            checks=compact_checks,
            error=bundle.error,
        )

    checks = list(truth_bundle.checks or [])
    if len(checks) <= pair_budget and _truth_summary_chars(truth_bundle) <= max_truth_chars:
        return truth_bundle, False

    if truth_bundle.summary.pairing_strategy == "required_creature_seams" and len(checks) <= pair_budget:
        compact_bundle = _compact_truth_bundle_details(truth_bundle)
        return compact_bundle, True

    ordered_checks = sorted(checks, key=_check_priority_score, reverse=True)
    trimmed = False
    selected_count = min(len(ordered_checks), pair_budget)

    while selected_count >= 1:
        selected_checks = ordered_checks[:selected_count]
        trimmed_bundle = SceneCorrectionTruthBundleContract(
            scope=truth_bundle.scope,
            summary=_rebuild_truth_summary(
                pairing_strategy=truth_bundle.summary.pairing_strategy,
                checks=selected_checks,
            ),
            checks=selected_checks,
            error=truth_bundle.error,
        )
        if _truth_summary_chars(trimmed_bundle) <= max_truth_chars or selected_count == 1:
            trimmed = selected_count < len(checks) or _truth_summary_chars(truth_bundle) > max_truth_chars
            return trimmed_bundle, trimmed
        selected_count -= 1

    return truth_bundle, False


def _trim_correction_candidates(
    candidates: list[ReferenceCorrectionCandidateContract],
    *,
    candidate_budget: int,
) -> tuple[list[ReferenceCorrectionCandidateContract], bool]:
    if len(candidates) <= candidate_budget:
        return candidates, False
    return list(candidates[:candidate_budget]), True


def _candidate_matches_pair_label(focus_item: str, pair_label: str) -> bool:
    normalized_focus = _normalized_focus_key(focus_item)
    normalized_pair = _normalized_focus_key(pair_label)
    if not normalized_focus or not normalized_pair:
        return False
    if normalized_pair in normalized_focus:
        return True
    from_object, to_object = pair_label.split(" -> ", 1)
    return (
        _normalized_focus_key(from_object) in normalized_focus and _normalized_focus_key(to_object) in normalized_focus
    )


def _macro_candidate_matches_pair(
    candidate: SceneRepairMacroCandidateContract,
    *,
    from_object: str,
    to_object: str,
) -> bool:
    arguments = candidate.arguments_hint or {}
    candidate_from = (
        arguments.get("part_object")
        or arguments.get("left_object")
        or arguments.get("primary_object")
        or arguments.get("supported_object")
    )
    candidate_to = (
        arguments.get("reference_object")
        or arguments.get("surface_object")
        or arguments.get("right_object")
        or arguments.get("support_object")
    )
    return (candidate_from == from_object and candidate_to == to_object) or (
        candidate_from == to_object and candidate_to == from_object
    )


def _build_vision_candidate_evidence(
    *,
    vision_result,
    focus_items: list[str],
) -> ReferenceCorrectionVisionEvidenceContract | None:
    if vision_result is None or not focus_items:
        return None
    return ReferenceCorrectionVisionEvidenceContract(
        correction_focus=focus_items,
        shape_mismatches=list(vision_result.shape_mismatches or []),
        proportion_mismatches=list(vision_result.proportion_mismatches or []),
        next_corrections=list(vision_result.next_corrections or []),
    )


def _build_correction_candidates(
    compare_result: ReferenceCompareStageCheckpointResponseContract,
) -> list[ReferenceCorrectionCandidateContract]:
    truth_followup = compare_result.truth_followup
    vision_result = compare_result.vision_assistant.result if compare_result.vision_assistant else None
    correction_focus = _resolve_actionable_focus(compare_result)
    candidates: list[ReferenceCorrectionCandidateContract] = []
    used_focus_items: set[str] = set()
    rank = 1
    focus_pairs = list(truth_followup.focus_pairs or []) if truth_followup is not None else []

    truth_items_by_pair: dict[str, list[SceneTruthFollowupItemContract]] = {}
    for item in list(truth_followup.items or []) if truth_followup is not None else []:
        if item.from_object is None or item.to_object is None:
            continue
        pair_label = _pair_label(item.from_object, item.to_object)
        truth_items_by_pair.setdefault(pair_label, []).append(item)

    truth_macros_by_pair: dict[str, list[SceneRepairMacroCandidateContract]] = {}
    for macro_candidate in list(truth_followup.macro_candidates or []) if truth_followup is not None else []:
        for pair_label in focus_pairs:
            from_object, to_object = pair_label.split(" -> ", 1)
            if _macro_candidate_matches_pair(macro_candidate, from_object=from_object, to_object=to_object):
                truth_macros_by_pair.setdefault(pair_label, []).append(macro_candidate)

    for pair_label in focus_pairs:
        pair_items = truth_items_by_pair.get(pair_label, [])
        pair_macros = truth_macros_by_pair.get(pair_label, [])
        matched_focus = [item for item in correction_focus if _candidate_matches_pair_label(item, pair_label)]
        used_focus_items.update(_normalized_focus_key(item) for item in matched_focus)
        item_priorities = {item.priority for item in pair_items}
        macro_priorities = {item.priority for item in pair_macros}
        priority: Literal["high", "normal"] = (
            "high" if "high" in item_priorities or "high" in macro_priorities else "normal"
        )
        signals: list[Literal["vision", "truth", "macro"]] = ["truth"]
        if pair_macros:
            signals.append("macro")
        if matched_focus:
            signals.append("vision")
        summary = (
            pair_items[0].summary
            if pair_items
            else (matched_focus[0] if matched_focus else f"Review pair {pair_label}")
        )
        from_object, to_object = pair_label.split(" -> ", 1)
        candidates.append(
            ReferenceCorrectionCandidateContract(
                candidate_id=f"pair:{_normalized_focus_key(pair_label).replace(' ', '_')}",
                summary=summary,
                priority_rank=rank,
                priority=priority,
                candidate_kind="hybrid" if matched_focus else "truth_only",
                target_object=compare_result.target_object,
                target_objects=[from_object, to_object],
                focus_pairs=[pair_label],
                source_signals=signals,
                vision_evidence=_build_vision_candidate_evidence(
                    vision_result=vision_result,
                    focus_items=matched_focus,
                ),
                truth_evidence=ReferenceCorrectionTruthEvidenceContract(
                    focus_pairs=[pair_label],
                    relation_kinds=list(
                        dict.fromkeys(kind for item in pair_items for kind in list(item.relation_kinds or []))
                    ),
                    relation_verdicts=list(
                        dict.fromkeys(verdict for item in pair_items for verdict in list(item.relation_verdicts or []))
                    ),
                    item_kinds=[item.kind for item in pair_items],
                    items=pair_items,
                    macro_candidates=pair_macros,
                ),
            )
        )
        rank += 1

    for focus_item in correction_focus:
        normalized_focus = _normalized_focus_key(focus_item)
        if not normalized_focus or normalized_focus in used_focus_items:
            continue
        target_objects = list(compare_result.target_objects or [])
        if compare_result.target_object and compare_result.target_object not in target_objects:
            target_objects = [compare_result.target_object, *target_objects]
        candidates.append(
            ReferenceCorrectionCandidateContract(
                candidate_id=f"vision:{normalized_focus.replace(' ', '_')}",
                summary=focus_item,
                priority_rank=rank,
                priority="normal",
                candidate_kind="vision_only",
                target_object=compare_result.target_object,
                target_objects=target_objects,
                focus_pairs=[],
                source_signals=["vision"],
                vision_evidence=_build_vision_candidate_evidence(
                    vision_result=vision_result,
                    focus_items=[focus_item],
                ),
                truth_evidence=None,
            )
        )
        rank += 1

    return candidates


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
            "This compare/iterate path does not yet execute the sidecar and currently reports it as unavailable.",
            "The sidecar path is advisory-only and separate from vision_contract_profile routing.",
        ],
    )


def _blocked_reference_understanding_summary(
    *,
    goal: str | None,
    reason: Literal["goal_required", "reference_images_required", "vision_backend_unavailable"],
    message: str,
    reference_ids: list[str] | None = None,
) -> ReferenceUnderstandingSummaryContract:
    status: Literal["blocked", "unavailable"] = "blocked"
    if reason == "vision_backend_unavailable":
        status = "unavailable"
    return ReferenceUnderstandingSummaryContract(
        status=status,
        goal=goal,
        reference_ids=list(reference_ids or []),
        reason=reason,
        message=message,
    )


def _active_reference_records(session: SessionCapabilityState) -> tuple[ReferenceImageRecordContract, ...]:
    return tuple(ReferenceImageRecordContract.model_validate(item) for item in list(session.reference_images or []))


def _reference_understanding_request(
    *,
    goal: str,
    reference_records: tuple[ReferenceImageRecordContract, ...],
) -> VisionRequest:
    reference_images = build_reference_capture_images(reference_records)
    return VisionRequest(
        goal=goal,
        images=tuple(
            VisionImageInput(
                path=image.image_path,
                role="reference",
                label=image.label,
                media_type=image.media_type,
            )
            for image in reference_images
        ),
        prompt_hint="reference_understanding",
        metadata={
            "mode": "reference_understanding",
            "reference_ids": [record.reference_id for record in reference_records],
            "reference_labels": [record.label or record.reference_id for record in reference_records],
            "source": "reference_images",
        },
    )


def _without_reference_understanding_gates(
    gate_plan: GatePlanContract | None,
    *,
    tracked_gate_ids: list[str] | None,
) -> GatePlanContract | None:
    if gate_plan is None:
        return None

    tracked_ids = {str(item).strip() for item in tracked_gate_ids or [] if str(item).strip()}
    retained_gates = []
    removed_gate_ids: set[str] = set()
    for gate in gate_plan.gates:
        if gate.gate_id not in tracked_ids and "reference_understanding" not in gate.proposal_sources:
            retained_gates.append(gate)
            continue
        retained_gate = without_proposal_source(gate, "reference_understanding")
        if retained_gate is None:
            removed_gate_ids.add(gate.gate_id)
            continue
        retained_gates.append(retained_gate)
    retained_warnings = [
        warning
        for warning in gate_plan.policy_warnings
        if warning.gate_id is None or warning.gate_id not in removed_gate_ids
    ]
    return refresh_gate_plan_status(
        gate_plan.model_copy(
            update={
                "gates": retained_gates,
                "policy_warnings": retained_warnings,
            }
        )
    )


def _reference_understanding_gate_slice(gate_plan: GatePlanContract | None) -> GatePlanContract | None:
    if gate_plan is None:
        return None

    slice_gates = [gate for gate in gate_plan.gates if "reference_understanding" in gate.proposal_sources]
    if not slice_gates:
        return None

    slice_gate_ids = {gate.gate_id for gate in slice_gates}
    slice_warnings = [
        warning for warning in gate_plan.policy_warnings if warning.gate_id is None or warning.gate_id in slice_gate_ids
    ]
    return refresh_gate_plan_status(
        gate_plan.model_copy(
            update={
                "gates": slice_gates,
                "policy_warnings": slice_warnings,
            }
        )
    )


async def _persist_reference_understanding_state_async(
    ctx: Context,
    state: SessionCapabilityState,
) -> SessionCapabilityState:
    """Persist one RU-driven session state update and immediately reapply visibility."""

    await set_session_capability_state_async(ctx, state)
    await apply_visibility_for_session_state(ctx, state)
    return state


async def refresh_reference_understanding_summary_async(
    ctx: Context,
    *,
    session: SessionCapabilityState | None = None,
) -> SessionCapabilityState:
    """Refresh session-scoped reference understanding from active references when possible."""

    current = session or await get_session_capability_state_async(ctx)
    existing_gate_plan = GatePlanContract.model_validate(current.gate_plan) if current.gate_plan is not None else None
    base_gate_plan = _without_reference_understanding_gates(
        existing_gate_plan,
        tracked_gate_ids=current.reference_understanding_gate_ids,
    )
    if not current.goal:
        cleared = replace(
            current,
            gate_plan=None if base_gate_plan is None else base_gate_plan.model_dump(mode="json", exclude_none=True),
            reference_understanding_summary=None,
            reference_understanding_gate_ids=None,
        )
        return await _persist_reference_understanding_state_async(ctx, cleared)

    reference_records = _active_reference_records(current)
    reference_ids = [record.reference_id for record in reference_records]
    if not reference_records:
        blocked = _blocked_reference_understanding_summary(
            goal=current.goal,
            reason="reference_images_required",
            message="Attach at least one active reference image before reference understanding can run.",
        )
        updated = replace(
            current,
            gate_plan=None if base_gate_plan is None else base_gate_plan.model_dump(mode="json", exclude_none=True),
            reference_understanding_summary=blocked.model_dump(mode="json", exclude_none=True),
            reference_understanding_gate_ids=None,
        )
        return await _persist_reference_understanding_state_async(ctx, updated)

    existing_summary = current.reference_understanding_summary or {}
    if (
        existing_summary.get("status") == "available"
        and existing_summary.get("goal") == current.goal
        and list(existing_summary.get("reference_ids") or []) == reference_ids
    ):
        return current

    request = _reference_understanding_request(goal=current.goal, reference_records=reference_records)
    resolver = get_vision_backend_resolver()
    try:
        backend = resolver.resolve_default()
        payload = await backend.analyze(request)
        summary = ReferenceUnderstandingSummaryContract.model_validate(payload)
    except VisionBackendUnavailableError as exc:
        unavailable = _blocked_reference_understanding_summary(
            goal=current.goal,
            reason="vision_backend_unavailable",
            message=str(exc),
            reference_ids=reference_ids,
        )
        updated = replace(
            current,
            gate_plan=None if base_gate_plan is None else base_gate_plan.model_dump(mode="json", exclude_none=True),
            reference_understanding_summary=unavailable.model_dump(mode="json", exclude_none=True),
            reference_understanding_gate_ids=None,
        )
        return await _persist_reference_understanding_state_async(ctx, updated)
    except Exception as exc:
        unavailable = _blocked_reference_understanding_summary(
            goal=current.goal,
            reason="vision_backend_unavailable",
            message=f"Reference understanding could not complete: {exc}",
            reference_ids=reference_ids,
        )
        updated = replace(
            current,
            gate_plan=None if base_gate_plan is None else base_gate_plan.model_dump(mode="json", exclude_none=True),
            reference_understanding_summary=unavailable.model_dump(mode="json", exclude_none=True),
            reference_understanding_gate_ids=None,
        )
        return await _persist_reference_understanding_state_async(ctx, updated)

    accepted_gate_ids: list[str] | None = None
    updated_session = replace(
        current,
        gate_plan=None if base_gate_plan is None else base_gate_plan.model_dump(mode="json", exclude_none=True),
    )
    if summary.gate_proposals:
        gate_proposal = GateProposalContract(
            proposal_id=summary.understanding_id,
            source="reference_understanding",
            goal=current.goal,
            gates=summary.gate_proposals,
            source_provenance=summary.source_provenance,
        )
        intake_result = await ingest_quality_gate_proposal_async(
            ctx,
            gate_proposal.model_dump(mode="json", exclude_none=True),
        )
        if intake_result.status == "accepted" and intake_result.gate_plan is not None:
            replacement_slice = _reference_understanding_gate_slice(intake_result.gate_plan)
            updated_session = replace(
                updated_session,
                gate_plan=intake_result.gate_plan.model_dump(mode="json", exclude_none=True),
            )
            accepted_gate_ids = (
                None if replacement_slice is None else [gate.gate_id for gate in replacement_slice.gates]
            )

    final_state = replace(
        updated_session,
        reference_understanding_summary=summary.model_dump(mode="json", exclude_none=True),
        reference_understanding_gate_ids=accepted_gate_ids or None,
    )
    return await _persist_reference_understanding_state_async(ctx, final_state)


def _build_silhouette_analysis_payload(
    *,
    selected_reference_records: list[ReferenceImageRecordContract] | tuple[ReferenceImageRecordContract, ...],
    captures: list[VisionCaptureImageContract] | tuple[VisionCaptureImageContract, ...],
    target_view: str | None,
) -> ReferenceSilhouetteAnalysisContract | None:
    if not selected_reference_records or not captures:
        return None

    reference_record = selected_reference_records[0]
    capture = _select_silhouette_analysis_capture(captures=captures, target_view=target_view)
    payload = build_silhouette_analysis(
        reference_path=reference_record.stored_path,
        capture_path=capture.image_path,
        reference_label=reference_record.label or reference_record.reference_id,
        capture_label=capture.label,
        target_view=target_view,
    )
    return ReferenceSilhouetteAnalysisContract.model_validate(payload)


def _capture_matches_target_view(capture: VisionCaptureImageContract, target_view: str) -> bool:
    normalized_target = target_view.strip().lower()
    if not normalized_target:
        return False

    for value in (capture.preset_name, capture.label):
        normalized_value = str(value or "").strip().lower()
        if not normalized_value:
            continue
        if normalized_value == normalized_target or normalized_value.endswith(f"_{normalized_target}"):
            return True
        tokens = [token for token in re.split(r"[^a-z0-9]+", normalized_value) if token]
        if normalized_target in tokens:
            return True
    return False


def _select_silhouette_analysis_capture(
    *,
    captures: list[VisionCaptureImageContract] | tuple[VisionCaptureImageContract, ...],
    target_view: str | None,
) -> VisionCaptureImageContract:
    if target_view:
        for capture in captures:
            if capture.view_kind == "focus" and _capture_matches_target_view(capture, target_view):
                return capture
        for capture in captures:
            if _capture_matches_target_view(capture, target_view):
                return capture

    for capture in captures:
        if capture.view_kind == "focus":
            return capture
    return captures[0]


def _resolve_stage_view_diagnostics_preset(
    *,
    captures: list[VisionCaptureImageContract] | tuple[VisionCaptureImageContract, ...],
    preset_profile: CapturePresetProfile,
    target_view: str | None,
) -> tuple[VisionCaptureImageContract, CapturePresetSpec | None]:
    capture = _select_silhouette_analysis_capture(captures=captures, target_view=target_view)
    preset_name = str(capture.preset_name or "").strip()
    if not preset_name:
        return capture, None

    for preset in resolve_capture_preset_specs(preset_profile):
        if preset.name == preset_name:
            return capture, preset
    return capture, None


def _build_stage_view_diagnostics_hints(
    *,
    scene_handler: Any,
    captures: list[VisionCaptureImageContract] | tuple[VisionCaptureImageContract, ...],
    preset_profile: CapturePresetProfile,
    target_object: str | None,
    target_objects: list[str] | tuple[str, ...],
    collection_name: str | None,
    target_view: str | None,
) -> list[ReferenceViewDiagnosticsHintContract] | None:
    diagnostic_target = target_object or next((name for name in target_objects if str(name or "").strip()), None)
    if not diagnostic_target or not captures or not hasattr(scene_handler, "get_view_diagnostics"):
        return None

    capture, preset = _resolve_stage_view_diagnostics_preset(
        captures=captures,
        preset_profile=preset_profile,
        target_view=target_view,
    )
    focus_target = (
        diagnostic_target if (preset.focus_target if preset is not None else capture.view_kind == "focus") else None
    )
    view_name = preset.standard_view if preset is not None else None
    orbit_horizontal = float(preset.orbit_horizontal or 0.0) if preset is not None else 0.0
    orbit_vertical = float(preset.orbit_vertical or 0.0) if preset is not None else 0.0
    zoom_factor = None
    if preset is not None and preset.focus_zoom_factor != 1.0:
        zoom_factor = float(preset.focus_zoom_factor)

    try:
        diagnostics_payload = scene_handler.get_view_diagnostics(
            target_object=diagnostic_target,
            target_objects=list(target_objects or []),
            collection_name=collection_name,
            camera_name=None,
            focus_target=focus_target,
            view_name=view_name,
            orbit_horizontal=orbit_horizontal,
            orbit_vertical=orbit_vertical,
            zoom_factor=zoom_factor,
            persist_view=False,
        )
    except Exception:
        return None

    return _build_view_diagnostics_hints(
        diagnostics_payload=diagnostics_payload,
        target_object=diagnostic_target,
        camera_name=None,
        focus_target=focus_target,
        view_name=view_name,
        orbit_horizontal=orbit_horizontal,
        orbit_vertical=orbit_vertical,
        zoom_factor=zoom_factor,
    )


def _build_action_hints_from_silhouette(
    silhouette_analysis: ReferenceSilhouetteAnalysisContract | None,
    *,
    target_object: str | None,
) -> list[ReferenceActionHintContract]:
    if silhouette_analysis is None or silhouette_analysis.status != "available":
        return []

    metrics = {metric.metric_id: metric for metric in silhouette_analysis.metrics}
    hints: list[ReferenceActionHintContract] = []

    def add_hint(
        *,
        hint_id: str,
        hint_type: str,
        summary: str,
        metric_ids: list[str],
        recommended_tools: list[ReferenceRefinementToolCandidateContract],
        priority: Literal["high", "normal"] = "normal",
    ) -> None:
        hints.append(
            ReferenceActionHintContract(
                hint_id=hint_id,
                hint_type=hint_type,  # type: ignore[arg-type]
                summary=summary,
                priority=priority,
                target_object=target_object,
                metric_ids=metric_ids,
                recommended_tools=recommended_tools,
            )
        )

    upper_band = metrics.get("upper_band_width_delta")
    if upper_band is not None and upper_band.delta <= -0.03:
        add_hint(
            hint_id="silhouette_upper_expand",
            hint_type="widen_upper_profile",
            summary="Upper silhouette band is narrower than the reference; build the upper profile mass before another broad pass.",
            metric_ids=["upper_band_width_delta"],
            recommended_tools=[
                ReferenceRefinementToolCandidateContract(
                    tool_name="mesh_extrude_region",
                    reason="Extrude the upper silhouette mass to widen the creature profile in a bounded way.",
                    priority="high",
                ),
                ReferenceRefinementToolCandidateContract(
                    tool_name="mesh_loop_cut",
                    reason="Add support loops so the widened upper silhouette stays controllable.",
                    priority="normal",
                ),
            ],
            priority="high",
        )
    if upper_band is not None and upper_band.delta >= 0.03:
        add_hint(
            hint_id="silhouette_upper_reduce",
            hint_type="reduce_upper_profile",
            summary="Upper silhouette band is broader than the reference; simplify or tighten the upper profile before adding detail.",
            metric_ids=["upper_band_width_delta"],
            recommended_tools=[
                ReferenceRefinementToolCandidateContract(
                    tool_name="mesh_dissolve",
                    reason="Dissolve or simplify support edges while preserving the overall low-poly form.",
                    priority="normal",
                ),
                ReferenceRefinementToolCandidateContract(
                    tool_name="mesh_merge_by_distance",
                    reason="Clean up doubled or noisy vertices after reducing the upper profile.",
                    priority="normal",
                ),
            ],
        )

    left_projection_metric = metrics.get("left_projection_delta")
    if left_projection_metric is not None and left_projection_metric.delta < -0.05:
        add_hint(
            hint_id="silhouette_left_extend",
            hint_type="extend_left_profile",
            summary="Left-side silhouette projection is shorter than the reference; extend that profile mass before smoothing.",
            metric_ids=["left_projection_delta"],
            recommended_tools=[
                ReferenceRefinementToolCandidateContract(
                    tool_name="mesh_extrude_region",
                    reason="Extend the silhouette profile with a bounded extrusion in the underbuilt direction.",
                    priority="high",
                ),
                ReferenceRefinementToolCandidateContract(
                    tool_name="modeling_transform_object",
                    reason="If the profile is object-level, nudge the blocker object instead of overediting mesh topology.",
                    priority="normal",
                ),
            ],
            priority="high",
        )

    right_projection_metric = metrics.get("right_projection_delta")
    if right_projection_metric is not None and right_projection_metric.delta < -0.05:
        add_hint(
            hint_id="silhouette_right_extend",
            hint_type="extend_right_profile",
            summary="Right-side silhouette projection is shorter than the reference; extend that profile mass before smoothing.",
            metric_ids=["right_projection_delta"],
            recommended_tools=[
                ReferenceRefinementToolCandidateContract(
                    tool_name="mesh_extrude_region",
                    reason="Extend the silhouette profile with a bounded extrusion in the underbuilt direction.",
                    priority="high",
                ),
                ReferenceRefinementToolCandidateContract(
                    tool_name="modeling_transform_object",
                    reason="If the profile is object-level, nudge the blocker object instead of overediting mesh topology.",
                    priority="normal",
                ),
            ],
            priority="high",
        )

    aspect_ratio = metrics.get("aspect_ratio_delta")
    if aspect_ratio is not None and abs(aspect_ratio.delta) >= 0.18:
        add_hint(
            hint_id="silhouette_rebalance_proportion",
            hint_type="rebalance_proportion",
            summary="Overall silhouette aspect ratio drift is still significant; re-check proportions before continuing free-form edits.",
            metric_ids=["aspect_ratio_delta"],
            recommended_tools=[
                ReferenceRefinementToolCandidateContract(
                    tool_name="scene_measure_dimensions",
                    reason="Measure the current object dimensions before scaling a major mass.",
                    priority="high",
                ),
                ReferenceRefinementToolCandidateContract(
                    tool_name="scene_assert_proportion",
                    reason="Verify the repaired ratio against an explicit expected proportion.",
                    priority="high",
                ),
                ReferenceRefinementToolCandidateContract(
                    tool_name="macro_adjust_relative_proportion",
                    reason="Use a bounded ratio repair instead of ad hoc free-form scaling when major proportions drift.",
                    priority="high",
                ),
            ],
            priority="high",
        )

    mask_iou = metrics.get("mask_iou")
    contour_drift = metrics.get("contour_drift")
    if (mask_iou is not None and mask_iou.observed_value <= 0.55) or (
        contour_drift is not None and contour_drift.observed_value >= 0.14
    ):
        metric_ids: list[str] = []
        if mask_iou is not None and mask_iou.observed_value <= 0.55:
            metric_ids.append("mask_iou")
        if contour_drift is not None and contour_drift.observed_value >= 0.14:
            metric_ids.append("contour_drift")
        add_hint(
            hint_id="silhouette_inspect_before_edit",
            hint_type="inspect_before_edit",
            summary="Global silhouette mismatch is still high; inspect the current object state before applying another free-form correction.",
            metric_ids=metric_ids,
            recommended_tools=[
                ReferenceRefinementToolCandidateContract(
                    tool_name="inspect_scene",
                    reason="Inspect the object state before another silhouette correction when deterministic drift remains high.",
                    priority="high",
                ),
                ReferenceRefinementToolCandidateContract(
                    tool_name="reference_iterate_stage_checkpoint",
                    reason="Re-run a bounded iterate checkpoint after a targeted correction instead of making a large uncontrolled edit.",
                    priority="normal",
                ),
            ],
            priority="high",
        )

    return hints


def _build_view_diagnostics_hints(
    *,
    diagnostics_payload: dict[str, Any] | None,
    target_object: str | None,
    camera_name: str | None,
    focus_target: str | None,
    view_name: str | None,
    orbit_horizontal: float,
    orbit_vertical: float,
    zoom_factor: float | None,
) -> list[ReferenceViewDiagnosticsHintContract]:
    if not isinstance(diagnostics_payload, dict):
        return []

    hints: list[ReferenceViewDiagnosticsHintContract] = []
    for item in list(diagnostics_payload.get("targets") or []):
        if not isinstance(item, dict):
            continue
        object_name = str(item.get("object_name") or "").strip()
        verdict = str(item.get("visibility_verdict") or "").strip()
        projection = item.get("projection") if isinstance(item.get("projection"), dict) else {}
        centered = bool(projection.get("centered")) if isinstance(projection, dict) else False
        raw_frame_coverage_ratio = projection.get("frame_coverage_ratio") if isinstance(projection, dict) else None
        frame_coverage_ratio: float | None
        if isinstance(raw_frame_coverage_ratio, (int, float)):
            frame_coverage_ratio = float(raw_frame_coverage_ratio)
        else:
            frame_coverage_ratio = None

        trigger: Literal["framing_ambiguity", "visibility_ambiguity", "occlusion_detected", "target_off_frame"] | None
        priority: Literal["high", "normal"] = "normal"
        reason: str | None = None

        if verdict == "fully_occluded":
            trigger = "occlusion_detected"
            priority = "high"
            reason = (
                f"'{object_name or target_object or focus_target or 'target'}' is currently fully occluded from this view. "
                "Call scene_view_diagnostics(...) before another compare/correction step so framing and occlusion are explicit."
            )
        elif verdict == "outside_frame":
            trigger = "target_off_frame"
            priority = "high"
            reason = (
                f"'{object_name or target_object or focus_target or 'target'}' is currently outside the frame. "
                "Call scene_view_diagnostics(...) before another compare/correction step so reframing is driven by typed view facts."
            )
        elif verdict == "partially_visible":
            trigger = "visibility_ambiguity"
            reason = (
                f"'{object_name or target_object or focus_target or 'target'}' is only partially visible from this view. "
                "Call scene_view_diagnostics(...) to inspect frame coverage and occlusion before another correction pass."
            )
        elif frame_coverage_ratio is not None and (frame_coverage_ratio < 0.999 or not centered):
            trigger = "framing_ambiguity"
            reason = (
                f"'{object_name or target_object or focus_target or 'target'}' is not cleanly centered/framed in the current view. "
                "Call scene_view_diagnostics(...) if the next decision depends on precise framing facts."
            )
        else:
            trigger = None

        if trigger is None or reason is None:
            continue

        arguments_hint: dict[str, object] = {
            "target_object": object_name or target_object or focus_target,
        }
        if camera_name:
            arguments_hint["camera_name"] = camera_name
        if focus_target:
            arguments_hint["focus_target"] = focus_target
        if view_name:
            arguments_hint["view_name"] = view_name
        if orbit_horizontal:
            arguments_hint["orbit_horizontal"] = orbit_horizontal
        if orbit_vertical:
            arguments_hint["orbit_vertical"] = orbit_vertical
        if zoom_factor is not None:
            arguments_hint["zoom_factor"] = zoom_factor

        hints.append(
            ReferenceViewDiagnosticsHintContract(
                hint_id=f"view_diag_{trigger}_{(object_name or 'target').lower()}",
                trigger=trigger,
                reason=reason,
                priority=priority,
                arguments_hint=arguments_hint,
            )
        )

    return hints


def _dedupe_names(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in values:
        normalized = item.strip()
        key = normalized.lower()
        if not normalized or key in seen:
            continue
        seen.add(key)
        result.append(normalized)
    return result


def _name_role_tokens(object_name: str) -> list[str]:
    normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", object_name.strip())
    return [token for token in re.split(r"[^a-zA-Z0-9]+", normalized.lower()) if token]


def _has_name_hint(object_name: str, hints: tuple[str, ...]) -> bool:
    normalized = object_name.strip().lower()
    return any(hint in normalized for hint in hints)


def _is_head_like(object_name: str) -> bool:
    return _has_name_hint(object_name, _HEAD_ROLE_HINTS)


def _is_body_like(object_name: str) -> bool:
    return _has_name_hint(object_name, _BODY_ROLE_HINTS)


def _is_snout_like(object_name: str) -> bool:
    return _has_name_hint(object_name, _SNOUT_ROLE_HINTS)


def _is_nose_like(object_name: str) -> bool:
    return _has_name_hint(object_name, _NOSE_ROLE_HINTS)


def _is_eye_like(object_name: str) -> bool:
    return _has_name_hint(object_name, _EYE_ROLE_HINTS)


def _is_face_attachment(object_name: str) -> bool:
    return _has_name_hint(object_name, _FACE_ATTACHMENT_HINTS)


def _is_tail_like(object_name: str) -> bool:
    return _has_name_hint(object_name, _TAIL_ROLE_HINTS)


def _is_roof_like(object_name: str) -> bool:
    return _has_name_hint(object_name, _ROOF_ROLE_HINTS)


def _is_building_mass_like(object_name: str) -> bool:
    return _has_name_hint(object_name, _BUILDING_MASS_HINTS)


def _is_limb_like(object_name: str) -> bool:
    if _has_name_hint(object_name, _LIMB_ROLE_HINTS):
        return True

    tokens = _name_role_tokens(object_name)
    directional_tokens = {"fore", "hind"}
    side_tokens = {"l", "r", "left", "right"}
    if not any(token in directional_tokens for token in tokens) or not any(token in side_tokens for token in tokens):
        return False
    return all(token in directional_tokens or token in side_tokens or token.isdigit() for token in tokens)


def _is_distal_limb_like(object_name: str) -> bool:
    return _has_name_hint(object_name, _DISTAL_LIMB_HINTS)


def _is_proximal_limb_like(object_name: str) -> bool:
    return _has_name_hint(object_name, _PROXIMAL_LIMB_HINTS) and not _is_distal_limb_like(object_name)


def _select_role_anchor(object_names: list[str]) -> str | None:
    if not object_names:
        return None
    return _select_scope_primary_target(object_names)


def _name_side_hint(object_name: str) -> Literal["left", "right"] | None:
    normalized = object_name.strip().lower()
    if (
        normalized.endswith("left")
        or normalized.endswith("_l")
        or normalized.endswith(".l")
        or re.search(r"(?:^|[_\-.])left(?:$|[_\-.])", normalized)
        or re.search(r"(?:^|[_\-.])l(?:$|[_\-.])", normalized)
    ):
        return "left"
    if (
        normalized.endswith("right")
        or normalized.endswith("_r")
        or normalized.endswith(".r")
        or re.search(r"(?:^|[_\-.])right(?:$|[_\-.])", normalized)
        or re.search(r"(?:^|[_\-.])r(?:$|[_\-.])", normalized)
    ):
        return "right"
    return None


def _limb_chain_hint(object_name: str) -> Literal["fore", "hind"] | None:
    normalized = object_name.strip().lower()
    if any(token in normalized for token in ("fore", "front")):
        return "fore"
    if any(token in normalized for token in ("hind", "rear", "back")):
        return "hind"
    return None


def _limb_match_score(part_object: str, anchor_object: str) -> tuple[int, int, int, str]:
    same_side = (
        1 if _name_side_hint(part_object) == _name_side_hint(anchor_object) and _name_side_hint(part_object) else 0
    )
    same_chain = (
        1 if _limb_chain_hint(part_object) == _limb_chain_hint(anchor_object) and _limb_chain_hint(part_object) else 0
    )
    proximal_bonus = 1 if _is_proximal_limb_like(anchor_object) else 0
    return (same_side, same_chain, proximal_bonus, anchor_object.lower())


def _select_limb_anchor_for_distal(part_object: str, candidate_objects: list[str]) -> str | None:
    if not candidate_objects:
        return None
    return max(candidate_objects, key=lambda name: _limb_match_score(part_object, name))


def _preferred_attachment_macro(
    relation_kind: _CreatureRelationKind,
) -> Literal["macro_attach_part_to_surface", "macro_align_part_with_contact"]:
    if relation_kind == "embedded_attachment":
        return "macro_attach_part_to_surface"
    return "macro_align_part_with_contact"


def _append_creature_seam(
    seams: list[_PlannedCreatureSeam],
    seen_pairs: set[tuple[str, str]],
    *,
    part_object: str,
    anchor_object: str,
    relation_kind: _CreatureRelationKind,
    seam_kind: _CreatureSeamKind,
) -> None:
    pair_key = (part_object, anchor_object)
    if part_object == anchor_object or pair_key in seen_pairs:
        return
    seen_pairs.add(pair_key)
    seams.append(
        _PlannedCreatureSeam(
            part_object=part_object,
            anchor_object=anchor_object,
            relation_kind=relation_kind,
            seam_kind=seam_kind,
        )
    )


def _required_creature_seams(scope: SceneAssembledTargetScopeContract) -> list[_PlannedCreatureSeam]:
    object_names = list(scope.object_names or [])
    if len(object_names) < 2:
        return []

    heads = [name for name in object_names if _is_head_like(name)]
    bodies = [name for name in object_names if _is_body_like(name)]
    snouts = [name for name in object_names if _is_snout_like(name)]
    noses = [name for name in object_names if _is_nose_like(name)]
    tails = [name for name in object_names if _is_tail_like(name)]
    eyes = [name for name in object_names if _is_eye_like(name)]
    face_attachments = [
        name
        for name in object_names
        if _is_face_attachment(name) and not _is_eye_like(name) and not _is_nose_like(name) and not _is_snout_like(name)
    ]
    limbs = [name for name in object_names if _is_limb_like(name)]

    head_anchor = _select_role_anchor(heads)
    body_anchor = _select_role_anchor(bodies)
    snout_anchor = _select_role_anchor(snouts)

    seams: list[_PlannedCreatureSeam] = []
    seen_pairs: set[tuple[str, str]] = set()

    if head_anchor is not None and body_anchor is not None:
        _append_creature_seam(
            seams,
            seen_pairs,
            part_object=head_anchor,
            anchor_object=body_anchor,
            relation_kind="segment_attachment",
            seam_kind="head_body",
        )

    if head_anchor is not None:
        for eye_name in eyes:
            _append_creature_seam(
                seams,
                seen_pairs,
                part_object=eye_name,
                anchor_object=head_anchor,
                relation_kind="seated_attachment",
                seam_kind="face_head",
            )
        for face_name in face_attachments:
            _append_creature_seam(
                seams,
                seen_pairs,
                part_object=face_name,
                anchor_object=head_anchor,
                relation_kind="embedded_attachment",
                seam_kind="face_head",
            )
        for snout_name in snouts:
            _append_creature_seam(
                seams,
                seen_pairs,
                part_object=snout_name,
                anchor_object=head_anchor,
                relation_kind="embedded_attachment",
                seam_kind="face_head",
            )
        if snout_anchor is None:
            for nose_name in noses:
                _append_creature_seam(
                    seams,
                    seen_pairs,
                    part_object=nose_name,
                    anchor_object=head_anchor,
                    relation_kind="embedded_attachment",
                    seam_kind="face_head",
                )

    if snout_anchor is not None:
        for nose_name in noses:
            _append_creature_seam(
                seams,
                seen_pairs,
                part_object=nose_name,
                anchor_object=snout_anchor,
                relation_kind="embedded_attachment",
                seam_kind="nose_snout",
            )

    if body_anchor is not None:
        for tail_name in tails:
            _append_creature_seam(
                seams,
                seen_pairs,
                part_object=tail_name,
                anchor_object=body_anchor,
                relation_kind="segment_attachment",
                seam_kind="tail_body",
            )

    distal_limbs = [name for name in limbs if _is_distal_limb_like(name)]
    proximal_limbs = [name for name in limbs if _is_proximal_limb_like(name)]
    remaining_limb_bodies: list[str] = []

    for limb_name in limbs:
        if limb_name in distal_limbs:
            anchor_name = _select_limb_anchor_for_distal(
                limb_name,
                [candidate for candidate in proximal_limbs if candidate != limb_name],
            )
            if anchor_name is not None:
                _append_creature_seam(
                    seams,
                    seen_pairs,
                    part_object=limb_name,
                    anchor_object=anchor_name,
                    relation_kind="segment_attachment",
                    seam_kind="limb_segment",
                )
                continue
        remaining_limb_bodies.append(limb_name)

    if body_anchor is not None:
        for limb_name in remaining_limb_bodies:
            _append_creature_seam(
                seams,
                seen_pairs,
                part_object=limb_name,
                anchor_object=body_anchor,
                relation_kind="segment_attachment",
                seam_kind="limb_body",
            )

    seam_priority = {
        "head_body": 60,
        "tail_body": 50,
        "limb_segment": 45,
        "limb_body": 40,
        "face_head": 30,
        "nose_snout": 25,
    }
    return sorted(
        seams,
        key=lambda seam: (
            -seam_priority.get(seam.seam_kind, 0),
            seam.part_object.lower(),
            seam.anchor_object.lower(),
        ),
    )


def _attachment_relation(
    from_object: str,
    to_object: str,
) -> tuple[_CreatureRelationKind, str, str] | None:
    if _is_nose_like(from_object) and _is_snout_like(to_object):
        return "embedded_attachment", from_object, to_object
    if _is_nose_like(to_object) and _is_snout_like(from_object):
        return "embedded_attachment", to_object, from_object
    if _is_face_attachment(from_object) and _is_head_like(to_object):
        relation_kind: _CreatureRelationKind
        relation_kind = "seated_attachment" if _is_eye_like(from_object) else "embedded_attachment"
        return relation_kind, from_object, to_object
    if _is_face_attachment(to_object) and _is_head_like(from_object):
        relation_kind = "seated_attachment" if _is_eye_like(to_object) else "embedded_attachment"
        return relation_kind, to_object, from_object
    if _is_head_like(from_object) and _is_body_like(to_object):
        return "segment_attachment", from_object, to_object
    if _is_head_like(to_object) and _is_body_like(from_object):
        return "segment_attachment", to_object, from_object
    if _is_tail_like(from_object) and _is_body_like(to_object):
        return "segment_attachment", from_object, to_object
    if _is_tail_like(to_object) and _is_body_like(from_object):
        return "segment_attachment", to_object, from_object
    if _is_roof_like(from_object) and _is_building_mass_like(to_object):
        return "seated_attachment", from_object, to_object
    if _is_roof_like(to_object) and _is_building_mass_like(from_object):
        return "seated_attachment", to_object, from_object
    if _is_limb_like(from_object) and (_is_body_like(to_object) or _is_limb_like(to_object)):
        return "segment_attachment", from_object, to_object
    if _is_limb_like(to_object) and (_is_body_like(from_object) or _is_limb_like(from_object)):
        if _is_distal_limb_like(from_object) and not _is_distal_limb_like(to_object):
            return "segment_attachment", from_object, to_object
        return "segment_attachment", to_object, from_object
    return None


def _attachment_seam_kind(part_object: str, anchor_object: str) -> _CreatureSeamKind:
    if _is_nose_like(part_object) and _is_snout_like(anchor_object):
        return "nose_snout"
    if _is_head_like(part_object) and _is_body_like(anchor_object):
        return "head_body"
    if _is_tail_like(part_object) and _is_body_like(anchor_object):
        return "tail_body"
    if _is_roof_like(part_object) and _is_building_mass_like(anchor_object):
        return "roof_wall"
    if _is_limb_like(part_object) and _is_limb_like(anchor_object):
        return "limb_segment"
    if _is_limb_like(part_object) and _is_body_like(anchor_object):
        return "limb_body"
    return "face_head"


def _attachment_item_summary(
    *,
    pair_label: str,
    relation_kind: Literal["embedded_attachment", "seated_attachment", "segment_attachment"],
    has_overlap: bool,
    has_gap: bool,
    has_contact_failure: bool,
    has_alignment_issue: bool,
) -> str:
    if has_overlap:
        if relation_kind == "embedded_attachment":
            return (
                f"{pair_label} is an embedded attachment relation; generic overlap cleanup alone is not enough "
                "to seat the part correctly into the anchor mass."
            )
        return (
            f"{pair_label} is an attachment relation; the pair should stay seated/attached, not just be "
            "pushed apart until overlap reaches zero."
        )
    if has_gap or has_contact_failure:
        return f"{pair_label} is still floating or detached for this attachment relation."
    if has_alignment_issue:
        return f"{pair_label} is still seated on the wrong attachment line for this attachment relation."
    return f"{pair_label} still has wrong attachment semantics."


def _support_item_summary(
    *,
    pair_label: str,
    support_semantics: SceneSupportSemanticsContract,
) -> str:
    return (
        f"{pair_label} is not yet supported as expected on {support_semantics.axis}; "
        "the supported object still needs a stable base/contact relation."
    )


def _symmetry_item_summary(
    *,
    pair_label: str,
    symmetry_semantics: SceneSymmetrySemanticsContract,
) -> str:
    return (
        f"{pair_label} is still asymmetric across {symmetry_semantics.axis}; "
        "the mirrored pair needs another bounded symmetry correction."
    )


def _resolve_capture_scope(
    *,
    target_object: str | None,
    target_objects: list[str] | None,
    collection_name: str | None,
) -> tuple[str | None, list[str], str | None]:
    resolved_target_objects = _dedupe_names(list(target_objects or []))
    if target_object:
        resolved_target_objects = _dedupe_names([target_object, *resolved_target_objects])

    if collection_name:
        collection_payload = get_collection_handler().list_objects(
            collection_name=collection_name,
            recursive=True,
            include_hidden=False,
        )
        collection_objects = [
            str(item.get("name")).strip()
            for item in collection_payload.get("objects", [])
            if isinstance(item, dict) and str(item.get("name") or "").strip()
        ]
        resolved_target_objects = _dedupe_names([*resolved_target_objects, *collection_objects])

    normalized_primary = (
        target_object if target_object else (resolved_target_objects[0] if len(resolved_target_objects) == 1 else None)
    )
    return normalized_primary, resolved_target_objects, collection_name


def _name_anchor_weight(object_name: str) -> int:
    normalized = object_name.strip().lower()
    tokens = _name_role_tokens(object_name)
    trailing_token = tokens[-1] if tokens else ""
    score = 0
    for token, weight in _ANCHOR_ROLE_HINTS:
        if trailing_token == token:
            score += weight * 3
        elif token in tokens:
            score += max(1, weight // 3)
        elif token in normalized:
            score += max(1, weight // 4)
    for token in _ACCESSORY_ROLE_HINTS:
        if trailing_token == token:
            score -= 40
        elif token in tokens:
            score -= 10
        elif token in normalized:
            score -= 15
    return score


def _bbox_volume_or_zero(object_name: str) -> float:
    try:
        bbox = get_scene_handler().get_bounding_box(object_name, world_space=True)
    except Exception:
        return 0.0
    dimensions = bbox.get("dimensions") if isinstance(bbox, dict) else None
    if not isinstance(dimensions, list) or len(dimensions) != 3:
        return 0.0
    try:
        return float(dimensions[0]) * float(dimensions[1]) * float(dimensions[2])
    except Exception:
        return 0.0


def _looks_like_accessory_anchor(object_name: str) -> bool:
    normalized = object_name.strip().lower()
    return any(token in normalized for token in _ACCESSORY_ROLE_HINTS)


def _select_scope_primary_target(object_names: list[str]) -> str | None:
    if not object_names:
        return None
    return max(
        object_names,
        key=lambda name: (
            0 if _looks_like_accessory_anchor(name) else 1,
            _name_anchor_weight(name),
            _bbox_volume_or_zero(name),
            -object_names.index(name),
        ),
    )


def _assembled_target_scope(
    *,
    target_object: str | None,
    target_objects: list[str] | None,
    collection_name: str | None,
) -> SceneAssembledTargetScopeContract:
    def _list_collection_objects(name: str) -> list[str]:
        payload = get_collection_handler().list_objects(
            collection_name=name,
            recursive=True,
            include_hidden=False,
        )
        return [
            str(item.get("name")).strip()
            for item in payload.get("objects", [])
            if isinstance(item, dict) and str(item.get("name") or "").strip()
        ]

    scope_payload = get_spatial_graph_service().build_scope_graph(
        reader=get_scene_handler(),
        target_object=target_object,
        target_objects=target_objects,
        collection_name=collection_name,
        list_collection_objects=_list_collection_objects,
        allow_scene_scope=True,
    )
    return SceneAssembledTargetScopeContract.model_validate(scope_payload)


def _truth_bundle_pairs(
    scope: SceneAssembledTargetScopeContract,
) -> tuple[Literal["none", "primary_to_others", "required_creature_seams"], list[_PlannedTruthPair]]:
    object_names = list(scope.object_names or [])
    if len(object_names) < 2:
        return "none", []

    required_seams = _required_creature_seams(scope)
    if required_seams:
        return (
            "required_creature_seams",
            [
                _PlannedTruthPair(
                    from_object=seam.part_object,
                    to_object=seam.anchor_object,
                    seam=seam,
                )
                for seam in required_seams
            ],
        )

    if scope.primary_target is None:
        return "none", []
    anchor = scope.primary_target
    pairs = [_PlannedTruthPair(from_object=anchor, to_object=name) for name in object_names if name != anchor]
    return ("primary_to_others", pairs) if pairs else ("none", [])


def _build_correction_truth_bundle(
    scene_handler,
    scope: SceneAssembledTargetScopeContract,
    *,
    goal_hint: str | None = None,
) -> tuple[SceneCorrectionTruthBundleContract, dict[str, Any]]:
    relation_graph = get_spatial_graph_service().build_relation_graph(
        reader=scene_handler,
        scope_graph=scope.model_dump(mode="json"),
        goal_hint=goal_hint,
        include_truth_payloads=True,
        include_guided_pairs=True,
    )
    relation_pairs = list(relation_graph.get("pairs") or [])
    truth_pairs = relation_pairs
    if not truth_pairs:
        pairing_strategy: Literal["none", "primary_to_others", "required_creature_seams", "guided_spatial_pairs"] = (
            "none"
        )
    elif any(str(pair.get("pair_source") or "") == "required_creature_seam" for pair in truth_pairs):
        pairing_strategy = "required_creature_seams"
    elif all(str(pair.get("pair_source") or "") == "primary_to_other" for pair in truth_pairs):
        pairing_strategy = "primary_to_others"
    else:
        pairing_strategy = "guided_spatial_pairs"
    checks: list[SceneCorrectionTruthPairContract] = []
    contact_failures = 0
    overlap_pairs = 0
    separated_pairs = 0
    misaligned_pairs = 0

    for pair in truth_pairs:
        from_object = str(pair.get("from_object") or "")
        to_object = str(pair.get("to_object") or "")
        truth_payloads = pair.get("truth_payloads") or {}
        error = cast(str | None, pair.get("error"))
        gap = cast(dict[str, Any] | None, truth_payloads.get("gap"))
        alignment = cast(dict[str, Any] | None, truth_payloads.get("alignment"))
        overlap = cast(dict[str, Any] | None, truth_payloads.get("overlap"))
        contact_assertion_payload = truth_payloads.get("contact_assertion")
        contact_assertion = (
            SceneAssertionPayloadContract.model_validate(contact_assertion_payload)
            if isinstance(contact_assertion_payload, dict)
            else None
        )

        if gap is not None and str(gap.get("relation") or "").lower() == "separated":
            separated_pairs += 1
        if overlap is not None and bool(overlap.get("overlaps")):
            overlap_pairs += 1
        if (
            alignment is not None
            and not bool(alignment.get("is_aligned"))
            and not (contact_assertion is not None and contact_assertion.passed)
        ):
            misaligned_pairs += 1
        if contact_assertion is not None and not contact_assertion.passed:
            contact_failures += 1

        attachment_payload = pair.get("attachment_semantics")
        support_payload = pair.get("support_semantics")
        symmetry_payload = pair.get("symmetry_semantics")
        semantics_contract = (
            SceneAttachmentSemanticsContract.model_validate(attachment_payload)
            if isinstance(attachment_payload, dict)
            else None
        )
        support_contract = (
            SceneSupportSemanticsContract.model_validate(support_payload) if isinstance(support_payload, dict) else None
        )
        symmetry_contract = (
            SceneSymmetrySemanticsContract.model_validate(symmetry_payload)
            if isinstance(symmetry_payload, dict)
            else None
        )

        checks.append(
            SceneCorrectionTruthPairContract(
                from_object=from_object,
                to_object=to_object,
                relation_pair_id=cast(str | None, pair.get("pair_id")),
                relation_kinds=cast(list[SceneRelationKindLiteral], list(pair.get("relation_kinds") or [])),
                relation_verdicts=cast(
                    list[SceneRelationVerdictLiteral],
                    list(pair.get("relation_verdicts") or []),
                ),
                gap=gap,
                alignment=alignment,
                overlap=overlap,
                contact_assertion=contact_assertion,
                attachment_semantics=semantics_contract,
                support_semantics=support_contract,
                symmetry_semantics=symmetry_contract,
                error=error,
            )
        )

    return (
        SceneCorrectionTruthBundleContract(
            scope=scope,
            summary=SceneCorrectionTruthSummaryContract(
                pairing_strategy=pairing_strategy,
                pair_count=len(truth_pairs),
                evaluated_pairs=sum(1 for item in checks if item.error is None),
                contact_failures=contact_failures,
                overlap_pairs=overlap_pairs,
                separated_pairs=separated_pairs,
                misaligned_pairs=misaligned_pairs,
            ),
            checks=checks,
        ),
        relation_graph,
    )


def _pair_label(from_object: str, to_object: str) -> str:
    return f"{from_object} -> {to_object}"


def _contact_semantics_note(
    *,
    gap_payload: dict[str, Any] | None,
    contact_assertion: SceneAssertionPayloadContract | None,
) -> str | None:
    if contact_assertion is None:
        return None

    details = contact_assertion.details or {}
    actual = contact_assertion.actual or {}
    measurement_basis = str(details.get("measurement_basis") or (gap_payload or {}).get("measurement_basis") or "")
    bbox_relation = str(details.get("bbox_relation") or (gap_payload or {}).get("bbox_relation") or "")
    measured_relation = str(actual.get("relation") or (gap_payload or {}).get("relation") or "")

    if (
        measurement_basis == "mesh_surface"
        and bbox_relation in {"contact", "touching"}
        and measured_relation == "separated"
    ):
        return "Bounding boxes touch, but the measured mesh surfaces still have a real gap."
    return None


def _attachment_verdict(
    *,
    relation_kind: _CreatureRelationKind | None = None,
    seam_kind: _CreatureSeamKind | None = None,
    gap_payload: dict[str, Any] | None,
    alignment_payload: dict[str, Any] | None,
    overlap_payload: dict[str, Any] | None,
    contact_assertion: SceneAssertionPayloadContract | None,
) -> Literal["seated_contact", "floating_gap", "intersecting", "misaligned_attachment", "needs_followup"]:
    if overlap_payload is not None and bool(overlap_payload.get("overlaps")):
        return "intersecting"
    if contact_assertion is not None:
        if contact_assertion.passed:
            return "seated_contact"
        actual_relation = str((contact_assertion.actual or {}).get("relation") or "").lower()
        if actual_relation == "separated":
            return "floating_gap"
        if actual_relation == "overlapping":
            return "intersecting"
    if gap_payload is not None and str(gap_payload.get("relation") or "").lower() == "separated":
        return "floating_gap"
    if alignment_payload is not None and not bool(alignment_payload.get("is_aligned")):
        return "misaligned_attachment"
    return "needs_followup"


def _has_actionable_attachment_alignment_issue(
    *,
    attachment_semantics: SceneAttachmentSemanticsContract | None,
    alignment_payload: dict[str, Any] | None,
    contact_assertion: SceneAssertionPayloadContract | None,
) -> bool:
    """Return True only when alignment drift should remain an attachment finding."""

    if alignment_payload is None or bool(alignment_payload.get("is_aligned")):
        return False
    if contact_assertion is not None and contact_assertion.passed:
        return False
    return attachment_semantics is None or attachment_semantics.attachment_verdict == "misaligned_attachment"


def _preferred_attach_surface_axis(
    *,
    gap_payload: dict[str, Any] | None,
    alignment_payload: dict[str, Any] | None,
) -> Literal["X", "Y", "Z"]:
    axis_gap = (gap_payload or {}).get("axis_gap")
    if isinstance(axis_gap, dict) and axis_gap:
        axis_by_gap = sorted(
            ((str(axis_name).upper(), float(axis_value)) for axis_name, axis_value in axis_gap.items()),
            key=lambda item: (item[1], item[0]),
            reverse=True,
        )
        if axis_by_gap and axis_by_gap[0][1] > 1e-6 and axis_by_gap[0][0] in {"X", "Y", "Z"}:
            return cast(Literal["X", "Y", "Z"], axis_by_gap[0][0])

    deltas = (alignment_payload or {}).get("deltas")
    if isinstance(deltas, dict) and deltas:
        axis_by_delta = sorted(
            ((str(axis_name).upper(), abs(float(axis_value))) for axis_name, axis_value in deltas.items()),
            key=lambda item: (item[1], item[0]),
            reverse=True,
        )
        if axis_by_delta and axis_by_delta[0][0] in {"X", "Y", "Z"}:
            return cast(Literal["X", "Y", "Z"], axis_by_delta[0][0])

    return "X"


def _preferred_attach_surface_side(
    *,
    axis_name: Literal["X", "Y", "Z"],
    alignment_payload: dict[str, Any] | None,
) -> Literal["positive", "negative"]:
    deltas = (alignment_payload or {}).get("deltas")
    if not isinstance(deltas, dict):
        return "positive"
    axis_delta = deltas.get(axis_name.lower())
    if axis_delta is None:
        return "positive"
    return "negative" if float(axis_delta) >= 0.0 else "positive"


def _build_truth_followup(bundle: SceneCorrectionTruthBundleContract) -> SceneTruthFollowupContract:
    if bundle.summary.pair_count == 0:
        return SceneTruthFollowupContract(
            scope=bundle.scope,
            continue_recommended=False,
            message="No pairwise truth checks are available for this assembled target scope yet.",
            focus_pairs=[],
            items=[],
            macro_candidates=[],
        )

    items: list[SceneTruthFollowupItemContract] = []
    macro_candidates: list[SceneRepairMacroCandidateContract] = []
    focus_pairs: list[str] = []
    seen_pairs: set[str] = set()
    pair_issue_kinds: dict[str, set[str]] = {}
    pair_attachment_semantics: dict[str, SceneAttachmentSemanticsContract] = {}
    pair_support_semantics: dict[str, SceneSupportSemanticsContract] = {}
    pair_symmetry_semantics: dict[str, SceneSymmetrySemanticsContract] = {}
    pair_checks_by_label: dict[str, SceneCorrectionTruthPairContract] = {}

    for check in bundle.checks:
        pair_label = _pair_label(check.from_object, check.to_object)
        pair_checks_by_label[pair_label] = check
        pair_items: list[SceneTruthFollowupItemContract] = []
        if check.error:
            pair_items.append(
                SceneTruthFollowupItemContract(
                    kind="measurement_error",
                    summary=f"Truth checks failed for {pair_label}: {check.error}",
                    priority="high",
                    from_object=check.from_object,
                    to_object=check.to_object,
                    relation_pair_id=check.relation_pair_id,
                    relation_kinds=list(check.relation_kinds or []),
                    relation_verdicts=list(check.relation_verdicts or []),
                )
            )
        else:
            contact_note = _contact_semantics_note(gap_payload=check.gap, contact_assertion=check.contact_assertion)
            attachment_semantics = check.attachment_semantics
            attachment_relation = _attachment_relation(check.from_object, check.to_object)
            if attachment_semantics is None and attachment_relation is not None:
                relation_kind, part_object, anchor_object = attachment_relation
                attachment_semantics = SceneAttachmentSemanticsContract(
                    relation_kind=relation_kind,
                    seam_kind=_attachment_seam_kind(part_object, anchor_object),
                    part_object=part_object,
                    anchor_object=anchor_object,
                    required_seam=False,
                    preferred_macro=_preferred_attachment_macro(relation_kind),
                    attachment_verdict=_attachment_verdict(
                        relation_kind=relation_kind,
                        seam_kind=_attachment_seam_kind(part_object, anchor_object),
                        gap_payload=check.gap,
                        alignment_payload=check.alignment,
                        overlap_payload=check.overlap,
                        contact_assertion=check.contact_assertion,
                    ),
                )
            has_contact_failure = check.contact_assertion is not None and not check.contact_assertion.passed
            has_gap = check.gap is not None and str(check.gap.get("relation") or "").lower() == "separated"
            has_overlap = check.overlap is not None and bool(check.overlap.get("overlaps"))
            has_alignment_issue = _has_actionable_attachment_alignment_issue(
                attachment_semantics=attachment_semantics,
                alignment_payload=check.alignment,
                contact_assertion=check.contact_assertion,
            )
            if attachment_semantics is not None and (
                has_contact_failure or has_gap or has_overlap or has_alignment_issue
            ):
                pair_attachment_semantics[pair_label] = attachment_semantics
                pair_items.append(
                    SceneTruthFollowupItemContract(
                        kind="attachment",
                        summary=_attachment_item_summary(
                            pair_label=pair_label,
                            relation_kind=attachment_semantics.relation_kind,
                            has_overlap=has_overlap,
                            has_gap=has_gap,
                            has_contact_failure=has_contact_failure,
                            has_alignment_issue=has_alignment_issue,
                        ),
                        priority="high",
                        from_object=check.from_object,
                        to_object=check.to_object,
                        tool_name="scene_assert_contact",
                        relation_pair_id=check.relation_pair_id,
                        relation_kinds=list(check.relation_kinds or []),
                        relation_verdicts=list(check.relation_verdicts or []),
                    )
                )
            if check.support_semantics is not None and check.support_semantics.verdict != "supported":
                pair_support_semantics[pair_label] = check.support_semantics
                pair_items.append(
                    SceneTruthFollowupItemContract(
                        kind="support",
                        summary=_support_item_summary(
                            pair_label=pair_label,
                            support_semantics=check.support_semantics,
                        ),
                        priority="high",
                        from_object=check.from_object,
                        to_object=check.to_object,
                        tool_name="scene_relation_graph",
                        relation_pair_id=check.relation_pair_id,
                        relation_kinds=list(check.relation_kinds or []),
                        relation_verdicts=list(check.relation_verdicts or []),
                    )
                )
            if check.symmetry_semantics is not None and check.symmetry_semantics.verdict != "symmetric":
                pair_symmetry_semantics[pair_label] = check.symmetry_semantics
                pair_items.append(
                    SceneTruthFollowupItemContract(
                        kind="symmetry",
                        summary=_symmetry_item_summary(
                            pair_label=pair_label,
                            symmetry_semantics=check.symmetry_semantics,
                        ),
                        priority="high",
                        from_object=check.from_object,
                        to_object=check.to_object,
                        tool_name="scene_assert_symmetry",
                        relation_pair_id=check.relation_pair_id,
                        relation_kinds=list(check.relation_kinds or []),
                        relation_verdicts=list(check.relation_verdicts or []),
                    )
                )
            if check.contact_assertion is not None and not check.contact_assertion.passed:
                pair_items.append(
                    SceneTruthFollowupItemContract(
                        kind="contact_failure",
                        summary=(
                            f"{pair_label} failed the contact assertion: {contact_note}"
                            if contact_note
                            else f"{pair_label} failed the contact assertion."
                        ),
                        priority="high",
                        from_object=check.from_object,
                        to_object=check.to_object,
                        tool_name="scene_assert_contact",
                        relation_pair_id=check.relation_pair_id,
                        relation_kinds=list(check.relation_kinds or []),
                        relation_verdicts=list(check.relation_verdicts or []),
                    )
                )
            if check.gap is not None and str(check.gap.get("relation") or "").lower() == "separated":
                pair_items.append(
                    SceneTruthFollowupItemContract(
                        kind="gap",
                        summary=(
                            f"{pair_label} still has measurable surface separation. {contact_note}"
                            if contact_note
                            else f"{pair_label} still has measurable separation."
                        ),
                        priority="normal",
                        from_object=check.from_object,
                        to_object=check.to_object,
                        tool_name="scene_measure_gap",
                        relation_pair_id=check.relation_pair_id,
                        relation_kinds=list(check.relation_kinds or []),
                        relation_verdicts=list(check.relation_verdicts or []),
                    )
                )
            if check.overlap is not None and bool(check.overlap.get("overlaps")):
                pair_items.append(
                    SceneTruthFollowupItemContract(
                        kind="overlap",
                        summary=f"{pair_label} still overlaps.",
                        priority="high",
                        from_object=check.from_object,
                        to_object=check.to_object,
                        tool_name="scene_measure_overlap",
                        relation_pair_id=check.relation_pair_id,
                        relation_kinds=list(check.relation_kinds or []),
                        relation_verdicts=list(check.relation_verdicts or []),
                    )
                )
            if has_alignment_issue:
                pair_items.append(
                    SceneTruthFollowupItemContract(
                        kind="alignment",
                        summary=f"{pair_label} is still misaligned.",
                        priority="normal",
                        from_object=check.from_object,
                        to_object=check.to_object,
                        tool_name="scene_measure_alignment",
                        relation_pair_id=check.relation_pair_id,
                        relation_kinds=list(check.relation_kinds or []),
                        relation_verdicts=list(check.relation_verdicts or []),
                    )
                )
        items.extend(pair_items)

        if any(item.from_object == check.from_object and item.to_object == check.to_object for item in items):
            if pair_label not in seen_pairs:
                seen_pairs.add(pair_label)
                focus_pairs.append(pair_label)
            pair_issue_kinds[pair_label] = {item.kind for item in pair_items}

    for pair_label in focus_pairs:
        issue_kinds = pair_issue_kinds.get(pair_label, set())
        if not issue_kinds:
            continue
        if "measurement_error" in issue_kinds:
            continue
        from_object, to_object = pair_label.split(" -> ", 1)
        pair_check = pair_checks_by_label.get(pair_label)
        attachment_semantics = pair_attachment_semantics.get(pair_label)
        if attachment_semantics is not None:
            preferred_macro = attachment_semantics.preferred_macro or _preferred_attachment_macro(
                attachment_semantics.relation_kind
            )
            if attachment_semantics.attachment_verdict == "intersecting" and attachment_semantics.relation_kind in {
                "segment_attachment",
                "seated_attachment",
            }:
                preferred_macro = "macro_attach_part_to_surface"
            if preferred_macro == "macro_attach_part_to_surface":
                surface_axis = _preferred_attach_surface_axis(
                    gap_payload=pair_check.gap if pair_check is not None else None,
                    alignment_payload=pair_check.alignment if pair_check is not None else None,
                )
                surface_side = _preferred_attach_surface_side(
                    axis_name=surface_axis,
                    alignment_payload=pair_check.alignment if pair_check is not None else None,
                )
                macro_candidates.append(
                    SceneRepairMacroCandidateContract(
                        macro_name="macro_attach_part_to_surface",
                        reason=(
                            "Use a bounded surface-seating move for this attachment seam instead of treating "
                            "intersecting parts as a generic side-push cleanup."
                        ),
                        priority="high",
                        arguments_hint={
                            "part_object": attachment_semantics.part_object,
                            "surface_object": attachment_semantics.anchor_object,
                            "surface_axis": surface_axis,
                            "surface_side": surface_side,
                            "align_mode": "center",
                            "gap": 0.0,
                        },
                    )
                )
                continue
            macro_candidates.append(
                SceneRepairMacroCandidateContract(
                    macro_name="macro_align_part_with_contact",
                    reason=(
                        "Use a bounded attachment/contact repair for this seam instead of relying on generic "
                        "overlap cleanup alone."
                    ),
                    priority="high",
                    arguments_hint={
                        "part_object": attachment_semantics.part_object,
                        "reference_object": attachment_semantics.anchor_object,
                        "target_relation": "contact",
                        "align_mode": "none",
                        "preserve_side": True,
                    },
                )
            )
            continue
        support_semantics = pair_support_semantics.get(pair_label)
        if support_semantics is not None:
            macro_candidates.append(
                SceneRepairMacroCandidateContract(
                    macro_name="macro_place_supported_pair",
                    reason=(
                        "Use a bounded support-placement move so the supported object rests on the intended base "
                        "instead of relying on free-form transforms."
                    ),
                    priority="high",
                    arguments_hint={
                        "supported_object": support_semantics.supported_object,
                        "support_object": support_semantics.support_object,
                        "axis": support_semantics.axis,
                        "gap": 0.0,
                    },
                )
            )
            continue
        symmetry_semantics = pair_symmetry_semantics.get(pair_label)
        if symmetry_semantics is not None:
            macro_candidates.append(
                SceneRepairMacroCandidateContract(
                    macro_name="macro_place_symmetry_pair",
                    reason=(
                        "Use a bounded symmetry placement move so the pair is re-mirrored instead of relying on "
                        "free-form manual offsets."
                    ),
                    priority="high",
                    arguments_hint={
                        "left_object": symmetry_semantics.left_object,
                        "right_object": symmetry_semantics.right_object,
                        "axis": symmetry_semantics.axis,
                    },
                )
            )
            continue
        if "overlap" in issue_kinds:
            macro_candidates.append(
                SceneRepairMacroCandidateContract(
                    macro_name="macro_cleanup_part_intersections",
                    reason="Use a bounded cleanup push to separate the overlapping pair without broad manual re-placement.",
                    priority="high",
                    arguments_hint={
                        "part_object": from_object,
                        "reference_object": to_object,
                        "gap": 0.0,
                        "preserve_side": True,
                    },
                )
            )
            continue
        if not issue_kinds.intersection({"contact_failure", "gap", "alignment"}):
            continue
        macro_candidates.append(
            SceneRepairMacroCandidateContract(
                macro_name="macro_align_part_with_contact",
                reason="Use a bounded repair nudge to restore contact/alignment without re-placing the pair from scratch.",
                priority="high" if "contact_failure" in issue_kinds else "normal",
                arguments_hint={
                    "part_object": from_object,
                    "reference_object": to_object,
                    "target_relation": "contact",
                    "align_mode": "none",
                    "preserve_side": True,
                },
            )
        )

    return SceneTruthFollowupContract(
        scope=bundle.scope,
        continue_recommended=bool(items),
        message=(
            f"Truth follow-up identified {len(items)} actionable finding(s), plus {len(macro_candidates)} repair macro candidate(s), across {len(focus_pairs)} pair(s)."
            if items
            else "Truth follow-up found no actionable pairwise issues for the current assembled target scope."
        ),
        focus_pairs=focus_pairs,
        items=items,
        macro_candidates=macro_candidates,
    )


def _repeated_focus(current: list[str], prior: list[str]) -> list[str]:
    prior_keys = {_normalized_focus_key(item) for item in prior if _normalized_focus_key(item)}
    repeated: list[str] = []
    for item in current:
        normalized = _normalized_focus_key(item)
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

    session = await get_session_capability_state_async(ctx)
    goal = goal_override or session.goal
    if not goal:
        return _compare_response(
            action=response_action,
            checkpoint_path=str(checkpoint),
            checkpoint_label=checkpoint_label,
            goal=None,
            target_object=target_object,
            target_view=target_view,
            reference_ids=[],
            reference_labels=[],
            error="Set an active goal with router_set_goal(...) before comparing a checkpoint, or pass goal_override.",
        )

    references = list(session.reference_images or [])
    selected_reference_records = select_reference_records_for_target(
        references,
        target_object=target_object,
        target_view=target_view,
    )
    if not selected_reference_records:
        return _compare_response(
            action=response_action,
            checkpoint_path=str(checkpoint),
            checkpoint_label=checkpoint_label,
            goal=goal,
            target_object=target_object,
            target_view=target_view,
            reference_ids=[],
            reference_labels=[],
            error="No matching reference images are attached for the requested target_object/target_view.",
        )

    reference_images = build_reference_capture_images(selected_reference_records)
    vision_request = VisionRequest(
        goal=goal,
        images=(
            VisionImageInput(
                path=str(checkpoint),
                role="after",
                label=checkpoint_label or checkpoint.name,
                media_type=mimetypes.guess_type(str(checkpoint))[0] or "image/png",
            ),
            *tuple(
                VisionImageInput(
                    path=item.image_path,
                    role="reference",
                    label=item.label,
                    media_type=item.media_type,
                )
                for item in reference_images
            ),
        ),
        target_object=target_object,
        prompt_hint=" | ".join(
            part
            for part in (
                prompt_hint,
                "comparison_mode=checkpoint_vs_reference",
                f"checkpoint_label={checkpoint_label}" if checkpoint_label else None,
                f"target_view={target_view}" if target_view else None,
                *[
                    f"reference[{index}] label={record.label}"
                    for index, record in enumerate(selected_reference_records, start=1)
                    if record.label
                ],
            )
            if part
        )
        or None,
        metadata={
            "source": response_action,
            "checkpoint_path": str(checkpoint),
            "reference_count": len(selected_reference_records),
        },
    )
    outcome = await run_vision_assist(
        ctx,
        request=vision_request,
        resolver=get_vision_backend_resolver(),
    )
    vision_assistant = to_vision_assistant_contract(outcome)
    return _compare_response(
        action=response_action,
        checkpoint_path=str(checkpoint),
        checkpoint_label=checkpoint_label,
        goal=goal,
        target_object=target_object,
        target_view=target_view,
        reference_ids=[item.reference_id for item in selected_reference_records],
        reference_labels=[item.label or item.reference_id for item in selected_reference_records],
        vision_assistant=vision_assistant,
        message=(
            f"Compared checkpoint '{checkpoint_label or checkpoint.name}' against {len(selected_reference_records)} reference image(s)."
            if outcome.status == "success"
            else "Checkpoint comparison executed but vision assistance did not complete successfully."
        ),
        error=vision_assistant.rejection_reason if vision_assistant.status != "success" else None,
    )


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
    reference_understanding_gate_ids = list(session.reference_understanding_gate_ids or [])
    goal = session.goal
    if not readiness.compare_ready or goal is None:
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
            error=_guided_stage_reference_recovery_error(
                readiness,
                target_object=target_object,
                target_objects=target_objects,
                collection_name=collection_name,
            ),
        )

    try:
        resolved_target_object, resolved_target_objects, resolved_collection_name = _resolve_capture_scope(
            target_object=target_object,
            target_objects=target_objects,
            collection_name=collection_name,
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
            error=str(exc),
        )
    assembled_target_scope = _assembled_target_scope(
        target_object=resolved_target_object,
        target_objects=resolved_target_objects,
        collection_name=resolved_collection_name,
    )
    capture_target_object = resolved_target_object or assembled_target_scope.primary_target
    scope_error = _guided_checkpoint_scope_error(session.guided_flow_state, assembled_target_scope)
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
            error=scope_error,
        )

    references = list(session.reference_images or [])
    selected_reference_records = select_reference_records_for_target(
        references,
        target_object=resolved_target_object,
        target_view=target_view,
    )
    if not selected_reference_records:
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
    runtime_max_tokens, runtime_max_images, runtime_model_name = _resolve_hybrid_budget_runtime(resolver)
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
        int(VISION_ASSIST_POLICY.max_input_chars * truth_char_share),
        max(truth_char_floor, runtime_max_tokens * 12),
    )
    budgeted_truth_bundle, scope_trimmed = _trim_truth_bundle_to_budget(
        truth_bundle=truth_bundle,
        pair_budget=pair_budget,
        max_truth_chars=max_truth_chars,
    )
    truth_followup = _build_truth_followup(budgeted_truth_bundle)
    reference_images = build_reference_capture_images(selected_reference_records)
    vision_request = build_vision_request_from_stage_captures(
        captures,
        goal=goal,
        target_object=resolved_target_object,
        reference_images=reference_images,
        truth_summary=budgeted_truth_bundle.model_dump(mode="json"),
        prompt_hint=" | ".join(
            part
            for part in (
                prompt_hint,
                "comparison_mode=stage_checkpoint_vs_reference",
                f"checkpoint_label={checkpoint_label}" if checkpoint_label else None,
                f"preset_profile={preset_profile}",
                f"collection_name={resolved_collection_name}" if resolved_collection_name else None,
                f"target_objects={','.join(resolved_target_objects)}" if resolved_target_objects else None,
                f"target_view={target_view}" if target_view else None,
                *[f"capture[{index}] label={capture.label}" for index, capture in enumerate(captures, start=1)],
                *[
                    f"reference[{index}] label={record.label}"
                    for index, record in enumerate(selected_reference_records, start=1)
                    if record.label
                ],
            )
            if part
        )
        or None,
        metadata={
            "source": "compare_stage_checkpoint",
            "checkpoint_id": checkpoint_id,
            "preset_profile": preset_profile,
            "capture_count": len(captures),
            "collection_name": resolved_collection_name,
            "target_objects": list(resolved_target_objects),
            "assembled_target_scope": assembled_target_scope.model_dump(mode="json"),
        },
    )
    outcome = await run_vision_assist(
        ctx,
        request=vision_request,
        resolver=resolver,
    )
    vision_assistant = to_vision_assistant_contract(outcome)
    silhouette_analysis = _build_silhouette_analysis_payload(
        selected_reference_records=selected_reference_records,
        captures=captures,
        target_view=target_view,
    )
    action_hints = _build_action_hints_from_silhouette(
        silhouette_analysis,
        target_object=resolved_target_object or assembled_target_scope.primary_target,
    )
    part_segmentation = _configured_part_segmentation()
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
    budget_control = ReferenceHybridBudgetControlContract(
        model_name=runtime_model_name,
        max_input_chars=VISION_ASSIST_POLICY.max_input_chars,
        max_output_tokens=runtime_max_tokens,
        max_images=runtime_max_images,
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
    refinement_route = _select_refinement_route(staged_compare_contract)
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

    return _stage_compare_response(
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
        vision_assistant=vision_assistant,
        truth_bundle=budgeted_truth_bundle,
        truth_followup=truth_followup,
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
        message=(
            f"Captured and compared stage checkpoint '{checkpoint_label or checkpoint_id}' using {len(captures)} deterministic view(s)."
            if outcome.status == "success"
            else "Stage checkpoint capture executed but vision assistance did not complete successfully."
        ),
        error=vision_assistant.rejection_reason if vision_assistant.status != "success" else None,
    )


async def reference_images(
    ctx: Context,
    action: str,
    source_path: str | None = None,
    images: list[dict[str, Any]] | None = None,
    source_paths: list[str] | None = None,
    reference_id: str | None = None,
    label: str | None = None,
    notes: str | None = None,
    target_object: str | None = None,
    target_view: str | None = None,
) -> ReferenceImagesResponseContract:
    """Manage goal-scoped reference images for later vision/capture interpretation."""

    normalized_action = str(action).lower()
    if normalized_action not in {"attach", "list", "remove", "clear"}:
        return _as_response(
            action="list", goal=None, references=[], error="action must be attach, list, remove, or clear"
        )

    session = await get_session_capability_state_async(ctx)
    stage_for_later_adoption = not session_has_ready_guided_reference_goal(session)
    active_references = list(session.reference_images or [])
    pending_references = list(session.pending_reference_images or [])
    visible_references = (
        _merge_visible_references(active_references, pending_references)
        if session.goal is not None
        else list(pending_references)
    )

    if normalized_action == "list":
        return _as_response(action="list", goal=session.goal, references=_sorted_references(visible_references))

    if normalized_action == "clear":
        _delete_reference_files(visible_references)
        if active_references:
            session = await replace_session_reference_images_async(ctx, [])
            if session.goal is not None:
                await refresh_reference_understanding_summary_async(ctx, session=session)
        if pending_references:
            await replace_session_pending_reference_images_async(ctx, [])

        if active_references and pending_references:
            message = "Cleared active and pending reference images."
        elif pending_references or session.goal is None:
            message = "Cleared pending reference images."
        else:
            message = "Cleared session reference images."

        if stage_for_later_adoption or pending_references:
            ctx_info(ctx, "[REFERENCE] Cleared visible session reference images")
        else:
            ctx_info(ctx, "[REFERENCE] Cleared session reference images")
        return _as_response(action="clear", goal=session.goal, references=[], message=message)

    if normalized_action == "remove":
        if not reference_id:
            return _as_response(
                action="remove",
                goal=session.goal,
                references=_sorted_references(visible_references),
                error="reference_id is required for remove",
            )
        remaining: list[dict] = []
        remaining_pending: list[dict] = []
        removed_records: list[dict] = []
        for item in active_references:
            if item.get("reference_id") == reference_id:
                removed_records.append(item)
                continue
            remaining.append(item)
        for item in pending_references:
            if item.get("reference_id") == reference_id:
                removed_records.append(item)
                continue
            remaining_pending.append(item)
        if not removed_records:
            return _as_response(
                action="remove",
                goal=session.goal,
                references=_sorted_references(visible_references),
                error=f"Reference image not found: {reference_id}",
            )
        _delete_reference_files(removed_records)
        if len(remaining) != len(active_references):
            session = await replace_session_reference_images_async(ctx, remaining)
            if session.goal is not None:
                await refresh_reference_understanding_summary_async(ctx, session=session)
        if len(remaining_pending) != len(pending_references):
            await replace_session_pending_reference_images_async(ctx, remaining_pending)
        remaining_visible = (
            _merge_visible_references(remaining, remaining_pending) if session.goal is not None else remaining_pending
        )
        if stage_for_later_adoption or len(remaining_pending) != len(pending_references):
            ctx_info(ctx, f"[REFERENCE] Removed visible session reference image {reference_id}")
        else:
            ctx_info(ctx, f"[REFERENCE] Removed reference image {reference_id}")
        return _as_response(
            action="remove",
            goal=session.goal,
            references=_sorted_references(remaining_visible),
            removed_reference_id=reference_id,
            message=f"Removed reference image '{reference_id}'.",
        )

    try:
        canonical_arguments = canonicalize_reference_images_arguments(
            {
                key: value
                for key, value in {
                    "action": normalized_action,
                    "source_path": source_path,
                    "images": images,
                    "source_paths": source_paths,
                }.items()
                if value is not None
            }
        )
    except ValueError as exc:
        return _as_response(
            action="attach",
            goal=session.goal,
            references=_sorted_references(visible_references),
            error=str(exc),
        )
    source_path = cast(str | None, canonical_arguments.get("source_path"))

    if not source_path:
        return _as_response(
            action="attach",
            goal=session.goal,
            references=_sorted_references(visible_references),
            error="source_path is required for attach",
        )

    try:
        source = _validate_local_reference_path(source_path)
        stored_path, host_visible_path = _copy_reference_image(source)
    except ValueError as exc:
        return _as_response(
            action="attach",
            goal=session.goal,
            references=_sorted_references(visible_references),
            error=str(exc),
        )

    reference = {
        "reference_id": f"ref_{uuid4().hex[:8]}",
        "goal": session.goal or "__pending_goal__",
        "label": label,
        "notes": notes,
        "target_object": target_object,
        "target_view": target_view,
        "media_type": mimetypes.guess_type(str(source))[0] or "image/png",
        "source_kind": "local_path",
        "original_path": str(source),
        "stored_path": stored_path,
        "host_visible_path": host_visible_path,
        "added_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }
    if stage_for_later_adoption:
        pending_updated = [*pending_references, reference]
        await replace_session_pending_reference_images_async(ctx, pending_updated)
        visible_updated = (
            _merge_visible_references(active_references, pending_updated)
            if session.goal is not None
            else pending_updated
        )
        ctx_info(ctx, f"[REFERENCE] Attached pending reference image {reference['reference_id']}")
        return _as_response(
            action="attach",
            goal=session.goal,
            references=_sorted_references(visible_updated),
            message=(
                f"Attached pending reference image '{reference['reference_id']}'. "
                "It will be adopted automatically when the guided goal session becomes ready."
            ),
        )

    updated_active = [*active_references, reference]
    session = await replace_session_reference_images_async(ctx, updated_active)
    session = await refresh_reference_understanding_summary_async(ctx, session=session)
    ctx_info(ctx, f"[REFERENCE] Attached reference image {reference['reference_id']} for goal '{session.goal}'")
    return _as_response(
        action="attach",
        goal=session.goal,
        references=_sorted_references(updated_active),
        message=f"Attached reference image '{reference['reference_id']}'.",
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

    session = await get_session_capability_state_async(ctx)
    effective_goal = goal_override or session.goal
    if not effective_goal:
        return _compare_response(
            action="compare_current_view",
            checkpoint_path="",
            checkpoint_label=checkpoint_label,
            goal=None,
            target_object=target_object,
            target_view=target_view,
            reference_ids=[],
            reference_labels=[],
            error="Set an active goal with router_set_goal(...) before comparing the current view, or pass goal_override.",
        )

    try:
        b64_data = get_scene_handler().get_viewport(
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
        )
    except RuntimeError as exc:
        return _compare_response(
            action="compare_current_view",
            checkpoint_path="",
            checkpoint_label=checkpoint_label,
            goal=goal_override,
            target_object=target_object,
            target_view=target_view,
            reference_ids=[],
            reference_labels=[],
            error=str(exc),
        )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"checkpoint_compare_{timestamp}_{uuid4().hex[:8]}.jpg"
    latest_name = "checkpoint_compare_latest.jpg"
    internal_file, internal_latest, _external_file, _external_latest = get_viewport_output_paths(
        filename,
        latest_name=latest_name,
    )
    image_bytes = base64.b64decode(b64_data)
    internal_file.write_bytes(image_bytes)
    internal_latest.write_bytes(image_bytes)

    view_diagnostics_hints: list[ReferenceViewDiagnosticsHintContract] | None = None
    diagnostic_target = target_object or focus_target
    if diagnostic_target:
        use_explicit_scene_camera = bool(camera_name and camera_name != "USER_PERSPECTIVE")
        diagnostics_focus_target = focus_target
        diagnostics_view_name = view_name
        diagnostics_orbit_horizontal = orbit_horizontal
        diagnostics_orbit_vertical = orbit_vertical
        diagnostics_zoom_factor = zoom_factor
        if persist_view and not use_explicit_scene_camera:
            diagnostics_focus_target = None
            diagnostics_view_name = None
            diagnostics_orbit_horizontal = 0.0
            diagnostics_orbit_vertical = 0.0
            diagnostics_zoom_factor = None
        try:
            diagnostics_payload = get_scene_handler().get_view_diagnostics(
                target_object=diagnostic_target,
                camera_name=camera_name,
                focus_target=diagnostics_focus_target,
                view_name=diagnostics_view_name,
                orbit_horizontal=diagnostics_orbit_horizontal,
                orbit_vertical=diagnostics_orbit_vertical,
                zoom_factor=diagnostics_zoom_factor,
                persist_view=persist_view,
            )
            candidate_hints = _build_view_diagnostics_hints(
                diagnostics_payload=diagnostics_payload,
                target_object=diagnostic_target,
                camera_name=camera_name,
                focus_target=diagnostics_focus_target,
                view_name=diagnostics_view_name,
                orbit_horizontal=diagnostics_orbit_horizontal,
                orbit_vertical=diagnostics_orbit_vertical,
                zoom_factor=diagnostics_zoom_factor,
            )
            if candidate_hints:
                view_diagnostics_hints = candidate_hints
        except Exception:
            view_diagnostics_hints = None

    compare_result = await _run_checkpoint_compare(
        ctx,
        checkpoint=internal_file,
        checkpoint_label=checkpoint_label,
        target_object=target_object or focus_target,
        target_view=target_view,
        goal_override=goal_override,
        prompt_hint=" | ".join(
            part
            for part in (
                prompt_hint,
                "comparison_mode=current_view_checkpoint",
                f"camera_name={camera_name}" if camera_name else None,
                f"view_name={view_name}" if view_name else None,
                f"shading={shading}",
            )
            if part
        )
        or None,
        response_action="compare_current_view",
    )
    if view_diagnostics_hints:
        compare_result.view_diagnostics_hints = view_diagnostics_hints
    return compare_result


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
    """Capture one deterministic stage view-set and compare it against attached references."""

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
    """Run one session-aware stage checkpoint iteration and return continuation guidance."""

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
    session = await get_session_capability_state_async(ctx)
    hold_in_build = _should_hold_guided_build_loop_in_build(session.guided_flow_state)
    readiness = compare_result.guided_reference_readiness
    goal = compare_result.goal
    correction_focus = _resolve_actionable_focus(compare_result)
    if not correction_focus:
        correction_focus = _resolve_gate_blocker_focus(compare_result)
    action_hints = list(compare_result.action_hints or [])
    gate_blockers_present = bool(compare_result.completion_blockers)
    continue_recommended = bool(correction_focus or action_hints or gate_blockers_present)
    inspect_from_truth_signal = _should_inspect_from_truth_signal(compare_result.correction_candidates)
    inspect_from_gate_blockers = gate_blockers_present
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
        return _iterate_stage_response(
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
            continue_recommended=truth_only_handoff,
            prior_checkpoint_id=None,
            prior_correction_focus=[],
            correction_focus=correction_focus,
            repeated_correction_focus=[],
            stagnation_count=0,
            compare_result=compare_result,
            guided_reference_readiness=readiness,
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

    return _iterate_stage_response(
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
        correction_candidates=compare_result.correction_candidates,
        budget_control=compare_result.budget_control,
        refinement_route=compare_result.refinement_route,
        refinement_handoff=compare_result.refinement_handoff,
        stop_reason=stop_reason,
        message=message,
    )
