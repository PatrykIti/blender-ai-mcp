"""Shared packet-planning and synthesis policy for staged reference compare."""

from __future__ import annotations

import hashlib
import os
import re
from collections import OrderedDict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from dataclasses import replace as dataclass_replace
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
    ReferenceCompareScopeSourceLiteral,
    ReferenceDefectVerifyStatusContract,
    ReferenceImageRecordContract,
    ReferenceLocalizedSupportReasonLiteral,
    ReferenceOpenDefectContract,
    ReferencePartSegmentationContract,
    ReferencePartSegmentationLandmarkContract,
    ReferencePartSegmentationPartContract,
    ReferenceRuntimeCapabilityUsageContract,
    ReferenceRuntimeEvidenceContract,
    ReferenceSilhouetteAnalysisContract,
)
from server.adapters.mcp.contracts.scene import (
    SceneAssembledTargetScopeContract,
    SceneCorrectionTruthBundleContract,
    SceneCorrectionTruthPairContract,
    SceneCorrectionTruthSummaryContract,
    SceneTruthFollowupContract,
)
from server.adapters.mcp.contracts.vision import VisionCaptureImageContract, VisionOverlayMarkContract
from server.adapters.mcp.sampling.result_types import (
    VisionAssistantContract,
    VisionAssistContract,
    VisionBoundaryPolicyContract,
    VisionDefectVerifyStatusContract,
    VisionFindingContract,
    VisionInputSummaryContract,
    VisionIssueContract,
    VisionMarkCorrespondenceContract,
    VisionOpenDefectContract,
    VisionPacketStatusContract,
    VisionRecommendedCheckContract,
    to_vision_assistant_contract,
)
from server.adapters.mcp.vision import (
    build_reference_capture_images,
    build_vision_request_from_stage_captures,
    run_vision_assist,
)
from server.adapters.mcp.vision.config import (
    VisionLocalizationCandidate,
    VisionLocalizationConfig,
    VisionSegmentationSidecarConfig,
)

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
_SUPPLEMENTAL_CAPTURE_VIEW_KINDS: set[str] = {"depth", "normal", "object_id", "overlay"}
_HEAD_HINTS: tuple[str, ...] = ("head", "skull", "face")
_BODY_HINTS: tuple[str, ...] = ("body", "torso", "trunk", "chest", "abdomen", "pelvis", "hip")
_TAIL_HINTS: tuple[str, ...] = ("tail",)
_EAR_HINTS: tuple[str, ...] = ("ear",)
_ROOF_HINTS: tuple[str, ...] = ("roof", "gable", "ridge", "roofline")
_OPENING_HINTS: tuple[str, ...] = ("opening", "window", "door", "cutout", "portal", "arch")
_SUPPORT_HINTS: tuple[str, ...] = ("support", "post", "column", "pillar", "buttress", "beam")
_BUILDING_MASS_HINTS: tuple[str, ...] = ("facade", "wall", "shell", "volume", "main", "footprint", "tower")
_LOCALIZATION_QUERY_HINTS: tuple[tuple[str, str], ...] = (
    ("tail", "tail_mass"),
    ("snout", "snout_mass"),
    ("nose", "snout_mass"),
    ("muzzle", "snout_mass"),
    ("ear", "ear_pair"),
    ("head", "head_mass"),
    ("foreleg", "foreleg_pair"),
    ("front_leg", "foreleg_pair"),
    ("forelimb", "foreleg_pair"),
    ("hindleg", "hindleg_pair"),
    ("rear_leg", "hindleg_pair"),
    ("back_leg", "hindleg_pair"),
    ("hindlimb", "hindleg_pair"),
)


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


def _is_supplemental_capture(capture: VisionCaptureImageContract) -> bool:
    return str(capture.view_kind or "").strip().lower() in _SUPPLEMENTAL_CAPTURE_VIEW_KINDS


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


def _unique_bounded_with_omitted(values: Sequence[str], *, max_items: int) -> tuple[list[str], int]:
    unique_values = _unique_preserving_order(values)
    bounded = unique_values[:max_items]
    return bounded, max(0, len(unique_values) - len(bounded))


def _append_unique_note(notes: list[str], note: str) -> None:
    if note not in notes:
        notes.append(note)


def _slug_tokenize(value: str | None) -> list[str]:
    return [token for token in re.split(r"[^a-z0-9]+", str(value or "").strip().lower()) if token]


def _query_labels_for_packet(packet: ReferenceComparePacketContract) -> list[str]:
    query_labels: list[str] = []
    sources = [packet.scope_label, packet.packet_label, *list(packet.target_objects or [])]
    normalized_sources = ["_".join(_slug_tokenize(source)) for source in sources]
    for normalized_source in normalized_sources:
        for hint, query_label in _LOCALIZATION_QUERY_HINTS:
            if hint in normalized_source and query_label not in query_labels:
                query_labels.append(query_label)
    if not query_labels and packet.scope_label:
        fallback_label = "_".join(_slug_tokenize(packet.scope_label))
        if fallback_label and fallback_label not in {
            "single_object",
            "object_set",
            "collection",
            "scene",
            "general_packet",
            "front_packet",
            "side_packet",
            "top_packet",
            "back_packet",
        }:
            query_labels.append(fallback_label)
    return query_labels[:4]


_CREATURE_DOMAIN_TOKENS: frozenset[str] = frozenset(
    {"creature", "animal", "squirrel", "rabbit", "mouse", "fox", "cat", "dog", "bird"}
)
_CREATURE_APPENDAGE_TOKENS: frozenset[str] = frozenset(
    {
        "tail",
        "ear",
        "leg",
        "foreleg",
        "hindleg",
        "paw",
        "foot",
        "limb",
        "snout",
        "muzzle",
        "nose",
        "wing",
        "horn",
        "antler",
    }
)


def _text_tokens_for_packet(packet: ReferenceComparePacketContract) -> str:
    return " ".join(
        str(item or "").strip().lower()
        for item in [
            packet.packet_label,
            packet.scope_label,
            packet.compare_question,
            *list(packet.target_objects or []),
        ]
    )


def _is_creature_compare_domain(*, goal: str | None, guided_domain_profile: str | None) -> bool:
    if str(guided_domain_profile or "").strip().lower() == "creature":
        return True
    goal_text = str(goal or "").strip().lower()
    return any(token in goal_text for token in _CREATURE_DOMAIN_TOKENS)


def _is_bounded_creature_appendage_packet(packet: ReferenceComparePacketContract) -> bool:
    text = _text_tokens_for_packet(packet)
    if "body + head" in text:
        return False
    return any(token in text for token in _CREATURE_APPENDAGE_TOKENS)


def _prior_defect_matches_packet(
    packet: ReferenceComparePacketContract,
    prior_open_defects: Sequence[Mapping[str, Any] | ReferenceOpenDefectContract],
) -> bool:
    packet_text = _text_tokens_for_packet(packet)
    for raw_defect in prior_open_defects:
        if isinstance(raw_defect, ReferenceOpenDefectContract):
            defect_text = " ".join(
                item for item in [raw_defect.scope_label or "", raw_defect.summary or ""] if item
            ).lower()
        elif isinstance(raw_defect, Mapping):
            defect_text = " ".join(
                str(raw_defect.get(key) or "")
                for key in ("scope_label", "summary", "relation_ref")
                if raw_defect.get(key)
            ).lower()
        else:
            continue
        if not defect_text:
            continue
        if any(token in packet_text and token in defect_text for token in _CREATURE_APPENDAGE_TOKENS):
            return True
    return False


