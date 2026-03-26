"""Tests for deterministic capture runtime helpers."""

from __future__ import annotations

import base64

from server.adapters.mcp.vision import (
    build_capture_bundle,
    capture_scene_state,
    capture_stage_images,
    restore_scene_state,
)


class _Handler:
    def __init__(self) -> None:
        self.calls: list[dict] = []
        self.focus_calls: list[dict] = []
        self.orbit_calls: list[dict] = []
        self.hide_calls: list[dict] = []

    def get_viewport(self, width=1024, height=768, shading="SOLID", camera_name=None, focus_target=None):
        self.calls.append(
            {
                "width": width,
                "height": height,
                "shading": shading,
                "camera_name": camera_name,
                "focus_target": focus_target,
            }
        )
        return base64.b64encode(b"fake-jpeg").decode("ascii")

    def camera_focus(self, object_name: str, zoom_factor: float = 1.0):
        self.focus_calls.append({"object_name": object_name, "zoom_factor": zoom_factor})
        return "focus ok"

    def camera_orbit(self, angle_horizontal=0.0, angle_vertical=0.0, target_object=None, target_point=None):
        self.orbit_calls.append(
            {
                "angle_horizontal": angle_horizontal,
                "angle_vertical": angle_vertical,
                "target_object": target_object,
                "target_point": target_point,
            }
        )
        return "orbit ok"

    def snapshot_state(self, include_mesh_stats=False, include_materials=False):
        return {
            "snapshot": {
                "objects": [
                    {"name": "Housing", "visible": True},
                    {"name": "Panel", "visible": False},
                ]
            }
        }

    def hide_object(self, object_name: str, hide: bool = True, hide_render: bool = False):
        self.hide_calls.append({"object_name": object_name, "hide": hide, "hide_render": hide_render})
        return "hide ok"


def test_capture_stage_images_builds_wide_and_focus_variants(tmp_path, monkeypatch):
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    handler = _Handler()
    captures = capture_stage_images(
        handler,
        bundle_id="bundle1",
        stage="before",
        target_object="Housing",
    )

    assert [capture.preset_name for capture in captures] == ["context_wide", "target_focus", "target_oblique"]
    assert captures[0].view_kind == "wide"
    assert captures[1].view_kind == "focus"
    assert captures[2].view_kind == "focus"
    assert captures[0].host_visible_path is not None
    assert tmp_path.joinpath("internal", "blender-ai-mcp", "bundle1_before_context_wide.jpg").exists()
    assert tmp_path.joinpath("internal", "blender-ai-mcp", "bundle1_before_target_focus.jpg").exists()
    assert tmp_path.joinpath("internal", "blender-ai-mcp", "bundle1_before_target_oblique.jpg").exists()
    assert handler.calls[0]["focus_target"] is None
    assert handler.calls[1]["focus_target"] == "Housing"
    assert handler.calls[2]["focus_target"] == "Housing"
    assert [call["object_name"] for call in handler.focus_calls] == ["Housing", "Housing"]
    assert handler.orbit_calls == [
        {
            "angle_horizontal": 35.0,
            "angle_vertical": 15.0,
            "target_object": "Housing",
            "target_point": None,
        }
    ]


def test_build_capture_bundle_collects_preset_names(tmp_path, monkeypatch):
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    handler = _Handler()
    before = capture_stage_images(handler, bundle_id="bundle2", stage="before", target_object="Housing")
    after = capture_stage_images(handler, bundle_id="bundle2", stage="after", target_object="Housing")

    bundle = build_capture_bundle(
        bundle_id="bundle2",
        goal_id="goal1",
        target_object="Housing",
        captures_before=before,
        captures_after=after,
        truth_summary={"dimensions": [1, 2, 3]},
    )

    assert bundle.bundle_id == "bundle2"
    assert bundle.goal_id == "goal1"
    assert bundle.target_object == "Housing"
    assert bundle.preset_names == ["context_wide", "target_focus", "target_oblique"]
    assert bundle.truth_summary == {"dimensions": [1, 2, 3]}


def test_capture_scene_state_collects_visibility_snapshot():
    handler = _Handler()

    state = capture_scene_state(handler)

    assert state.visibility_snapshot == {"Housing": True, "Panel": False}
    assert state.view_state is None


def test_restore_scene_state_replays_visibility_snapshot():
    handler = _Handler()
    state = capture_scene_state(handler)

    restore_scene_state(handler, state)

    assert handler.hide_calls == [
        {"object_name": "Housing", "hide": False, "hide_render": False},
        {"object_name": "Panel", "hide": True, "hide_render": False},
    ]
