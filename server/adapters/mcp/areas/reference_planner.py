# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Planner and budget helpers for staged reference compare responses."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Sequence
from typing import Any, Literal, cast

from server.adapters.mcp.areas.reference_truth import dedupe_names, pair_label
from server.adapters.mcp.contracts.reference import (
    ReferenceCompareComplexityTierLiteral,
    ReferenceCompareDiagnosticsContract,
    ReferenceComparePacketContract,
    ReferenceCompareStageCheckpointResponseContract,
    ReferenceCorrectionCandidateContract,
    ReferenceCorrectionTruthEvidenceContract,
    ReferenceCorrectionVisionEvidenceContract,
    ReferenceImageRecordContract,
    ReferencePlannerBlockerContract,
    ReferencePlannerEvidenceSourceContract,
    ReferencePlannerSourceLiteral,
    ReferencePlannerTargetScopeContract,
    ReferenceRefinementHandoffContract,
    ReferenceRefinementRouteContract,
    ReferenceRefinementToolCandidateContract,
    ReferenceRepairPlannerDetailContract,
    ReferenceRepairPlannerSummaryContract,
)
from server.adapters.mcp.contracts.scene import (
    SceneAssembledTargetScopeContract,
    SceneRepairMacroCandidateContract,
    SceneTruthFollowupContract,
    SceneTruthFollowupItemContract,
)
from server.adapters.mcp.contracts.vision import VisionCaptureImageContract
from server.adapters.mcp.sampling.result_types import (
    VisionAssistContract,
    VisionBoundaryPolicyContract,
    VisionInputSummaryContract,
    VisionIssueContract,
    VisionRecommendedCheckContract,
)
from server.adapters.mcp.vision.runner import VISION_ASSIST_POLICY