def _high_silhouette_severity(silhouette_analysis: ReferenceSilhouetteAnalysisContract | None) -> bool:
    return silhouette_analysis is not None and any(
        metric.severity == "high" for metric in list(silhouette_analysis.metrics)
    )


def _normalize_box_xyxy(raw_box: Any) -> tuple[float, float, float, float] | None:
    if not isinstance(raw_box, list | tuple) or len(raw_box) != 4:
        return None
    if not all(isinstance(value, int | float) for value in raw_box):
        return None
    x1, y1, x2, y2 = (float(value) for value in raw_box)
    if x2 <= x1 or y2 <= y1:
        return None
    return x1, y1, x2, y2


def _derive_localization_landmarks(
    box_xyxy: tuple[float, float, float, float],
) -> list[ReferencePartSegmentationLandmarkContract]:
    x1, y1, x2, y2 = box_xyxy
    center_x = (x1 + x2) / 2.0
    center_y = (y1 + y2) / 2.0
    return [ReferencePartSegmentationLandmarkContract(landmark_id="box_center", x=center_x, y=center_y)]


def _resolve_localized_support_reason(
    *,
    goal: str | None = None,
    guided_domain_profile: str | None = None,
    packet: ReferenceComparePacketContract,
    packet_truth_bundle: SceneCorrectionTruthBundleContract,
    silhouette_analysis: ReferenceSilhouetteAnalysisContract | None,
    action_hints: Sequence[ReferenceActionHintContract],
    prior_open_defects: Sequence[Mapping[str, Any] | ReferenceOpenDefectContract] = (),
) -> ReferenceLocalizedSupportReasonLiteral | None:
    """Resolve one normalized packet-local reason for optional localized support."""

    if not _is_creature_compare_domain(goal=goal, guided_domain_profile=guided_domain_profile):
        return None
    if not _is_bounded_creature_appendage_packet(packet):
        return None

    truth_summary = packet_truth_bundle.summary
    if truth_summary.contact_failures or truth_summary.separated_pairs:
        return "attachment_gap"
    if truth_summary.misaligned_pairs or truth_summary.overlap_pairs:
        return "anchor_ambiguity"
    if action_hints:
        return "mask_needed"
    if _high_silhouette_severity(silhouette_analysis):
        return "seam_unclear"
    if _prior_defect_matches_packet(packet, prior_open_defects):
        return "part_missing_ambiguity"
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


def _build_compare_localization_request_payload(
    *,
    goal: str | None,
    packet: ReferenceComparePacketContract,
    reference_records: Sequence[ReferenceImageRecordContract],
    captures: Sequence[VisionCaptureImageContract],
) -> dict[str, Any]:
    payload = _build_compare_segmentation_request_payload(
        goal=goal,
        packet_id=packet.packet_id,
        packet_label=packet.packet_label,
        target_view=packet.target_view,
        scope_label=packet.scope_label,
        target_objects=packet.target_objects,
        reference_records=reference_records,
        captures=captures,
    )
    payload["localized_support_reason"] = packet.localized_support_reason
    payload["query_labels"] = _query_labels_for_packet(packet)
    payload["packet"]["mark_id_map"] = dict(packet.mark_id_map)
    return payload


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


def _normalize_compare_localization_payload(
    payload: dict[str, Any],
    *,
    packet_id: str,
    max_candidates: int,
    fallback_target_view: str | None,
) -> list[VisionLocalizationCandidate]:
    value = payload.get("candidates")
    if not isinstance(value, list):
        return []

    candidates: list[VisionLocalizationCandidate] = []
    for raw_item in value:
        if not isinstance(raw_item, dict):
            continue
        query_label = _bounded_text(raw_item.get("query_label") or raw_item.get("part_label"))
        box_xyxy = _normalize_box_xyxy(raw_item.get("box_xyxy"))
        if query_label is None or box_xyxy is None:
            continue
        confidence = raw_item.get("confidence")
        normalized_confidence = float(confidence) if isinstance(confidence, (int, float)) else None
        if normalized_confidence is not None and not 0.0 <= normalized_confidence <= 1.0:
            normalized_confidence = None
        candidates.append(
            VisionLocalizationCandidate(
                packet_id=packet_id,
                query_label=query_label,
                reference_id=_bounded_text(raw_item.get("reference_id")),
                capture_label=_bounded_text(raw_item.get("capture_label")),
                target_view=_bounded_text(raw_item.get("target_view"), fallback=fallback_target_view),
                confidence=normalized_confidence,
                box_xyxy=box_xyxy,
                crop_path=_bounded_path(raw_item.get("crop_path")),
            )
        )
    return candidates[:max_candidates]


def _project_localization_candidates_to_part_segmentation(
    *,
    provider_name: str | None,
    candidates: Sequence[VisionLocalizationCandidate],
) -> ReferencePartSegmentationContract:
    parts = [
        ReferencePartSegmentationPartContract(
            part_label=item.query_label,
            crop_path=item.crop_path,
            confidence=item.confidence,
            landmarks=_derive_localization_landmarks(item.box_xyxy),
        )
        for item in candidates
    ]
    return ReferencePartSegmentationContract(
        status="available",
        provider_name=provider_name,
        advisory_only=True,
        parts=parts[:16],
        notes=[
            f"Optional compare-time localization returned {len(parts[:16])} bounded candidate(s) for compare support.",
            "Literal localization boxes stay internal; public payload projects only crops and derived anchors.",
        ],
    )


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


def _is_guided_registry_scope(
    assembled_target_scope: SceneAssembledTargetScopeContract | None,
) -> bool:
    if assembled_target_scope is None:
        return False
    for role in list(assembled_target_scope.object_roles or []):
        if "guided_part_registry" in set(role.signals or []):
            return True
    return False


def _registered_compare_scope(
    assembled_target_scope: SceneAssembledTargetScopeContract | None,
) -> SceneAssembledTargetScopeContract | None:
    if not _is_guided_registry_scope(assembled_target_scope):
        return None
    return assembled_target_scope


def _scope_clusters_from_registered_graph(
    assembled_target_scope: SceneAssembledTargetScopeContract | None,
    *,
    focus_pairs: Sequence[str],
) -> list[_ScopeCluster]:
    if assembled_target_scope is None or not _is_guided_registry_scope(assembled_target_scope):
        return []
    object_names = _unique_preserving_order(list(assembled_target_scope.object_names or []))
    if len(object_names) < 2:
        return []
    return [
        _ScopeCluster(
            scope_label="Registered Part Graph",
            target_objects=tuple(object_names),
            truth_pairs=tuple(_unique_preserving_order(list(focus_pairs))),
        )
    ]


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


