from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

from server.adapters.mcp.contracts.macro import MacroExecutionReportContract


def test_macro_adjust_head_body_proportion_mcp_tool_returns_structured_contract(monkeypatch):
    from server.adapters.mcp.areas.scene import macro_adjust_head_body_proportion

    class Handler:
        def adjust_head_body_proportion(self, **kwargs):
            return {
                "status": "success",
                "macro_name": "macro_adjust_head_body_proportion",
                "intent": "Repair head/body proportion",
                "actions_taken": [
                    {
                        "status": "applied",
                        "action": "adjust_head_body_proportion",
                        "tool_name": "modeling_transform_object",
                    }
                ],
                "objects_modified": [kwargs.get("head_object", "Head")],
                "verification_recommended": [
                    {"tool_name": "scene_assert_proportion", "reason": "Confirm repaired ratio after scaling."}
                ],
                "requires_followup": True,
            }

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_macro_handler", lambda: Handler())

    result = asyncio.run(
        macro_adjust_head_body_proportion(
            MagicMock(),
            head_object="Head",
            body_object="Body",
            expected_ratio=0.4,
        )
    )

    assert isinstance(result, MacroExecutionReportContract)
    assert result.macro_name == "macro_adjust_head_body_proportion"
    assert result.actions_taken[0].action == "adjust_head_body_proportion"
