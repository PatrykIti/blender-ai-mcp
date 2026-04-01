from __future__ import annotations

from server.application.tool_handlers.macro_handler import MacroToolHandler


class FakeSceneTool:
    pass


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


def test_macro_finish_form_builds_rounded_housing_stack():
    handler = MacroToolHandler(FakeSceneTool(), FakeModelingTool())

    result = handler.finish_form(
        target_object="BodyShell",
        preset="rounded_housing",
        bevel_width=0.02,
        bevel_segments=4,
        subsurf_levels=2,
    )

    assert result["status"] == "success"
    assert result["macro_name"] == "macro_finish_form"
    assert result["objects_modified"] == ["BodyShell"]
    assert result["requires_followup"] is True
    assert [item["action"] for item in result["actions_taken"][:2]] == [
        "add_bevel_finish",
        "add_subdivision_finish",
    ]
    stack_details = result["actions_taken"][-1]["details"]["modifier_stack"]
    assert [item["type"] for item in stack_details] == ["BEVEL", "SUBSURF"]


def test_macro_finish_form_builds_shell_thicken_stack():
    modeling = FakeModelingTool()
    handler = MacroToolHandler(FakeSceneTool(), modeling)

    result = handler.finish_form(
        target_object="Panel",
        preset="shell_thicken",
        thickness=0.08,
        solidify_offset=-1.0,
    )

    assert result["status"] == "success"
    assert len(modeling.calls) == 1
    assert modeling.calls[0][1]["modifier_type"] == "SOLIDIFY"
    assert modeling.calls[0][1]["properties"] == {"thickness": 0.08, "offset": -1.0}
    assert any(item["tool_name"] == "scene_measure_dimensions" for item in result["verification_recommended"])


def test_macro_finish_form_rejects_invalid_override_for_panel_finish():
    handler = MacroToolHandler(FakeSceneTool(), FakeModelingTool())

    try:
        handler.finish_form(
            target_object="Panel",
            preset="panel_finish",
            thickness=0.05,
        )
    except ValueError as exc:
        assert "thickness override" in str(exc)
    else:
        raise AssertionError("Expected invalid override to raise")
