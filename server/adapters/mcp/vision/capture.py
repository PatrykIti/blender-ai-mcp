# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Helpers for converting deterministic capture artifacts into vision requests."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any
from uuid import uuid4

from server.adapters.mcp.contracts.reference import ReferenceImageRecordContract
from server.adapters.mcp.contracts.vision import (
    VisionCaptureBundleContract,
    VisionCaptureImageContract,
)
from server.infrastructure.tmp_paths import get_viewport_output_paths

from .backend import VisionImageInput, VisionImageRole, VisionRequest
from .composite import build_labeled_view_grid

AUXILIARY_VIEW_KINDS = {"depth", "normal", "object_id"}
SUPPLEMENTAL_VIEW_KINDS = {*AUXILIARY_VIEW_KINDS, "overlay"}


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
        view_kind=capture.view_kind,
        projection=capture.projection,
    )


def _resolve_grid_output_paths(stage_label: str, output_path: str | None) -> tuple[str, str]:
    if output_path is not None:
        return output_path, output_path
    filename = f"vision_capture_grid_{stage_label}_{uuid4().hex}.jpg"
    latest_name = f"vision_capture_grid_{stage_label}_latest.jpg"
    internal_file, _internal_latest, external_file, _external_latest = get_viewport_output_paths(
        filename,
        latest_name=latest_name,
    )
    return str(internal_file), external_file


def _build_labeled_grid_capture(
    captures: Sequence[VisionCaptureImageContract],
    *,
    stage_label: str,
    output_path: str | None = None,
) -> VisionCaptureImageContract | None:
    if len(captures) <= 1:
        return None
    grid_label = f"view_grid_{stage_label}"
    grid_path, host_visible_path = _resolve_grid_output_paths(stage_label, output_path)
    try:
        built_grid_path = build_labeled_view_grid(
            [
                (capture.label or capture.preset_name or f"capture_{index}", capture.image_path)
                for index, capture in enumerate(captures, start=1)
            ],
            grid_path,
        )
    except Exception:
        return None
    if built_grid_path is None:
        return None
    warnings = [capture.capture_warning for capture in captures if capture.capture_warning]
    return VisionCaptureImageContract(
        label=grid_label,
        image_path=built_grid_path,
        host_visible_path=host_visible_path,
        preset_name="view_grid",
        media_type="image/jpeg",
        view_kind="grid",
        capture_ok=all(capture.capture_ok for capture in captures),
        capture_warning="; ".join(warnings)[:240] if warnings else None,
    )


def _capture_grid_metadata(
    capture: VisionCaptureImageContract, sources: Sequence[VisionCaptureImageContract]
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "label": capture.label,
        "view_kind": capture.view_kind,
        "source_labels": [source.label for source in sources],
    }
    if capture.projection is not None:
        payload["projection"] = capture.projection
    return payload


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


def _is_auxiliary_capture(capture: VisionCaptureImageContract) -> bool:
    return str(capture.view_kind or "") in AUXILIARY_VIEW_KINDS


def _is_supplemental_capture(capture: VisionCaptureImageContract) -> bool:
    return str(capture.view_kind or "") in SUPPLEMENTAL_VIEW_KINDS


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
    chosen = sorted(
        indexed,
        key=lambda pair: (
            _is_supplemental_capture(pair[1]),
            _view_selection_rank(pair[1]),
            pair[0],
        ),
    )[:bounded_max]
    return [capture for _, capture in sorted(chosen, key=lambda pair: pair[0])]


def _split_auxiliary_captures(
    captures: Sequence[VisionCaptureImageContract],
    *,
    enabled: bool,
) -> tuple[list[VisionCaptureImageContract], list[VisionCaptureImageContract]]:
    kept: list[VisionCaptureImageContract] = []
    dropped: list[VisionCaptureImageContract] = []
    for capture in captures:
        if _is_auxiliary_capture(capture) and not enabled:
            dropped.append(capture)
        else:
            kept.append(capture)
    return kept, dropped


def _record_auxiliary_capture_metadata(
    metadata: dict[str, Any],
    *,
    enabled: bool,
    before_selection: Sequence[VisionCaptureImageContract],
    after_selection: Sequence[VisionCaptureImageContract],
    disabled_drops: Sequence[VisionCaptureImageContract] = (),
) -> None:
    auxiliary_before = [capture for capture in before_selection if _is_auxiliary_capture(capture)]
    auxiliary_after = [capture for capture in after_selection if _is_auxiliary_capture(capture)]
    disabled_labels = [capture.label for capture in disabled_drops]
    if not enabled and not auxiliary_before and not auxiliary_after and not disabled_labels:
        return

    transmitted = {capture.label for capture in auxiliary_after}
    available = [capture.label for capture in auxiliary_before]
    budget_dropped = [label for label in available if label not in transmitted]
    payload: dict[str, Any] = {
        "enabled": enabled,
        "available": available,
        "transmitted": [capture.label for capture in auxiliary_after],
    }
    if budget_dropped:
        payload["dropped"] = budget_dropped
        payload["drop_reason"] = "image_budget"
    if disabled_labels:
        payload["disabled_drops"] = disabled_labels
    metadata["auxiliary_captures"] = payload


def _record_overlay_capture_metadata(
    metadata: dict[str, Any],
    captures: Sequence[VisionCaptureImageContract],
) -> None:
    overlays: list[dict[str, Any]] = []
    for capture in captures:
        if capture.view_kind != "overlay" or not capture.overlay_marks:
            continue
        overlays.append(
            {
                "label": capture.label,
                "preset_name": capture.preset_name,
                "marks": [mark.model_dump(mode="json") for mark in capture.overlay_marks],
            }
        )
    if overlays:
        metadata["mark_overlays"] = overlays


