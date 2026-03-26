# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Helpers for converting deterministic capture bundles into vision requests."""

from __future__ import annotations

from collections.abc import Sequence

from server.adapters.mcp.contracts.reference import ReferenceImageRecordContract
from server.adapters.mcp.contracts.vision import (
    VisionCaptureBundleContract,
    VisionCaptureImageContract,
)

from .backend import VisionImageInput, VisionRequest


def _capture_to_image_input(
    capture: VisionCaptureImageContract,
    *,
    role: str,
) -> VisionImageInput:
    return VisionImageInput(
        path=capture.image_path,
        role=role,
        label=capture.label,
        media_type=capture.media_type,
    )


def build_vision_request_from_capture_bundle(
    bundle: VisionCaptureBundleContract,
    *,
    goal: str,
    reference_images: Sequence[VisionCaptureImageContract] = (),
    prompt_hint: str | None = None,
) -> VisionRequest:
    """Build a normalized VisionRequest from a deterministic capture bundle."""

    images = tuple(
        [
            *[_capture_to_image_input(capture, role="before") for capture in bundle.captures_before],
            *[_capture_to_image_input(capture, role="after") for capture in bundle.captures_after],
            *[_capture_to_image_input(capture, role="reference") for capture in reference_images],
        ]
    )
    return VisionRequest(
        goal=goal,
        images=images,
        target_object=bundle.target_object,
        prompt_hint=prompt_hint,
        truth_summary=bundle.truth_summary,
        metadata={
            "bundle_id": bundle.bundle_id,
            "goal_id": bundle.goal_id,
            "preset_names": list(bundle.preset_names),
        },
    )


def build_reference_capture_images(
    reference_records: Sequence[ReferenceImageRecordContract | dict],
) -> tuple[VisionCaptureImageContract, ...]:
    """Normalize stored session references into capture-image contracts."""

    captures: list[VisionCaptureImageContract] = []
    for record in reference_records:
        resolved = (
            record
            if isinstance(record, ReferenceImageRecordContract)
            else ReferenceImageRecordContract.model_validate(record)
        )
        captures.append(
            VisionCaptureImageContract(
                label=resolved.label or resolved.reference_id,
                image_path=resolved.stored_path,
                host_visible_path=resolved.host_visible_path,
                media_type=resolved.media_type,
                view_kind="reference",
            )
        )
    return tuple(captures)


def select_reference_records_for_target(
    reference_records: Sequence[ReferenceImageRecordContract | dict],
    *,
    target_object: str | None,
) -> tuple[ReferenceImageRecordContract, ...]:
    """Return the most relevant goal-scoped references for one target object.

    Current selection policy is intentionally simple and deterministic:
    - if there are references explicitly targeting the current object, prefer only those
    - otherwise fall back to generic session references
    - keep insertion order stable
    """

    resolved = tuple(
        record if isinstance(record, ReferenceImageRecordContract) else ReferenceImageRecordContract.model_validate(record)
        for record in reference_records
    )
    if target_object is None:
        return resolved

    targeted = tuple(record for record in resolved if record.target_object == target_object)
    if targeted:
        return targeted
    return tuple(record for record in resolved if record.target_object is None) or resolved
