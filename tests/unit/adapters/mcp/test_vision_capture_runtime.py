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
        self.object_id_calls: list[dict] = []
        self.depth_calls: list[dict] = []
        self.normal_calls: list[dict] = []
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

    def get_object_id_pass(self, object_names, width=1024, height=768, camera_name=None):
        names = [str(name) for name in object_names]
        self.object_id_calls.append(
            {
                "object_names": names,
                "width": width,
                "height": height,
                "camera_name": camera_name,
            }
        )
        return {
            "image": base64.b64encode(b"\x89PNG\r\n\x1a\nfake-object-id").decode("ascii"),
            "index_map": {index: name for index, name in enumerate(names, start=1)},
            "missing": [],
        }

    def get_depth_pass(self, width=1024, height=768, camera_name=None):
        self.depth_calls.append({"width": width, "height": height, "camera_name": camera_name})
        return base64.b64encode(b"\x89PNG\r\n\x1a\nfake-depth").decode("ascii")

    def get_normal_pass(self, width=1024, height=768, camera_name=None):
        self.normal_calls.append({"width": width, "height": height, "camera_name": camera_name})
        return base64.b64encode(b"\x89PNG\r\n\x1a\nfake-normal").decode("ascii")

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


class _OverlayHandler(_Handler):
    """Handler that returns real PNG images so the overlay builder can read them."""

    def __init__(self) -> None:
        super().__init__()
        self._isolated_objects: list[str] = []
        self._boxes = {"Body": (20, 20, 80, 80), "Head": (120, 120, 180, 180)}

    def isolate_object(self, object_names):
        names = [str(name) for name in object_names]
        self.isolate_calls.append(names)
        self._isolated_objects = names
        return "isolate ok"

    def get_viewport(self, width=1024, height=768, shading="SOLID", camera_name=None, focus_target=None):
        import io

        from PIL import Image, ImageDraw

        self.calls.append(
            {
                "width": width,
                "height": height,
                "shading": shading,
                "camera_name": camera_name,
                "focus_target": focus_target,
            }
        )
        image = Image.new("RGB", (200, 200), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        for name in self._isolated_objects or list(self._boxes):
            draw.rectangle(self._boxes.get(name, (90, 90, 110, 110)), fill=(0, 0, 0))
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("ascii")


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
        "target_oblique_left",
    ]
    assert captures[0].view_kind == "wide"
    assert captures[1].view_kind == "focus"
    assert captures[2].view_kind == "focus"
    assert captures[3].view_kind == "top"
    assert captures[3].projection == "orthographic"
    assert captures[4].view_kind == "oblique"
    assert captures[4].projection == "perspective"
    assert captures[0].host_visible_path is not None
    assert tmp_path.joinpath("internal", "blender-ai-mcp", "bundle1_before_context_wide.jpg").exists()
    assert tmp_path.joinpath("internal", "blender-ai-mcp", "bundle1_before_target_front.jpg").exists()
    assert tmp_path.joinpath("internal", "blender-ai-mcp", "bundle1_before_target_side.jpg").exists()
    assert tmp_path.joinpath("internal", "blender-ai-mcp", "bundle1_before_target_top.jpg").exists()
    assert tmp_path.joinpath("internal", "blender-ai-mcp", "bundle1_before_target_oblique_left.jpg").exists()
    assert handler.calls[0]["focus_target"] is None
    assert handler.calls[1]["focus_target"] == "Housing"
    assert handler.calls[2]["focus_target"] == "Housing"
    assert handler.calls[3]["focus_target"] == "Housing"
    assert [call["object_name"] for call in handler.focus_calls] == ["Housing", "Housing", "Housing", "Housing"]
    assert handler.isolate_calls == [["Housing"], ["Housing"], ["Housing"], ["Housing"]]
    assert handler.standard_view_calls == ["FRONT", "RIGHT", "TOP"]
    assert len(handler.restore_view_state_calls) == 5
    assert len(handler.orbit_calls) == 1