def build_vision_request_from_capture_bundle(
    bundle: VisionCaptureBundleContract,
    *,
    goal: str,
    reference_images: Sequence[VisionCaptureImageContract] = (),
    prompt_hint: str | None = None,
    max_images: int | None = None,
    capture_grid_enabled: bool = False,
    transmit_auxiliary_channels: bool = False,
    before_grid_output_path: str | None = None,
    after_grid_output_path: str | None = None,
) -> VisionRequest:
    """Build a normalized VisionRequest from a deterministic capture bundle.

    When ``max_images`` is provided, the before/after captures are down-selected
    to fit the budget (references are preserved first), so a richer capture set
    degrades gracefully instead of being hard-rejected as over-budget.
    """

    captures_before = list(bundle.captures_before)
    captures_after = list(bundle.captures_after)
    captures_before, disabled_before = _split_auxiliary_captures(
        captures_before,
        enabled=transmit_auxiliary_channels,
    )
    captures_after, disabled_after = _split_auxiliary_captures(
        captures_after,
        enabled=transmit_auxiliary_channels,
    )
    metadata: dict[str, Any] = {
        "bundle_id": bundle.bundle_id,
        "goal_id": bundle.goal_id,
        "preset_names": list(bundle.preset_names),
    }
    before_auxiliary_selection = list(captures_before)
    after_auxiliary_selection = list(captures_after)
    if max_images is not None:
        capture_budget = max(0, max_images - len(reference_images))
        # Split the capture budget across the two stages, favouring the after set.
        after_budget = capture_budget - min(len(captures_before), capture_budget // 2)
        before_budget = capture_budget - after_budget
        captures_after = select_capture_views_within_budget(captures_after, max_views=after_budget)
        captures_before = select_capture_views_within_budget(captures_before, max_views=before_budget)
    _record_auxiliary_capture_metadata(
        metadata,
        enabled=transmit_auxiliary_channels,
        before_selection=[*before_auxiliary_selection, *after_auxiliary_selection],
        after_selection=[*captures_before, *captures_after],
        disabled_drops=[*disabled_before, *disabled_after],
    )
    if capture_grid_enabled:
        source_captures_before = [capture for capture in captures_before if not _is_supplemental_capture(capture)]
        source_captures_after = [capture for capture in captures_after if not _is_supplemental_capture(capture)]
        supplemental_captures_before = [capture for capture in captures_before if _is_supplemental_capture(capture)]
        supplemental_captures_after = [capture for capture in captures_after if _is_supplemental_capture(capture)]
        before_grid = _build_labeled_grid_capture(
            source_captures_before,
            stage_label="before",
            output_path=before_grid_output_path,
        )
        after_grid = _build_labeled_grid_capture(
            source_captures_after,
            stage_label="after",
            output_path=after_grid_output_path,
        )
        grid_metadata: dict[str, Any] = {"enabled": True}
        if before_grid is not None:
            captures_before = [before_grid, *supplemental_captures_before]
            grid_metadata["before"] = _capture_grid_metadata(before_grid, source_captures_before)
        if after_grid is not None:
            captures_after = [after_grid, *supplemental_captures_after]
            grid_metadata["after"] = _capture_grid_metadata(after_grid, source_captures_after)
        metadata["capture_grid"] = grid_metadata
    _record_overlay_capture_metadata(metadata, [*captures_before, *captures_after])
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
        metadata=metadata,
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
    capture_grid_enabled: bool = False,
    transmit_auxiliary_channels: bool = False,
    grid_output_path: str | None = None,
) -> VisionRequest:
    """Build a normalized VisionRequest from one stage checkpoint capture set.

    When ``max_images`` is provided, the stage captures are down-selected to fit
    the budget after reserving room for the reference images, so a richer capture
    set degrades gracefully instead of being hard-rejected as over-budget.
    """

    stage_captures = list(captures)
    request_metadata = dict(metadata or {})
    stage_captures, disabled_auxiliary = _split_auxiliary_captures(
        stage_captures,
        enabled=transmit_auxiliary_channels,
    )
    before_auxiliary_selection = list(stage_captures)
    if max_images is not None:
        capture_budget = max(0, max_images - len(reference_images))
        stage_captures = select_capture_views_within_budget(stage_captures, max_views=capture_budget)
    _record_auxiliary_capture_metadata(
        request_metadata,
        enabled=transmit_auxiliary_channels,
        before_selection=before_auxiliary_selection,
        after_selection=stage_captures,
        disabled_drops=disabled_auxiliary,
    )
    if capture_grid_enabled:
        source_captures = [capture for capture in stage_captures if not _is_supplemental_capture(capture)]
        supplemental_captures = [capture for capture in stage_captures if _is_supplemental_capture(capture)]
        grid_capture = _build_labeled_grid_capture(source_captures, stage_label="after", output_path=grid_output_path)
        if grid_capture is not None:
            stage_captures = [grid_capture, *supplemental_captures]
            request_metadata["capture_grid"] = {
                "enabled": True,
                "after": _capture_grid_metadata(grid_capture, source_captures),
            }
        else:
            request_metadata["capture_grid"] = {"enabled": True, "status": "unavailable"}
    _record_overlay_capture_metadata(request_metadata, stage_captures)
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
        metadata=request_metadata,
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
