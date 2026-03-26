"""Tests for deterministic capture runtime helpers."""

from __future__ import annotations

import base64

from server.adapters.mcp.vision import build_capture_bundle, capture_stage_images


class _Handler:
    def __init__(self) -> None:
        self.calls: list[dict] = []

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

    assert [capture.preset_name for capture in captures] == ["context_wide", "target_focus"]
    assert captures[0].view_kind == "wide"
    assert captures[1].view_kind == "focus"
    assert captures[0].host_visible_path is not None
    assert tmp_path.joinpath("internal", "blender-ai-mcp", "bundle1_before_context_wide.jpg").exists()
    assert tmp_path.joinpath("internal", "blender-ai-mcp", "bundle1_before_target_focus.jpg").exists()
    assert handler.calls[0]["focus_target"] is None
    assert handler.calls[1]["focus_target"] == "Housing"


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
    assert bundle.preset_names == ["context_wide", "target_focus"]
    assert bundle.truth_summary == {"dimensions": [1, 2, 3]}
