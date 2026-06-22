"""E2E coverage for deterministic Set-of-Mark overlay capture."""

from __future__ import annotations

import pytest
from PIL import Image
from server.adapters.mcp.vision import capture_stage_images
from server.application.tool_handlers.scene_handler import SceneToolHandler

pytestmark = pytest.mark.e2e


def _snapshot_visibility(snapshot: dict, object_names: set[str]) -> dict[str, bool]:
    raw_snapshot = snapshot.get("snapshot", snapshot)
    objects = raw_snapshot.get("objects", []) if isinstance(raw_snapshot, dict) else []
    return {
        item["name"]: bool(item.get("visible", True))
        for item in objects
        if isinstance(item, dict) and item.get("name") in object_names
    }


def _image_contains_red_mark(path: str) -> bool:
    with Image.open(path) as opened:
        image = opened.convert("RGB")
        data = image.tobytes()
        return any(
            data[index] > 150 and data[index + 1] < 120 and data[index + 2] < 120 for index in range(0, len(data), 3)
        )


def test_capture_stage_images_emits_set_of_mark_overlay_for_object_set(rpc_client, tmp_path, monkeypatch):
    """A real Blender object-set capture emits an overlay with object-bound marks."""

    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))
    scene_handler = SceneToolHandler(rpc_client)
    object_names = {"MarkBody", "MarkHead"}

    try:
        scene_handler.clean_scene(keep_lights_and_cameras=True)
        rpc_client.send_request(
            "modeling.create_primitive",
            {"primitive_type": "CUBE", "name": "MarkBody", "size": 0.8, "location": [-0.25, 0.0, 0.0]},
        )
        rpc_client.send_request(
            "modeling.create_primitive",
            {"primitive_type": "SPHERE", "name": "MarkHead", "radius": 0.24, "location": [0.25, -0.45, 0.25]},
        )
        scene_handler.set_standard_view("FRONT")
        scene_handler.camera_focus("MarkBody")
        before_visibility = _snapshot_visibility(
            scene_handler.snapshot_state(include_mesh_stats=False, include_materials=False),
            object_names,
        )

        captures = capture_stage_images(
            scene_handler,
            bundle_id="e2e_mark_overlay",
            stage="after",
            target_object="MarkBody",
            target_objects=["MarkHead", "MarkBody"],
            include_mark_overlay=True,
            mark_overlay_preset_names={"target_front"},
        )

        overlay = next(capture for capture in captures if capture.view_kind == "overlay")
        assert overlay.label == "target_front_after_overlay"
        assert [(mark.mark_id, mark.object_name, mark.status) for mark in overlay.overlay_marks] == [
            (1, "MarkBody", "placed"),
            (2, "MarkHead", "placed"),
        ]
        assert _image_contains_red_mark(overlay.image_path)

        after_visibility = _snapshot_visibility(
            scene_handler.snapshot_state(include_mesh_stats=False, include_materials=False),
            object_names,
        )
        assert after_visibility == before_visibility
    except RuntimeError as exc:
        pytest.skip(f"Blender not available: {exc}")