def test_capture_preset_profiles_resolve_expected_named_sets():
    assert resolve_capture_preset_specs("compact") == COMPACT_CAPTURE_PRESET_SPECS
    assert resolve_capture_preset_specs("rich") == RICH_CAPTURE_PRESET_SPECS
    assert [preset.name for preset in COMPACT_CAPTURE_PRESET_SPECS] == [
        "context_wide",
        "target_front",
        "target_side",
        "target_top",
        "target_oblique_left",
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


def test_capture_stage_images_can_attach_object_id_sidecar_for_target_view(tmp_path, monkeypatch):
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    handler = _Handler()
    captures = capture_stage_images(
        handler,
        bundle_id="bundle_object_id",
        stage="after",
        target_object="Housing",
        preset_profile="compact",
        include_object_id_pass=True,
        object_id_preset_names={"target_side"},
    )

    assert [capture.preset_name for capture in captures] == [
        "context_wide",
        "target_front",
        "target_side",
        "target_top",
        "target_oblique_left",
    ]
    assert len(handler.object_id_calls) == 1
    assert handler.object_id_calls[0] == {
        "object_names": ["Housing"],
        "width": 1280,
        "height": 960,
        "camera_name": "USER_PERSPECTIVE",
    }
    side = next(capture for capture in captures if capture.preset_name == "target_side")
    assert side.object_id_artifact is not None
    assert side.object_id_artifact.capture_ok is True
    assert side.object_id_artifact.index_map == {1: "Housing"}
    assert side.object_id_artifact.image_path is not None
    assert tmp_path.joinpath("internal", "blender-ai-mcp", "bundle_object_id_after_target_side_object_id.png").exists()
    assert all(capture.object_id_artifact is None for capture in captures if capture.preset_name != "target_side")


def test_capture_stage_images_can_append_auxiliary_pass_captures(tmp_path, monkeypatch):
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    handler = _Handler()
    captures = capture_stage_images(
        handler,
        bundle_id="bundle_aux",
        stage="after",
        target_object="Housing",
        preset_profile="compact",
        include_auxiliary_passes=True,
        auxiliary_preset_names={"target_front"},
    )

    assert [capture.label for capture in captures] == [
        "context_wide_after",
        "target_front_after",
        "target_front_after_depth",
        "target_front_after_normal",
        "target_front_after_object_id",
        "target_side_after",
        "target_top_after",
        "target_oblique_left_after",
    ]
    assert [capture.view_kind for capture in captures[2:5]] == ["depth", "normal", "object_id"]
    assert handler.depth_calls == [{"width": 1280, "height": 960, "camera_name": "USER_PERSPECTIVE"}]
    assert handler.normal_calls == [{"width": 1280, "height": 960, "camera_name": "USER_PERSPECTIVE"}]
    assert handler.object_id_calls == [
        {"object_names": ["Housing"], "width": 1280, "height": 960, "camera_name": "USER_PERSPECTIVE"}
    ]
    assert tmp_path.joinpath("internal", "blender-ai-mcp", "bundle_aux_after_target_front_depth.png").exists()
    assert tmp_path.joinpath("internal", "blender-ai-mcp", "bundle_aux_after_target_front_normal.png").exists()
    front = next(capture for capture in captures if capture.label == "target_front_after")
    object_id_aux = next(capture for capture in captures if capture.view_kind == "object_id")
    assert front.object_id_artifact is not None
    assert object_id_aux.image_path == front.object_id_artifact.image_path


def test_capture_stage_images_can_append_mark_overlay_capture(tmp_path, monkeypatch):
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    handler = _OverlayHandler()
    captures = capture_stage_images(
        handler,
        bundle_id="bundle_mark",
        stage="after",
        target_objects=["Head", "Body"],
        preset_profile="compact",
        include_mark_overlay=True,
        mark_overlay_preset_names={"target_front"},
    )

    assert [capture.label for capture in captures] == [
        "context_wide_after",
        "target_front_after",
        "target_front_after_overlay",
        "target_side_after",
        "target_top_after",
        "target_oblique_left_after",
    ]
    overlay = next(capture for capture in captures if capture.view_kind == "overlay")
    assert overlay.preset_name == "target_front"
    assert overlay.media_type == "image/jpeg"
    assert overlay.host_visible_path is not None
    assert [(mark.mark_id, mark.object_name, mark.status) for mark in overlay.overlay_marks] == [
        (1, "Body", "placed"),
        (2, "Head", "placed"),
    ]
    assert tmp_path.joinpath("internal", "blender-ai-mcp", "bundle_mark_after_target_front_overlay.jpg").exists()


def test_capture_stage_images_uses_supplied_stable_mark_id_map(tmp_path, monkeypatch):
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    captures = capture_stage_images(
        _OverlayHandler(),
        bundle_id="bundle_stable_mark",
        stage="after",
        target_objects=["Head", "Body"],
        preset_profile="compact",
        include_mark_overlay=True,
        mark_overlay_preset_names={"target_front"},
        mark_id_map={"Body": 4, "Head": 9},
    )

    overlay = next(capture for capture in captures if capture.view_kind == "overlay")
    assert [(mark.mark_id, mark.object_name, mark.status) for mark in overlay.overlay_marks] == [
        (4, "Body", "placed"),
        (9, "Head", "placed"),
    ]


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

    assert len(captures) == 5
    assert handler.isolate_calls == [
        ["Squirrel_Head", "Squirrel_Body", "Squirrel_Tail"],
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
    assert bundle.preset_names == [
        "context_wide",
        "target_front",
        "target_oblique_left",
        "target_side",
        "target_top",
    ]
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

    assert len(handler.restore_view_state_calls) == 5
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


class _FailingObjectIdHandler(_Handler):
    def get_object_id_pass(self, object_names, width=1024, height=768, camera_name=None):
        self.object_id_calls.append(
            {
                "object_names": list(object_names),
                "width": width,
                "height": height,
                "camera_name": camera_name,
            }
        )
        return "No camera available. Object-ID pass requires a scene camera or explicit camera_name."


class _FailingViewHandler(_Handler):
    """Handler whose set_standard_view returns a headless failure marker string."""

    def set_standard_view(self, view_name: str):
        self.standard_view_calls.append(view_name)
        return "No 3D viewport found. Standard view requires an active 3D view."


def test_capture_records_capture_ok_true_on_success_strings(tmp_path, monkeypatch):
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    captures = capture_stage_images(_Handler(), bundle_id="b", stage="after", target_object="Housing")

    # Success-confirmation strings ("view ok"/"focus ok"/"orbit ok") are not failures.
    assert captures, "expected at least one capture"
    assert all(c.capture_ok is True for c in captures)
    assert all(c.capture_warning is None for c in captures)


def test_capture_flags_failed_view_op_without_aborting(tmp_path, monkeypatch):
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    captures = capture_stage_images(_FailingViewHandler(), bundle_id="b", stage="after", target_object="Housing")

    # The capture still completes (image written) but the failed framing is recorded.
    flagged = [
        c
        for c in captures
        if c.preset_name and c.preset_name.startswith("target_") and c.preset_name != "target_oblique_left"
    ]
    assert flagged, "expected target presets that use set_standard_view"
    for capture in flagged:
        assert capture.capture_ok is False
        assert capture.capture_warning is not None
        assert "set_standard_view" in capture.capture_warning
        assert "no 3d viewport found" in capture.capture_warning.lower()


def test_capture_records_object_id_sidecar_failure_without_failing_primary_capture(tmp_path, monkeypatch):
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    captures = capture_stage_images(
        _FailingObjectIdHandler(),
        bundle_id="boid",
        stage="after",
        target_object="Housing",
        include_object_id_pass=True,
        object_id_preset_names={"target_front"},
    )

    front = next(capture for capture in captures if capture.preset_name == "target_front")
    assert front.capture_ok is True
    assert front.capture_warning is None
    assert front.object_id_artifact is not None
    assert front.object_id_artifact.capture_ok is False
    assert front.object_id_artifact.image_path is None
    assert "No camera available" in str(front.object_id_artifact.capture_warning)


def test_build_capture_bundle_aggregates_capture_warnings(tmp_path, monkeypatch):
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    handler = _FailingViewHandler()
    before = capture_stage_images(handler, bundle_id="bw", stage="before", target_object="Housing")
    after = capture_stage_images(handler, bundle_id="bw", stage="after", target_object="Housing")
    bundle = build_capture_bundle(
        bundle_id="bw",
        target_object="Housing",
        captures_before=before,
        captures_after=after,
    )

    assert bundle.capture_warnings, "expected aggregated capture warnings"
    assert all("set_standard_view" in w for w in bundle.capture_warnings)
    # Clean handler yields an empty warnings list.
    clean_bundle = build_capture_bundle(
        bundle_id="bc",
        target_object="Housing",
        captures_before=capture_stage_images(_Handler(), bundle_id="bc", stage="before", target_object="Housing"),
        captures_after=capture_stage_images(_Handler(), bundle_id="bc", stage="after", target_object="Housing"),
    )
    assert clean_bundle.capture_warnings == []
