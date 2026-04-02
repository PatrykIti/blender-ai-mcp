from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

from server.adapters.mcp.contracts.macro import MacroExecutionReportContract


def test_macro_adjust_tail_arc_mcp_tool_returns_structured_contract(monkeypatch):
    from server.adapters.mcp.areas.scene import macro_adjust_tail_arc

    class Handler:
        def adjust_tail_arc(self, **kwargs):
            return {
                "status": "success",
                "macro_name": "macro_adjust_tail_arc",
                "intent": "Adjust tail arc",
                "actions_taken": [
                    {"status": "applied", "action": "adjust_tail_arc", "tool_name": "modeling_transform_object"}
                ],
                "objects_modified": list(kwargs.get("segment_objects", [])[1:]),
                "verification_recommended": [
                    {"tool_name": "inspect_scene", "reason": "Verify the updated tail arc after the move."}
                ],
                "requires_followup": True,
            }

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_macro_handler", lambda: Handler())

    result = asyncio.run(
        macro_adjust_tail_arc(
            MagicMock(),
            segment_objects=["Tail_01", "Tail_02", "Tail_03"],
        )
    )

    assert isinstance(result, MacroExecutionReportContract)
    assert result.macro_name == "macro_adjust_tail_arc"
    assert result.actions_taken[0].action == "adjust_tail_arc"