def _capture_mark_id_map(captures: Sequence[VisionCaptureImageContract]) -> dict[str, int]:
    mark_id_map: dict[str, int] = {}
    for capture in captures:
        if capture.view_kind != "overlay":
            continue
        for mark in list(capture.overlay_marks or []):
            if mark.status != "placed" or mark.image_side != "render":
                continue
            object_name = str(mark.object_name or "").strip()
            mark_id = mark.mark_id
            if not object_name or not isinstance(mark_id, int) or isinstance(mark_id, bool) or mark_id <= 0:
                continue
            mark_id_map.setdefault(object_name, mark_id)
    return mark_id_map


def _packet_mark_id_map(
    *,
    full_mark_id_map: dict[str, int],
    packet_target_objects: Sequence[str],
) -> dict[str, int]:
    if not full_mark_id_map:
        return {}
    packet_targets = {str(name).strip() for name in packet_target_objects if str(name).strip()}
    if not packet_targets:
        return dict(sorted(full_mark_id_map.items(), key=lambda item: (item[1], item[0])))
    return {
        object_name: mark_id
        for object_name, mark_id in sorted(full_mark_id_map.items(), key=lambda item: (item[1], item[0]))
        if object_name in packet_targets
    }


def _object_role_map(scope: SceneAssembledTargetScopeContract) -> dict[str, str]:
    return {
        role.object_name: role.role for role in list(scope.object_roles or []) if str(role.object_name or "").strip()
    }


def _object_name_for_reference_query(
    packet: ReferenceComparePacketContract,
    query_label: str | None,
) -> str | None:
    normalized_query = "_".join(_slug_tokenize(query_label))
    if not normalized_query:
        return None
    for object_name in packet.mark_id_map:
        normalized_object = "_".join(_slug_tokenize(object_name))
        if normalized_query == normalized_object or normalized_query in normalized_object:
            return object_name
    for hint, candidate_label in _LOCALIZATION_QUERY_HINTS:
        if candidate_label != normalized_query:
            continue
        for object_name in packet.mark_id_map:
            if hint in "_".join(_slug_tokenize(object_name)):
                return object_name
    return None


def _reference_marks_for_localization_candidates(
    packet: ReferenceComparePacketContract,
    candidates: Sequence[VisionLocalizationCandidate],
) -> list[VisionOverlayMarkContract]:
    marks: list[VisionOverlayMarkContract] = []
    seen_ids: set[int] = set()
    for candidate in candidates:
        object_name = _object_name_for_reference_query(packet, candidate.query_label)
        if object_name is None:
            continue
        mark_id = packet.mark_id_map.get(object_name)
        if mark_id is None or mark_id in seen_ids:
            continue
        seen_ids.add(mark_id)
        marks.append(
            VisionOverlayMarkContract(
                mark_id=mark_id,
                object_name=object_name,
                status="placed",
                source="grounded_sam_sidecar",
                image_side="reference",
            )
        )
    return marks


def _packet_mark_request_metadata(packet: ReferenceComparePacketContract) -> dict[str, Any]:
    """Return mark-keyed request metadata only when packet marks are available."""

    metadata: dict[str, Any] = {}
    if packet.mark_id_map:
        metadata["packet_mark_id_map"] = dict(packet.mark_id_map)
    if packet.reference_marks:
        metadata["reference_marks"] = [
            mark.model_dump(mode="json", exclude_none=True) for mark in packet.reference_marks
        ]
    return metadata


def _mark_correspondence_for_result(
    result: VisionAssistContract,
    *,
    packet: ReferenceComparePacketContract,
    assembled_target_scope: SceneAssembledTargetScopeContract,
    retry_attempted: bool,
) -> tuple[VisionAssistContract, list[int]]:
    if not packet.mark_id_map:
        return result.model_copy(update={"validity_retry_attempted": retry_attempted}), []

    mark_id_to_object = {mark_id: object_name for object_name, mark_id in packet.mark_id_map.items()}
    reference_mark_ids = {mark.mark_id for mark in list(packet.reference_marks or []) if mark.status == "placed"}
    role_by_object = _object_role_map(assembled_target_scope)
    rejected_mark_ids: list[int] = []
    rows_by_mark: OrderedDict[int, VisionMarkCorrespondenceContract] = OrderedDict()
    for finding in list(result.findings or []):
        mark_id = finding.mark_id
        if mark_id is None:
            continue
        object_name = mark_id_to_object.get(mark_id)
        if object_name is None:
            rejected_mark_ids.append(mark_id)
            continue
        existing = rows_by_mark.get(mark_id)
        sides: list[Literal["render", "reference"]] = ["render"]
        if mark_id in reference_mark_ids:
            sides.append("reference")
        finding_text = finding.finding.strip()
        if existing is None:
            rows_by_mark[mark_id] = VisionMarkCorrespondenceContract(
                mark_id=mark_id,
                object_name=object_name,
                role=role_by_object.get(object_name),
                image_sides=sides,
                proportional_ratio_vs_anchor=finding.magnitude_ratio,
                findings=[finding_text] if finding_text else [],
            )
            continue
        rows_by_mark[mark_id] = existing.model_copy(
            update={
                "image_sides": _unique_preserving_order([*existing.image_sides, *sides]),
                "findings": _unique_preserving_order([*existing.findings, *([finding_text] if finding_text else [])])[
                    :3
                ],
                "proportional_ratio_vs_anchor": existing.proportional_ratio_vs_anchor
                if existing.proportional_ratio_vs_anchor is not None
                else finding.magnitude_ratio,
            }
        )

    rejected = sorted(set(rejected_mark_ids))
    return (
        result.model_copy(
            update={
                "object_correspondence": list(rows_by_mark.values()),
                "rejected_mark_ids": rejected,
                "validity_retry_attempted": retry_attempted,
            }
        ),
        rejected,
    )


def _normalized_defect_text(value: str | None) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def _packet_scoped_defect_id(
    packet: ReferenceComparePacketContract,
    *,
    summary: str,
    target_label: str | None = None,
    axis: str | None = None,
    direction: str | None = None,
) -> str:
    key = "|".join(
        (
            packet.packet_id,
            str(packet.scope_label or ""),
            str(target_label or ""),
            str(axis or ""),
            str(direction or ""),
            _normalized_defect_text(summary)[:120],
        )
    )
    return "defect_" + hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]


def _defect_scope_label(
    *,
    packet: ReferenceComparePacketContract,
    target_label: str | None = None,
) -> str | None:
    label = str(target_label or "").strip()
    if label:
        return label
    return packet.scope_label


def _defect_relation_ref(finding: VisionFindingContract) -> str | None:
    parts = [
        str(finding.target_label or "").strip(),
        str(finding.axis or "").strip(),
        str(finding.direction or "").strip(),
    ]
    normalized = [part for part in parts if part and part != "none"]
    return " ".join(normalized) if normalized else None


