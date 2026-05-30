# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Helpers for converting deterministic capture artifacts into vision requests."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from server.adapters.mcp.contracts.reference import ReferenceImageRecordContract
from server.adapters.mcp.contracts.vision import (
    VisionCaptureBundleContract,
    VisionCaptureImageContract,
)

from .backend import VisionImageInput, VisionImageRole, VisionRequest


def _capture_to_image_input(
    capture: VisionCaptureImageContract,
    *,
    role: VisionImageRole,
) -> VisionImageInput:
    return VisionImageInput(
        path=capture.image_path,
        role=role,
        label=capture.label,
        media_type=capture.media_type,
    )


# Canonical informativeness ordering used to down-select capture views when a
# richer capture set must fit a smaller transmission budget. The orthographic
# triad (front/side/top) anchors shape/proportion comparison; an oblique 3/4 best
# reveals 3D form (DiffuRank: a few well-chosen views beat many); wide gives
# context; focus/detail are supplementary. Captures whose preset is unknown sort
# last but keep stable order.
_VIEW_SELECTION_PRIORITY = (
    "target_front",
    "target_side",
    "target_top",
    "target_oblique",
    "target_oblique_left",
    "target_oblique_right",
    "target_focus",
    "context_wide",
    "target_detail",
)


def _view_selection_rank(capture: VisionCaptureImageContract) -> int:
    name = capture.preset_name or ""
    try:
        return _VIEW_SELECTION_PRIORITY.index(name)
    except ValueError:
        return len(_VIEW_SELECTION_PRIORITY)


def select_capture_views_within_budget(
    captures: Sequence[VisionCaptureImageContract], *, max_views: int
) -> list[VisionCaptureImageContract]:
    """Deterministically down-select capture views to fit a transmission budget.

    Returns at most ``max_views`` captures, ranked by the canonical
    informativeness priority and tie-broken by original order, then re-emitted in
    the original capture order so the roster/caption ordering stays stable. When
    ``max_views`` already covers the input, the captures are returned unchanged.
    This lets a caller capture a richer view-set and still respect the image
    budget instead of having the whole request hard-rejected as over-budget.
    """

    bounded_max = max(0, max_views)
    if len(captures) <= bounded_max:
        return list(captures)
    indexed = list(enumerate(captures))
    chosen = sorted(indexed, key=lambda pair: (_view_selection_rank(pair[1]), pair[0]))[:bounded_max]
    return [capture for _, capture in sorted(chosen, key=lambda pair: pair[0])]


def build_vision_request_from_capture_bundle(
    bundle: VisionCaptureBundleContract,
    *,
    goal: str,
    reference_images: Sequence[VisionCaptureImageContract] = (),
    prompt_hint: str | None = None,
    max_images: int | None = None,
) -> VisionRequest:
    """Build a normalized VisionRequest from a deterministic capture bundle.

    When ``max_images`` is provided, the before/after captures are down-selected
    to fit the budget (references are preserved first), so a richer capture set
    degrades gracefully instead of being hard-rejected as over-budget.
    """

    captures_before = list(bundle.captures_before)
    captures_after = list(bundle.captures_after)
    if max_images is not None:
        capture_budget = max(0, max_images - len(reference_images))
        # Split the capture budget across the two stages, favouring the after set.
        after_budget = capture_budget - min(len(captures_before), capture_budget // 2)
        before_budget = capture_budget - after_budget
        captures_after = select_capture_views_within_budget(captures_after, max_views=after_budget)
        captures_before = select_capture_views_within_budget(captures_before, max_views=before_budget)
    images = tuple(
        [
            *[_capture_to_image_input(capture, role="before") for capture in captures_before],
            *[_capture_to_image_input(capture, role="after") for capture in captures_after],
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


def build_vision_request_from_stage_captures(
    captures: Sequence[VisionCaptureImageContract],
    *,
    goal: str,
    target_object: str | None = None,
    reference_images: Sequence[VisionCaptureImageContract] = (),
    prompt_hint: str | None = None,
    truth_summary: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
    max_images: int | None = None,
) -> VisionRequest:
    """Build a normalized VisionRequest from one stage checkpoint capture set.

    When ``max_images`` is provided, the stage captures are down-selected to fit
    the budget after reserving room for the reference images, so a richer capture
    set degrades gracefully instead of being hard-rejected as over-budget.
    """

    stage_captures = list(captures)
    if max_images is not None:
        capture_budget = max(0, max_images - len(reference_images))
        stage_captures = select_capture_views_within_budget(stage_captures, max_views=capture_budget)
    images = tuple(
        [
            *[_capture_to_image_input(capture, role="after") for capture in stage_captures],
            *[_capture_to_image_input(capture, role="reference") for capture in reference_images],
        ]
    )
    return VisionRequest(
        goal=goal,
        images=images,
        target_object=target_object,
        prompt_hint=prompt_hint,
        truth_summary=truth_summary,
        metadata=metadata or {},
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
    target_view: str | None = None,
) -> tuple[ReferenceImageRecordContract, ...]:
    """Return the most relevant goal-scoped references for one target object.

    Current selection policy is intentionally simple and deterministic:
    - if there are references explicitly targeting the current object and view, prefer only those
    - otherwise prefer object-specific references
    - otherwise fall back to generic references matching the requested view
    - otherwise fall back to generic session references
    - keep insertion order stable
    """

    resolved = tuple(
        record
        if isinstance(record, ReferenceImageRecordContract)
        else ReferenceImageRecordContract.model_validate(record)
        for record in reference_records
    )
    if target_object is None and target_view is None:
        return resolved

    if target_object is not None and target_view is not None:
        targeted_view = tuple(
            record for record in resolved if record.target_object == target_object and record.target_view == target_view
        )
        if targeted_view:
            return targeted_view

    if target_object is not None:
        targeted = tuple(record for record in resolved if record.target_object == target_object)
        if targeted:
            return targeted

    if target_view is not None:
        generic_view = tuple(
            record for record in resolved if record.target_object is None and record.target_view == target_view
        )
        if generic_view:
            return generic_view

    generic = tuple(record for record in resolved if record.target_object is None)
    return generic or resolved
