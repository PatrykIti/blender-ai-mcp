"""Shared packet-planning and synthesis policy for staged reference compare."""

from __future__ import annotations

import hashlib
import os
import re
from collections import OrderedDict
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Literal, cast

import httpx

from server.adapters.mcp.areas.reference_silhouette import (
    build_action_hints_from_silhouette,
    build_compare_support_evidence,
    build_silhouette_analysis_payload,
    summarize_compare_support_evidence,
)
from server.adapters.mcp.contracts.reference import (
    ReferenceActionHintContract,
    ReferenceCompareComplexityTierLiteral,
    ReferenceCompareDiagnosticsContract,
    ReferenceComparePacketContract,
    ReferenceImageRecordContract,
    ReferenceLocalizedSupportReasonLiteral,
    ReferencePartSegmentationContract,
    ReferencePartSegmentationLandmarkContract,
    ReferencePartSegmentationPartContract,
    ReferenceSilhouetteAnalysisContract,
)
from server.adapters.mcp.contracts.scene import (
    SceneAssembledTargetScopeContract,
    SceneCorrectionTruthBundleContract,
    SceneCorrectionTruthPairContract,
    SceneCorrectionTruthSummaryContract,
    SceneTruthFollowupContract,
)
from server.adapters.mcp.contracts.vision import VisionCaptureImageContract
from server.adapters.mcp.sampling.result_types import (
    VisionAssistantContract,
    VisionAssistContract,
    VisionBoundaryPolicyContract,
    VisionInputSummaryContract,
    VisionIssueContract,
    VisionPacketStatusContract,
    VisionRecommendedCheckContract,
    to_vision_assistant_contract,
)
from server.adapters.mcp.vision import (
    build_reference_capture_images,
    build_vision_request_from_stage_captures,
    run_vision_assist,
)
from server.adapters.mcp.vision.config import VisionSegmentationSidecarConfig