def _defect_severity(
    summary: str,
    *,
    result: VisionAssistContract,
    finding: VisionFindingContract | None = None,
) -> Literal["high", "medium", "low"]:
    normalized_summary = _normalized_defect_text(summary)
    correction_keys = {_normalized_defect_text(item) for item in list(result.correction_focus or [])}
    if normalized_summary and any(
        normalized_summary in correction_key or correction_key in normalized_summary
        for correction_key in correction_keys
    ):
        return "high"
    for issue in list(result.likely_issues or []):
        if issue.severity == "high" and _normalized_defect_text(issue.summary) in normalized_summary:
            return "high"
    if finding is not None and finding.confidence is not None and finding.confidence < 0.35:
        return "low"
    return "medium"


def _open_defects_for_result(
    result: VisionAssistContract,
    *,
    packet: ReferenceComparePacketContract,
) -> tuple[list[VisionFindingContract], list[VisionOpenDefectContract]]:
    if result.packet_guidance is not None and result.packet_guidance.packet_status == "clean":
        return list(result.findings or []), []

    findings: list[VisionFindingContract] = []
    open_defects: list[VisionOpenDefectContract] = []
    seen_defect_ids: set[str] = set()
    for finding in list(result.findings or []):
        summary = str(finding.finding or "").strip()
        if not summary:
            findings.append(finding)
            continue
        defect_id = _packet_scoped_defect_id(
            packet,
            summary=summary,
            target_label=finding.target_label,
            axis=finding.axis,
            direction=finding.direction,
        )
        scoped_finding = finding.model_copy(update={"defect_id": defect_id})
        findings.append(scoped_finding)
        if defect_id in seen_defect_ids:
            continue
        seen_defect_ids.add(defect_id)
        open_defects.append(
            VisionOpenDefectContract(
                defect_id=defect_id,
                summary=_bounded_text(summary, fallback="Packet compare defect.") or "Packet compare defect.",
                scope_label=_defect_scope_label(packet=packet, target_label=finding.target_label),
                relation_ref=_defect_relation_ref(finding),
                severity=_defect_severity(summary, result=result, finding=finding),
            )
        )

    if open_defects:
        return findings, open_defects[:8]

    fallback_items = _unique_preserving_order(
        [
            *list(result.correction_focus or []),
            *list(result.shape_mismatches or []),
            *list(result.proportion_mismatches or []),
        ]
    )
    for summary in fallback_items:
        defect_id = _packet_scoped_defect_id(packet, summary=summary, target_label=packet.scope_label)
        if defect_id in seen_defect_ids:
            continue
        seen_defect_ids.add(defect_id)
        open_defects.append(
            VisionOpenDefectContract(
                defect_id=defect_id,
                summary=_bounded_text(summary, fallback="Packet compare defect.") or "Packet compare defect.",
                scope_label=packet.scope_label,
                relation_ref=packet.target_view,
                severity=_defect_severity(summary, result=result),
            )
        )
        if len(open_defects) >= 8:
            break
    return findings, open_defects


def _coerce_prior_open_defect(value: object) -> ReferenceOpenDefectContract | None:
    if isinstance(value, ReferenceOpenDefectContract):
        return value
    if isinstance(value, VisionOpenDefectContract):
        return ReferenceOpenDefectContract.model_validate(value.model_dump(mode="json"))
    if isinstance(value, Mapping):
        try:
            return ReferenceOpenDefectContract.model_validate(dict(value))
        except Exception:
            return None
    return None


def _prior_defects_for_packet(
    prior_open_defects: Sequence[Mapping[str, Any] | ReferenceOpenDefectContract],
    *,
    packet: ReferenceComparePacketContract,
) -> list[ReferenceOpenDefectContract]:
    defects: list[ReferenceOpenDefectContract] = []
    for item in prior_open_defects:
        if isinstance(item, Mapping):
            item_packet_id = str(item.get("packet_id") or "").strip()
            item_scope_label = str(item.get("scope_label") or "").strip()
            nested_defects = item.get("defects")
            if item_packet_id and item_packet_id != packet.packet_id:
                continue
            if not item_packet_id and item_scope_label and item_scope_label != str(packet.scope_label or "").strip():
                continue
            if isinstance(nested_defects, Sequence) and not isinstance(nested_defects, (str, bytes)):
                for nested in nested_defects:
                    defect = _coerce_prior_open_defect(nested)
                    if defect is not None:
                        defects.append(defect)
                continue
        defect = _coerce_prior_open_defect(item)
        if defect is not None and (
            not defect.scope_label
            or defect.scope_label == packet.scope_label
            or defect.scope_label in list(packet.target_objects or [])
        ):
            defects.append(defect)
    return defects


def _verify_status_for_prior_defects(
    *,
    packet: ReferenceComparePacketContract,
    prior_defects: Sequence[ReferenceOpenDefectContract],
    current_defects: Sequence[VisionOpenDefectContract],
    packet_status: str | None,
) -> list[VisionDefectVerifyStatusContract]:
    if not prior_defects:
        return []

    current_ids = {defect.defect_id for defect in current_defects}
    current_has_defects = bool(current_defects)
    statuses: list[VisionDefectVerifyStatusContract] = []
    seen: set[str] = set()
    for prior in prior_defects:
        if prior.defect_id in seen:
            continue
        seen.add(prior.defect_id)
        if prior.defect_id in current_ids:
            status: Literal["resolved", "unresolved", "downgraded"] = "unresolved"
            reason = "Same-view Critic emitted this stable defect again."
        elif packet_status == "clean" or not current_has_defects:
            status = "resolved"
            reason = (
                "Same-view rerender did not re-emit this defect and the packet has no remaining advisory defect; "
                "deterministic gates still own final completion."
            )
        else:
            status = "downgraded"
            reason = (
                "Same-view rerender no longer emitted this exact defect, but other packet defects remain; "
                "keep deterministic verification active."
            )
        statuses.append(
            VisionDefectVerifyStatusContract(
                defect_id=prior.defect_id,
                status=status,
                reason=reason,
                scope_label=prior.scope_label or packet.scope_label,
            )
        )
    return statuses


def _apply_packet_defect_tracking(
    result: VisionAssistContract,
    *,
    packet: ReferenceComparePacketContract,
    prior_open_defects: Sequence[Mapping[str, Any] | ReferenceOpenDefectContract],
) -> VisionAssistContract:
    findings, open_defects = _open_defects_for_result(result, packet=packet)
    verify_status = _verify_status_for_prior_defects(
        packet=packet,
        prior_defects=_prior_defects_for_packet(prior_open_defects, packet=packet),
        current_defects=open_defects,
        packet_status=result.packet_guidance.packet_status if result.packet_guidance is not None else None,
    )
    return result.model_copy(
        update={
            "findings": findings,
            "open_defects": open_defects,
            "verify_status": verify_status,
        }
    )


def _reference_open_defects(defects: Sequence[VisionOpenDefectContract]) -> list[ReferenceOpenDefectContract]:
    return [ReferenceOpenDefectContract.model_validate(defect.model_dump(mode="json")) for defect in defects]


def _reference_verify_statuses(
    statuses: Sequence[VisionDefectVerifyStatusContract],
) -> list[ReferenceDefectVerifyStatusContract]:
    return [ReferenceDefectVerifyStatusContract.model_validate(status.model_dump(mode="json")) for status in statuses]


