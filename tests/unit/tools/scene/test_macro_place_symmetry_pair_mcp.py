from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

from server.adapters.mcp.contracts.macro import MacroExecutionReportContract


def test_macro_place_symmetry_pair_mcp_tool_returns_structured_contract(monkeypatch):
    from server.adapters.mcp.areas.scene import macro_place_symmetry_pair

    class Handler:
        def place_symmetry_pair(self, **kwargs):
            return {
                "status": "success",
                "macro_name": "macro_place_symmetry_pair",
                "intent": "Place mirrored pair 'Ear_L' / 'Ear_R'",
                "actions_taken": [
                    {"status": "applied", "action": "place_symmetry_pair", "tool_name": "modeling_transform_object"}
                ],
                "objects_modified": [kwargs.get("right_object", "Ear_R")],
                "verification_recommended": [
                    {"tool_name": "scene_assert_symmetry", "reason": "Confirm mirrored placement after the move."}
                ],
                "requires_followup": True,
            }

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_macro_handler", lambda: Handler())

    result = asyncio.run(
        macro_place_symmetry_pair(
            MagicMock(),
            left_object="Ear_L",
            right_object="Ear_R",
        )
    )

    assert isinstance(result, MacroExecutionReportContract)
    assert result.macro_name == "macro_place_symmetry_pair"
    assert result.actions_taken[0].action == "place_symmetry_pair"
