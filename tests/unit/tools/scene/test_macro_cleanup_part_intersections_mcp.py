from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

from server.adapters.mcp.contracts.macro import MacroExecutionReportContract


def test_macro_cleanup_part_intersections_mcp_tool_returns_structured_contract(monkeypatch):
    from server.adapters.mcp.areas.scene import macro_cleanup_part_intersections

    class Handler:
        def cleanup_part_intersections(self, **kwargs):
            return {
                "status": "success",
                "macro_name": "macro_cleanup_part_intersections",
                "intent": "Clean intersection between 'Horn' and 'Head'",
                "actions_taken": [
                    {
                        "status": "applied",
                        "action": "cleanup_part_intersections",
                        "tool_name": "modeling_transform_object",
                    }
                ],
                "objects_modified": [kwargs.get("part_object", "Horn")],
                "verification_recommended": [
                    {"tool_name": "scene_measure_overlap", "reason": "Confirm overlap is gone after cleanup."}
                ],
                "requires_followup": True,
            }

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_macro_handler", lambda: Handler())

    result = asyncio.run(
        macro_cleanup_part_intersections(
            MagicMock(),
            part_object="Horn",
            reference_object="Head",
        )
    )

    assert isinstance(result, MacroExecutionReportContract)
    assert result.macro_name == "macro_cleanup_part_intersections"
    assert result.actions_taken[0].action == "cleanup_part_intersections"
