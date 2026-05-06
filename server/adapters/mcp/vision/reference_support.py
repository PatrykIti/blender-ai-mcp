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
    ReferenceUnderstandingClassificationScoreContract,
    ReferenceUnderstandingSegmentationArtifactContract,
    ReferenceUnderstandingSummaryContract,
    ReferenceUnderstandingVisualEvidenceRefContract,
)

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
    redacted = re.sub(r"(?<!\w)(?:[A-Za-z]:[\\/]|/|\./|\.\./|~/)[^\s,;:]+", "[redacted-path]", text)
    return redacted


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
) -> list[ReferenceUnderstandingVisualEvidenceRefContract]:
    merged: dict[str, ReferenceUnderstandingVisualEvidenceRefContract] = {}
    for item in [*list(existing), *list(incoming)]:
        key = item.evidence_id.strip().lower()
        if key not in merged:
            merged[key] = item
    return list(merged.values())[:16]


def _merge_source_provenance(
    existing: Sequence[GateSourceProvenanceContract],
    incoming: Sequence[GateSourceProvenanceContract],
) -> list[GateSourceProvenanceContract]:
    merged: dict[tuple[str, str | None, str | None, str | None], GateSourceProvenanceContract] = {}
    for item in [*list(existing), *list(incoming)]:
        key = (item.source, item.provider, item.model_id, item.summary)
        if key not in merged:
            merged[key] = item
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
            ),
            "source_provenance": _merge_source_provenance(
                summary.source_provenance,
                [item for item in (classifier_provenance, segmentation_provenance) if item is not None],
            ),
        }
    )
