"""Shared packet-planning and synthesis policy for staged reference compare."""

from __future__ import annotations

import hashlib
import re
from collections import OrderedDict
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

from server.adapters.mcp.contracts.reference import (
    ReferenceCompareComplexityTierLiteral,
    ReferenceCompareDiagnosticsContract,
    ReferenceComparePacketContract,
    ReferenceImageRecordContract,
)
from server.adapters.mcp.contracts.scene import SceneAssembledTargetScopeContract, SceneTruthFollowupContract
from server.adapters.mcp.contracts.vision import VisionCaptureImageContract
from server.adapters.mcp.sampling.result_types import (
    VisionAssistContract,
    VisionBoundaryPolicyContract,
    VisionInputSummaryContract,
    VisionIssueContract,
    VisionPacketStatusContract,
    VisionRecommendedCheckContract,
)

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
_HEAD_HINTS: tuple[str, ...] = ("head", "skull", "face")
_BODY_HINTS: tuple[str, ...] = ("body", "torso", "trunk", "chest", "abdomen", "pelvis", "hip")
_TAIL_HINTS: tuple[str, ...] = ("tail",)
_EAR_HINTS: tuple[str, ...] = ("ear",)


@dataclass(frozen=True)
class _ScopeCluster:
    scope_label: str
    target_objects: tuple[str, ...]
    truth_pairs: tuple[str, ...]


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


def _name_role_tokens(object_name: str) -> list[str]:
    normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", object_name.strip())
    return [token for token in re.split(r"[^a-zA-Z0-9]+", normalized.lower()) if token]


def _has_name_hint(object_name: str, hints: tuple[str, ...]) -> bool:
    normalized = object_name.strip().lower()
    return any(hint in normalized for hint in hints) or any(hint in _name_role_tokens(object_name) for hint in hints)


def _is_head_like(object_name: str) -> bool:
    return _has_name_hint(object_name, _HEAD_HINTS)


def _is_body_like(object_name: str) -> bool:
    return _has_name_hint(object_name, _BODY_HINTS)


def _is_tail_like(object_name: str) -> bool:
    return _has_name_hint(object_name, _TAIL_HINTS)


def _is_ear_like(object_name: str) -> bool:
    return _has_name_hint(object_name, _EAR_HINTS)


def _semantic_scope_label(part_object: str, anchor_object: str) -> str:
    if _is_head_like(part_object) and _is_body_like(anchor_object):
        return "Body + Head"
    if _is_tail_like(part_object):
        return "Tail"
    if _is_ear_like(part_object):
        return "Ears"
    return f"{part_object} + {anchor_object}"


def _append_scope_cluster(
    clusters: "OrderedDict[str, _ScopeCluster]",
    *,
    scope_label: str,
    target_objects: Sequence[str],
    truth_pair: str | None = None,
) -> None:
    normalized_objects = tuple(_unique_preserving_order(list(target_objects)))
    if not normalized_objects:
        return
    existing = clusters.get(scope_label)
    if existing is None:
        clusters[scope_label] = _ScopeCluster(
            scope_label=scope_label,
            target_objects=normalized_objects,
            truth_pairs=((truth_pair,) if truth_pair else ()),
        )
        return
    merged_objects = tuple(_unique_preserving_order([*existing.target_objects, *normalized_objects]))
    merged_truth_pairs = tuple(_unique_preserving_order([*existing.truth_pairs, *([truth_pair] if truth_pair else [])]))
    clusters[scope_label] = _ScopeCluster(
        scope_label=scope_label,
        target_objects=merged_objects,
        truth_pairs=merged_truth_pairs,
    )


def _scope_clusters_from_focus_pairs(
    focus_pairs: Sequence[str],
    *,
    primary_target: str | None,
) -> list[_ScopeCluster]:
    clusters: OrderedDict[str, _ScopeCluster] = OrderedDict()
    for focus_pair in focus_pairs:
        if " -> " not in focus_pair:
            continue
        from_object, to_object = focus_pair.split(" -> ", 1)
        scope_label = _semantic_scope_label(from_object, to_object)
        _append_scope_cluster(
            clusters,
            scope_label=scope_label,
            target_objects=(to_object, from_object),
            truth_pair=focus_pair,
        )
    if clusters:
        return list(clusters.values())
    if primary_target is None:
        return []
    return [
        _ScopeCluster(
            scope_label=primary_target,
            target_objects=(primary_target,),
            truth_pairs=(),
        )
    ]


