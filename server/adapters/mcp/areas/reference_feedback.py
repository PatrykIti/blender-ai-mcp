# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Server-owned reference feedback helpers for guided orchestrator surfaces."""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any, Literal, cast

import numpy as np

from server.adapters.mcp.contracts.guided_flow import GuidedFlowStateContract
from server.adapters.mcp.contracts.quality_gates import GatePlanContract
from server.adapters.mcp.contracts.reference import (
    GuidedReferenceReadinessContract,
    ReferenceCorrectionCandidateContract,
    ReferenceOrchestratorFeedbackContract,
    ReferencePlannerFamilyLiteral,
    ReferenceRepairPlannerSummaryContract,
    ReferenceStrategyStateContract,
    ReferenceUnderstandingSummaryContract,
    ReferenceUnderstandingViewContract,
    ReferenceUnderstandingVisualEvidenceRefContract,
    ReferenceUnderstandingVisualMetricContract,
)

_PLANNER_FAMILIES: tuple[ReferencePlannerFamilyLiteral, ...] = (
    "macro",
    "modeling_mesh",
    "sculpt_region",
    "inspect_only",
)
_CHECKPOINT_TOOLS = Literal[
    "reference_images",
    "router_get_status",
    "reference_compare_stage_checkpoint",
    "reference_iterate_stage_checkpoint",
]
_VIEW_ALIASES: dict[str, str] = {
    "front": "front",
    "side": "side",
    "top": "top",
    "back": "back",
    "rear": "back",
    "three": "three_quarter",
    "quarter": "three_quarter",
    "3q": "three_quarter",
    "detail": "detail",
    "close": "detail",
}


def _dedupe_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for item in values:
        value = str(item).strip()
        key = value.lower()
        if not value or key in seen:
            continue
        seen.add(key)
        deduped.append(value)
    return deduped


def _normalize_view_id(value: str | None) -> str:
    tokens = [token for token in re.split(r"[^a-z0-9]+", str(value or "").strip().lower()) if token]
    for token in tokens:
        normalized = _VIEW_ALIASES.get(token)
        if normalized is not None:
            return normalized
    return "unknown"


def _component_count(mask: np.ndarray) -> int:
    if mask.ndim != 2 or not bool(mask.any()):
        return 0

    visited = np.zeros(mask.shape, dtype=bool)
    count = 0
    for y, x in np.argwhere(mask):
        if visited[y, x]:
            continue
        count += 1
        queue = [(int(y), int(x))]
        visited[y, x] = True
        while queue:
            current_y, current_x = queue.pop()
            for delta_y, delta_x in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                next_y = current_y + delta_y
                next_x = current_x + delta_x
                if next_y < 0 or next_y >= mask.shape[0] or next_x < 0 or next_x >= mask.shape[1]:
                    continue
                if visited[next_y, next_x] or not bool(mask[next_y, next_x]):
                    continue
                visited[next_y, next_x] = True
                queue.append((next_y, next_x))
    return count


def _finite_float(value: float | int | np.floating[Any]) -> float:
    numeric = float(value)
    return numeric if np.isfinite(numeric) else 0.0


