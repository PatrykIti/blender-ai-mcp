"""Tests for deterministic capture bundle scaffolding."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from server.adapters.mcp.contracts import (
    VisionCaptureBundleContract,
    VisionCaptureImageContract,
    VisionObjectIdCaptureArtifactContract,
    VisionOverlayMarkContract,
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


def _aux(preset: str, view_kind: Literal["depth", "normal", "object_id"]) -> VisionCaptureImageContract:
    return VisionCaptureImageContract(
        label=f"{preset}_after_{view_kind}",
        image_path=f"/tmp/{preset}_{view_kind}.png",
        preset_name=preset,
        view_kind=view_kind,
        media_type="image/png",
    )


def _overlay(preset: str) -> VisionCaptureImageContract:
    return VisionCaptureImageContract(
        label=f"{preset}_after_overlay",
        image_path=f"/tmp/{preset}_overlay.jpg",
        preset_name=preset,
        view_kind="overlay",
        media_type="image/jpeg",
        overlay_marks=[
            VisionOverlayMarkContract(mark_id=1, object_name="Body"),
            VisionOverlayMarkContract(mark_id=2, object_name="Head"),
        ],
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


def test_stage_request_does_not_transmit_internal_object_id_sidecar():
    capture = VisionCaptureImageContract(
        label="target_front_after",
        image_path="/tmp/front_after.png",
        preset_name="target_front",
        view_kind="focus",
        object_id_artifact=VisionObjectIdCaptureArtifactContract(
            image_path="/tmp/front_after_object_id.png",
            index_map={1: "Housing"},
        ),
    )

    request = build_vision_request_from_stage_captures([capture], goal="g")

    assert [image.label for image in request.images] == ["target_front_after"]
    assert all("object_id" not in str(image.path) for image in request.images)


def test_stage_request_transmits_auxiliary_channels_only_when_enabled():
    captures = [
        _cap("target_front"),
        _aux("target_front", "depth"),
        _aux("target_front", "normal"),
        _aux("target_front", "object_id"),
    ]

    default_request = build_vision_request_from_stage_captures(captures, goal="g")
    enabled_request = build_vision_request_from_stage_captures(
        captures,
        goal="g",
        transmit_auxiliary_channels=True,
    )

    assert [image.label for image in default_request.images] == ["target_front_after"]
    assert default_request.metadata["auxiliary_captures"] == {
        "enabled": False,
        "available": [],
        "transmitted": [],
        "disabled_drops": [
            "target_front_after_depth",
            "target_front_after_normal",
            "target_front_after_object_id",
        ],
    }
    assert [image.label for image in enabled_request.images] == [
        "target_front_after",
        "target_front_after_depth",
        "target_front_after_normal",
        "target_front_after_object_id",
    ]
    assert enabled_request.metadata["auxiliary_captures"] == {
        "enabled": True,
        "available": [
            "target_front_after_depth",
            "target_front_after_normal",
            "target_front_after_object_id",
        ],
        "transmitted": [
            "target_front_after_depth",
            "target_front_after_normal",
            "target_front_after_object_id",
        ],
    }


def test_stage_request_budget_drops_auxiliary_channels_before_primary_capture():
    captures = [
        _cap("target_front"),
        _cap("target_side"),
        _aux("target_front", "depth"),
        _aux("target_front", "normal"),
    ]

    request = build_vision_request_from_stage_captures(
        captures,
        goal="g",
        max_images=2,
        transmit_auxiliary_channels=True,
    )

    assert [image.label for image in request.images] == ["target_front_after", "target_side_after"]
    assert request.metadata["auxiliary_captures"] == {
        "enabled": True,
        "available": ["target_front_after_depth", "target_front_after_normal"],
        "transmitted": [],
        "dropped": ["target_front_after_depth", "target_front_after_normal"],
        "drop_reason": "image_budget",
    }


def test_stage_request_records_overlay_mark_metadata():
    captures = [_cap("target_front"), _overlay("target_front")]

    request = build_vision_request_from_stage_captures(captures, goal="g")

    assert [image.label for image in request.images] == ["target_front_after", "target_front_after_overlay"]
    assert request.metadata["mark_overlays"] == [
        {
            "label": "target_front_after_overlay",
            "preset_name": "target_front",
            "marks": [
                {"mark_id": 1, "object_name": "Body", "status": "placed"},
                {"mark_id": 2, "object_name": "Head", "status": "placed"},
            ],
        }
    ]


def test_stage_request_can_replace_views_with_labeled_grid(tmp_path: Path):
    captures = [_cap("target_front"), _cap("target_side"), _cap("target_top")]
    grid_path = tmp_path / "grid.png"

    request = build_vision_request_from_stage_captures(
        captures,
        goal="g",
        capture_grid_enabled=True,
        grid_output_path=str(grid_path),
    )

    after_images = [image for image in request.images if image.role == "after"]
    assert [image.label for image in after_images] == ["view_grid_after"]
    assert after_images[0].path == str(grid_path)
    assert grid_path.exists()
    assert request.metadata["capture_grid"] == {
        "enabled": True,
        "after": {
            "label": "view_grid_after",
            "view_kind": "grid",
            "source_labels": ["target_front_after", "target_side_after", "target_top_after"],
        },
    }


def test_stage_request_keeps_overlay_outside_labeled_grid(tmp_path: Path):
    captures = [_cap("target_front"), _cap("target_side"), _cap("target_top"), _overlay("target_front")]
    grid_path = tmp_path / "grid.png"

    request = build_vision_request_from_stage_captures(
        captures,
        goal="g",
        capture_grid_enabled=True,
        grid_output_path=str(grid_path),
    )

    after_images = [image for image in request.images if image.role == "after"]
    assert [image.label for image in after_images] == ["view_grid_after", "target_front_after_overlay"]
    assert request.metadata["capture_grid"]["after"]["source_labels"] == [
        "target_front_after",
        "target_side_after",
        "target_top_after",
    ]
    assert request.metadata["mark_overlays"][0]["label"] == "target_front_after_overlay"


def test_bundle_request_can_replace_before_after_views_with_labeled_grids(tmp_path: Path):
    bundle = VisionCaptureBundleContract(
        bundle_id="bundle_1",
        preset_names=["target_front", "target_side"],
        captures_before=[_cap("target_front"), _cap("target_side")],
        captures_after=[_cap("target_front"), _cap("target_side")],
    )

    request = build_vision_request_from_capture_bundle(
        bundle,
        goal="g",
        capture_grid_enabled=True,
        before_grid_output_path=str(tmp_path / "before_grid.png"),
        after_grid_output_path=str(tmp_path / "after_grid.png"),
    )

    assert [image.label for image in request.images] == ["view_grid_before", "view_grid_after"]
    assert request.metadata["capture_grid"]["before"]["view_kind"] == "grid"
    assert request.metadata["capture_grid"]["after"]["source_labels"] == [
        "target_front_after",
        "target_side_after",
    ]
