from __future__ import annotations

import base64

from server.application.tool_handlers.macro_handler import MacroToolHandler


class FakeSceneTool:
    def __init__(self) -> None:
        self.viewport_calls: list[dict] = []

    def get_viewport(self, width=1024, height=768, shading="SOLID", camera_name=None, focus_target=None):
        self.viewport_calls.append(
            {
                "width": width,
                "height": height,
                "shading": shading,
                "camera_name": camera_name,
                "focus_target": focus_target,
            }
        )
        return base64.b64encode(b"fake-jpeg").decode("ascii")

    def measure_dimensions(self, object_name, world_space=True):
        return {"object_name": object_name, "world_space": world_space, "dimensions": [1.0, 2.0, 3.0]}

    def get_bounding_box(self, object_name, world_space=True):
        return {
            "object_name": object_name,
            "world_space": world_space,
            "min": [0.0, 0.0, 0.0],
            "max": [1.0, 2.0, 3.0],
            "center": [0.5, 1.0, 1.5],
            "dimensions": [1.0, 2.0, 3.0],
        }


class FakeModelingTool:
    def __init__(self):
        self.calls: list[tuple[str, dict]] = []
        self._modifiers: dict[str, list[dict[str, str]]] = {}

    def add_modifier(self, name, modifier_type, properties=None):
        current = self._modifiers.setdefault(name, [])
        modifier_name = modifier_type if not current else f"{modifier_type}.{len(current):03d}"
        current.append({"name": modifier_name, "type": modifier_type})
        self.calls.append(
            ("add_modifier", {"name": name, "modifier_type": modifier_type, "properties": properties or {}})
        )
        return f"Added modifier '{modifier_type}' to '{name}'"

    def get_modifiers(self, name):
        return list(self._modifiers.get(name, []))


def test_macro_finish_form_attaches_capture_bundle_when_vision_enabled(monkeypatch, tmp_path):
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))
    monkeypatch.setattr(
        "server.application.tool_handlers.macro_handler.get_config",
        lambda: type("Cfg", (), {"VISION_ENABLED": True})(),
    )

    scene = FakeSceneTool()
    handler = MacroToolHandler(scene, FakeModelingTool())

    result = handler.finish_form(
        target_object="BodyShell",
        preset="rounded_housing",
    )

    assert result["status"] == "success"
    assert "capture_bundle" in result
    bundle = result["capture_bundle"]
    assert bundle["target_object"] == "BodyShell"
    assert bundle["preset_names"] == ["context_wide", "target_front", "target_side", "target_top"]
    assert len(bundle["captures_before"]) == 4
    assert len(bundle["captures_after"]) == 4
    assert bundle["truth_summary"]["dimensions"]["dimensions"] == [1.0, 2.0, 3.0]
    assert scene.viewport_calls[0]["focus_target"] is None
    assert scene.viewport_calls[1]["focus_target"] == "BodyShell"
    assert scene.viewport_calls[2]["focus_target"] == "BodyShell"
    assert scene.viewport_calls[3]["focus_target"] == "BodyShell"
