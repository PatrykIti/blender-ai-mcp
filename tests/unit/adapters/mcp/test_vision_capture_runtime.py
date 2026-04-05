"""Tests for deterministic capture runtime helpers."""

from __future__ import annotations

import base64

from server.adapters.mcp.vision import (
    COMPACT_CAPTURE_PRESET_SPECS,
    RICH_CAPTURE_PRESET_SPECS,
    build_capture_bundle,
    capture_scene_state,
    capture_stage_images,
    resolve_capture_preset_specs,
    restore_scene_state,
)


class _Handler:
    def __init__(self) -> None:
        self.calls: list[dict] = []
        self.focus_calls: list[dict] = []
        self.orbit_calls: list[dict] = []
        self.hide_calls: list[dict] = []
        self.isolate_calls: list[list[str]] = []
        self.restore_view_state_calls: list[dict] = []
        self.standard_view_calls: list[str] = []

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

    def set_standard_view(self, view_name: str):
        self.standard_view_calls.append(view_name)
        return "view ok"

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

    def isolate_object(self, object_names):
        self.isolate_calls.append(list(object_names))
        return "isolate ok"

    def get_view_state(self):
        return {
            "available": True,
            "view_location": [1.0, 2.0, 3.0],
            "view_distance": 10.0,
            "view_rotation": [1.0, 0.0, 0.0, 0.0],
            "view_perspective": "PERSP",
        }

    def restore_view_state(self, view_state):
        self.restore_view_state_calls.append(view_state)
        return "restored"


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

    assert [capture.preset_name for capture in captures] == [
        "context_wide",
        "target_front",
        "target_side",
        "target_top",
    ]
    assert captures[0].view_kind == "wide"
    assert captures[1].view_kind == "focus"
    assert captures[2].view_kind == "focus"
    assert captures[3].view_kind == "focus"
    assert captures[0].host_visible_path is not None
    assert tmp_path.joinpath("internal", "blender-ai-mcp", "bundle1_before_context_wide.jpg").exists()
    assert tmp_path.joinpath("internal", "blender-ai-mcp", "bundle1_before_target_front.jpg").exists()
    assert tmp_path.joinpath("internal", "blender-ai-mcp", "bundle1_before_target_side.jpg").exists()
    assert tmp_path.joinpath("internal", "blender-ai-mcp", "bundle1_before_target_top.jpg").exists()
    assert handler.calls[0]["focus_target"] is None
    assert handler.calls[1]["focus_target"] == "Housing"
    assert handler.calls[2]["focus_target"] == "Housing"
    assert handler.calls[3]["focus_target"] == "Housing"
    assert [call["object_name"] for call in handler.focus_calls] == ["Housing", "Housing", "Housing"]
    assert handler.isolate_calls == [["Housing"], ["Housing"], ["Housing"]]
    assert handler.standard_view_calls == ["FRONT", "RIGHT", "TOP"]
    assert len(handler.restore_view_state_calls) == 4
    assert handler.orbit_calls == []


def test_capture_preset_profiles_resolve_expected_named_sets():
    assert resolve_capture_preset_specs("compact") == COMPACT_CAPTURE_PRESET_SPECS
    assert resolve_capture_preset_specs("rich") == RICH_CAPTURE_PRESET_SPECS
    assert [preset.name for preset in COMPACT_CAPTURE_PRESET_SPECS] == [
        "context_wide",
        "target_front",
        "target_side",
        "target_top",
    ]
    assert [preset.name for preset in RICH_CAPTURE_PRESET_SPECS] == [
        "context_wide",
        "target_focus",
        "target_oblique_left",
        "target_oblique_right",
        "target_front",
        "target_side",
        "target_top",
        "target_detail",
    ]


def test_capture_stage_images_can_use_rich_profile(tmp_path, monkeypatch):
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    handler = _Handler()
    captures = capture_stage_images(
        handler,
        bundle_id="bundle_rich",
        stage="after",
        target_object="Housing",
        preset_profile="rich",
    )

    assert len(captures) == 8
    assert captures[0].preset_name == "context_wide"
    assert captures[-1].preset_name == "target_detail"
    assert len(handler.orbit_calls) == 2


def test_capture_stage_images_can_isolate_multiple_objects_without_single_focus(tmp_path, monkeypatch):
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    handler = _Handler()
    captures = capture_stage_images(
        handler,
        bundle_id="bundle_multi",
        stage="after",
        target_objects=["Squirrel_Head", "Squirrel_Body", "Squirrel_Tail"],
        preset_profile="compact",
    )

    assert len(captures) == 4
    assert handler.isolate_calls == [
        ["Squirrel_Head", "Squirrel_Body", "Squirrel_Tail"],
        ["Squirrel_Head", "Squirrel_Body", "Squirrel_Tail"],
        ["Squirrel_Head", "Squirrel_Body", "Squirrel_Tail"],
    ]
    assert handler.focus_calls == []
    assert handler.calls[1]["focus_target"] is None


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
    assert bundle.assembled_target_scope is None
    assert bundle.preset_names == ["context_wide", "target_front", "target_side", "target_top"]
    assert bundle.truth_summary == {"dimensions": [1, 2, 3]}


def test_capture_scene_state_collects_visibility_snapshot():
    handler = _Handler()

    state = capture_scene_state(handler)

    assert state.visibility_snapshot == {"Housing": True, "Panel": False}
    assert state.view_state is not None
    assert state.view_state["view_perspective"] == "PERSP"


def test_restore_scene_state_replays_visibility_snapshot():
    handler = _Handler()
    state = capture_scene_state(handler)

    restore_scene_state(handler, state)

    assert handler.hide_calls == [
        {"object_name": "Housing", "hide": False, "hide_render": False},
        {"object_name": "Panel", "hide": True, "hide_render": False},
    ]


def test_capture_stage_images_restores_state_after_capture(tmp_path, monkeypatch):
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    handler = _Handler()

    capture_stage_images(
        handler,
        bundle_id="bundle3",
        stage="before",
        target_object="Housing",
    )

    assert len(handler.restore_view_state_calls) == 4
    assert all(
        call
        == {
            "available": True,
            "view_location": [1.0, 2.0, 3.0],
            "view_distance": 10.0,
            "view_rotation": [1.0, 0.0, 0.0, 0.0],
            "view_perspective": "PERSP",
        }
        for call in handler.restore_view_state_calls
    )
    assert handler.hide_calls[-2:] == [
        {"object_name": "Housing", "hide": False, "hide_render": False},
        {"object_name": "Panel", "hide": True, "hide_render": False},
    ]
