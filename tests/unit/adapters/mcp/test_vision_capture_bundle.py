"""Tests for deterministic capture bundle scaffolding."""

from __future__ import annotations

from server.adapters.mcp.contracts import (
    VisionCaptureBundleContract,
    VisionCaptureImageContract,
)
from server.adapters.mcp.contracts.reference import ReferenceImageRecordContract
from server.adapters.mcp.vision import (
    build_vision_request_from_capture_bundle,
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