_VIEW_TOKEN_ALIASES: dict[str, str] = {
    "plan": "top",
    "floor": "top",
    "site": "top",
    "front": "front",
    "facade": "front",
    "elevation": "front",
    "side": "side",
    "profile": "side",
    "section": "side",
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
_ROOF_HINTS: tuple[str, ...] = ("roof", "gable", "ridge", "roofline")
_OPENING_HINTS: tuple[str, ...] = ("opening", "window", "door", "cutout", "portal", "arch")
_SUPPORT_HINTS: tuple[str, ...] = ("support", "post", "column", "pillar", "buttress", "beam")
_BUILDING_MASS_HINTS: tuple[str, ...] = ("facade", "wall", "shell", "volume", "main", "footprint", "tower")


@dataclass(frozen=True)
class _ScopeCluster:
    scope_label: str
    target_objects: tuple[str, ...]
    truth_pairs: tuple[str, ...]


@dataclass(frozen=True)
class ComparePacketPolicy:
    """Resolved packet sizing policy for one staged compare run."""

    max_images_per_packet: int | None
    max_capture_labels_per_packet: int | None
    max_reference_ids_per_packet: int | None


@dataclass(frozen=True)
class PacketCompareExecutionResult:
    compare_diagnostics: ReferenceCompareDiagnosticsContract
    vision_assistant: VisionAssistantContract | None
    part_segmentation: ReferencePartSegmentationContract | None


def _resolve_api_key(*, inline_key: str | None, env_name: str | None) -> str | None:
    if inline_key:
        return inline_key
    if env_name:
        return os.getenv(env_name) or None
    return None


def _bounded_text(value: Any, *, fallback: str | None = None) -> str | None:
    text = str(value).strip() if value is not None else ""
    if not text:
        return fallback
    return text[:240]


def _bounded_path(value: Any) -> str | None:
    text = str(value or "").strip()
    if not text:
        return None
    return text[:240]


def _redact_local_paths(text: str | None) -> str | None:
    if text is None:
        return None
    redacted = re.sub(
        r"(?<!\w)(?:[A-Za-z]:[\\/]|/|\.{1,2}[\\/]|~[\\/])[^\s,;:]+|[^\s,;:]*\\[^\s,;:]+",
        "[redacted-path]",
        text,
    )
    return redacted


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


def _append_unique_note(notes: list[str], note: str) -> None:
    if note not in notes:
        notes.append(note)


def _resolve_localized_support_reason(
    *,
    packet: ReferenceComparePacketContract,
    packet_truth_bundle: SceneCorrectionTruthBundleContract,
    silhouette_analysis: ReferenceSilhouetteAnalysisContract | None,
    action_hints: Sequence[ReferenceActionHintContract],
) -> ReferenceLocalizedSupportReasonLiteral | None:
    """Resolve one normalized packet-local reason for optional localized support."""

    truth_summary = packet_truth_bundle.summary
    scope_label = str(packet.scope_label or "").strip().lower()
    if truth_summary.contact_failures or truth_summary.separated_pairs:
        return "attachment_gap"
    if truth_summary.misaligned_pairs or truth_summary.overlap_pairs:
        return "anchor_ambiguity"
    if any(token in scope_label for token in ("body + head", "head", "snout", "ear", "tail", "limb")):
        return "part_missing_ambiguity"
    if any(token in scope_label for token in ("support", "roofline", "opening", "facade")):
        return "anchor_ambiguity"
    if action_hints:
        return "mask_needed"
    if silhouette_analysis is not None and any(
        metric.severity == "high" for metric in list(silhouette_analysis.metrics)
    ):
        return "seam_unclear"
    return None


def _build_compare_segmentation_request_payload(
    *,
    goal: str | None,
    packet_id: str,
    packet_label: str,
    target_view: str | None,
    scope_label: str | None,
    target_objects: Sequence[str],
    reference_records: Sequence[ReferenceImageRecordContract],
    captures: Sequence[VisionCaptureImageContract],
) -> dict[str, Any]:
    references: list[dict[str, Any]] = []
    for record in reference_records:
        reference_id = str(record.reference_id or "").strip()
        image_path = (
            str(record.stored_path or "").strip()
            or str(record.host_visible_path or "").strip()
            or str(record.original_path or "").strip()
        )
        if not reference_id or not image_path:
            continue
        references.append(
            {
                "reference_id": reference_id,
                "label": str(record.label or "").strip() or None,
                "target_view": str(record.target_view or "").strip() or None,
                "media_type": str(record.media_type or "").strip() or None,
                "image_path": image_path,
            }
        )

    capture_payload = [
        {
            "label": capture.label,
            "preset_name": capture.preset_name,
            "view_kind": capture.view_kind,
            "image_path": capture.image_path,
            "media_type": capture.media_type,
        }
        for capture in captures
        if str(capture.image_path or "").strip()
    ]

    return {
        "goal": goal,
        "packet": {
            "packet_id": packet_id,
            "packet_label": packet_label,
            "target_view": target_view,
            "scope_label": scope_label,
            "target_objects": list(target_objects),
        },
        "references": references,
        "captures": capture_payload,
    }


async def _post_sidecar_payload(
    *,
    endpoint: str,
    timeout_seconds: float,
    api_key: str | None,
    payload: dict[str, Any],
) -> dict[str, Any]:
    timeout = httpx.Timeout(timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            endpoint,
            headers={"Content-Type": "application/json", **({"Authorization": f"Bearer {api_key}"} if api_key else {})},
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("Sidecar returned a non-object JSON payload.")
        return cast(dict[str, Any], data)


def _normalize_part_segmentation_landmarks(
    raw_landmarks: Any,
) -> list[ReferencePartSegmentationLandmarkContract]:
    if not isinstance(raw_landmarks, list):
        return []

    landmarks: list[ReferencePartSegmentationLandmarkContract] = []
    for index, raw_item in enumerate(raw_landmarks, start=1):
        if not isinstance(raw_item, dict):
            continue
        x = raw_item.get("x")
        y = raw_item.get("y")
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            continue
        landmark_id = _bounded_text(raw_item.get("landmark_id"), fallback=f"landmark_{index}") or f"landmark_{index}"
        landmarks.append(
            ReferencePartSegmentationLandmarkContract(
                landmark_id=landmark_id,
                x=float(x),
                y=float(y),
            )
        )
    return landmarks[:16]


def _normalize_compare_part_segmentation_payload(
    payload: dict[str, Any],
    *,
    max_parts: int,
) -> list[ReferencePartSegmentationPartContract]:
    value = payload.get("parts")
    if not isinstance(value, list):
        return []

    parts: list[ReferencePartSegmentationPartContract] = []
    for index, raw_item in enumerate(value, start=1):
        if not isinstance(raw_item, dict):
            continue
        part_label = _bounded_text(raw_item.get("part_label"), fallback=f"part_{index}")
        if not part_label:
            continue
        confidence = raw_item.get("confidence")
        normalized_confidence = float(confidence) if isinstance(confidence, (int, float)) else None
        if normalized_confidence is not None and not 0.0 <= normalized_confidence <= 1.0:
            normalized_confidence = None
        parts.append(
            ReferencePartSegmentationPartContract(
                part_label=part_label,
                mask_path=_bounded_path(raw_item.get("mask_path")),
                crop_path=_bounded_path(raw_item.get("crop_path")),
                confidence=normalized_confidence,
                landmarks=_normalize_part_segmentation_landmarks(raw_item.get("landmarks")),
            )
        )
    return parts[:max_parts]


def _packet_question_for_view(view_id: str | None, *, scope_label: str | None = None) -> str:
    normalized_scope = str(scope_label or "").strip().lower()
    if scope_label and any(token in normalized_scope for token in ("facade", "opening", "bay", "window", "door")):
        return (
            f"Compare the {scope_label} architecture scope against the references. "
            "Focus on opening count, spacing, floor-band rhythm, centerline drift, and bounded facade corrections."
        )
    if scope_label and any(token in normalized_scope for token in ("roof", "ridge", "roofline")):
        return (
            f"Compare the {scope_label} architecture scope against the references. "
            "Focus on roof pitch, ridge height, overhang, roof-wall seating, and upper silhouette drift."
        )
    if scope_label and any(token in normalized_scope for token in ("support", "post", "column", "beam", "buttress")):
        return (
            f"Compare the {scope_label} architecture scope against the references. "
            "Focus on support spacing, seated contact, beam/post alignment, and unsupported or floating elements."
        )
    if view_id == "top":
        return (
            "Compare the plan/top view against the references. "
            "Focus on footprint ratio, depth/width drift, wall-shell alignment, and modular grid placement."
        )
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


def _is_roof_like(object_name: str) -> bool:
    return _has_name_hint(object_name, _ROOF_HINTS)


def _is_opening_like(object_name: str) -> bool:
    return _has_name_hint(object_name, _OPENING_HINTS)


def _is_support_like(object_name: str) -> bool:
    return _has_name_hint(object_name, _SUPPORT_HINTS)


def _is_building_mass_like(object_name: str) -> bool:
    return _has_name_hint(object_name, _BUILDING_MASS_HINTS)


def _semantic_scope_label(part_object: str, anchor_object: str) -> str:
    if _is_opening_like(part_object) and _is_building_mass_like(anchor_object):
        return "Facade + Openings"
    if _is_roof_like(part_object) and _is_building_mass_like(anchor_object):
        return "Roofline"
    if _is_support_like(part_object) or _is_support_like(anchor_object):
        return "Supports"
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
    roofs = [name for name in object_names if _is_roof_like(name)]
    openings = [name for name in object_names if _is_opening_like(name)]
    supports = [name for name in object_names if _is_support_like(name)]
    building_masses = [name for name in object_names if _is_building_mass_like(name)]
    anchor_body = bodies[0] if bodies else primary_target
    head_anchor = heads[0] if heads else primary_target
    building_anchor = building_masses[0] if building_masses else primary_target

    clusters: OrderedDict[str, _ScopeCluster] = OrderedDict()
    consumed: set[str] = {primary_target}

    if building_masses and openings:
        _append_scope_cluster(
            clusters,
            scope_label="Facade + Openings",
            target_objects=(building_anchor, *openings),
        )
        consumed.update(openings)
        consumed.add(building_anchor)

    if building_masses and roofs:
        _append_scope_cluster(
            clusters,
            scope_label="Roofline",
            target_objects=(building_anchor, *roofs),
        )
        consumed.update(roofs)
        consumed.add(building_anchor)

    if supports:
        _append_scope_cluster(
            clusters,
            scope_label="Supports",
            target_objects=(building_anchor, *supports),
        )
        consumed.update(supports)
        consumed.add(building_anchor)

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


def resolve_complex_compare_policy(
    *,
    complexity_tier: ReferenceCompareComplexityTierLiteral,
    max_images_per_packet: int | None,
) -> ComparePacketPolicy:
    """Resolve packet-local image limits for complex staged compare."""

    normalized_max_images = max(1, int(max_images_per_packet)) if max_images_per_packet is not None else None
    if normalized_max_images is None:
        return ComparePacketPolicy(
            max_images_per_packet=None,
            max_capture_labels_per_packet=None,
            max_reference_ids_per_packet=2 if complexity_tier == "super_complex" else None,
        )

    max_capture_labels = max(1, normalized_max_images - 1)
    max_reference_ids = max(0, normalized_max_images - 1)
    if complexity_tier == "super_complex":
        max_reference_ids = min(max_reference_ids, 2)

    return ComparePacketPolicy(
        max_images_per_packet=normalized_max_images,
        max_capture_labels_per_packet=max_capture_labels,
        max_reference_ids_per_packet=max_reference_ids,
    )


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
    packet_target_objects: Sequence[str],
    reference_records: Sequence[ReferenceImageRecordContract],
) -> list[str]:
    packet_targets = {value.strip() for value in packet_target_objects if value.strip()}
    targeted_view: list[str] = []
    targeted_any_view: list[str] = []
    generic_view: list[str] = []
    generic_any_view: list[str] = []

    for reference in reference_records:
        reference_id = reference.reference_id
        reference_target = str(reference.target_object or "").strip() or None
        reference_view = _reference_view_id(reference)
        in_packet_scope = reference_target is not None and reference_target in packet_targets

        if view_id is None:
            if in_packet_scope:
                targeted_any_view.append(reference_id)
            elif reference_target is None:
                generic_any_view.append(reference_id)
            continue

        if in_packet_scope and reference_view == view_id:
            targeted_view.append(reference_id)
            continue
        if in_packet_scope:
            targeted_any_view.append(reference_id)
            continue
        if reference_target is None and reference_view == view_id:
            generic_view.append(reference_id)
            continue
        if reference_target is None:
            generic_any_view.append(reference_id)

    if targeted_view:
        return _unique_preserving_order(targeted_view)
    if generic_view:
        return _unique_preserving_order(generic_view)
    if targeted_any_view:
        return _unique_preserving_order(targeted_any_view)
    if generic_any_view:
        return _unique_preserving_order(generic_any_view)
    return []


def _budgeted_capture_labels(
    capture_labels: Sequence[str],
    *,
    context_capture_labels: Sequence[str],
    policy: ComparePacketPolicy,
) -> tuple[list[str], bool]:
    ordered_capture_labels = _unique_preserving_order(list(capture_labels))
    max_capture_labels = policy.max_capture_labels_per_packet
    if max_capture_labels is None or len(ordered_capture_labels) <= max_capture_labels:
        return ordered_capture_labels, False

    context_labels = set(context_capture_labels)
    focus_labels = [label for label in ordered_capture_labels if label not in context_labels]
    fallback_context_labels = [label for label in ordered_capture_labels if label in context_labels]
    return _unique_preserving_order([*focus_labels, *fallback_context_labels])[:max_capture_labels], True


def _reference_id_chunks_for_policy(
    reference_ids: Sequence[str],
    *,
    capture_count: int,
    policy: ComparePacketPolicy,
) -> tuple[list[list[str]], bool]:
    ordered_reference_ids = _unique_preserving_order(list(reference_ids))
    if not ordered_reference_ids:
        return [[]], False

    max_reference_ids = policy.max_reference_ids_per_packet
    if policy.max_images_per_packet is not None:
        image_slots = max(0, policy.max_images_per_packet - capture_count)
        max_reference_ids = image_slots if max_reference_ids is None else min(max_reference_ids, image_slots)

    if max_reference_ids is None:
        return [ordered_reference_ids], False
    if max_reference_ids <= 0:
        return [[]], True
    if len(ordered_reference_ids) <= max_reference_ids:
        return [ordered_reference_ids], False

    chunks = [
        ordered_reference_ids[index : index + max_reference_ids]
        for index in range(0, len(ordered_reference_ids), max_reference_ids)
    ]
    return chunks, True


def _append_policy_packets(
    packets: list[ReferenceComparePacketContract],
    *,
    packet_id_parts: Sequence[str],
    packet_kind: Literal["view", "scope", "view_scope"],
    packet_label: str,
    target_view: str | None,
    scope_label: str | None,
    target_objects: Sequence[str],
    truth_pairs: Sequence[str] = (),
    reference_ids: Sequence[str],
    capture_labels: Sequence[str],
    compare_question: str,
    context_capture_labels: Sequence[str],
    policy: ComparePacketPolicy,
    budget_notes: list[str],
) -> None:
    effective_capture_labels, captures_trimmed = _budgeted_capture_labels(
        capture_labels,
        context_capture_labels=context_capture_labels,
        policy=policy,
    )
    reference_chunks, references_split = _reference_id_chunks_for_policy(
        reference_ids,
        capture_count=len(effective_capture_labels),
        policy=policy,
    )

    if captures_trimmed and policy.max_images_per_packet is not None:
        _append_unique_note(
            budget_notes,
            (
                "Compare packet policy omitted context captures from some packets to stay within "
                f"VISION_MAX_IMAGES={policy.max_images_per_packet}."
            ),
        )
    if references_split and policy.max_images_per_packet is not None:
        _append_unique_note(
            budget_notes,
            (
                "Compare packet policy split reference evidence into bounded packet-local slices to stay within "
                f"VISION_MAX_IMAGES={policy.max_images_per_packet}."
            ),
        )
    if references_split and not any(reference_chunks) and policy.max_images_per_packet is not None:
        _append_unique_note(
            budget_notes,
            (
                "Runtime image budget is below the 2-image minimum for reference compare packets; "
                "raise VISION_MAX_IMAGES before treating packet conclusions as complete."
            ),
        )

    for index, chunk in enumerate(reference_chunks, start=1):
        sliced = len(reference_chunks) > 1
        effective_packet_label = f"{packet_label} reference slice {index}" if sliced else packet_label
        stable_parts = [
            *packet_id_parts,
            *([f"slice_{index}"] if sliced else []),
            *(chunk or ["no_reference_slice"]),
            *effective_capture_labels,
        ]
        packets.append(
            ReferenceComparePacketContract(
                packet_id=_stable_packet_id("packet", *stable_parts),
                packet_kind=packet_kind,
                packet_label=effective_packet_label,
                target_view=target_view,
                scope_label=scope_label,
                target_objects=list(target_objects),
                truth_pairs=list(truth_pairs),
                reference_ids=list(chunk),
                capture_labels=list(effective_capture_labels),
                compare_question=compare_question,
            )
        )


def build_compare_packets(
    *,
    target_view: str | None,
    captures: Sequence[VisionCaptureImageContract],
    reference_records: Sequence[ReferenceImageRecordContract],
    assembled_target_scope: SceneAssembledTargetScopeContract | None,
    truth_followup: SceneTruthFollowupContract | None,
    max_images_per_packet: int | None = None,
    prefer_target_scope_clusters: bool = False,
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

    all_reference_ids = [reference.reference_id for reference in reference_records]

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
    packet_policy = resolve_complex_compare_policy(
        complexity_tier=complexity_tier,
        max_images_per_packet=max_images_per_packet,
    )

    packets: list[ReferenceComparePacketContract] = []
    budget_notes: list[str] = []
    if complexity_tier == "simple":
        if not selected_views:
            scope_label = assembled_target_scope.scope_kind if assembled_target_scope is not None else None
            _append_policy_packets(
                packets,
                packet_id_parts=(complexity_tier, scope_label or "general"),
                packet_kind="scope",
                packet_label="general packet",
                target_view=None,
                scope_label=scope_label,
                target_objects=list(assembled_target_scope.object_names or [])
                if assembled_target_scope is not None
                else [],
                reference_ids=all_reference_ids,
                capture_labels=all_capture_labels,
                compare_question=_packet_question_for_view(None, scope_label=scope_label),
                context_capture_labels=context_capture_labels,
                policy=packet_policy,
                budget_notes=budget_notes,
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
                packet_target_objects=list(assembled_target_scope.object_names or [])
                if assembled_target_scope is not None
                else [],
                reference_records=reference_records,
            )
            _append_policy_packets(
                packets,
                packet_id_parts=("simple", view_id),
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
                context_capture_labels=context_capture_labels,
                policy=packet_policy,
                budget_notes=budget_notes,
            )
    else:
        scope_clusters = (
            _scope_clusters_from_focus_pairs(
                focus_pairs,
                primary_target=assembled_target_scope.primary_target if assembled_target_scope is not None else None,
            )
            if focus_pairs and not prefer_target_scope_clusters
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
                        packet_target_objects=cluster.target_objects,
                        reference_records=reference_records,
                    )
                    _append_policy_packets(
                        packets,
                        packet_id_parts=(cluster.scope_label, view_id or "scope"),
                        packet_kind="view_scope" if view_id is not None else "scope",
                        packet_label=cluster.scope_label,
                        target_view=view_id,
                        scope_label=cluster.scope_label,
                        target_objects=list(cluster.target_objects),
                        truth_pairs=list(cluster.truth_pairs),
                        reference_ids=packet_reference_ids,
                        capture_labels=packet_capture_labels,
                        compare_question=_packet_question_for_view(view_id, scope_label=cluster.scope_label),
                        context_capture_labels=context_capture_labels,
                        policy=packet_policy,
                        budget_notes=budget_notes,
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
                    packet_target_objects=list(assembled_target_scope.object_names or [])
                    if assembled_target_scope is not None
                    else [],
                    reference_records=reference_records,
                )
                _append_policy_packets(
                    packets,
                    packet_id_parts=("view", view_id),
                    packet_kind="view",
                    packet_label=f"{view_id} packet",
                    target_view=view_id,
                    scope_label=None,
                    target_objects=list(assembled_target_scope.object_names or [])
                    if assembled_target_scope is not None
                    else [],
                    reference_ids=packet_reference_ids,
                    capture_labels=packet_capture_labels,
                    compare_question=_packet_question_for_view(view_id),
                    context_capture_labels=context_capture_labels,
                    policy=packet_policy,
                    budget_notes=budget_notes,
                )
        else:
            scope_label = assembled_target_scope.scope_kind if assembled_target_scope is not None else None
            _append_policy_packets(
                packets,
                packet_id_parts=(complexity_tier, scope_label or "general"),
                packet_kind="scope",
                packet_label="general packet",
                target_view=None,
                scope_label=scope_label,
                target_objects=list(assembled_target_scope.object_names or [])
                if assembled_target_scope is not None
                else [],
                reference_ids=all_reference_ids,
                capture_labels=all_capture_labels,
                compare_question=_packet_question_for_view(None, scope_label=scope_label),
                context_capture_labels=context_capture_labels,
                policy=packet_policy,
                budget_notes=budget_notes,
            )

    return ReferenceCompareDiagnosticsContract(
        complexity_tier=complexity_tier,
        packet_count=len(packets),
        packet_order=[packet.packet_id for packet in packets],
        synthesis_required=len(packets) > 1,
        synthesis_status="not_needed" if len(packets) <= 1 else "skipped",
        packets=packets,
        budget_notes=budget_notes,
    )


def merge_packet_phase_results(
    extraction_result: VisionAssistContract,
    ranking_result: VisionAssistContract,
) -> VisionAssistContract:
    ranking_guidance = ranking_result.packet_guidance
    ranking_downgraded = ranking_guidance is not None and (
        ranking_guidance.packet_status in {"blocked", "low_information"}
        or ranking_guidance.ranking_recommendation in {"skip_blocked", "skip_low_information"}
    )
    if ranking_downgraded:
        shape_mismatches: list[str] = []
        proportion_mismatches: list[str] = []
        correction_focus: list[str] = []
        likely_issues: list[VisionIssueContract] = []
        next_corrections: list[str] = []
        recommended_checks: list[VisionRecommendedCheckContract] = []
    else:
        shape_mismatches = list(extraction_result.shape_mismatches or [])
        proportion_mismatches = list(extraction_result.proportion_mismatches or [])
        correction_focus = list(ranking_result.correction_focus or extraction_result.correction_focus or [])
        likely_issues = list(ranking_result.likely_issues or extraction_result.likely_issues or [])
        next_corrections = list(ranking_result.next_corrections or extraction_result.next_corrections or [])
        recommended_checks = list(ranking_result.recommended_checks or extraction_result.recommended_checks or [])
    return extraction_result.model_copy(
        update={
            "goal_summary": ranking_result.goal_summary or extraction_result.goal_summary,
            "reference_match_summary": ranking_result.reference_match_summary
            or extraction_result.reference_match_summary,
            "visible_changes": list(ranking_result.visible_changes or extraction_result.visible_changes or []),
            "shape_mismatches": shape_mismatches,
            "proportion_mismatches": proportion_mismatches,
            "correction_focus": correction_focus,
            "likely_issues": likely_issues,
            "next_corrections": next_corrections,
            "recommended_checks": recommended_checks,
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
            packet_status="ready" if correction_focus else "clean",
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
        packet.extraction_status in {"blocked", "low_information", "error"}
        or packet.packet_status in {"blocked", "low_information"}
        or packet.ranking_status == "error"
        for packet in compare_diagnostics.packets
    )


def append_compare_synthesis_conflict_notes(compare_diagnostics: ReferenceCompareDiagnosticsContract) -> None:
    """Surface mixed packet conclusions as explicit synthesis uncertainty."""

    if not compare_diagnostics.synthesis_required:
        return

    packet_statuses = {
        packet.packet_status
        for packet in compare_diagnostics.packets
        if packet.packet_status in {"clean", "ready", "blocked", "low_information"}
    }
    if "clean" in packet_statuses and packet_statuses.intersection({"ready", "blocked", "low_information"}):
        _append_unique_note(
            compare_diagnostics.conflict_notes,
            (
                "Compare packets returned mixed clean and corrective/uncertain statuses; "
                "treat synthesis as advisory until the bounded packet details are inspected."
            ),
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


def _packet_capture_subset(
    captures: Sequence[VisionCaptureImageContract],
    packet: ReferenceComparePacketContract,
) -> list[VisionCaptureImageContract]:
    if not packet.capture_labels:
        return []
    selected_labels = set(packet.capture_labels)
    return [capture for capture in captures if capture.label in selected_labels]


def _packet_reference_subset(
    reference_records: Sequence[ReferenceImageRecordContract],
    packet: ReferenceComparePacketContract,
) -> list[ReferenceImageRecordContract]:
    if not packet.reference_ids:
        return []
    selected_ids = set(packet.reference_ids)
    return [record for record in reference_records if record.reference_id in selected_ids]


def _packet_target_object(
    packet: ReferenceComparePacketContract,
    *,
    fallback_target_object: str | None,
) -> str | None:
    if packet.truth_pairs:
        first_pair = str(packet.truth_pairs[0]).strip()
        if " -> " in first_pair:
            focus_object, _anchor_object = first_pair.split(" -> ", 1)
            normalized_focus = focus_object.strip()
            if normalized_focus:
                return normalized_focus
    packet_targets = [value.strip() for value in list(packet.target_objects or []) if value.strip()]
    if len(packet_targets) > 1:
        return packet_targets[1]
    if packet_targets:
        return packet_targets[0]
    return fallback_target_object


def _packet_truth_bundle(
    truth_bundle: SceneCorrectionTruthBundleContract,
    *,
    packet: ReferenceComparePacketContract,
) -> SceneCorrectionTruthBundleContract:
    if not packet.truth_pairs and not packet.target_objects:
        return truth_bundle

    truth_pairs = set(packet.truth_pairs)
    target_objects = set(packet.target_objects)
    selected_checks: list[SceneCorrectionTruthPairContract] = []
    for check in list(truth_bundle.checks or []):
        current_pair_label = (
            f"{check.from_object} -> {check.to_object}" if check.from_object and check.to_object else None
        )
        if current_pair_label is not None and current_pair_label in truth_pairs:
            selected_checks.append(check)
            continue
        if target_objects and {check.from_object, check.to_object}.issubset(target_objects):
            selected_checks.append(check)

    if not selected_checks:
        return truth_bundle

    selected_scope = truth_bundle.scope.model_copy(
        update={
            "scope_kind": "object_set" if len(target_objects) > 1 else truth_bundle.scope.scope_kind,
            "primary_target": packet.target_objects[0] if packet.target_objects else truth_bundle.scope.primary_target,
            "object_names": list(packet.target_objects or truth_bundle.scope.object_names or []),
            "object_count": len(packet.target_objects or truth_bundle.scope.object_names or []),
        }
    )
    selected_summary = SceneCorrectionTruthSummaryContract(
        pairing_strategy=truth_bundle.summary.pairing_strategy,
        pair_count=len(selected_checks),
        evaluated_pairs=len(selected_checks),
        contact_failures=sum(
            1
            for check in selected_checks
            if check.contact_assertion is not None and check.contact_assertion.passed is False
        ),
        overlap_pairs=sum(
            1 for check in selected_checks if any(verdict == "overlap" for verdict in check.relation_verdicts)
        ),
        separated_pairs=sum(
            1 for check in selected_checks if any(verdict == "separated" for verdict in check.relation_verdicts)
        ),
        misaligned_pairs=sum(
            1 for check in selected_checks if any(verdict == "misaligned" for verdict in check.relation_verdicts)
        ),
    )
    return SceneCorrectionTruthBundleContract(
        scope=selected_scope,
        summary=selected_summary,
        checks=selected_checks,
        error=truth_bundle.error,
    )


def merge_compare_time_part_segmentation(
    existing: ReferencePartSegmentationContract | None,
    incoming: ReferencePartSegmentationContract | None,
) -> ReferencePartSegmentationContract | None:
    """Merge packet-local segmentation results into one staged compare payload."""

    if incoming is None:
        return existing
    if existing is None:
        return incoming

    merged_parts: dict[tuple[str, str | None, str | None], ReferencePartSegmentationPartContract] = {}
    for item in [*list(existing.parts or []), *list(incoming.parts or [])]:
        key = (item.part_label.strip().lower(), item.mask_path, item.crop_path)
        if key not in merged_parts:
            merged_parts[key] = item

    merged_notes = _unique_preserving_order([*list(existing.notes or []), *list(incoming.notes or [])])[:8]
    merged_status: Literal["disabled", "available", "unavailable"]
    if existing.status == "available" or incoming.status == "available":
        merged_status = "available"
    elif existing.status == "disabled" and incoming.status == "disabled":
        merged_status = "disabled"
    else:
        merged_status = "unavailable"

    return ReferencePartSegmentationContract(
        status=merged_status,
        provider_name=incoming.provider_name or existing.provider_name,
        advisory_only=True,
        parts=list(merged_parts.values())[:16],
        notes=merged_notes,
    )


async def collect_compare_time_segmentation_support(
    *,
    config: VisionSegmentationSidecarConfig | None,
    goal: str | None,
    packet_id: str,
    packet_label: str,
    target_view: str | None,
    scope_label: str | None,
    target_objects: Sequence[str],
    reference_records: Sequence[ReferenceImageRecordContract],
    captures: Sequence[VisionCaptureImageContract],
) -> ReferencePartSegmentationContract | None:
    """Run the optional advisory-only segmentation sidecar for one compare packet."""

    if config is None or not bool(getattr(config, "enabled", False)) or not getattr(config, "endpoint", None):
        return None

    payload = _build_compare_segmentation_request_payload(
        goal=goal,
        packet_id=packet_id,
        packet_label=packet_label,
        target_view=target_view,
        scope_label=scope_label,
        target_objects=target_objects,
        reference_records=reference_records,
        captures=captures,
    )
    if not payload["references"] or not payload["captures"]:
        return ReferencePartSegmentationContract(
            status="unavailable",
            provider_name=config.provider_name,
            advisory_only=True,
            parts=[],
            notes=[
                "No bounded packet-local reference/capture slice was available for optional part segmentation.",
                "The sidecar path is advisory-only and separate from vision_contract_profile routing.",
            ],
        )

    try:
        response_payload = await _post_sidecar_payload(
            endpoint=str(getattr(config, "endpoint")),
            timeout_seconds=float(getattr(config, "timeout_seconds", 15.0)),
            api_key=_resolve_api_key(
                inline_key=getattr(config, "api_key", None),
                env_name=getattr(config, "api_key_env", None),
            ),
            payload=payload,
        )
        parts = _normalize_compare_part_segmentation_payload(
            response_payload,
            max_parts=int(getattr(config, "max_parts", 16)),
        )
    except Exception as exc:
        return ReferencePartSegmentationContract(
            status="unavailable",
            provider_name=getattr(config, "provider_name", None),
            advisory_only=True,
            parts=[],
            notes=[
                _bounded_text(
                    _redact_local_paths(f"Optional compare-time part segmentation unavailable: {exc}"),
                    fallback="Optional compare-time part segmentation unavailable.",
                )
                or "Optional compare-time part segmentation unavailable.",
                "The sidecar path is advisory-only and separate from vision_contract_profile routing.",
            ],
        )

    if parts:
        summary_note = f"Optional part segmentation sidecar returned {len(parts)} bounded part(s) for compare support."
    else:
        summary_note = "Optional part segmentation sidecar returned no bounded parts for compare support."
        return ReferencePartSegmentationContract(
            status="unavailable",
            provider_name=getattr(config, "provider_name", None),
            advisory_only=True,
            parts=[],
            notes=[
                summary_note,
                "The sidecar path is advisory-only and separate from vision_contract_profile routing.",
            ],
        )
    return ReferencePartSegmentationContract(
        status="available",
        provider_name=getattr(config, "provider_name", None),
        advisory_only=True,
        parts=parts,
        notes=[
            summary_note,
            "The sidecar path is advisory-only and separate from vision_contract_profile routing.",
        ],
    )


async def execute_compare_packets(
    *,
    ctx: Any,
    compare_diagnostics: ReferenceCompareDiagnosticsContract,
    captures: Sequence[VisionCaptureImageContract],
    reference_records: Sequence[ReferenceImageRecordContract],
    truth_bundle: SceneCorrectionTruthBundleContract,
    goal: str | None,
    prompt_hint: str | None,
    checkpoint_label: str | None,
    checkpoint_id: str,
    preset_profile: Literal["compact", "rich"],
    target_view: str | None,
    resolved_collection_name: str | None,
    resolved_target_object: str | None,
    resolved_target_objects: Sequence[str],
    assembled_target_scope: SceneAssembledTargetScopeContract,
    segmentation_sidecar_config: Any,
    resolver: Any,
    run_vision_assist_fn=run_vision_assist,
    to_vision_assistant_contract_fn=to_vision_assistant_contract,
) -> PacketCompareExecutionResult:
    request_goal = goal or "reference-guided staged compare"
    part_segmentation: ReferencePartSegmentationContract | None = None
    packet_assistants: list[tuple[ReferenceComparePacketContract, VisionAssistantContract | None]] = []
    localized_support_requested = False
    sidecar_enabled = bool(
        segmentation_sidecar_config is not None
        and bool(getattr(segmentation_sidecar_config, "enabled", False))
        and getattr(segmentation_sidecar_config, "endpoint", None)
    )

    for packet in compare_diagnostics.packets:
        packet_captures = _packet_capture_subset(captures, packet)
        packet_reference_records = _packet_reference_subset(reference_records, packet)
        if not packet_captures:
            packet.extraction_status = "low_information"
            packet.ranking_status = "skipped"
            packet.packet_status = "low_information"
            packet.ranking_recommendation = "skip_low_information"
            packet.status_reason = "No packet-local staged captures were available for this compare packet."
            packet.uncertainty_notes = [packet.status_reason]
            packet_assistants.append((packet, None))
            continue
        if not packet_reference_records:
            packet.extraction_status = "blocked"
            packet.ranking_status = "skipped"
            packet.packet_status = "blocked"
            packet.ranking_recommendation = "skip_blocked"
            packet.status_reason = "No packet-local reference slice was available for this compare packet."
            packet.uncertainty_notes = [packet.status_reason]
            packet_assistants.append((packet, None))
            continue

        packet_truth_bundle = _packet_truth_bundle(truth_bundle, packet=packet)
        packet_reference_images = build_reference_capture_images(packet_reference_records)
        packet_target_object = _packet_target_object(
            packet,
            fallback_target_object=resolved_target_object or assembled_target_scope.primary_target,
        )
        packet_silhouette_analysis = build_silhouette_analysis_payload(
            selected_reference_records=packet_reference_records,
            captures=packet_captures,
            target_view=packet.target_view or target_view,
        )
        packet_action_hints = build_action_hints_from_silhouette(
            packet_silhouette_analysis,
            target_object=packet.target_objects[0]
            if packet.target_objects
            else (resolved_target_object or assembled_target_scope.primary_target),
        )
        packet.localized_support_reason = _resolve_localized_support_reason(
            packet=packet,
            packet_truth_bundle=packet_truth_bundle,
            silhouette_analysis=packet_silhouette_analysis,
            action_hints=packet_action_hints,
        )
        packet_part_segmentation: ReferencePartSegmentationContract | None = None
        if packet.localized_support_reason is not None:
            localized_support_requested = True
            packet_part_segmentation = await collect_compare_time_segmentation_support(
                config=segmentation_sidecar_config,
                goal=goal,
                packet_id=packet.packet_id,
                packet_label=packet.packet_label,
                target_view=packet.target_view or target_view,
                scope_label=packet.scope_label,
                target_objects=packet.target_objects or list(resolved_target_objects),
                reference_records=packet_reference_records,
                captures=packet_captures,
            )
        part_segmentation = merge_compare_time_part_segmentation(part_segmentation, packet_part_segmentation)
        packet.support_evidence = build_compare_support_evidence(
            packet_silhouette_analysis,
            action_hints=packet_action_hints,
            part_segmentation=packet_part_segmentation,
        )
        packet_support_evidence_summaries = summarize_compare_support_evidence(packet.support_evidence)
        extraction_request = build_vision_request_from_stage_captures(
            packet_captures,
            goal=request_goal,
            target_object=packet_target_object,
            reference_images=packet_reference_images,
            truth_summary=packet_truth_bundle.model_dump(mode="json"),
            prompt_hint=" | ".join(
                part
                for part in (
                    prompt_hint,
                    "comparison_mode=stage_checkpoint_vs_reference",
                    "compare_phase=packet_extraction",
                    f"checkpoint_label={checkpoint_label}" if checkpoint_label else None,
                    f"preset_profile={preset_profile}",
                    f"packet_id={packet.packet_id}",
                    f"packet_kind={packet.packet_kind}",
                    f"packet_label={packet.packet_label}",
                    f"packet_view={packet.target_view}" if packet.target_view else None,
                    f"packet_scope={packet.scope_label}" if packet.scope_label else None,
                    (
                        f"localized_support_reason={packet.localized_support_reason}"
                        if packet.localized_support_reason is not None
                        else None
                    ),
                    f"compare_question={packet.compare_question}",
                    *[
                        f"support_evidence[{index}]={item}"
                        for index, item in enumerate(packet_support_evidence_summaries, start=1)
                    ],
                    f"collection_name={resolved_collection_name}" if resolved_collection_name else None,
                    f"target_objects={','.join(packet.target_objects or list(resolved_target_objects))}"
                    if (packet.target_objects or resolved_target_objects)
                    else None,
                    *[
                        f"capture[{index}] label={capture.label}"
                        for index, capture in enumerate(packet_captures, start=1)
                    ],
                    *[
                        f"reference[{index}] label={record.label}"
                        for index, record in enumerate(packet_reference_records, start=1)
                        if record.label
                    ],
                )
                if part
            )
            or None,
            metadata={
                "mode": "reference_compare_packet",
                "compare_phase": "packet_extraction",
                "source": "compare_stage_checkpoint",
                "checkpoint_id": checkpoint_id,
                "preset_profile": preset_profile,
                "capture_count": len(packet_captures),
                "packet_id": packet.packet_id,
                "packet_kind": packet.packet_kind,
                "packet_label": packet.packet_label,
                "packet_view": packet.target_view,
                "packet_scope": packet.scope_label,
                "localized_support_reason": packet.localized_support_reason,
                "packet_target_object": packet_target_object,
                "packet_reference_ids": list(packet.reference_ids),
                "packet_capture_labels": list(packet.capture_labels),
                "support_evidence_summaries": list(packet_support_evidence_summaries),
                "collection_name": resolved_collection_name,
                "target_objects": list(packet.target_objects or resolved_target_objects),
                "assembled_target_scope": assembled_target_scope.model_dump(mode="json"),
            },
        )
        extraction_outcome = await run_vision_assist_fn(
            ctx,
            request=extraction_request,
            resolver=resolver,
        )
        extraction_vision_assistant = to_vision_assistant_contract_fn(extraction_outcome)
        if extraction_vision_assistant.status != "success" or extraction_vision_assistant.result is None:
            packet.extraction_status = "error"
            packet.ranking_status = "skipped"
            packet.status_reason = extraction_vision_assistant.rejection_reason or extraction_vision_assistant.message
            packet.uncertainty_notes = [packet.status_reason] if packet.status_reason else []
            packet_assistants.append((packet, extraction_vision_assistant))
            continue

        packet_guidance = extraction_vision_assistant.result.packet_guidance
        packet_status = packet_guidance.packet_status if packet_guidance is not None else None
        packet.packet_status = packet_status
        packet.extraction_status = cast(
            Literal["success", "blocked", "low_information", "skipped", "error"],
            {
                "ready": "success",
                "clean": "success",
                "low_information": "low_information",
                "blocked": "blocked",
                None: "success",
            }[packet_status],
        )
        effective_packet_assistant = extraction_vision_assistant
        effective_packet_result = extraction_vision_assistant.result
        packet.evidence_summary = extraction_vision_assistant.result.goal_summary
        packet.correction_focus = list(
            extraction_vision_assistant.result.correction_focus
            or extraction_vision_assistant.result.next_corrections
            or extraction_vision_assistant.result.shape_mismatches
        )[:3]
        packet.status_reason = packet_guidance.status_reason if packet_guidance is not None else None
        packet.ranking_recommendation = packet_guidance.ranking_recommendation if packet_guidance is not None else None
        packet.uncertainty_notes = _unique_preserving_order(
            [
                *(extraction_vision_assistant.result.proportion_mismatches or []),
                *(item.summary for item in list(extraction_vision_assistant.result.likely_issues or [])),
                *([packet.status_reason] if packet.status_reason else []),
            ]
        )[:3]
        ranking_recommendation = packet.ranking_recommendation
        if ranking_recommendation == "rank":
            ranking_request = build_vision_request_from_stage_captures(
                packet_captures,
                goal=request_goal,
                target_object=packet_target_object,
                reference_images=packet_reference_images,
                truth_summary=packet_truth_bundle.model_dump(mode="json"),
                prompt_hint=" | ".join(
                    part
                    for part in (
                        prompt_hint,
                        "comparison_mode=stage_checkpoint_vs_reference",
                        "compare_phase=packet_ranking",
                        f"checkpoint_label={checkpoint_label}" if checkpoint_label else None,
                        f"preset_profile={preset_profile}",
                        f"packet_id={packet.packet_id}",
                        f"packet_kind={packet.packet_kind}",
                        f"packet_label={packet.packet_label}",
                        f"packet_view={packet.target_view}" if packet.target_view else None,
                        f"packet_scope={packet.scope_label}" if packet.scope_label else None,
                        (
                            f"localized_support_reason={packet.localized_support_reason}"
                            if packet.localized_support_reason is not None
                            else None
                        ),
                        *[
                            f"support_evidence[{index}]={item}"
                            for index, item in enumerate(packet_support_evidence_summaries, start=1)
                        ],
                    )
                    if part
                )
                or None,
                metadata={
                    "mode": "reference_compare_packet",
                    "compare_phase": "packet_ranking",
                    "source": "compare_stage_checkpoint",
                    "checkpoint_id": checkpoint_id,
                    "preset_profile": preset_profile,
                    "capture_count": len(packet_captures),
                    "packet_id": packet.packet_id,
                    "packet_kind": packet.packet_kind,
                    "packet_label": packet.packet_label,
                    "packet_view": packet.target_view,
                    "packet_scope": packet.scope_label,
                    "localized_support_reason": packet.localized_support_reason,
                    "packet_target_object": packet_target_object,
                    "packet_reference_ids": list(packet.reference_ids),
                    "packet_capture_labels": list(packet.capture_labels),
                    "support_evidence_summaries": list(packet_support_evidence_summaries),
                    "collection_name": resolved_collection_name,
                    "target_objects": list(packet.target_objects or resolved_target_objects),
                    "assembled_target_scope": assembled_target_scope.model_dump(mode="json"),
                    "extraction_goal_summary": extraction_vision_assistant.result.goal_summary,
                    "extraction_reference_match_summary": extraction_vision_assistant.result.reference_match_summary,
                    "extraction_visible_changes": list(extraction_vision_assistant.result.visible_changes or []),
                    "extraction_shape_mismatches": list(extraction_vision_assistant.result.shape_mismatches or []),
                    "extraction_proportion_mismatches": list(
                        extraction_vision_assistant.result.proportion_mismatches or []
                    ),
                    "extraction_correction_focus": list(extraction_vision_assistant.result.correction_focus or []),
                    "extraction_next_corrections": list(extraction_vision_assistant.result.next_corrections or []),
                    "extraction_status_reason": packet.status_reason,
                },
            )
            ranking_outcome = await run_vision_assist_fn(
                ctx,
                request=ranking_request,
                resolver=resolver,
            )
            ranking_vision_assistant = to_vision_assistant_contract_fn(ranking_outcome)
            if ranking_vision_assistant.status != "success" or ranking_vision_assistant.result is None:
                packet.ranking_status = "error"
                ranking_error = ranking_vision_assistant.rejection_reason or ranking_vision_assistant.message
                packet.uncertainty_notes = _unique_preserving_order(
                    [*packet.uncertainty_notes, f"Packet ranking failed: {ranking_error}"]
                )[:3]
            else:
                packet.ranking_status = "success"
                effective_packet_result = merge_packet_phase_results(
                    extraction_vision_assistant.result,
                    ranking_vision_assistant.result,
                )
                effective_packet_assistant = extraction_vision_assistant.model_copy(
                    update={
                        "message": "vision_assist completed extraction and ranking for one compare packet.",
                        "result": effective_packet_result,
                    }
                )
                effective_packet_guidance = effective_packet_result.packet_guidance
                packet.packet_status = (
                    effective_packet_guidance.packet_status if effective_packet_guidance else packet.packet_status
                )
                packet.ranking_recommendation = (
                    effective_packet_guidance.ranking_recommendation
                    if effective_packet_guidance
                    else packet.ranking_recommendation
                )
                packet.status_reason = (
                    effective_packet_guidance.status_reason if effective_packet_guidance else packet.status_reason
                )
                packet.evidence_summary = effective_packet_result.goal_summary
                packet.correction_focus = list(
                    effective_packet_result.correction_focus
                    or effective_packet_result.next_corrections
                    or effective_packet_result.shape_mismatches
                )[:3]
                if packet.packet_status in {"blocked", "low_information"} and packet.status_reason:
                    packet.uncertainty_notes = _unique_preserving_order(
                        [*packet.uncertainty_notes, packet.status_reason]
                    )[:3]
        elif ranking_recommendation == "skip_clean":
            packet.ranking_status = "not_needed"
        elif ranking_recommendation in {"skip_low_information", "skip_blocked"}:
            packet.ranking_status = "skipped"
        else:
            packet.ranking_status = "success" if packet.correction_focus else "skipped"
        packet_assistants.append((packet, effective_packet_assistant))

    if part_segmentation is None and sidecar_enabled and not localized_support_requested:
        part_segmentation = ReferencePartSegmentationContract(
            status="disabled",
            provider_name=getattr(segmentation_sidecar_config, "provider_name", None),
            advisory_only=True,
            parts=[],
            notes=[
                "Optional part segmentation sidecar is enabled, but no bounded packet-local localized support reason requested it for this staged compare run.",
                "The sidecar path is advisory-only and separate from vision_contract_profile routing.",
            ],
        )

    successful_packet_results = [
        (packet, assistant.result)
        for packet, assistant in packet_assistants
        if (
            assistant is not None
            and assistant.status == "success"
            and assistant.result is not None
            and packet.extraction_status == "success"
            and packet.packet_status not in {"blocked", "low_information"}
        )
    ]
    if compare_diagnostics.synthesis_required:
        synthesized_packet_result = synthesize_packet_vision_result(successful_packet_results)
        compare_diagnostics.synthesis_status = "success" if synthesized_packet_result is not None else "error"
    else:
        synthesized_packet_result = successful_packet_results[0][1] if successful_packet_results else None
        compare_diagnostics.synthesis_status = "not_needed"

    successful_assistants = [
        assistant for _, assistant in packet_assistants if assistant is not None and assistant.status == "success"
    ]
    vision_assistant: VisionAssistantContract | None
    if successful_assistants and synthesized_packet_result is not None:
        if len(successful_assistants) == 1 and not compare_diagnostics.synthesis_required:
            vision_assistant = successful_assistants[0]
        else:
            vision_assistant = successful_assistants[0].model_copy(
                update={
                    "message": f"vision_assist completed across {len(successful_assistants)} compare packet(s).",
                    "result": synthesized_packet_result,
                }
            )
    else:
        vision_assistant = next((assistant for _, assistant in packet_assistants if assistant is not None), None)

    failed_packet_count = count_failed_compare_packets(compare_diagnostics)
    if failed_packet_count:
        _append_unique_note(
            compare_diagnostics.conflict_notes,
            f"{failed_packet_count} compare packet(s) were blocked, low-information, or failed before synthesis.",
        )
    append_compare_synthesis_conflict_notes(compare_diagnostics)

    return PacketCompareExecutionResult(
        compare_diagnostics=compare_diagnostics,
        vision_assistant=vision_assistant,
        part_segmentation=part_segmentation,
    )
