from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

from server.adapters.mcp.contracts.macro import MacroExecutionReportContract


def test_macro_place_supported_pair_mcp_tool_returns_structured_contract(monkeypatch):
    from server.adapters.mcp.areas.scene import macro_place_supported_pair

    class Handler:
        def place_supported_pair(self, **kwargs):
            return {
                "status": "success",
                "macro_name": "macro_place_supported_pair",
                "intent": "Place supported pair 'Foot_L' / 'Foot_R' on 'Floor'",
                "actions_taken": [
                    {
                        "status": "applied",
                        "action": "place_supported_pair_anchor",
                        "tool_name": "modeling_transform_object",
                    }
                ],
                "objects_modified": [
                    kwargs.get("left_object", "Foot_L"),
                    kwargs.get("right_object", "Foot_R"),
                ],
                "verification_recommended": [
                    {"tool_name": "scene_assert_contact", "reason": "Confirm support contact after placement."}
                ],
                "requires_followup": True,
            }

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_macro_handler", lambda: Handler())

    result = asyncio.run(
        macro_place_supported_pair(
            MagicMock(),
            left_object="Foot_L",
            right_object="Foot_R",
            support_object="Floor",
        )
    )

    assert isinstance(result, MacroExecutionReportContract)
    assert result.macro_name == "macro_place_supported_pair"
    assert result.actions_taken[0].action == "place_supported_pair_anchor"