def _extract_image_metrics(image_path: str) -> dict[str, float] | None:
    try:
        from PIL import Image
    except ImportError:
        return None

    try:
        with Image.open(image_path) as image:
            rgba = np.asarray(image.convert("RGBA"))
    except Exception:
        return None

    if rgba.size == 0:
        return None

    rgb = rgba[:, :, :3].astype(np.float64)
    grayscale = np.dot(rgb, np.array([0.299, 0.587, 0.114], dtype=np.float64))
    grad_x = np.abs(np.diff(grayscale, axis=1))
    grad_y = np.abs(np.diff(grayscale, axis=0))
    edge_density = _finite_float(
        (
            (float((grad_x > 18.0).mean()) if grad_x.size else 0.0)
            + (float((grad_y > 18.0).mean()) if grad_y.size else 0.0)
        )
        / 2.0
    )

    alpha = rgba[:, :, 3]
    if np.any(alpha < 250):
        mask = alpha > 32
    else:
        grayscale_uint8 = grayscale.astype(np.uint8)
        threshold = float(grayscale_uint8.mean())
        mask_dark = grayscale <= threshold
        mask_light = grayscale >= threshold
        mask = mask_dark if float(mask_dark.mean()) <= float(mask_light.mean()) else mask_light

    component_count = float(_component_count(mask))
    positions = np.argwhere(mask)
    if positions.size == 0:
        aspect_ratio = float(rgba.shape[1] / max(rgba.shape[0], 1))
    else:
        y_min, x_min = positions.min(axis=0)
        y_max, x_max = positions.max(axis=0)
        width = float((x_max - x_min) + 1)
        height = float((y_max - y_min) + 1)
        aspect_ratio = width / max(height, 1.0)

    quantized = (rgb // 32).astype(np.int16).reshape(-1, 3)
    dominant_color_count = _finite_float(len(np.unique(quantized, axis=0)))
    low_palette_score = max(0.0, 1.0 - min(dominant_color_count, 24.0) / 24.0)
    polygonal_ratio = _finite_float(min(1.0, max(0.0, (edge_density * 1.8) + (low_palette_score * 0.45))))
    facet_likelihood = _finite_float(
        min(1.0, max(0.0, (polygonal_ratio * 0.6) + (edge_density * 0.25) + (low_palette_score * 0.15)))
    )

    return {
        "edge_density": _finite_float(edge_density),
        "contour_count": _finite_float(component_count),
        "polygonal_contour_ratio": _finite_float(polygonal_ratio),
        "dominant_color_count": _finite_float(dominant_color_count),
        "silhouette_aspect_ratio": _finite_float(aspect_ratio),
        "facet_likelihood": _finite_float(facet_likelihood),
    }


def _metric_summary(metric_id: str, observed_value: float, *, reference_id: str) -> str:
    if metric_id == "edge_density":
        return f"{reference_id} edge density is {observed_value:.3f}."
    if metric_id == "contour_count":
        return f"{reference_id} exposes {int(round(observed_value))} primary contour components."
    if metric_id == "polygonal_contour_ratio":
        return f"{reference_id} polygonal contour ratio is {observed_value:.3f}."
    if metric_id == "dominant_color_count":
        return f"{reference_id} quantized dominant color count is {int(round(observed_value))}."
    if metric_id == "silhouette_aspect_ratio":
        return f"{reference_id} silhouette aspect ratio is {observed_value:.3f}."
    return f"{reference_id} facet likelihood is {observed_value:.3f}."


def augment_reference_understanding_summary(
    summary: ReferenceUnderstandingSummaryContract,
    *,
    reference_records: list[Any] | tuple[Any, ...],
) -> ReferenceUnderstandingSummaryContract:
    """Add server-owned view and lightweight image evidence to the summary."""

    derived_views: dict[str, list[str]] = defaultdict(list)
    derived_metrics: list[ReferenceUnderstandingVisualMetricContract] = []
    derived_evidence_refs = list(summary.visual_evidence_refs or [])

    for record in reference_records:
        reference_id = str(getattr(record, "reference_id", "") or "").strip()
        if not reference_id:
            continue
        view_id = _normalize_view_id(getattr(record, "target_view", None) or getattr(record, "label", None))
        derived_views[view_id].append(reference_id)

        metrics = _extract_image_metrics(str(getattr(record, "stored_path", "") or ""))
        if metrics is None:
            continue
        for metric_id, observed_value in metrics.items():
            metric = ReferenceUnderstandingVisualMetricContract(
                metric_id=metric_id,  # type: ignore[arg-type]
                reference_id=reference_id,
                observed_value=float(observed_value),
                summary=_metric_summary(metric_id, float(observed_value), reference_id=reference_id),
            )
            derived_metrics.append(metric)
            if metric_id in {"silhouette_aspect_ratio", "facet_likelihood"}:
                derived_evidence_refs.append(
                    ReferenceUnderstandingVisualEvidenceRefContract(
                        evidence_id=f"{reference_id}_{metric_id}",
                        source_class="style_cue",
                        summary=metric.summary or f"{metric_id} derived for {reference_id}.",
                        reference_id=reference_id,
                    )
                )

    merged_views = list(summary.views or [])
    existing_view_ids = {item.view_id for item in merged_views}
    for view_id, reference_ids in sorted(derived_views.items()):
        if view_id in existing_view_ids:
            continue
        merged_views.append(
            ReferenceUnderstandingViewContract(
                view_id=view_id,  # type: ignore[arg-type]
                detected=view_id != "unknown",
                confidence=1.0 if view_id != "unknown" else 0.5,
                reference_ids=sorted(reference_ids),
            )
        )

    merged_evidence_refs = derived_evidence_refs[:12]
    merged_metrics = derived_metrics[:24]
    return summary.model_copy(
        update={
            "views": merged_views,
            "visual_metrics": merged_metrics,
            "visual_evidence_refs": merged_evidence_refs,
        }
    )


def build_reference_strategy_state(
    summary: ReferenceUnderstandingSummaryContract | None,
) -> ReferenceStrategyStateContract | None:
    """Normalize one server-owned reference strategy snapshot from the RU summary."""

    if summary is None:
        return None

    if summary.status != "available" or summary.construction_strategy is None:
        reason_to_checkpoint: dict[str, _CHECKPOINT_TOOLS] = {
            "reference_images_required": "reference_images",
            "goal_required": "router_get_status",
            "vision_backend_unavailable": "router_get_status",
        }
        return ReferenceStrategyStateContract(
            status=summary.status,
            understanding_id=summary.understanding_id,
            construction_path="unknown",
            primary_family="inspect_only",
            allowed_families=["inspect_only"],
            blocked_families=["macro", "modeling_mesh", "sculpt_region"],
            sculpt_policy="hidden",
            finish_policy="unknown",
            recommended_next_checkpoint=reason_to_checkpoint.get(summary.reason or ""),
            message=summary.message,
        )

    strategy = summary.construction_strategy
    hints = summary.router_handoff_hints
    allowed_families = list(strategy.allowed_families or [])
    primary_family = strategy.primary_family
    if primary_family not in allowed_families:
        allowed_families = [primary_family, *allowed_families]
    allowed_families = [family for family in _PLANNER_FAMILIES if family in allowed_families]
    blocked_families = [family for family in _PLANNER_FAMILIES if family not in allowed_families]
    sculpt_policy = hints.sculpt_policy if hints is not None else "hidden"
    next_checkpoint: _CHECKPOINT_TOOLS = (
        "reference_compare_stage_checkpoint" if summary.reference_ids else "router_get_status"
    )

    return ReferenceStrategyStateContract(
        status=summary.status,
        understanding_id=summary.understanding_id,
        construction_path=strategy.construction_path,
        primary_family=primary_family,
        allowed_families=allowed_families,
        blocked_families=blocked_families,
        sculpt_policy=sculpt_policy,
        finish_policy=strategy.finish_policy,
        recommended_next_checkpoint=next_checkpoint,
        message=summary.message or f"Reference strategy prefers {primary_family} for {strategy.construction_path}.",
    )


def _pending_required_parts(
    summary: ReferenceUnderstandingSummaryContract | None,
    gate_plan: GatePlanContract | None,
) -> list[str]:
    if summary is None:
        return []
    if gate_plan is None:
        return [part.part_label for part in list(summary.required_parts or [])[:6]]

    gate_by_target: dict[str, str] = {}
    for gate in gate_plan.gates:
        if gate.target_label:
            gate_by_target[str(gate.target_label)] = gate.status

    pending: list[str] = []
    for part in summary.required_parts:
        target_label = str(part.target_label or "").strip()
        status = gate_by_target.get(target_label)
        if status in {"passed", "waived"}:
            continue
        pending.append(part.part_label)
    return pending[:6]


def build_reference_orchestrator_feedback(
    *,
    goal: str | None,
    summary: ReferenceUnderstandingSummaryContract | None,
    strategy_state: ReferenceStrategyStateContract | None,
    guided_flow_state: GuidedFlowStateContract | None = None,
    gate_plan: GatePlanContract | None = None,
    guided_reference_readiness: GuidedReferenceReadinessContract | None = None,
    planner_summary: ReferenceRepairPlannerSummaryContract | None = None,
    correction_candidates: list[ReferenceCorrectionCandidateContract] | None = None,
    next_gate_actions: list[str] | None = None,
    recommended_bounded_tools: list[str] | None = None,
    correction_focus: list[str] | None = None,
    loop_disposition: str | None = None,
) -> ReferenceOrchestratorFeedbackContract | None:
    """Project one compact read model for LLM orchestrators."""

    if summary is None and strategy_state is None:
        return None

    effective_status = strategy_state.status if strategy_state is not None else summary.status  # type: ignore[union-attr]
    active_gate_ids = [gate.gate_id for gate in list(gate_plan.gates or [])[:8]] if gate_plan is not None else []
    blockers = (
        [blocker.message for blocker in list(gate_plan.completion_blockers or [])[:4]] if gate_plan is not None else []
    )
    if guided_reference_readiness is not None and guided_reference_readiness.blocking_reason:
        blockers = _dedupe_strings([guided_reference_readiness.blocking_reason, *blockers])

    actions = list(next_gate_actions or [])
    if guided_flow_state is not None:
        actions = [*actions, *list(guided_flow_state.next_actions or [])]
    if guided_reference_readiness is not None and guided_reference_readiness.next_action:
        actions.append(guided_reference_readiness.next_action)
    actions = _dedupe_strings(actions)[:6]

    support_tools = list(recommended_bounded_tools or [])
    if planner_summary is not None:
        support_tools.extend(item.tool_name for item in planner_summary.required_support_tools)
    support_tools = _dedupe_strings(support_tools)[:6]

    evidence_summary: list[str] = []
    uncertainty_notes: list[str] = []
    if summary is not None:
        evidence_summary.extend(item.summary for item in list(summary.visual_evidence_refs or [])[:3])
        evidence_summary.extend(
            item.summary for item in list(summary.visual_metrics or [])[:2] if item.summary is not None
        )
        if summary.subject is not None:
            uncertainty_notes.extend(summary.subject.uncertainty_notes)
        if summary.style is not None:
            uncertainty_notes.extend(summary.style.notes)
    if planner_summary is not None:
        evidence_summary.append(planner_summary.rationale)
    evidence_summary = _dedupe_strings(evidence_summary)[:6]
    uncertainty_notes = _dedupe_strings(uncertainty_notes)[:6]

    selected_family = (
        planner_summary.selected_family
        if planner_summary is not None
        else (strategy_state.primary_family if strategy_state is not None else "inspect_only")
    )
    next_checkpoint_tool = None
    if loop_disposition is not None or correction_candidates:
        next_checkpoint_tool = "reference_iterate_stage_checkpoint"
    elif strategy_state is not None:
        next_checkpoint_tool = strategy_state.recommended_next_checkpoint
    elif summary is not None:
        next_checkpoint_tool = cast(
            _CHECKPOINT_TOOLS | None,
            {
                "reference_images_required": "reference_images",
                "goal_required": "router_get_status",
                "vision_backend_unavailable": "router_get_status",
            }.get(summary.reason or ""),
        )

    focus = list(correction_focus or [])
    if not focus and correction_candidates:
        focus = [candidate.summary for candidate in list(correction_candidates)[:3]]

    return ReferenceOrchestratorFeedbackContract(
        status=effective_status,
        goal=goal or (summary.goal if summary is not None else None),
        understanding_id=summary.understanding_id if summary is not None else None,
        construction_path=(
            strategy_state.construction_path
            if strategy_state is not None
            else (
                summary.construction_strategy.construction_path
                if summary and summary.construction_strategy
                else "unknown"
            )
        ),
        current_guided_step=guided_flow_state.current_step if guided_flow_state is not None else None,
        selected_family=selected_family,
        allowed_families=list(strategy_state.allowed_families or []) if strategy_state is not None else [],
        blocked_families=list(strategy_state.blocked_families or []) if strategy_state is not None else [],
        required_parts_pending=_pending_required_parts(summary, gate_plan),
        active_gate_ids=active_gate_ids,
        blocking_reasons=blockers,
        next_actions=actions,
        next_checkpoint_tool=next_checkpoint_tool,  # type: ignore[arg-type]
        recommended_support_tools=support_tools,
        evidence_summary=evidence_summary,
        uncertainty_notes=uncertainty_notes,
        correction_focus=focus[:3],
        loop_disposition=loop_disposition,  # type: ignore[arg-type]
        message=(
            strategy_state.message if strategy_state is not None else (summary.message if summary is not None else None)
        ),
    )
