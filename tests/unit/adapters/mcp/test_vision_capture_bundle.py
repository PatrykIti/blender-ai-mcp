"""Tests for deterministic capture bundle scaffolding."""

from __future__ import annotations

from server.adapters.mcp.contracts import (
    VisionCaptureBundleContract,
    VisionCaptureImageContract,
)
from server.adapters.mcp.vision import build_vision_request_from_capture_bundle


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
