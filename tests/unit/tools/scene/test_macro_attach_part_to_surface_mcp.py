from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

from server.adapters.mcp.contracts.macro import MacroExecutionReportContract


def test_macro_attach_part_to_surface_mcp_tool_returns_structured_contract(monkeypatch):
    from server.adapters.mcp.areas.scene import macro_attach_part_to_surface

    class Handler:
        def attach_part_to_surface(self, **kwargs):
            return {
                "status": "success",
                "macro_name": "macro_attach_part_to_surface",
                "intent": "Attach 'Ear' to the positive X surface of 'Head'",
                "actions_taken": [
                    {"status": "applied", "action": "attach_part_to_surface", "tool_name": "modeling_transform_object"}
                ],
                "objects_modified": [kwargs.get("part_object", "Ear")],
                "verification_recommended": [
                    {"tool_name": "scene_measure_gap", "reason": "Confirm seating/contact after attach."}
                ],
                "requires_followup": True,
            }

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_macro_handler", lambda: Handler())

    result = asyncio.run(
        macro_attach_part_to_surface(
            MagicMock(),
            part_object="Ear",
            surface_object="Head",
            surface_axis="X",
        )
    )

    assert isinstance(result, MacroExecutionReportContract)
    assert result.macro_name == "macro_attach_part_to_surface"
    assert result.actions_taken[0].action == "attach_part_to_surface"
