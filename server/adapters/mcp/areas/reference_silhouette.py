# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Advisory silhouette helpers for the reference MCP surface."""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Literal

from server.adapters.mcp.contracts.reference import (
    ReferenceActionHintContract,
    ReferenceCompareSupportEvidenceContract,
    ReferenceImageRecordContract,
    ReferencePartSegmentationContract,
    ReferencePartSegmentationPartContract,
    ReferenceRefinementToolCandidateContract,
    ReferenceSilhouetteAnalysisContract,
    ReferenceSilhouetteMetricContract,
)
from server.adapters.mcp.contracts.vision import VisionCaptureImageContract
from server.adapters.mcp.vision.silhouette import build_silhouette_analysis


def build_silhouette_analysis_payload(
    *,
    selected_reference_records: list[ReferenceImageRecordContract] | tuple[ReferenceImageRecordContract, ...],
    captures: list[VisionCaptureImageContract] | tuple[VisionCaptureImageContract, ...],
    target_view: str | None,
    target_objects: Sequence[str] = (),
) -> ReferenceSilhouetteAnalysisContract | None:
    if not selected_reference_records or not captures:
        return None

    reference_record = selected_reference_records[0]
    capture = select_silhouette_analysis_capture(captures=captures, target_view=target_view)
    object_id_artifact = capture.object_id_artifact
    payload = build_silhouette_analysis(
        reference_path=reference_record.stored_path,
        capture_path=capture.image_path,
        reference_label=reference_record.label or reference_record.reference_id,
        capture_label=capture.label,
        target_view=target_view,
        object_id_path=object_id_artifact.image_path if object_id_artifact is not None else None,
        object_id_index_map=object_id_artifact.index_map if object_id_artifact is not None else None,
        object_names=target_objects if object_id_artifact is not None else (),
        object_id_unavailable_note=(
            object_id_artifact.capture_warning
            if object_id_artifact is not None and object_id_artifact.capture_warning
            else None
        ),
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


def select_silhouette_analysis_capture(
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
            if capture.object_id_artifact is not None:
                return capture

    for capture in captures:
        if capture.view_kind == "focus":
            return capture
    return captures[0]


def build_action_hints_from_silhouette(
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


def _metric_summary(metric: ReferenceSilhouetteMetricContract) -> str:
    if metric.metric_id == "mask_iou":
        return f"Silhouette overlap is {metric.observed_value:.2f} ({metric.severity})."
    if metric.metric_id == "contour_drift":
        return f"Contour drift is {metric.observed_value:.2f} ({metric.severity})."
    if metric.metric_id == "aspect_ratio_delta":
        return f"Aspect ratio delta is {metric.delta:.2f} ({metric.severity})."
    return f"{metric.metric_id} delta is {metric.delta:.2f} ({metric.severity})."


def build_compare_support_evidence(
    silhouette_analysis: ReferenceSilhouetteAnalysisContract | None,
    *,
    action_hints: list[ReferenceActionHintContract] | None = None,
    part_segmentation: ReferencePartSegmentationContract | None = None,
) -> list[ReferenceCompareSupportEvidenceContract]:
    """Project compact compare-time CV evidence for packet-local staged compare."""

    evidence: list[ReferenceCompareSupportEvidenceContract] = []
    if silhouette_analysis is not None and silhouette_analysis.status == "available":
        if silhouette_analysis.consistency_score is not None:
            score = silhouette_analysis.consistency_score
            severity: Literal["high", "medium", "low"] = "high" if score < 0.45 else "medium" if score < 0.7 else "low"
            evidence.append(
                ReferenceCompareSupportEvidenceContract(
                    evidence_kind="silhouette_metric",
                    summary=f"Deterministic silhouette consistency score is {score:.2f} ({severity}).",
                    metric_id="consistency_score",
                    severity=severity,
                    observed_value=score,
                    reference_label=silhouette_analysis.reference_label,
                    capture_label=silhouette_analysis.capture_label,
                    target_view=silhouette_analysis.target_view,
                )
            )
        prioritized_metrics = [
            metric for metric in silhouette_analysis.metrics if metric.severity in {"high", "medium"}
        ] or list(silhouette_analysis.metrics[:2])
        evidence.extend(
            ReferenceCompareSupportEvidenceContract(
                evidence_kind="silhouette_metric",
                summary=_metric_summary(metric),
                metric_id=metric.metric_id,
                severity=metric.severity,
                observed_value=metric.observed_value,
                delta=metric.delta,
                reference_label=silhouette_analysis.reference_label,
                capture_label=silhouette_analysis.capture_label,
                target_view=silhouette_analysis.target_view,
            )
            for metric in prioritized_metrics[:3]
        )
        evidence.extend(
            ReferenceCompareSupportEvidenceContract(
                evidence_kind="per_object_iou",
                summary=(
                    f"Capture-side object-level Object Index visible-surface IoU for {metric.object_name} "
                    f"against the reference silhouette "
                    f"is {metric.mask_iou:.2f} ({metric.severity})."
                    if metric.mask_iou is not None
                    else f"Capture-side object-level Object Index IoU for {metric.object_name} is unavailable."
                ),
                metric_id="per_object_mask_iou",
                severity=metric.severity,
                observed_value=metric.mask_iou,
                reference_label=silhouette_analysis.reference_label,
                capture_label=silhouette_analysis.capture_label,
                target_view=silhouette_analysis.target_view,
                part_label=metric.object_name,
            )
            for metric in list(silhouette_analysis.per_object_metrics or [])
            if metric.status == "available"
        )
    if part_segmentation is not None and part_segmentation.status == "available":
        evidence.extend(
            ReferenceCompareSupportEvidenceContract(
                evidence_kind="part_segmentation",
                summary=_part_segmentation_summary(part),
                severity="medium",
                reference_label=silhouette_analysis.reference_label if silhouette_analysis is not None else None,
                capture_label=silhouette_analysis.capture_label if silhouette_analysis is not None else None,
                target_view=silhouette_analysis.target_view if silhouette_analysis is not None else None,
                part_label=part.part_label,
                confidence=part.confidence,
            )
            for part in list(part_segmentation.parts or [])[:2]
        )
    if action_hints:
        evidence.extend(
            ReferenceCompareSupportEvidenceContract(
                evidence_kind="action_hint",
                summary=f"Action hint: {hint.summary}",
                hint_type=hint.hint_type,
                severity="high" if hint.priority == "high" else "medium",
                reference_label=silhouette_analysis.reference_label if silhouette_analysis is not None else None,
                capture_label=silhouette_analysis.capture_label if silhouette_analysis is not None else None,
                target_view=silhouette_analysis.target_view if silhouette_analysis is not None else None,
            )
            for hint in list(action_hints)[:2]
        )
    return evidence[:6]


def summarize_compare_support_evidence(
    evidence: list[ReferenceCompareSupportEvidenceContract] | tuple[ReferenceCompareSupportEvidenceContract, ...],
) -> list[str]:
    """Return short prompt-facing summaries for typed packet support evidence."""

    return [item.summary for item in evidence if item.summary.strip()]


def _part_segmentation_summary(part: ReferencePartSegmentationPartContract) -> str:
    if part.confidence is not None:
        return f"Optional localized support marked {part.part_label} at {part.confidence:.2f} confidence."
    return f"Optional localized support marked {part.part_label} for advisory compare support."
