from __future__ import annotations

from server.application.tool_handlers.macro_handler import MacroToolHandler


class FakeSceneTool:
    def __init__(self):
        self.hidden: list[tuple[str, bool, bool]] = []
        self.deleted: list[str] = []

    def list_objects(self):
        return [{"name": "BodyShell"}]

    def get_bounding_box(self, object_name, world_space=True):
        return {
            "object_name": object_name,
            "min": [-1.0, -0.5, -2.0],
            "max": [1.0, 0.5, 2.0],
            "center": [0.0, 0.0, 0.0],
            "dimensions": [2.0, 1.0, 4.0],
        }

    def delete_object(self, name):
        self.deleted.append(name)
        return f"Successfully deleted object: {name}"

    def hide_object(self, object_name, hide=True, hide_render=False):
        self.hidden.append((object_name, hide, hide_render))
        return "hidden"


class FakeModelingTool:
    def __init__(self):
        self.calls: list[tuple[str, dict]] = []
        self._modifiers: dict[str, list[dict[str, str]]] = {}

    def create_primitive(self, primitive_type, radius=1.0, size=2.0, location=(0, 0, 0), rotation=(0, 0, 0), name=None):
        self.calls.append(
            (
                "create_primitive",
                {
                    "primitive_type": primitive_type,
                    "size": size,
                    "location": location,
                    "rotation": rotation,
                    "name": name,
                },
            )
        )
        self._modifiers.setdefault(name, [])
        return f"Created {primitive_type} named '{name}'"

    def transform_object(self, name, location=None, rotation=None, scale=None):
        self.calls.append(
            ("transform_object", {"name": name, "location": location, "rotation": rotation, "scale": scale})
        )
        return f"Transformed object '{name}'"

    def add_modifier(self, name, modifier_type, properties=None):
        current = self._modifiers.setdefault(name, [])
        modifier_name = modifier_type if not current else f"{modifier_type}.{len(current):03d}"
        current.append({"name": modifier_name, "type": modifier_type})
        self.calls.append(
            ("add_modifier", {"name": name, "modifier_type": modifier_type, "properties": properties or {}})
        )
        return f"Added modifier '{modifier_type}' to '{name}'"

    def apply_modifier(self, name, modifier_name):
        self.calls.append(("apply_modifier", {"name": name, "modifier_name": modifier_name}))
        return f"Applied modifier '{modifier_name}' to '{name}'"

    def get_modifiers(self, name):
        return list(self._modifiers.get(name, []))


def test_macro_cutout_recess_builds_bounded_boolean_sequence():
    scene = FakeSceneTool()
    modeling = FakeModelingTool()
    handler = MacroToolHandler(scene, modeling)

    result = handler.cutout_recess(
        target_object="BodyShell",
        width=0.8,
        height=1.2,
        depth=0.2,
        face="front",
        offset=[0.0, 0.0, 0.3],
        mode="recess",
        bevel_width=0.01,
        bevel_segments=3,
        cleanup="hide",
        cutter_name="ScreenSeatCutter",
    )

    assert result["status"] == "success"
    assert result["macro_name"] == "macro_cutout_recess"
    assert result["objects_modified"] == ["BodyShell"]
    assert result["requires_followup"] is True
    assert result["verification_recommended"][0]["tool_name"] == "inspect_scene"
    assert scene.hidden == [("ScreenSeatCutter", True, True)]

    create_call = modeling.calls[0]
    transform_call = modeling.calls[1]
    assert create_call[0] == "create_primitive"
    assert create_call[1]["name"] == "ScreenSeatCutter"
    assert transform_call[1]["scale"] == [0.4, 0.1, 0.6]


def test_macro_cutout_recess_cut_through_uses_target_thickness():
    scene = FakeSceneTool()
    modeling = FakeModelingTool()
    handler = MacroToolHandler(scene, modeling)

    result = handler.cutout_recess(
        target_object="BodyShell",
        width=0.8,
        height=1.2,
        depth=0.2,
        face="front",
        mode="cut_through",
        cleanup="delete",
        cutter_name="ThroughCut",
    )

    assert result["status"] == "success"
    assert scene.deleted == ["ThroughCut"]
    transform_call = modeling.calls[1]
    assert transform_call[1]["scale"] == [0.4, 0.501, 0.6]


def test_macro_cutout_recess_rejects_invalid_recess_depth():
    scene = FakeSceneTool()
    modeling = FakeModelingTool()
    handler = MacroToolHandler(scene, modeling)

    try:
        handler.cutout_recess(
            target_object="BodyShell",
            width=0.8,
            height=1.2,
            depth=1.0,
            face="front",
            mode="recess",
        )
    except ValueError as exc:
        assert "recess depth" in str(exc)
    else:
        raise AssertionError("Expected invalid recess depth to raise")
