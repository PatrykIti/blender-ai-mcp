"""Tests for deterministic capture bundle scaffolding."""

from __future__ import annotations

from server.adapters.mcp.contracts import (
    VisionCaptureBundleContract,
    VisionCaptureImageContract,
)
from server.adapters.mcp.contracts.reference import ReferenceImageRecordContract
from server.adapters.mcp.vision import (
    build_vision_request_from_capture_bundle,
    build_vision_request_from_stage_captures,
    select_capture_views_within_budget,
    select_reference_records_for_target,
)


def test_capture_bundle_can_be_converted_into_vision_request():
    bundle = VisionCaptureBundleContract(
        bundle_id="bundle_1",
        goal_id="goal_1",
        target_object="Housing",
        preset_names=["front", "iso_focus"],
        captures_before=[
            VisionCaptureImageContract(
                label="front_before",
                image_path="/tmp/front_before.png",
                preset_name="front",
                view_kind="wide",
            )
        ],
        captures_after=[
            VisionCaptureImageContract(
                label="front_after",
                image_path="/tmp/front_after.png",
                preset_name="front",
                view_kind="wide",
            )
        ],
        truth_summary={"dimensions": [0.2, 0.1, 0.05]},
    )
    reference = VisionCaptureImageContract(
        label="reference_main",
        image_path="/tmp/reference.png",
        view_kind="reference",
    )

    request = build_vision_request_from_capture_bundle(
        bundle,
        goal="Make the housing closer to the reference.",
        reference_images=[reference],
        prompt_hint="Focus on the front silhouette.",
    )

    assert request.goal == "Make the housing closer to the reference."
    assert request.target_object == "Housing"
    assert [image.role for image in request.images] == ["before", "after", "reference"]
    assert request.metadata["bundle_id"] == "bundle_1"
    assert request.metadata["preset_names"] == ["front", "iso_focus"]
    assert request.truth_summary == {"dimensions": [0.2, 0.1, 0.05]}


def test_stage_captures_can_be_converted_into_vision_request():
    captures = [
        VisionCaptureImageContract(
            label="target_front_after",
            image_path="/tmp/front_after.png",
            preset_name="target_front",
            view_kind="focus",
        ),
        VisionCaptureImageContract(
            label="target_side_after",
            image_path="/tmp/side_after.png",
            preset_name="target_side",
            view_kind="focus",
        ),
    ]
    reference = VisionCaptureImageContract(
        label="reference_side",
        image_path="/tmp/reference_side.png",
        view_kind="reference",
    )

    request = build_vision_request_from_stage_captures(
        captures,
        goal="Move this squirrel stage closer to the front and side references.",
        target_object="Squirrel",
        reference_images=[reference],
        prompt_hint="Focus on silhouette and tail arc.",
        metadata={"checkpoint_id": "stage_3", "preset_profile": "compact"},
    )

    assert request.goal == "Move this squirrel stage closer to the front and side references."
    assert request.target_object == "Squirrel"
    assert [image.role for image in request.images] == ["after", "after", "reference"]
    assert request.metadata["checkpoint_id"] == "stage_3"
    assert request.metadata["preset_profile"] == "compact"


def test_select_reference_records_prefers_object_specific_matches():
    generic = ReferenceImageRecordContract(
        reference_id="ref_generic",
        goal="rounded housing",
        media_type="image/png",
        original_path="/tmp/generic.png",
        stored_path="/tmp/generic_stored.png",
        added_at="2026-03-26T00:00:00Z",
    )
    specific = ReferenceImageRecordContract(
        reference_id="ref_specific",
        goal="rounded housing",
        target_object="Housing",
        media_type="image/png",
        original_path="/tmp/housing.png",
        stored_path="/tmp/housing_stored.png",
        added_at="2026-03-26T00:00:01Z",
    )

    selected = select_reference_records_for_target([generic, specific], target_object="Housing")

    assert [item.reference_id for item in selected] == ["ref_specific"]


