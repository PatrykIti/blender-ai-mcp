# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Optional advisory-only RU support adapters for classifier and segmentation sidecars."""

from __future__ import annotations

import os
import re
from collections.abc import Sequence
from typing import Any, Literal, cast

import httpx

from server.adapters.mcp.contracts.quality_gates import GateSourceProvenanceContract
from server.adapters.mcp.contracts.reference import (
    ReferencePartSegmentationContract,
    ReferencePartSegmentationLandmarkContract,
    ReferencePartSegmentationPartContract,
    ReferenceUnderstandingClassificationScoreContract,
    ReferenceUnderstandingSegmentationArtifactContract,
    ReferenceUnderstandingSummaryContract,
    ReferenceUnderstandingVisualEvidenceRefContract,
)
from server.adapters.mcp.contracts.vision import VisionCaptureImageContract

from . import OpenAICompatibleVisionBackend
from .backend import VisionImageInput, VisionRequest
from .config import (
    VisionOpenAICompatibleConfig,
    VisionReferenceClassifierConfig,
    VisionRuntimeConfig,
    VisionSegmentationSidecarConfig,
)

_SEGMENTATION_ARTIFACT_KINDS = {"mask", "crop", "box"}


def _resolve_api_key(*, inline_key: str | None, env_name: str | None) -> str | None:
    if inline_key:
        return inline_key
    if env_name:
        return os.getenv(env_name) or None
    return None