def _scope_clusters_from_target_scope(
    assembled_target_scope: SceneAssembledTargetScopeContract | None,
) -> list[_ScopeCluster]:
    if assembled_target_scope is None:
        return []
    object_names = _unique_preserving_order(list(assembled_target_scope.object_names or []))
    if len(object_names) < 2:
        return []

    primary_target = assembled_target_scope.primary_target or object_names[0]
    heads = [name for name in object_names if _is_head_like(name)]
    bodies = [name for name in object_names if _is_body_like(name)]
    tails = [name for name in object_names if _is_tail_like(name)]
    ears = [name for name in object_names if _is_ear_like(name)]
    anchor_body = bodies[0] if bodies else primary_target
    head_anchor = heads[0] if heads else primary_target

    clusters: OrderedDict[str, _ScopeCluster] = OrderedDict()
    consumed: set[str] = {primary_target}

    if heads and anchor_body:
        _append_scope_cluster(
            clusters,
            scope_label="Body + Head",
            target_objects=(anchor_body, heads[0]),
        )
        consumed.update({anchor_body, heads[0]})

    if tails and anchor_body:
        _append_scope_cluster(
            clusters,
            scope_label="Tail",
            target_objects=(anchor_body, *tails),
        )
        consumed.update(tails)

    if ears and head_anchor:
        _append_scope_cluster(
            clusters,
            scope_label="Ears",
            target_objects=(head_anchor, *ears),
        )
        consumed.update(ears)
        consumed.add(head_anchor)

    for object_name in object_names:
        if object_name in consumed:
            continue
        if object_name == primary_target:
            continue
        _append_scope_cluster(
            clusters,
            scope_label=object_name,
            target_objects=(primary_target, object_name),
        )

    return list(clusters.values())


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


def _ordered_views(view_map: dict[str, list[str]]) -> list[str]:
    return [view_id for view_id in _PACKET_VIEW_ORDER if view_id in view_map]


def _selected_packet_views(
    *,
    normalized_target_view: str | None,
    capture_views: list[str],
    complexity_tier: ReferenceCompareComplexityTierLiteral,
) -> list[str]:
    if normalized_target_view is not None:
        return [normalized_target_view]
    if not capture_views:
        return []
    if complexity_tier == "super_complex":
        return capture_views
    return capture_views[:2]


def _packet_capture_labels(
    *,
    view_id: str | None,
    capture_labels_by_view: dict[str, list[str]],
    context_capture_labels: list[str],
    all_capture_labels: list[str],
) -> list[str]:
    if view_id is None:
        return _unique_preserving_order(context_capture_labels or all_capture_labels)
    matched_labels = list(capture_labels_by_view.get(view_id, []))
    if not matched_labels:
        return []
    return _unique_preserving_order([*context_capture_labels, *matched_labels])


def _packet_reference_ids(
    *,
    view_id: str | None,
    reference_ids_by_view: dict[str, list[str]],
    generic_reference_ids: list[str],
    all_reference_ids: list[str],
) -> list[str]:
    if view_id is None:
        return _unique_preserving_order(generic_reference_ids or all_reference_ids)
    matched_ids = list(reference_ids_by_view.get(view_id, []))
    if matched_ids:
        return _unique_preserving_order([*matched_ids, *generic_reference_ids])
    if generic_reference_ids:
        return _unique_preserving_order(generic_reference_ids)
    return []


