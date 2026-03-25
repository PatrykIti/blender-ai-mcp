from __future__ import annotations

from unittest.mock import MagicMock

from server.adapters.mcp.contracts.macro import MacroExecutionReportContract


def test_macro_relative_layout_mcp_tool_returns_structured_contract(monkeypatch):
    from server.adapters.mcp.areas.scene import macro_relative_layout

    class Handler:
        def relative_layout(self, **kwargs):
            return {
                "status": "success",
                "macro_name": "macro_relative_layout",
                "intent": "layout 'Leg' relative to 'TableTop'",
                "actions_taken": [
                    {"status": "applied", "action": "apply_relative_layout", "tool_name": "modeling_transform_object"}
                ],
                "objects_modified": [kwargs.get("moving_object", "Leg")],
                "verification_recommended": [
                    {"tool_name": "scene_measure_gap", "reason": "Confirm contact/gap after layout."}
                ],
                "requires_followup": True,
            }

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_macro_handler", lambda: Handler())

    result = macro_relative_layout(
        MagicMock(),
        moving_object="Leg",
        reference_object="TableTop",
    )

    assert isinstance(result, MacroExecutionReportContract)
    assert result.macro_name == "macro_relative_layout"
    assert result.actions_taken[0].action == "apply_relative_layout"