LOW_POLY_HINTS: tuple[str, ...] = ("low poly", "low-poly", "blockout")
HARD_SURFACE_HINTS: tuple[str, ...] = (
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
GARMENT_HINTS: tuple[str, ...] = (
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
ANATOMY_HINTS: tuple[str, ...] = (
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
ORGANIC_HINTS: tuple[str, ...] = (
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
SCULPT_RECOMMENDED_TOOLS: tuple[str, ...] = (
    "sculpt_deform_region",
    "sculpt_smooth_region",
    "sculpt_inflate_region",
    "sculpt_pinch_region",
    "sculpt_crease_region",
)

_STRUCTURAL_RELATION_BLOCKER_KINDS: frozenset[str] = frozenset(
    {"contact_failure", "gap", "overlap", "attachment", "support", "symmetry", "measurement_error"}
)
_PROPORTION_BLOCKING_HINT_TYPES: frozenset[str] = frozenset({"rebalance_proportion"})
_VIEW_TOKEN_ALIASES: dict[str, str] = {
    "front": "front",
    "side": "side",
    "profile": "side",
    "top": "top",
    "back": "back",
    "rear": "back",
    "three": "three_quarter",
    "quarter": "three_quarter",
    "3q": "three_quarter",
    "detail": "detail",
    "close": "detail",
    "silhouette": "detail",
}
_PACKET_VIEW_ORDER: tuple[str, ...] = ("front", "side", "top", "back", "three_quarter", "detail")


def _normalize_view_token(value: str | None) -> str | None:
    tokens = [token for token in re.split(r"[^a-z0-9]+", str(value or "").strip().lower()) if token]
    for token in tokens:
        normalized = _VIEW_TOKEN_ALIASES.get(token)
        if normalized is not None:
            return normalized
    return None


def _capture_view_id(capture: VisionCaptureImageContract) -> str | None:
    return _normalize_view_token(capture.preset_name) or _normalize_view_token(capture.label)


def _reference_view_id(reference_record: ReferenceImageRecordContract) -> str | None:
    return _normalize_view_token(reference_record.target_view) or _normalize_view_token(reference_record.label)


def _stable_packet_id(prefix: str, *parts: str) -> str:
    normalized_parts = [re.sub(r"[^a-z0-9]+", "_", part.strip().lower()).strip("_") for part in parts if part.strip()]
    digest = hashlib.sha1("|".join(normalized_parts).encode("utf-8")).hexdigest()[:8]
    slug = "__".join(normalized_parts[:3]) or "packet"
    return f"{prefix}:{slug}:{digest}"


def _unique_preserving_order(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        normalized = value.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        ordered.append(normalized)
    return ordered


def _packet_question_for_view(view_id: str | None, *, scope_label: str | None = None) -> str:
    if scope_label and view_id == "side":
        return (
            f"Compare the side/profile silhouette for the {scope_label} scope. "
            "Focus on depth, arc length, attachment continuity, and obvious proportion drift."
        )
    if scope_label and view_id == "front":
        return (
            f"Compare the front silhouette for the {scope_label} scope. "
            "Focus on visible width, symmetry, attachment readability, and dominant shape mismatches."
        )
    if scope_label:
        return (
            f"Compare the {scope_label} scope against the references. "
            "Focus on the intended local silhouette, attachment/seam state, and dominant shape drift."
        )
    if view_id == "side":
        return (
            "Compare the side/profile silhouette against the references. "
            "Focus on length, depth, arc shape, and obvious proportion drift."
        )
    if view_id == "front":
        return (
            "Compare the front silhouette against the references. "
            "Focus on width, symmetry, primary masses, and dominant shape mismatches."
        )
    if view_id == "top":
        return (
            "Compare the top-view mass layout against the references. "
            "Focus on width balance, spacing, and large placement errors."
        )
    return (
        "Compare this bounded packet against the references. "
        "Focus only on the dominant visible mismatch, required local relations, and the safest next correction."
    )


def resolve_compare_complexity_tier(
    *,
    assembled_target_scope: SceneAssembledTargetScopeContract | None,
    reference_count: int,
    capture_count: int,
    focus_pair_count: int,
) -> ReferenceCompareComplexityTierLiteral:
    scope_kind = assembled_target_scope.scope_kind if assembled_target_scope is not None else "unknown"
    object_count = assembled_target_scope.object_count if assembled_target_scope is not None else 0
    if reference_count >= 6 or focus_pair_count >= 4 or object_count >= 6 or capture_count >= 5:
        return "super_complex"
    if scope_kind in {"collection", "object_set"} or reference_count >= 3 or focus_pair_count >= 1 or object_count >= 3:
        return "complex"
    return "simple"


def build_compare_packets(
    *,
    target_view: str | None,
    captures: Sequence[VisionCaptureImageContract],
    reference_records: Sequence[ReferenceImageRecordContract],
    assembled_target_scope: SceneAssembledTargetScopeContract | None,
    truth_followup: SceneTruthFollowupContract | None,
) -> ReferenceCompareDiagnosticsContract:
    capture_labels_by_view: dict[str, list[str]] = {}
    context_capture_labels: list[str] = []
    for capture in captures:
        view_id = _capture_view_id(capture)
        if view_id is None:
            context_capture_labels.append(capture.label)
            continue
        capture_labels_by_view.setdefault(view_id, []).append(capture.label)

    reference_ids_by_view: dict[str, list[str]] = {}
    generic_reference_ids: list[str] = []
    for reference in reference_records:
        view_id = _reference_view_id(reference)
        if view_id is None:
            generic_reference_ids.append(reference.reference_id)
            continue
        reference_ids_by_view.setdefault(view_id, []).append(reference.reference_id)

    normalized_target_view = _normalize_view_token(target_view)
    available_views = [
        view_id
        for view_id in _PACKET_VIEW_ORDER
        if view_id in capture_labels_by_view or view_id in reference_ids_by_view
    ]
    focus_pairs = list(truth_followup.focus_pairs or []) if truth_followup is not None else []
    complexity_tier = resolve_compare_complexity_tier(
        assembled_target_scope=assembled_target_scope,
        reference_count=len(reference_records),
        capture_count=len(captures),
        focus_pair_count=len(focus_pairs),
    )
    packets: list[ReferenceComparePacketContract] = []

    if complexity_tier == "simple":
        packet_views = [normalized_target_view] if normalized_target_view is not None else available_views[:2]
        packet_views = [view for view in packet_views if view is not None]
        packet_capture_labels = _unique_preserving_order(
            [
                *context_capture_labels,
                *[label for view in packet_views for label in capture_labels_by_view.get(view, [])],
            ]
            or [capture.label for capture in captures]
        )
        packet_reference_ids = _unique_preserving_order(
            [
                *[reference_id for view in packet_views for reference_id in reference_ids_by_view.get(view, [])],
                *generic_reference_ids,
            ]
            or [reference.reference_id for reference in reference_records]
        )
        paired_label = " + ".join(packet_views) if packet_views else "general"
        packets.append(
            ReferenceComparePacketContract(
                packet_id=_stable_packet_id(
                    "packet", "simple", paired_label, *packet_reference_ids, *packet_capture_labels
                ),
                packet_kind="view_scope" if len(packet_views) > 1 else "view",
                packet_label=f"{paired_label} packet" if paired_label != "general" else "simple packet",
                target_view=packet_views[0] if len(packet_views) == 1 else None,
                scope_label=assembled_target_scope.scope_kind if assembled_target_scope is not None else None,
                target_objects=list(assembled_target_scope.object_names or [])
                if assembled_target_scope is not None
                else [],
                reference_ids=packet_reference_ids,
                capture_labels=packet_capture_labels,
                compare_question=_packet_question_for_view(packet_views[0] if len(packet_views) == 1 else None),
            )
        )
    elif focus_pairs:
        packet_views = (
            [normalized_target_view] if normalized_target_view is not None else available_views[:2] or ["front"]
        )
        for focus_pair in focus_pairs:
            from_object, to_object = focus_pair.split(" -> ", 1)
            if complexity_tier == "super_complex":
                active_views = packet_views
            else:
                active_views = [packet_views[0]]
            for view_id in active_views:
                packet_capture_labels = _unique_preserving_order(
                    [
                        *context_capture_labels,
                        *capture_labels_by_view.get(view_id, []),
                    ]
                    or [capture.label for capture in captures]
                )
                packet_reference_ids = _unique_preserving_order(
                    [
                        *reference_ids_by_view.get(view_id, []),
                        *generic_reference_ids,
                    ]
                    or [reference.reference_id for reference in reference_records]
                )
                packet_label = f"{from_object} + {to_object}"
                packets.append(
                    ReferenceComparePacketContract(
                        packet_id=_stable_packet_id(
                            "packet", focus_pair, view_id, *packet_reference_ids, *packet_capture_labels
                        ),
                        packet_kind="view_scope" if complexity_tier == "super_complex" else "scope",
                        packet_label=packet_label,
                        target_view=view_id if complexity_tier == "super_complex" else None,
                        scope_label=packet_label,
                        target_objects=[from_object, to_object],
                        truth_pairs=[focus_pair],
                        reference_ids=packet_reference_ids,
                        capture_labels=packet_capture_labels,
                        compare_question=_packet_question_for_view(view_id, scope_label=packet_label),
                    )
                )
    else:
        packet_views = [normalized_target_view] if normalized_target_view is not None else available_views or ["front"]
        for view_id in packet_views:
            packet_capture_labels = _unique_preserving_order(
                [
                    *context_capture_labels,
                    *capture_labels_by_view.get(view_id, []),
                ]
                or [capture.label for capture in captures]
            )
            packet_reference_ids = _unique_preserving_order(
                [
                    *reference_ids_by_view.get(view_id, []),
                    *generic_reference_ids,
                ]
                or [reference.reference_id for reference in reference_records]
            )
            packets.append(
                ReferenceComparePacketContract(
                    packet_id=_stable_packet_id(
                        "packet", "view", view_id, *packet_reference_ids, *packet_capture_labels
                    ),
                    packet_kind="view",
                    packet_label=f"{view_id} packet",
                    target_view=view_id,
                    target_objects=list(assembled_target_scope.object_names or [])
                    if assembled_target_scope is not None
                    else [],
                    reference_ids=packet_reference_ids,
                    capture_labels=packet_capture_labels,
                    compare_question=_packet_question_for_view(view_id),
                )
            )

    return ReferenceCompareDiagnosticsContract(
        complexity_tier=complexity_tier,
        packet_count=len(packets),
        packet_order=[packet.packet_id for packet in packets],
        synthesis_required=len(packets) > 1,
        synthesis_status="not_needed" if len(packets) <= 1 else "skipped",
        packets=packets,
    )


def synthesize_packet_vision_result(
    packet_results: Sequence[tuple[ReferenceComparePacketContract, VisionAssistContract | None]],
) -> VisionAssistContract | None:
    successful_results = [result for _, result in packet_results if result is not None]
    if not successful_results:
        return None

    goal_summaries = _unique_preserving_order(
        [result.goal_summary for result in successful_results if result.goal_summary]
    )
    reference_match_summaries = _unique_preserving_order(
        [summary for result in successful_results if (summary := result.reference_match_summary)]
    )
    visible_changes = _unique_preserving_order(
        [item for result in successful_results for item in list(result.visible_changes or [])]
    )[:8]
    shape_mismatches = _unique_preserving_order(
        [item for result in successful_results for item in list(result.shape_mismatches or [])]
    )[:6]
    proportion_mismatches = _unique_preserving_order(
        [item for result in successful_results for item in list(result.proportion_mismatches or [])]
    )[:6]
    correction_focus = _unique_preserving_order(
        [item for result in successful_results for item in list(result.correction_focus or [])]
    )[:6]
    next_corrections = _unique_preserving_order(
        [item for result in successful_results for item in list(result.next_corrections or [])]
    )[:6]
    captures_used = _unique_preserving_order(
        [item for result in successful_results for item in list(result.captures_used or [])]
    )

    likely_issues: list[VisionIssueContract] = []
    seen_issue_keys: set[tuple[str, str]] = set()
    for result in successful_results:
        for issue in list(result.likely_issues or []):
            issue_key = (issue.category, issue.summary)
            if issue_key in seen_issue_keys:
                continue
            seen_issue_keys.add(issue_key)
            likely_issues.append(issue)

    recommended_checks: list[VisionRecommendedCheckContract] = []
    seen_check_keys: set[tuple[str, str]] = set()
    for result in successful_results:
        for check in list(result.recommended_checks or []):
            check_key = (check.tool_name, check.reason)
            if check_key in seen_check_keys:
                continue
            seen_check_keys.add(check_key)
            recommended_checks.append(check)

    confidences = [float(result.confidence) for result in successful_results if result.confidence is not None]
    input_summaries = [result.input_summary for result in successful_results if result.input_summary is not None]
    merged_input_summary = (
        VisionInputSummaryContract(
            before_image_count=sum(item.before_image_count for item in input_summaries),
            after_image_count=sum(item.after_image_count for item in input_summaries),
            reference_image_count=sum(item.reference_image_count for item in input_summaries),
            target_object=next(
                (item.target_object for item in input_summaries if item.target_object),
                None,
            ),
        )
        if input_summaries
        else None
    )
    packet_labels = [packet.packet_label for packet, result in packet_results if result is not None]
    summary_prefix = (
        goal_summaries[0]
        if len(goal_summaries) == 1
        else f"Packeted compare synthesized {len(successful_results)} bounded packet result(s)."
    )
    if len(packet_labels) > 1:
        summary_prefix = f"{summary_prefix} Active packets: {', '.join(packet_labels[:4])}."

    return VisionAssistContract(
        backend_kind=successful_results[0].backend_kind,
        backend_name=successful_results[0].backend_name,
        model_name=successful_results[0].model_name,
        vision_contract_profile=successful_results[0].vision_contract_profile,
        goal_summary=summary_prefix,
        reference_match_summary=reference_match_summaries[0] if reference_match_summaries else None,
        visible_changes=visible_changes,
        shape_mismatches=shape_mismatches,
        proportion_mismatches=proportion_mismatches,
        correction_focus=correction_focus,
        likely_issues=likely_issues[:6],
        next_corrections=next_corrections,
        recommended_checks=recommended_checks[:6],
        confidence=(sum(confidences) / len(confidences)) if confidences else None,
        captures_used=captures_used,
        input_summary=merged_input_summary,
        boundary_policy=VisionBoundaryPolicyContract(),
    )


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
    if _contains_any(context_text, GARMENT_HINTS):
        return "garment"
    if _contains_any(context_text, ANATOMY_HINTS):
        return "anatomy"
    if _contains_any(context_text, HARD_SURFACE_HINTS):
        return "hard_surface"
    if _contains_any(context_text, ORGANIC_HINTS):
        return "organic_form"
    return "generic_form"


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

    target_objects = dedupe_names(
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


def select_refinement_route(
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
    low_poly_intent = _contains_any(_refinement_context_text(compare_result), LOW_POLY_HINTS)
    source_signals = _planner_source_signals(candidates=candidates, compare_result=compare_result)
    relation_blockers = _relation_planner_blockers(candidates)
    proportion_blockers = _proportion_planner_blockers(compare_result, low_poly_intent=low_poly_intent)

    if relation_blockers or has_macro or domain == "assembly":
        return ReferenceRefinementRouteContract(
            domain_classification=domain,
            selected_family="macro",
            reason=(
                "Assembly-oriented truth/macro signals dominate, so bounded macro repair remains the primary "
                "refinement family."
            ),
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
            reason=(
                "Local soft/organic-form refinement dominates without strong assembly signals, so deterministic "
                "sculpt-region tools are the preferred family."
            ),
            source_signals=source_signals,
            candidate_ids=candidate_ids,
            target_scope=_planner_target_scope(compare_result, local_region_hint=_local_form_reason(compare_result)),
            detail_available=True,
        )

    if domain in {"hard_surface", "generic_form", "soft_surface"} or low_poly_intent:
        return ReferenceRefinementRouteContract(
            domain_classification=domain,
            selected_family="modeling_mesh",
            reason=(
                "Current signals do not justify sculpt; bounded modeling/mesh refinement remains the safer default "
                "family."
            ),
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


def build_refinement_handoff(
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
            eligible_tool_names=list(SCULPT_RECOMMENDED_TOOLS),
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
        eligible_tool_names=list(SCULPT_RECOMMENDED_TOOLS),
        visibility_unlock_recommended=False,
        recommended_tools=[
            ReferenceRefinementToolCandidateContract(
                tool_name=tool_name,
                reason=(
                    "Deterministic local-form refinement is a better fit than more assembly-oriented "
                    "mesh/modeling edits."
                ),
                priority=(
                    "high"
                    if tool_name in {"sculpt_deform_region", "sculpt_smooth_region", "sculpt_crease_region"}
                    else "normal"
                ),
                arguments_hint=arguments_hint,
            )
            for tool_name in SCULPT_RECOMMENDED_TOOLS
        ],
    )


def build_repair_planner_summary(
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


def build_repair_planner_detail(
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


def model_budget_bias(model_name: str | None) -> int:
    normalized = str(model_name or "").lower()
    if re.search(r"(^|[-_./:])(2b|3b|4b|mini)($|[-_./:])", normalized):
        return -1
    if any(token in normalized for token in ("27b", "70b", "72b", "grok")):
        return 1
    return 0


def effective_pair_budget(*, max_tokens: int, model_name: str | None) -> int:
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
    return max(2, min(8, base + model_budget_bias(model_name)))


def effective_candidate_budget(*, pair_budget: int, max_tokens: int, model_name: str | None) -> int:
    base = pair_budget + 1
    if max_tokens <= 256:
        base = min(base, 3)
    elif max_tokens <= 400:
        base = min(base, 4)
    else:
        base = min(base, 6 + model_budget_bias(model_name))
    return max(2, base)


def trim_correction_candidates(
    candidates: list[ReferenceCorrectionCandidateContract],
    *,
    candidate_budget: int,
) -> tuple[list[ReferenceCorrectionCandidateContract], bool]:
    if len(candidates) <= candidate_budget:
        return candidates, False
    return list(candidates[:candidate_budget]), True


def resolve_hybrid_budget_runtime(resolver: Any) -> tuple[int, int, str | None]:
    runtime_config = getattr(resolver, "runtime_config", None)
    if runtime_config is None:
        return VISION_ASSIST_POLICY.max_tokens, 8, None
    return (
        int(getattr(runtime_config, "max_tokens", VISION_ASSIST_POLICY.max_tokens)),
        int(getattr(runtime_config, "max_images", 8)),
        cast(str | None, getattr(runtime_config, "active_model_name", None)),
    )


def normalize_focus_key(value: str) -> str:
    return " ".join(value.strip().lower().split())


def resolve_actionable_focus(compare_result: ReferenceCompareStageCheckpointResponseContract) -> list[str]:
    candidate_summaries = list(compare_result.correction_candidates or [])
    if candidate_summaries:
        deduped_candidates: list[str] = []
        seen_candidates: set[str] = set()
        for candidate in candidate_summaries:
            normalized = normalize_focus_key(candidate.summary)
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
        normalized = normalize_focus_key(item)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(item)
    return deduped[:3]


def resolve_gate_blocker_focus(compare_result: ReferenceCompareStageCheckpointResponseContract) -> list[str]:
    blockers = list(compare_result.completion_blockers or [])
    if not blockers:
        return []

    deduped: list[str] = []
    seen: set[str] = set()
    for blocker in blockers:
        item = (blocker.message or blocker.label or blocker.target_label or blocker.gate_id).strip()
        normalized = normalize_focus_key(item)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(item)
    return deduped[:3]


def should_inspect_from_truth_signal(
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


def _candidate_matches_pair_label(focus_item: str, current_pair_label: str) -> bool:
    normalized_focus = normalize_focus_key(focus_item)
    normalized_pair = normalize_focus_key(current_pair_label)
    if not normalized_focus or not normalized_pair:
        return False
    if normalized_pair in normalized_focus:
        return True
    from_object, to_object = current_pair_label.split(" -> ", 1)
    return normalize_focus_key(from_object) in normalized_focus and normalize_focus_key(to_object) in normalized_focus


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


def build_correction_candidates(
    compare_result: ReferenceCompareStageCheckpointResponseContract,
) -> list[ReferenceCorrectionCandidateContract]:
    truth_followup = compare_result.truth_followup
    vision_result = compare_result.vision_assistant.result if compare_result.vision_assistant else None
    correction_focus = resolve_actionable_focus(compare_result)
    candidates: list[ReferenceCorrectionCandidateContract] = []
    used_focus_items: set[str] = set()
    rank = 1
    focus_pairs = list(truth_followup.focus_pairs or []) if truth_followup is not None else []

    truth_items_by_pair: dict[str, list[SceneTruthFollowupItemContract]] = {}
    for item in list(truth_followup.items or []) if truth_followup is not None else []:
        if item.from_object is None or item.to_object is None:
            continue
        current_pair_label = pair_label(item.from_object, item.to_object)
        truth_items_by_pair.setdefault(current_pair_label, []).append(item)

    truth_macros_by_pair: dict[str, list[SceneRepairMacroCandidateContract]] = {}
    for macro_candidate in list(truth_followup.macro_candidates or []) if truth_followup is not None else []:
        for current_pair_label in focus_pairs:
            from_object, to_object = current_pair_label.split(" -> ", 1)
            if _macro_candidate_matches_pair(macro_candidate, from_object=from_object, to_object=to_object):
                truth_macros_by_pair.setdefault(current_pair_label, []).append(macro_candidate)

    for current_pair_label in focus_pairs:
        pair_items = truth_items_by_pair.get(current_pair_label, [])
        pair_macros = truth_macros_by_pair.get(current_pair_label, [])
        matched_focus = [item for item in correction_focus if _candidate_matches_pair_label(item, current_pair_label)]
        used_focus_items.update(normalize_focus_key(item) for item in matched_focus)
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
            else (matched_focus[0] if matched_focus else f"Review pair {current_pair_label}")
        )
        from_object, to_object = current_pair_label.split(" -> ", 1)
        candidates.append(
            ReferenceCorrectionCandidateContract(
                candidate_id=f"pair:{normalize_focus_key(current_pair_label).replace(' ', '_')}",
                summary=summary,
                priority_rank=rank,
                priority=priority,
                candidate_kind="hybrid" if matched_focus else "truth_only",
                target_object=compare_result.target_object,
                target_objects=[from_object, to_object],
                focus_pairs=[current_pair_label],
                source_signals=signals,
                vision_evidence=_build_vision_candidate_evidence(
                    vision_result=vision_result,
                    focus_items=matched_focus,
                ),
                truth_evidence=ReferenceCorrectionTruthEvidenceContract(
                    focus_pairs=[current_pair_label],
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
        normalized_focus = normalize_focus_key(focus_item)
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
