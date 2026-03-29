# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Helpers for attaching vision artifacts to macro execution reports."""

from __future__ import annotations

from server.adapters.mcp.contracts.macro import (
    MacroExecutionReportContract,
    MacroVerificationRecommendationContract,
)
from server.adapters.mcp.contracts.vision import VisionCaptureBundleContract
from server.adapters.mcp.sampling.result_types import VisionAssistantContract


def _dedupe_macro_recommendations(
    items: list[MacroVerificationRecommendationContract],
) -> list[MacroVerificationRecommendationContract]:
    seen: set[tuple[str, str, str]] = set()
    deduped: list[MacroVerificationRecommendationContract] = []
    for item in items:
        key = (item.tool_name, item.reason.strip().lower(), item.priority)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def _vision_recommendations_for_macro(
    vision_assistant: VisionAssistantContract | None,
) -> tuple[list[MacroVerificationRecommendationContract], bool]:
    """Map bounded vision output onto macro follow-up recommendations."""

    if vision_assistant is None or vision_assistant.result is None or vision_assistant.status != "success":
        return [], False

    result = vision_assistant.result
    recommendations: list[MacroVerificationRecommendationContract] = []

    for item in result.recommended_checks:
        recommendations.append(
            MacroVerificationRecommendationContract(
                tool_name=item.tool_name,
                reason=f"Vision follow-up: {item.reason}",
                priority=item.priority,
            )
        )

    if result.shape_mismatches:
        recommendations.append(
            MacroVerificationRecommendationContract(
                tool_name="inspect_scene",
                reason="Vision flagged visible form/silhouette mismatches. Inspect the object state before the next correction.",
                priority="high",
            )
        )

    if result.proportion_mismatches:
        recommendations.append(
            MacroVerificationRecommendationContract(
                tool_name="scene_measure_dimensions",
                reason="Vision flagged visible proportion/ratio mismatches. Measure the object dimensions before the next correction.",
                priority="high",
            )
        )

    if result.next_corrections and not (result.shape_mismatches or result.proportion_mismatches):
        recommendations.append(
            MacroVerificationRecommendationContract(
                tool_name="inspect_scene",
                reason="Vision suggested bounded next corrections. Inspect the current object state before applying them.",
                priority="normal",
            )
        )

    requires_followup = bool(
        result.shape_mismatches
        or result.proportion_mismatches
        or result.likely_issues
        or result.next_corrections
        or result.recommended_checks
    )
    return _dedupe_macro_recommendations(recommendations), requires_followup


def attach_vision_artifacts(
    report: MacroExecutionReportContract,
    *,
    capture_bundle: VisionCaptureBundleContract | None = None,
    vision_assistant: VisionAssistantContract | None = None,
) -> MacroExecutionReportContract:
    """Return a macro report enriched with optional capture/vision artifacts."""

    vision_recommendations, vision_requires_followup = _vision_recommendations_for_macro(vision_assistant)
    merged_recommendations = _dedupe_macro_recommendations(
        [
            *(report.verification_recommended or []),
            *vision_recommendations,
        ]
    )

    return report.model_copy(
        update={
            "capture_bundle": capture_bundle,
            "vision_assistant": vision_assistant,
            "verification_recommended": merged_recommendations or None,
            "requires_followup": report.requires_followup or vision_requires_followup,
        }
    )