def _general_packet(
    *,
    complexity_tier: ReferenceCompareComplexityTierLiteral,
    assembled_target_scope: SceneAssembledTargetScopeContract | None,
    all_reference_ids: list[str],
    all_capture_labels: list[str],
) -> ReferenceComparePacketContract:
    scope_label = assembled_target_scope.scope_kind if assembled_target_scope is not None else None
    return ReferenceComparePacketContract(
        packet_id=_stable_packet_id(
            "packet", complexity_tier, scope_label or "general", *all_reference_ids, *all_capture_labels
        ),
        packet_kind="scope",
        packet_label="general packet",
        scope_label=scope_label,
        target_objects=list(assembled_target_scope.object_names or []) if assembled_target_scope is not None else [],
        reference_ids=list(all_reference_ids),
        capture_labels=list(all_capture_labels),
        compare_question=_packet_question_for_view(None, scope_label=scope_label),
    )


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
    all_capture_labels = [capture.label for capture in captures]
    for capture in captures:
        view_id = _capture_view_id(capture)
        if view_id is None:
            context_capture_labels.append(capture.label)
            continue
        capture_labels_by_view.setdefault(view_id, []).append(capture.label)

    reference_ids_by_view: dict[str, list[str]] = {}
    generic_reference_ids: list[str] = []
    all_reference_ids = [reference.reference_id for reference in reference_records]
    for reference in reference_records:
        view_id = _reference_view_id(reference)
        if view_id is None:
            generic_reference_ids.append(reference.reference_id)
            continue
        reference_ids_by_view.setdefault(view_id, []).append(reference.reference_id)

    normalized_target_view = _normalize_view_token(target_view)
    capture_views = _ordered_views(capture_labels_by_view)
    focus_pairs = list(truth_followup.focus_pairs or []) if truth_followup is not None else []
    complexity_tier = resolve_compare_complexity_tier(
        assembled_target_scope=assembled_target_scope,
        reference_count=len(reference_records),
        capture_count=len(captures),
        focus_pair_count=len(focus_pairs),
    )
    selected_views = _selected_packet_views(
        normalized_target_view=normalized_target_view,
        capture_views=capture_views,
        complexity_tier=complexity_tier,
    )

    packets: list[ReferenceComparePacketContract] = []
    if complexity_tier == "simple":
        if not selected_views:
            packets.append(
                _general_packet(
                    complexity_tier=complexity_tier,
                    assembled_target_scope=assembled_target_scope,
                    all_reference_ids=all_reference_ids,
                    all_capture_labels=all_capture_labels,
                )
            )
        for view_id in selected_views:
            packet_capture_labels = _packet_capture_labels(
                view_id=view_id,
                capture_labels_by_view=capture_labels_by_view,
                context_capture_labels=context_capture_labels,
                all_capture_labels=all_capture_labels,
            )
            packet_reference_ids = _packet_reference_ids(
                view_id=view_id,
                reference_ids_by_view=reference_ids_by_view,
                generic_reference_ids=generic_reference_ids,
                all_reference_ids=all_reference_ids,
            )
            packets.append(
                ReferenceComparePacketContract(
                    packet_id=_stable_packet_id(
                        "packet", "simple", view_id, *packet_reference_ids, *packet_capture_labels
                    ),
                    packet_kind="view",
                    packet_label=f"{view_id} packet",
                    target_view=view_id,
                    scope_label=assembled_target_scope.scope_kind if assembled_target_scope is not None else None,
                    target_objects=list(assembled_target_scope.object_names or [])
                    if assembled_target_scope is not None
                    else [],
                    reference_ids=packet_reference_ids,
                    capture_labels=packet_capture_labels,
                    compare_question=_packet_question_for_view(view_id),
                )
            )
    else:
        scope_clusters = (
            _scope_clusters_from_focus_pairs(
                focus_pairs,
                primary_target=assembled_target_scope.primary_target if assembled_target_scope is not None else None,
            )
            if focus_pairs
            else _scope_clusters_from_target_scope(assembled_target_scope)
        )
        if scope_clusters:
            active_views: list[str | None] = list(selected_views) if selected_views else [None]
            for cluster in scope_clusters:
                for view_id in active_views:
                    packet_capture_labels = _packet_capture_labels(
                        view_id=view_id,
                        capture_labels_by_view=capture_labels_by_view,
                        context_capture_labels=context_capture_labels,
                        all_capture_labels=all_capture_labels,
                    )
                    packet_reference_ids = _packet_reference_ids(
                        view_id=view_id,
                        reference_ids_by_view=reference_ids_by_view,
                        generic_reference_ids=generic_reference_ids,
                        all_reference_ids=all_reference_ids,
                    )
                    packets.append(
                        ReferenceComparePacketContract(
                            packet_id=_stable_packet_id(
                                "packet",
                                cluster.scope_label,
                                view_id or "scope",
                                *packet_reference_ids,
                                *packet_capture_labels,
                            ),
                            packet_kind="view_scope" if view_id is not None else "scope",
                            packet_label=cluster.scope_label,
                            target_view=view_id,
                            scope_label=cluster.scope_label,
                            target_objects=list(cluster.target_objects),
                            truth_pairs=list(cluster.truth_pairs),
                            reference_ids=packet_reference_ids,
                            capture_labels=packet_capture_labels,
                            compare_question=_packet_question_for_view(view_id, scope_label=cluster.scope_label),
                        )
                    )
        elif selected_views:
            for view_id in selected_views:
                packet_capture_labels = _packet_capture_labels(
                    view_id=view_id,
                    capture_labels_by_view=capture_labels_by_view,
                    context_capture_labels=context_capture_labels,
                    all_capture_labels=all_capture_labels,
                )
                packet_reference_ids = _packet_reference_ids(
                    view_id=view_id,
                    reference_ids_by_view=reference_ids_by_view,
                    generic_reference_ids=generic_reference_ids,
                    all_reference_ids=all_reference_ids,
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
        else:
            packets.append(
                _general_packet(
                    complexity_tier=complexity_tier,
                    assembled_target_scope=assembled_target_scope,
                    all_reference_ids=all_reference_ids,
                    all_capture_labels=all_capture_labels,
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


def merge_packet_phase_results(
    extraction_result: VisionAssistContract,
    ranking_result: VisionAssistContract,
) -> VisionAssistContract:
    return extraction_result.model_copy(
        update={
            "goal_summary": ranking_result.goal_summary or extraction_result.goal_summary,
            "reference_match_summary": ranking_result.reference_match_summary
            or extraction_result.reference_match_summary,
            "visible_changes": list(ranking_result.visible_changes or extraction_result.visible_changes or []),
            "shape_mismatches": list(extraction_result.shape_mismatches or []),
            "proportion_mismatches": list(extraction_result.proportion_mismatches or []),
            "correction_focus": list(ranking_result.correction_focus or extraction_result.correction_focus or []),
            "likely_issues": list(ranking_result.likely_issues or extraction_result.likely_issues or []),
            "next_corrections": list(ranking_result.next_corrections or extraction_result.next_corrections or []),
            "recommended_checks": list(ranking_result.recommended_checks or extraction_result.recommended_checks or []),
            "packet_guidance": ranking_result.packet_guidance or extraction_result.packet_guidance,
            "confidence": ranking_result.confidence
            if ranking_result.confidence is not None
            else extraction_result.confidence,
            "captures_used": list(extraction_result.captures_used or ranking_result.captures_used or []),
            "input_summary": extraction_result.input_summary or ranking_result.input_summary,
        }
    )


def synthesize_packet_vision_result(
    packet_results: Sequence[tuple[ReferenceComparePacketContract, VisionAssistContract | None]],
) -> VisionAssistContract | None:
    successful_results = [(packet, result) for packet, result in packet_results if result is not None]
    if not successful_results:
        return None

    goal_summaries = _unique_preserving_order(
        [result.goal_summary for _, result in successful_results if result.goal_summary]
    )
    reference_match_summaries = _unique_preserving_order(
        [summary for _, result in successful_results if (summary := result.reference_match_summary)]
    )
    visible_changes = _unique_preserving_order(
        [item for _, result in successful_results for item in list(result.visible_changes or [])]
    )[:8]
    shape_mismatches = _unique_preserving_order(
        [item for _, result in successful_results for item in list(result.shape_mismatches or [])]
    )[:6]
    proportion_mismatches = _unique_preserving_order(
        [item for _, result in successful_results for item in list(result.proportion_mismatches or [])]
    )[:6]
    correction_focus = _unique_preserving_order(
        [item for _, result in successful_results for item in list(result.correction_focus or [])]
    )[:6]
    next_corrections = _unique_preserving_order(
        [item for _, result in successful_results for item in list(result.next_corrections or [])]
    )[:6]
    captures_used = _unique_preserving_order(
        [item for _, result in successful_results for item in list(result.captures_used or [])]
    )

    likely_issues: list[VisionIssueContract] = []
    seen_issue_keys: set[tuple[str, str]] = set()
    for _, result in successful_results:
        for issue in list(result.likely_issues or []):
            issue_key = (issue.category, issue.summary)
            if issue_key in seen_issue_keys:
                continue
            seen_issue_keys.add(issue_key)
            likely_issues.append(issue)

    recommended_checks: list[VisionRecommendedCheckContract] = []
    seen_check_keys: set[tuple[str, str]] = set()
    for _, result in successful_results:
        for check in list(result.recommended_checks or []):
            check_key = (check.tool_name, check.reason)
            if check_key in seen_check_keys:
                continue
            seen_check_keys.add(check_key)
            recommended_checks.append(check)

    confidences = [float(result.confidence) for _, result in successful_results if result.confidence is not None]
    unique_capture_labels = _unique_preserving_order(
        [label for packet, _ in successful_results for label in list(packet.capture_labels or [])]
    )
    unique_reference_ids = _unique_preserving_order(
        [reference_id for packet, _ in successful_results for reference_id in list(packet.reference_ids or [])]
    )
    before_image_count = max(
        (
            result.input_summary.before_image_count
            for _, result in successful_results
            if result.input_summary is not None
        ),
        default=0,
    )
    merged_input_summary = VisionInputSummaryContract(
        before_image_count=before_image_count,
        after_image_count=len(unique_capture_labels),
        reference_image_count=len(unique_reference_ids),
        target_object=next(
            (
                result.input_summary.target_object
                for _, result in successful_results
                if result.input_summary and result.input_summary.target_object
            ),
            None,
        ),
    )
    packet_labels = [packet.packet_label for packet, _ in successful_results]
    summary_prefix = (
        goal_summaries[0]
        if len(goal_summaries) == 1
        else f"Packeted compare synthesized {len(successful_results)} bounded packet result(s)."
    )
    if len(packet_labels) > 1:
        summary_prefix = f"{summary_prefix} Active packets: {', '.join(packet_labels[:4])}."

    return VisionAssistContract(
        backend_kind=successful_results[0][1].backend_kind,
        backend_name=successful_results[0][1].backend_name,
        model_name=successful_results[0][1].model_name,
        vision_contract_profile=successful_results[0][1].vision_contract_profile,
        goal_summary=summary_prefix,
        reference_match_summary=reference_match_summaries[0] if reference_match_summaries else None,
        visible_changes=visible_changes,
        shape_mismatches=shape_mismatches,
        proportion_mismatches=proportion_mismatches,
        correction_focus=correction_focus,
        likely_issues=likely_issues[:6],
        next_corrections=next_corrections,
        recommended_checks=recommended_checks[:6],
        packet_guidance=VisionPacketStatusContract(
            packet_status="ready",
            status_reason=None,
            ranking_recommendation="rank" if correction_focus else "skip_clean",
        ),
        confidence=(sum(confidences) / len(confidences)) if confidences else None,
        captures_used=captures_used,
        input_summary=merged_input_summary,
        boundary_policy=VisionBoundaryPolicyContract(),
    )


def count_failed_compare_packets(compare_diagnostics: ReferenceCompareDiagnosticsContract) -> int:
    return sum(
        1
        for packet in compare_diagnostics.packets
        if packet.extraction_status in {"blocked", "low_information", "error"}
    )


def has_compare_uncertainty(compare_diagnostics: ReferenceCompareDiagnosticsContract) -> bool:
    return any(
        packet.extraction_status in {"blocked", "low_information", "error"} or packet.ranking_status == "error"
        for packet in compare_diagnostics.packets
    )


def should_emit_compare_diagnostics(
    *,
    compare_diagnostics: ReferenceCompareDiagnosticsContract,
    preset_profile: Literal["compact", "rich"],
    model_aware_trimming_applied: bool,
) -> bool:
    return bool(
        preset_profile == "rich"
        or compare_diagnostics.synthesis_required
        or model_aware_trimming_applied
        or has_compare_uncertainty(compare_diagnostics)
    )