def test_select_reference_records_falls_back_to_generic_when_no_object_match():
    generic = ReferenceImageRecordContract(
        reference_id="ref_generic",
        goal="rounded housing",
        media_type="image/png",
        original_path="/tmp/generic.png",
        stored_path="/tmp/generic_stored.png",
        added_at="2026-03-26T00:00:00Z",
    )
    other = ReferenceImageRecordContract(
        reference_id="ref_other",
        goal="rounded housing",
        target_object="Panel",
        media_type="image/png",
        original_path="/tmp/panel.png",
        stored_path="/tmp/panel_stored.png",
        added_at="2026-03-26T00:00:01Z",
    )

    selected = select_reference_records_for_target([generic, other], target_object="Housing")

    assert [item.reference_id for item in selected] == ["ref_generic"]


def test_select_reference_records_prefers_target_view_within_object_matches():
    object_generic = ReferenceImageRecordContract(
        reference_id="ref_object_generic",
        goal="rounded housing",
        target_object="Housing",
        media_type="image/png",
        original_path="/tmp/object_generic.png",
        stored_path="/tmp/object_generic_stored.png",
        added_at="2026-03-26T00:00:00Z",
    )
    object_view = ReferenceImageRecordContract(
        reference_id="ref_object_view",
        goal="rounded housing",
        target_object="Housing",
        target_view="target_focus",
        media_type="image/png",
        original_path="/tmp/object_view.png",
        stored_path="/tmp/object_view_stored.png",
        added_at="2026-03-26T00:00:01Z",
    )

    selected = select_reference_records_for_target(
        [object_generic, object_view],
        target_object="Housing",
        target_view="target_focus",
    )

    assert [item.reference_id for item in selected] == ["ref_object_view"]


def test_select_reference_records_can_fall_back_to_generic_view_match():
    generic = ReferenceImageRecordContract(
        reference_id="ref_generic",
        goal="rounded housing",
        media_type="image/png",
        original_path="/tmp/generic.png",
        stored_path="/tmp/generic_stored.png",
        added_at="2026-03-26T00:00:00Z",
    )
    generic_view = ReferenceImageRecordContract(
        reference_id="ref_generic_view",
        goal="rounded housing",
        target_view="target_focus",
        media_type="image/png",
        original_path="/tmp/generic_view.png",
        stored_path="/tmp/generic_view_stored.png",
        added_at="2026-03-26T00:00:01Z",
    )

    selected = select_reference_records_for_target(
        [generic, generic_view],
        target_object="Housing",
        target_view="target_focus",
    )

    assert [item.reference_id for item in selected] == ["ref_generic_view"]


def _cap(preset: str) -> VisionCaptureImageContract:
    return VisionCaptureImageContract(
        label=f"{preset}_after",
        image_path=f"/tmp/{preset}.png",
        preset_name=preset,
        view_kind="focus",
    )


def test_select_capture_views_keeps_orthographic_triad_first():
    captures = [
        _cap("context_wide"),
        _cap("target_front"),
        _cap("target_side"),
        _cap("target_top"),
        _cap("target_detail"),
    ]
    chosen = select_capture_views_within_budget(captures, max_views=3)
    names = [c.preset_name for c in chosen]
    # The orthographic triad outranks wide/detail; original order is preserved.
    assert names == ["target_front", "target_side", "target_top"]


def test_select_capture_views_noop_when_within_budget():
    captures = [_cap("target_front"), _cap("target_side")]
    assert select_capture_views_within_budget(captures, max_views=5) == captures
    assert select_capture_views_within_budget(captures, max_views=2) == captures


def test_stage_request_downselects_to_budget_reserving_references():
    captures = [_cap("context_wide"), _cap("target_front"), _cap("target_side"), _cap("target_top")]
    references = [
        VisionCaptureImageContract(label="ref", image_path="/tmp/ref.png", view_kind="reference"),
    ]
    request = build_vision_request_from_stage_captures(
        captures,
        goal="g",
        reference_images=references,
        max_images=3,
    )
    roles = [img.role for img in request.images]
    # 3 budget - 1 reference = 2 stage captures + 1 reference.
    assert roles.count("after") == 2
    assert roles.count("reference") == 1
    after_labels = [img.label for img in request.images if img.role == "after"]
    assert after_labels == ["target_front_after", "target_side_after"]


def test_stage_request_without_budget_is_unchanged():
    captures = [_cap("target_front"), _cap("target_side"), _cap("target_top")]
    request = build_vision_request_from_stage_captures(captures, goal="g")
    assert sum(1 for img in request.images if img.role == "after") == 3