def _budgeted_capture_labels(
    capture_labels: Sequence[str],
    *,
    context_capture_labels: Sequence[str],
    supplemental_capture_labels: Sequence[str] = (),
    policy: ComparePacketPolicy,
) -> tuple[list[str], bool]:
    ordered_capture_labels = _unique_preserving_order(list(capture_labels))
    max_capture_labels = policy.max_capture_labels_per_packet
    if max_capture_labels is None or len(ordered_capture_labels) <= max_capture_labels:
        return ordered_capture_labels, False

    context_labels = set(context_capture_labels)
    supplemental_labels = set(supplemental_capture_labels)
    focus_labels = [
        label for label in ordered_capture_labels if label not in context_labels and label not in supplemental_labels
    ]
    fallback_context_labels = [label for label in ordered_capture_labels if label in context_labels]
    fallback_supplemental_labels = [label for label in ordered_capture_labels if label in supplemental_labels]
    return _unique_preserving_order([*focus_labels, *fallback_context_labels, *fallback_supplemental_labels])[
        :max_capture_labels
    ], True


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
    scope_source: ReferenceCompareScopeSourceLiteral | None,
    target_objects: Sequence[str],
    truth_pairs: Sequence[str] = (),
    mark_id_map: dict[str, int] | None = None,
    reference_ids: Sequence[str],
    capture_labels: Sequence[str],
    compare_question: str,
    context_capture_labels: Sequence[str],
    supplemental_capture_labels: Sequence[str],
    policy: ComparePacketPolicy,
    budget_notes: list[str],
) -> None:
    effective_capture_labels, captures_trimmed = _budgeted_capture_labels(
        capture_labels,
        context_capture_labels=context_capture_labels,
        supplemental_capture_labels=supplemental_capture_labels,
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
                "Compare packet policy omitted context or supplemental captures from some packets to stay within "
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
                scope_source=scope_source,
                target_objects=list(target_objects),
                truth_pairs=list(truth_pairs),
                reference_ids=list(chunk),
                capture_labels=list(effective_capture_labels),
                mark_id_map=dict(mark_id_map or {}),
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
    supplemental_capture_labels: list[str] = []
    all_capture_labels = [capture.label for capture in captures]
    primary_captures = [capture for capture in captures if not _is_supplemental_capture(capture)]
    for capture in captures:
        view_id = _capture_view_id(capture)
        if _is_supplemental_capture(capture):
            supplemental_capture_labels.append(capture.label)
        if view_id is None:
            context_capture_labels.append(capture.label)
            continue
        capture_labels_by_view.setdefault(view_id, []).append(capture.label)

    all_reference_ids = [reference.reference_id for reference in reference_records]
    full_mark_id_map = _capture_mark_id_map(captures)

    normalized_target_view = _normalize_view_token(target_view)
    capture_views = _ordered_views(capture_labels_by_view)
    focus_pairs = list(truth_followup.focus_pairs or []) if truth_followup is not None else []
    complexity_tier = resolve_compare_complexity_tier(
        assembled_target_scope=assembled_target_scope,
        reference_count=len(reference_records),
        capture_count=len(primary_captures),
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
    registered_compare_scope = _registered_compare_scope(assembled_target_scope)
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
                scope_source="fallback",
                target_objects=list(assembled_target_scope.object_names or [])
                if assembled_target_scope is not None
                else [],
                mark_id_map=_packet_mark_id_map(
                    full_mark_id_map=full_mark_id_map,
                    packet_target_objects=list(assembled_target_scope.object_names or [])
                    if assembled_target_scope is not None
                    else [],
                ),
                reference_ids=all_reference_ids,
                capture_labels=all_capture_labels,
                compare_question=_packet_question_for_view(None, scope_label=scope_label),
                context_capture_labels=context_capture_labels,
                supplemental_capture_labels=supplemental_capture_labels,
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
                scope_source="fallback",
                target_objects=list(assembled_target_scope.object_names or [])
                if assembled_target_scope is not None
                else [],
                mark_id_map=_packet_mark_id_map(
                    full_mark_id_map=full_mark_id_map,
                    packet_target_objects=list(assembled_target_scope.object_names or [])
                    if assembled_target_scope is not None
                    else [],
                ),
                reference_ids=packet_reference_ids,
                capture_labels=packet_capture_labels,
                compare_question=_packet_question_for_view(view_id),
                context_capture_labels=context_capture_labels,
                supplemental_capture_labels=supplemental_capture_labels,
                policy=packet_policy,
                budget_notes=budget_notes,
            )
    else:
        registered_scope_clusters = _scope_clusters_from_registered_graph(
            registered_compare_scope,
            focus_pairs=focus_pairs,
        )
        if registered_scope_clusters:
            scope_clusters = registered_scope_clusters
            scope_source: ReferenceCompareScopeSourceLiteral = "registered_graph"
        elif focus_pairs and not prefer_target_scope_clusters:
            scope_clusters = _scope_clusters_from_focus_pairs(
                focus_pairs,
                primary_target=assembled_target_scope.primary_target if assembled_target_scope is not None else None,
            )
            scope_source = "focus_pairs"
        else:
            scope_clusters = _scope_clusters_from_target_scope(assembled_target_scope)
            scope_source = "target_scope"
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
                        scope_source=scope_source,
                        target_objects=list(cluster.target_objects),
                        truth_pairs=list(cluster.truth_pairs),
                        mark_id_map=_packet_mark_id_map(
                            full_mark_id_map=full_mark_id_map,
                            packet_target_objects=cluster.target_objects,
                        ),
                        reference_ids=packet_reference_ids,
                        capture_labels=packet_capture_labels,
                        compare_question=_packet_question_for_view(view_id, scope_label=cluster.scope_label),
                        context_capture_labels=context_capture_labels,
                        supplemental_capture_labels=supplemental_capture_labels,
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
                    scope_source="fallback",
                    target_objects=list(assembled_target_scope.object_names or [])
                    if assembled_target_scope is not None
                    else [],
                    mark_id_map=_packet_mark_id_map(
                        full_mark_id_map=full_mark_id_map,
                        packet_target_objects=list(assembled_target_scope.object_names or [])
                        if assembled_target_scope is not None
                        else [],
                    ),
                    reference_ids=packet_reference_ids,
                    capture_labels=packet_capture_labels,
                    compare_question=_packet_question_for_view(view_id),
                    context_capture_labels=context_capture_labels,
                    supplemental_capture_labels=supplemental_capture_labels,
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
                scope_source="fallback",
                target_objects=list(assembled_target_scope.object_names or [])
                if assembled_target_scope is not None
                else [],
                mark_id_map=_packet_mark_id_map(
                    full_mark_id_map=full_mark_id_map,
                    packet_target_objects=list(assembled_target_scope.object_names or [])
                    if assembled_target_scope is not None
                    else [],
                ),
                reference_ids=all_reference_ids,
                capture_labels=all_capture_labels,
                compare_question=_packet_question_for_view(None, scope_label=scope_label),
                context_capture_labels=context_capture_labels,
                supplemental_capture_labels=supplemental_capture_labels,
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
        registered_compare_scope=registered_compare_scope,
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
            "findings": list(ranking_result.findings or extraction_result.findings or []),
            "object_correspondence": list(
                ranking_result.object_correspondence or extraction_result.object_correspondence or []
            ),
            "rejected_mark_ids": list(ranking_result.rejected_mark_ids or extraction_result.rejected_mark_ids or []),
            "validity_retry_attempted": bool(
                ranking_result.validity_retry_attempted or extraction_result.validity_retry_attempted
            ),
            "open_defects": list(ranking_result.open_defects or extraction_result.open_defects or []),
            "verify_status": list(extraction_result.verify_status or ranking_result.verify_status or []),
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
    omitted_count = sum(result.omitted_count for _, result in successful_results)
    evidence_truncated = any(result.evidence_truncated for _, result in successful_results)
    visible_changes, _omitted = _unique_bounded_with_omitted(
        [item for _, result in successful_results for item in list(result.visible_changes or [])],
        max_items=8,
    )
    omitted_count += _omitted
    shape_mismatches, _omitted = _unique_bounded_with_omitted(
        [item for _, result in successful_results for item in list(result.shape_mismatches or [])],
        max_items=6,
    )
    omitted_count += _omitted
    proportion_mismatches, _omitted = _unique_bounded_with_omitted(
        [item for _, result in successful_results for item in list(result.proportion_mismatches or [])],
        max_items=6,
    )
    omitted_count += _omitted
    correction_focus, _omitted = _unique_bounded_with_omitted(
        [item for _, result in successful_results for item in list(result.correction_focus or [])],
        max_items=6,
    )
    omitted_count += _omitted
    next_corrections, _omitted = _unique_bounded_with_omitted(
        [item for _, result in successful_results for item in list(result.next_corrections or [])],
        max_items=6,
    )
    omitted_count += _omitted
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
    findings = []
    seen_finding_ids: set[str] = set()
    for _, result in successful_results:
        for finding in list(result.findings or []):
            finding_key = finding.defect_id or finding.finding
            if finding_key in seen_finding_ids:
                continue
            seen_finding_ids.add(finding_key)
            findings.append(finding)
    object_correspondence = []
    seen_correspondence_ids: set[int] = set()
    for _, result in successful_results:
        for row in list(result.object_correspondence or []):
            if row.mark_id in seen_correspondence_ids:
                continue
            seen_correspondence_ids.add(row.mark_id)
            object_correspondence.append(row)
    rejected_mark_ids = sorted(
        {mark_id for _, result in successful_results for mark_id in list(result.rejected_mark_ids or [])}
    )
    open_defects: list[VisionOpenDefectContract] = []
    seen_defect_ids: set[str] = set()
    for _, result in successful_results:
        for defect in list(result.open_defects or []):
            if defect.defect_id in seen_defect_ids:
                continue
            seen_defect_ids.add(defect.defect_id)
            open_defects.append(defect)
    verify_status: list[VisionDefectVerifyStatusContract] = []
    seen_verify_ids: set[str] = set()
    for _, result in successful_results:
        for status in list(result.verify_status or []):
            key = f"{status.defect_id}:{status.status}"
            if key in seen_verify_ids:
                continue
            seen_verify_ids.add(key)
            verify_status.append(status)
    if len(likely_issues) > 6:
        omitted_count += len(likely_issues) - 6
    if len(recommended_checks) > 6:
        omitted_count += len(recommended_checks) - 6
    evidence_truncated = evidence_truncated or omitted_count > 0

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
        findings=findings[:8],
        object_correspondence=object_correspondence[:16],
        rejected_mark_ids=rejected_mark_ids,
        validity_retry_attempted=any(result.validity_retry_attempted for _, result in successful_results),
        open_defects=open_defects[:12],
        verify_status=verify_status[:12],
        packet_guidance=VisionPacketStatusContract(
            packet_status="ready" if correction_focus else "clean",
            status_reason=None,
            ranking_recommendation="rank" if correction_focus else "skip_clean",
        ),
        confidence=(sum(confidences) / len(confidences)) if confidences else None,
        captures_used=captures_used,
        evidence_truncated=evidence_truncated,
        omitted_count=omitted_count,
        input_summary=merged_input_summary,
        boundary_policy=VisionBoundaryPolicyContract(),
    )