def _build_headers(*, api_key: str | None) -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def _sanitize_identifier(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_") or "item"


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


def _looks_like_local_path(value: str) -> bool:
    candidate = value.strip()
    if not candidate:
        return False
    return bool(
        candidate.startswith(("/", "./", "../", "~"))
        or re.match(r"^[A-Za-z]:[\\/]", candidate) is not None
        or "\\" in candidate
    )


def _sanitize_segmentation_artifact_id(value: Any, *, fallback: str) -> str:
    artifact_id = str(value or "").strip()
    if not artifact_id or _looks_like_local_path(artifact_id) or "/" in artifact_id:
        return fallback
    return artifact_id[:120]


def _redact_local_paths(text: str | None) -> str | None:
    if text is None:
        return None
    redacted = re.sub(
        r"(?<!\w)(?:[A-Za-z]:[\\/]|/|\.{1,2}[\\/]|~[\\/])[^\s,;:]+|[^\s,;:]*\\[^\s,;:]+",
        "[redacted-path]",
        text,
    )
    return redacted


def _dedupe_strings(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for item in values:
        value = str(item).strip()
        lowered = value.lower()
        if not value or lowered in seen:
            continue
        seen.add(lowered)
        deduped.append(value)
    return deduped


def _build_support_request_payload(
    *,
    goal: str | None,
    summary: ReferenceUnderstandingSummaryContract,
    reference_records: Sequence[Any],
) -> dict[str, Any]:
    references: list[dict[str, Any]] = []
    for record in reference_records:
        reference_id = str(getattr(record, "reference_id", "") or "").strip()
        image_path = (
            str(getattr(record, "stored_path", "") or "").strip()
            or str(getattr(record, "host_visible_path", "") or "").strip()
            or str(getattr(record, "original_path", "") or "").strip()
        )
        if not reference_id or not image_path:
            continue
        references.append(
            {
                "reference_id": reference_id,
                "label": str(getattr(record, "label", "") or "").strip() or None,
                "target_view": str(getattr(record, "target_view", "") or "").strip() or None,
                "media_type": str(getattr(record, "media_type", "") or "").strip() or None,
                "image_path": image_path,
            }
        )

    return {
        "goal": goal or summary.goal,
        "reference_ids": list(summary.reference_ids or []),
        "references": references,
        "reference_understanding": {
            "understanding_id": summary.understanding_id,
            "subject": None if summary.subject is None else summary.subject.model_dump(mode="json", exclude_none=True),
            "style": None if summary.style is None else summary.style.model_dump(mode="json", exclude_none=True),
            "construction_strategy": (
                None
                if summary.construction_strategy is None
                else summary.construction_strategy.model_dump(mode="json", exclude_none=True)
            ),
        },
    }


def _build_compare_segmentation_request_payload(
    *,
    goal: str | None,
    packet_id: str,
    packet_label: str,
    target_view: str | None,
    scope_label: str | None,
    target_objects: Sequence[str],
    reference_records: Sequence[Any],
    captures: Sequence[VisionCaptureImageContract],
) -> dict[str, Any]:
    references: list[dict[str, Any]] = []
    for record in reference_records:
        reference_id = str(getattr(record, "reference_id", "") or "").strip()
        image_path = (
            str(getattr(record, "stored_path", "") or "").strip()
            or str(getattr(record, "host_visible_path", "") or "").strip()
            or str(getattr(record, "original_path", "") or "").strip()
        )
        if not reference_id or not image_path:
            continue
        references.append(
            {
                "reference_id": reference_id,
                "label": str(getattr(record, "label", "") or "").strip() or None,
                "target_view": str(getattr(record, "target_view", "") or "").strip() or None,
                "media_type": str(getattr(record, "media_type", "") or "").strip() or None,
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


def _build_classifier_request(
    *,
    goal: str | None,
    summary: ReferenceUnderstandingSummaryContract,
    reference_records: Sequence[Any],
) -> VisionRequest:
    images: list[VisionImageInput] = []
    reference_ids: list[str] = []
    for record in reference_records:
        reference_id = str(getattr(record, "reference_id", "") or "").strip()
        image_path = (
            str(getattr(record, "stored_path", "") or "").strip()
            or str(getattr(record, "host_visible_path", "") or "").strip()
            or str(getattr(record, "original_path", "") or "").strip()
        )
        if not reference_id or not image_path:
            continue
        reference_ids.append(reference_id)
        images.append(
            VisionImageInput(
                path=image_path,
                role="reference",
                label=str(getattr(record, "label", "") or "").strip() or reference_id,
                media_type=str(getattr(record, "media_type", "") or "").strip() or "image/png",
            )
        )

    return VisionRequest(
        goal=goal or summary.goal or "Classify the attached references for bounded Blender build strategy.",
        images=tuple(images),
        prompt_hint="reference_classification",
        metadata={
            "mode": "reference_classification",
            "reference_ids": reference_ids,
            "source": "reference_classifier",
        },
    )


async def _post_sidecar_payload(
    *,
    endpoint: str,
    timeout_seconds: float,
    api_key: str | None,
    payload: dict[str, Any],
) -> dict[str, Any]:
    timeout = httpx.Timeout(timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(endpoint, json=payload, headers=_build_headers(api_key=api_key))
    response.raise_for_status()
    response_payload = response.json()
    return response_payload if isinstance(response_payload, dict) else {}


def _merge_classification_scores(
    existing: Sequence[ReferenceUnderstandingClassificationScoreContract],
    incoming: Sequence[ReferenceUnderstandingClassificationScoreContract],
) -> list[ReferenceUnderstandingClassificationScoreContract]:
    merged: dict[str, ReferenceUnderstandingClassificationScoreContract] = {}
    for item in [*list(existing), *list(incoming)]:
        key = item.label.strip().lower()
        current = merged.get(key)
        if current is None or float(item.score) > float(current.score):
            merged[key] = item
    return sorted(merged.values(), key=lambda item: float(item.score), reverse=True)[:5]


def _merge_segmentation_artifacts(
    existing: Sequence[ReferenceUnderstandingSegmentationArtifactContract],
    incoming: Sequence[ReferenceUnderstandingSegmentationArtifactContract],
    *,
    limit: int = 16,
) -> list[ReferenceUnderstandingSegmentationArtifactContract]:
    merged: dict[str, ReferenceUnderstandingSegmentationArtifactContract] = {}
    for item in [*list(existing), *list(incoming)]:
        key = item.artifact_id.strip().lower()
        if key not in merged:
            merged[key] = item
    return list(merged.values())[:limit]


def _merge_visual_evidence_refs(
    existing: Sequence[ReferenceUnderstandingVisualEvidenceRefContract],
    incoming: Sequence[ReferenceUnderstandingVisualEvidenceRefContract],
    *,
    limit: int = 16,
) -> list[ReferenceUnderstandingVisualEvidenceRefContract]:
    merged: dict[str, ReferenceUnderstandingVisualEvidenceRefContract] = {}
    for item in [*list(existing), *list(incoming)]:
        key = item.evidence_id.strip().lower()
        if key not in merged:
            merged[key] = item
    return list(merged.values())[:limit]


def _merge_source_provenance(
    existing: Sequence[GateSourceProvenanceContract],
    incoming: Sequence[GateSourceProvenanceContract],
) -> list[GateSourceProvenanceContract]:
    merged: dict[tuple[Any, ...], GateSourceProvenanceContract] = {}
    for item in list(existing):
        if item.source in {"classification_scores", "part_segmentation"}:
            existing_key: tuple[Any, ...] = (item.source, item.provider, item.model_id, tuple(item.reference_ids))
        else:
            existing_key = (item.source, item.provider, item.model_id, item.summary)
        merged[existing_key] = item
    for item in list(incoming):
        if item.source in {"classification_scores", "part_segmentation"}:
            incoming_key: tuple[Any, ...] = (item.source, item.provider, item.model_id, tuple(item.reference_ids))
        else:
            incoming_key = (item.source, item.provider, item.model_id, item.summary)
        merged[incoming_key] = item
    return list(merged.values())[:12]


def _build_openai_compatible_classifier_runtime(config: VisionReferenceClassifierConfig) -> VisionRuntimeConfig:
    provider_name = cast(Any, config.provider_name)
    external_config = VisionOpenAICompatibleConfig(
        provider_name=provider_name,
        vision_contract_profile="generic_full",
        base_url=config.endpoint,
        model=config.model,
        api_key=config.api_key,
        api_key_env=config.api_key_env,
        site_url=None,
        site_name=None,
        require_parameters=provider_name == "openrouter",
        enable_response_healing=provider_name == "openrouter",
        prefer_json_object_for_qwen=provider_name == "openrouter",
        model_capabilities=None,
    )
    return VisionRuntimeConfig(
        enabled=True,
        provider="openai_compatible_external",
        allow_on_guided=True,
        max_images=8,
        max_tokens=300,
        timeout_seconds=config.timeout_seconds,
        openai_compatible_external=external_config,
        reference_classifier=None,
        segmentation_sidecar=None,
    )


def _normalize_classification_scores_payload(
    payload: dict[str, Any],
    *,
    max_labels: int,
) -> list[ReferenceUnderstandingClassificationScoreContract]:
    value = payload.get("classification_scores")
    if not isinstance(value, list):
        return []
    items: list[ReferenceUnderstandingClassificationScoreContract] = []
    for raw_item in value:
        if not isinstance(raw_item, dict):
            continue
        label = str(raw_item.get("label") or "").strip()
        score = raw_item.get("score")
        if not label or not isinstance(score, (int, float)):
            continue
        normalized_score = float(score)
        if not 0.0 <= normalized_score <= 1.0:
            continue
        items.append(ReferenceUnderstandingClassificationScoreContract(label=label, score=normalized_score))
    return _merge_classification_scores([], items)[:max_labels]


def _normalize_segmentation_artifacts_payload(
    payload: dict[str, Any],
    *,
    max_artifacts: int,
    allowed_reference_ids: set[str] | None = None,
) -> list[ReferenceUnderstandingSegmentationArtifactContract]:
    value = payload.get("segmentation_artifacts")
    if not isinstance(value, list):
        return []
    items: list[ReferenceUnderstandingSegmentationArtifactContract] = []
    for index, raw_item in enumerate(value, start=1):
        if not isinstance(raw_item, dict):
            continue
        artifact_id = _sanitize_segmentation_artifact_id(
            raw_item.get("artifact_id"),
            fallback=f"segmentation_artifact_{index}",
        )
        artifact_kind = str(raw_item.get("artifact_kind") or "mask").strip().lower()
        if artifact_kind not in _SEGMENTATION_ARTIFACT_KINDS:
            artifact_kind = "mask"
        reference_id = str(raw_item.get("reference_id") or "").strip() or None
        if reference_id is not None and allowed_reference_ids is not None and reference_id not in allowed_reference_ids:
            reference_id = None
        items.append(
            ReferenceUnderstandingSegmentationArtifactContract(
                artifact_id=artifact_id,
                artifact_kind=cast(Literal["mask", "crop", "box"], artifact_kind),
                reference_id=reference_id,
                summary=_redact_local_paths(_bounded_text(raw_item.get("summary"))),
            )
        )
    return _merge_segmentation_artifacts([], items, limit=max_artifacts)[:max_artifacts]


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


async def _collect_classifier_support(
    *,
    config: VisionReferenceClassifierConfig | None,
    summary: ReferenceUnderstandingSummaryContract,
    reference_records: Sequence[Any],
    request_payload: dict[str, Any],
) -> tuple[
    list[ReferenceUnderstandingClassificationScoreContract],
    list[ReferenceUnderstandingVisualEvidenceRefContract],
    GateSourceProvenanceContract | None,
]:
    if config is None or not config.enabled or not config.endpoint:
        return [], [], None

    reference_ids = [item["reference_id"] for item in request_payload.get("references", []) if item.get("reference_id")]
    if not reference_ids:
        return [], [], None

    try:
        if config.provider_name == "generic_sidecar":
            payload = await _post_sidecar_payload(
                endpoint=config.endpoint,
                timeout_seconds=config.timeout_seconds,
                api_key=_resolve_api_key(inline_key=config.api_key, env_name=config.api_key_env),
                payload=request_payload,
            )
        else:
            classifier_request = _build_classifier_request(
                goal=request_payload.get("goal"),
                summary=summary,
                reference_records=reference_records,
            )
            runtime = _build_openai_compatible_classifier_runtime(config)
            payload = await OpenAICompatibleVisionBackend(runtime).analyze(classifier_request)
        scores = _normalize_classification_scores_payload(payload, max_labels=config.max_labels)
        if scores:
            top_score = scores[0]
            summary_text = (
                f"Optional reference classifier returned {len(scores)} score(s); "
                f"top label {top_score.label} ({top_score.score:.2f})."
            )
        else:
            summary_text = "Optional reference classifier returned no bounded scores."
    except Exception as exc:
        return (
            [],
            [],
            GateSourceProvenanceContract(
                source="classification_scores",
                provider=config.provider_name,
                model_id=config.model,
                reference_ids=reference_ids,
                summary=_bounded_text(
                    _redact_local_paths(f"Optional reference classifier unavailable: {exc}"),
                    fallback=None,
                ),
            ),
        )

    evidence_refs = [
        ReferenceUnderstandingVisualEvidenceRefContract(
            evidence_id=f"classification_{index}_{_sanitize_identifier(item.label)}",
            source_class="style_cue",
            summary=f"Optional classifier scored {item.label} at {item.score:.2f}.",
            reference_id=reference_ids[0] if reference_ids else None,
        )
        for index, item in enumerate(scores, start=1)
    ]
    provenance = GateSourceProvenanceContract(
        source="classification_scores",
        provider=config.provider_name,
        model_id=config.model,
        reference_ids=reference_ids,
        evidence_ids=[ref.evidence_id for ref in evidence_refs],
        summary=summary_text,
    )
    return scores, evidence_refs, provenance


async def _collect_segmentation_support(
    *,
    config: VisionSegmentationSidecarConfig | None,
    request_payload: dict[str, Any],
) -> tuple[
    list[ReferenceUnderstandingSegmentationArtifactContract],
    list[ReferenceUnderstandingVisualEvidenceRefContract],
    GateSourceProvenanceContract | None,
]:
    if config is None or not config.enabled or not config.endpoint:
        return [], [], None

    reference_ids = [item["reference_id"] for item in request_payload.get("references", []) if item.get("reference_id")]
    if not reference_ids:
        return [], [], None

    try:
        payload = await _post_sidecar_payload(
            endpoint=config.endpoint,
            timeout_seconds=config.timeout_seconds,
            api_key=_resolve_api_key(inline_key=config.api_key, env_name=config.api_key_env),
            payload=request_payload,
        )
        artifacts = _normalize_segmentation_artifacts_payload(
            payload,
            max_artifacts=config.max_parts,
            allowed_reference_ids=set(reference_ids),
        )
        if artifacts:
            summary_text = f"Optional segmentation sidecar returned {len(artifacts)} artifact link(s)."
        else:
            summary_text = "Optional segmentation sidecar returned no bounded artifact links."
    except Exception as exc:
        return (
            [],
            [],
            GateSourceProvenanceContract(
                source="part_segmentation",
                provider=config.provider_name,
                model_id=config.model,
                reference_ids=reference_ids,
                summary=_bounded_text(
                    _redact_local_paths(f"Optional segmentation sidecar unavailable: {exc}"),
                    fallback=None,
                ),
            ),
        )

    evidence_refs = [
        ReferenceUnderstandingVisualEvidenceRefContract(
            evidence_id=item.artifact_id,
            source_class="part_cue",
            summary=item.summary or f"Optional segmentation artifact {item.artifact_id} linked for support-only RU.",
            reference_id=item.reference_id,
        )
        for item in artifacts
    ]
    provenance = GateSourceProvenanceContract(
        source="part_segmentation",
        provider=config.provider_name,
        model_id=config.model,
        reference_ids=reference_ids,
        evidence_ids=[item.artifact_id for item in artifacts],
        summary=summary_text,
    )
    return artifacts, evidence_refs, provenance


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

    merged_notes = _dedupe_strings([*list(existing.notes or []), *list(incoming.notes or [])])[:8]
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
    reference_records: Sequence[Any],
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
        status="available",
        provider_name=getattr(config, "provider_name", None),
        advisory_only=True,
        parts=parts,
        notes=[
            summary_note,
            "The sidecar path is advisory-only and separate from vision_contract_profile routing.",
        ],
    )


async def augment_reference_understanding_optional_support(
    summary: ReferenceUnderstandingSummaryContract,
    *,
    goal: str | None,
    reference_records: Sequence[Any],
    runtime_config: VisionRuntimeConfig | None,
) -> ReferenceUnderstandingSummaryContract:
    """Merge optional classifier/segmentation support evidence into RU without changing authority."""

    if summary.status != "available" or runtime_config is None:
        return summary

    request_payload = _build_support_request_payload(goal=goal, summary=summary, reference_records=reference_records)
    if not request_payload["references"]:
        return summary

    classifier_config = getattr(runtime_config, "active_reference_classifier", None)
    segmentation_config = getattr(runtime_config, "active_segmentation_sidecar", None)

    classifier_scores, classifier_evidence, classifier_provenance = await _collect_classifier_support(
        config=classifier_config,
        summary=summary,
        reference_records=reference_records,
        request_payload=request_payload,
    )
    segmentation_artifacts, segmentation_evidence, segmentation_provenance = await _collect_segmentation_support(
        config=segmentation_config,
        request_payload=request_payload,
    )
    evidence_limit = max(
        16,
        len(summary.visual_evidence_refs or []) + len(classifier_evidence) + len(segmentation_evidence),
    )

    return summary.model_copy(
        update={
            "classification_scores": _merge_classification_scores(
                summary.classification_scores,
                classifier_scores,
            ),
            "segmentation_artifacts": _merge_segmentation_artifacts(
                summary.segmentation_artifacts,
                segmentation_artifacts,
                limit=(getattr(segmentation_config, "max_parts", 16) if segmentation_config is not None else 16),
            ),
            "visual_evidence_refs": _merge_visual_evidence_refs(
                summary.visual_evidence_refs,
                [*classifier_evidence, *segmentation_evidence],
                limit=evidence_limit,
            ),
            "source_provenance": _merge_source_provenance(
                summary.source_provenance,
                [item for item in (classifier_provenance, segmentation_provenance) if item is not None],
            ),
        }
    )