def _runtime_capture_grid_enabled(resolver: Any) -> bool:
    runtime_config = getattr(resolver, "runtime_config", None)
    return bool(getattr(runtime_config, "capture_grid_enabled", False))


def _runtime_transmit_auxiliary_channels_enabled(resolver: Any) -> bool:
    runtime_config = getattr(resolver, "runtime_config", None)
    return bool(getattr(runtime_config, "transmit_auxiliary_channels", False))


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
    localization_candidates: Sequence[VisionLocalizationCandidate] = (),
) -> ReferencePartSegmentationContract | None:
    """Run the optional advisory-only segmentation sidecar for one compare packet."""

    if config is None or not bool(getattr(config, "enabled", False)):
        return None
    if not getattr(config, "endpoint", None):
        return ReferencePartSegmentationContract(
            status="unavailable",
            provider_name=getattr(config, "provider_name", None),
            advisory_only=True,
            parts=[],
            notes=[
                "Optional compare-time part segmentation is enabled, but no endpoint is configured.",
                "Set VISION_SEGMENTATION_ENDPOINT to activate bounded compare-time support.",
                "The sidecar path is advisory-only and separate from vision_contract_profile routing.",
            ],
        )

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
    if localization_candidates:
        payload["seed_boxes"] = [
            {
                "query_label": item.query_label,
                "reference_id": item.reference_id,
                "capture_label": item.capture_label,
                "target_view": item.target_view,
                "confidence": item.confidence,
                "box_xyxy": list(item.box_xyxy),
                "crop_path": item.crop_path,
            }
            for item in localization_candidates
        ]
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


async def collect_compare_time_localization_support(
    *,
    config: VisionLocalizationConfig | None,
    goal: str | None,
    packet: ReferenceComparePacketContract,
    reference_records: Sequence[ReferenceImageRecordContract],
    captures: Sequence[VisionCaptureImageContract],
) -> tuple[list[VisionLocalizationCandidate], ReferencePartSegmentationContract | None]:
    """Run the optional advisory-only localization sidecar for one compare packet."""

    if config is None or not bool(getattr(config, "enabled", False)):
        return [], None
    if not getattr(config, "endpoint", None):
        return (
            [],
            ReferencePartSegmentationContract(
                status="unavailable",
                provider_name=getattr(config, "provider_name", None),
                advisory_only=True,
                parts=[],
                notes=[
                    "Optional compare-time localization is enabled, but no endpoint is configured.",
                    "Set VISION_LOCALIZATION_ENDPOINT to activate bounded compare-time support.",
                    "Literal localization boxes stay internal; public payload projects only crops and derived anchors.",
                ],
            ),
        )

    payload = _build_compare_localization_request_payload(
        goal=goal,
        packet=packet,
        reference_records=reference_records,
        captures=captures,
    )
    if not payload["references"] or not payload["captures"] or not payload["query_labels"]:
        return (
            [],
            ReferencePartSegmentationContract(
                status="unavailable",
                provider_name=config.provider_name,
                advisory_only=True,
                parts=[],
                notes=[
                    "No bounded packet-local reference/capture slice or query labels were available for optional localization.",
                    "Literal localization boxes stay internal; public payload projects only crops and derived anchors.",
                ],
            ),
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
        candidates = _normalize_compare_localization_payload(
            response_payload,
            packet_id=packet.packet_id,
            max_candidates=int(getattr(config, "max_candidates", 8)),
            fallback_target_view=packet.target_view,
        )
    except Exception as exc:
        return (
            [],
            ReferencePartSegmentationContract(
                status="unavailable",
                provider_name=getattr(config, "provider_name", None),
                advisory_only=True,
                parts=[],
                notes=[
                    _bounded_text(
                        _redact_local_paths(f"Optional compare-time localization unavailable: {exc}"),
                        fallback="Optional compare-time localization unavailable.",
                    )
                    or "Optional compare-time localization unavailable.",
                    "Literal localization boxes stay internal; public payload projects only crops and derived anchors.",
                ],
            ),
        )

    if not candidates:
        return (
            [],
            ReferencePartSegmentationContract(
                status="unavailable",
                provider_name=getattr(config, "provider_name", None),
                advisory_only=True,
                parts=[],
                notes=[
                    "Optional compare-time localization returned no bounded candidates for compare support.",
                    "Literal localization boxes stay internal; public payload projects only crops and derived anchors.",
                ],
            ),
        )

    return (
        candidates,
        _project_localization_candidates_to_part_segmentation(
            provider_name=getattr(config, "provider_name", None),
            candidates=candidates,
        ),
    )


def _should_request_compare_time_segmentation(
    reason: ReferenceLocalizedSupportReasonLiteral | None,
    localization_candidates: Sequence[VisionLocalizationCandidate],
) -> bool:
    if reason in {"mask_needed", "seam_unclear"}:
        return True
    return bool(localization_candidates)


def _runtime_capability_usage(
    *,
    capability: Literal["vision", "localization", "segmentation"],
    configured: bool,
    considered_packet_ids: Sequence[str],
    invoked_packet_ids: Sequence[str],
    provider_name: str | None = None,
    available: bool = False,
    unavailable: bool = False,
    notes: Sequence[str] = (),
) -> ReferenceRuntimeCapabilityUsageContract:
    considered = bool(considered_packet_ids)
    invoked = bool(invoked_packet_ids)
    if not configured:
        status = "not_configured"
    elif invoked and available:
        status = "used"
    elif invoked and unavailable:
        status = "unavailable"
    elif invoked:
        status = "used"
    elif considered:
        status = "skipped_by_policy"
    else:
        status = "configured"
    packet_ids = _unique_preserving_order([*list(invoked_packet_ids), *list(considered_packet_ids)])[:8]
    return ReferenceRuntimeCapabilityUsageContract(
        capability=capability,
        status=cast(Any, status),
        configured=configured,
        considered=considered,
        invoked=invoked,
        provider_name=provider_name,
        packet_ids=packet_ids,
        notes=_unique_preserving_order([str(note).strip() for note in notes if str(note).strip()])[:4],
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
    guided_domain_profile: str | None,
    localization_config: Any,
    segmentation_sidecar_config: Any,
    resolver: Any,
    prior_open_defects: Sequence[Mapping[str, Any] | ReferenceOpenDefectContract] = (),
    run_vision_assist_fn=run_vision_assist,
    to_vision_assistant_contract_fn=to_vision_assistant_contract,
) -> PacketCompareExecutionResult:
    request_goal = goal or "reference-guided staged compare"
    part_segmentation: ReferencePartSegmentationContract | None = None
    packet_assistants: list[tuple[ReferenceComparePacketContract, VisionAssistantContract | None]] = []
    localized_support_requested = False
    creature_compare_domain = _is_creature_compare_domain(goal=goal, guided_domain_profile=guided_domain_profile)
    localization_configured = bool(
        localization_config is not None and bool(getattr(localization_config, "enabled", False))
    )
    segmentation_configured = bool(
        segmentation_sidecar_config is not None and bool(getattr(segmentation_sidecar_config, "enabled", False))
    )
    localization_enabled = bool(
        localization_config is not None
        and bool(getattr(localization_config, "enabled", False))
        and getattr(localization_config, "endpoint", None)
    )
    sidecar_enabled = bool(
        segmentation_sidecar_config is not None
        and bool(getattr(segmentation_sidecar_config, "enabled", False))
        and getattr(segmentation_sidecar_config, "endpoint", None)
    )
    localization_considered_packet_ids: list[str] = []
    localization_invoked_packet_ids: list[str] = []
    localization_available = False
    localization_unavailable = False
    localization_notes: list[str] = []
    segmentation_considered_packet_ids: list[str] = []
    segmentation_invoked_packet_ids: list[str] = []
    segmentation_available = False
    segmentation_unavailable = False
    segmentation_notes: list[str] = []
    capture_grid_enabled = _runtime_capture_grid_enabled(resolver)
    transmit_auxiliary_channels = _runtime_transmit_auxiliary_channels_enabled(resolver)

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
            target_objects=packet.target_objects or list(resolved_target_objects),
        )
        packet_action_hints = build_action_hints_from_silhouette(
            packet_silhouette_analysis,
            target_object=packet.target_objects[0]
            if packet.target_objects
            else (resolved_target_object or assembled_target_scope.primary_target),
        )
        packet.localized_support_reason = _resolve_localized_support_reason(
            goal=goal,
            guided_domain_profile=guided_domain_profile,
            packet=packet,
            packet_truth_bundle=packet_truth_bundle,
            silhouette_analysis=packet_silhouette_analysis,
            action_hints=packet_action_hints,
            prior_open_defects=prior_open_defects,
        )
        localization_candidates: list[VisionLocalizationCandidate] = []
        packet_part_segmentation: ReferencePartSegmentationContract | None = None
        appendage_packet = creature_compare_domain and _is_bounded_creature_appendage_packet(packet)
        if appendage_packet and (localization_configured or packet.localized_support_reason is not None):
            localization_considered_packet_ids.append(packet.packet_id)
        if appendage_packet and segmentation_configured:
            segmentation_considered_packet_ids.append(packet.packet_id)
        if packet.localized_support_reason is not None:
            localized_support_requested = True
            localization_invoked_packet_ids.append(packet.packet_id)
            (
                localization_candidates,
                packet_part_segmentation,
            ) = await collect_compare_time_localization_support(
                config=localization_config,
                goal=goal,
                packet=packet,
                reference_records=packet_reference_records,
                captures=packet_captures,
            )
            if packet_part_segmentation is not None:
                localization_notes.extend(packet_part_segmentation.notes)
                if packet_part_segmentation.status == "available":
                    localization_available = True
                elif packet_part_segmentation.status == "unavailable":
                    localization_unavailable = True
            packet.reference_marks = _reference_marks_for_localization_candidates(packet, localization_candidates)
            if _should_request_compare_time_segmentation(packet.localized_support_reason, localization_candidates):
                if packet.packet_id not in segmentation_considered_packet_ids:
                    segmentation_considered_packet_ids.append(packet.packet_id)
                segmentation_invoked_packet_ids.append(packet.packet_id)
                segmentation_result = await collect_compare_time_segmentation_support(
                    config=segmentation_sidecar_config,
                    goal=goal,
                    packet_id=packet.packet_id,
                    packet_label=packet.packet_label,
                    target_view=packet.target_view or target_view,
                    scope_label=packet.scope_label,
                    target_objects=packet.target_objects or list(resolved_target_objects),
                    reference_records=packet_reference_records,
                    captures=packet_captures,
                    localization_candidates=localization_candidates,
                )
                if segmentation_result is not None:
                    segmentation_notes.extend(segmentation_result.notes)
                    if segmentation_result.status == "available":
                        segmentation_available = True
                    elif segmentation_result.status == "unavailable":
                        segmentation_unavailable = True
                packet_part_segmentation = merge_compare_time_part_segmentation(
                    packet_part_segmentation,
                    segmentation_result,
                )
            elif segmentation_configured:
                segmentation_notes.append(
                    "Optional part segmentation was skipped by creature packet policy because no mask support "
                    "was requested for this bounded packet."
                )
        elif appendage_packet and (localization_configured or segmentation_configured):
            localization_notes.append(
                "Optional localization was skipped by creature packet policy because the appendage packet was not "
                "under-grounded by truth, silhouette, action-hint, or unresolved-defect evidence."
            )
            segmentation_notes.append(
                "Optional part segmentation was skipped by creature packet policy because localization/mask support "
                "was not requested for this bounded packet."
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
                **_packet_mark_request_metadata(packet),
            },
            capture_grid_enabled=capture_grid_enabled,
            transmit_auxiliary_channels=transmit_auxiliary_channels,
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
        corrected_result, rejected_mark_ids = _mark_correspondence_for_result(
            extraction_vision_assistant.result,
            packet=packet,
            assembled_target_scope=assembled_target_scope,
            retry_attempted=False,
        )
        if rejected_mark_ids:
            retry_metadata = dict(extraction_request.metadata)
            retry_metadata["valid_mark_ids"] = sorted(set(packet.mark_id_map.values()))
            retry_hint = " | ".join(
                part
                for part in (
                    extraction_request.prompt_hint,
                    f"valid_mark_ids={','.join(str(item) for item in retry_metadata['valid_mark_ids'])}",
                    "validity_retry=use_only_listed_mark_ids",
                )
                if part
            )
            retry_request = dataclass_replace(
                extraction_request,
                prompt_hint=retry_hint,
                metadata=retry_metadata,
            )
            retry_outcome = await run_vision_assist_fn(
                ctx,
                request=retry_request,
                resolver=resolver,
            )
            retry_assistant = to_vision_assistant_contract_fn(retry_outcome)
            if retry_assistant.status == "success" and retry_assistant.result is not None:
                corrected_result, rejected_mark_ids = _mark_correspondence_for_result(
                    retry_assistant.result,
                    packet=packet,
                    assembled_target_scope=assembled_target_scope,
                    retry_attempted=True,
                )
                extraction_vision_assistant = retry_assistant.model_copy(update={"result": corrected_result})
            else:
                corrected_result = corrected_result.model_copy(update={"validity_retry_attempted": True})
                extraction_vision_assistant = extraction_vision_assistant.model_copy(
                    update={"result": corrected_result}
                )
        else:
            extraction_vision_assistant = extraction_vision_assistant.model_copy(update={"result": corrected_result})

        tracked_result = _apply_packet_defect_tracking(
            extraction_vision_assistant.result,
            packet=packet,
            prior_open_defects=prior_open_defects,
        )
        packet.open_defects = _reference_open_defects(tracked_result.open_defects)
        packet.verify_status = _reference_verify_statuses(tracked_result.verify_status)
        extraction_vision_assistant = extraction_vision_assistant.model_copy(update={"result": tracked_result})

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
                *[
                    f"Rejected invalid mark id {mark_id}; it was not present in this packet overlay."
                    for mark_id in extraction_vision_assistant.result.rejected_mark_ids
                ],
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
                    **_packet_mark_request_metadata(packet),
                },
                capture_grid_enabled=capture_grid_enabled,
                transmit_auxiliary_channels=transmit_auxiliary_channels,
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
                packet.open_defects = _reference_open_defects(effective_packet_result.open_defects)
                packet.verify_status = _reference_verify_statuses(effective_packet_result.verify_status)
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

    if part_segmentation is None and (sidecar_enabled or localization_enabled) and not localized_support_requested:
        part_segmentation = ReferencePartSegmentationContract(
            status="disabled",
            provider_name=(
                getattr(segmentation_sidecar_config, "provider_name", None)
                or getattr(localization_config, "provider_name", None)
            ),
            advisory_only=True,
            parts=[],
            notes=[
                "Optional localized support is configured, but no bounded packet-local localized support reason requested it for this staged compare run.",
                "Localized support stays advisory-only and separate from vision_contract_profile routing.",
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
    vision_invoked_packet_ids = [packet.packet_id for packet, assistant in packet_assistants if assistant is not None]
    vision_available = any(
        assistant is not None and assistant.status == "success" for _, assistant in packet_assistants
    )
    vision_unavailable = bool(vision_invoked_packet_ids) and not vision_available
    compare_diagnostics.runtime_evidence = ReferenceRuntimeEvidenceContract(
        capabilities=[
            _runtime_capability_usage(
                capability="vision",
                configured=True,
                considered_packet_ids=[packet.packet_id for packet in list(compare_diagnostics.packets or [])],
                invoked_packet_ids=vision_invoked_packet_ids,
                available=vision_available,
                unavailable=vision_unavailable,
                notes=[
                    f"Vision assistant was invoked for {len(vision_invoked_packet_ids)} compare packet(s)."
                    if vision_invoked_packet_ids
                    else "No compare packet reached the vision assistant.",
                ],
            ),
            _runtime_capability_usage(
                capability="localization",
                configured=localization_configured,
                considered_packet_ids=localization_considered_packet_ids,
                invoked_packet_ids=localization_invoked_packet_ids,
                provider_name=getattr(localization_config, "provider_name", None),
                available=localization_available,
                unavailable=localization_unavailable,
                notes=localization_notes,
            ),
            _runtime_capability_usage(
                capability="segmentation",
                configured=segmentation_configured,
                considered_packet_ids=segmentation_considered_packet_ids,
                invoked_packet_ids=segmentation_invoked_packet_ids,
                provider_name=getattr(segmentation_sidecar_config, "provider_name", None),
                available=segmentation_available,
                unavailable=segmentation_unavailable,
                notes=segmentation_notes,
            ),
        ],
        checkpoint_id=checkpoint_id,
        packet_ids=[packet.packet_id for packet in list(compare_diagnostics.packets or [])][:12],
        notes=[
            "Optional localization/segmentation policy is creature-domain, appendage-packet bounded, and advisory-only."
        ],
    )

    return PacketCompareExecutionResult(
        compare_diagnostics=compare_diagnostics,
        vision_assistant=vision_assistant,
        part_segmentation=part_segmentation,
    )
