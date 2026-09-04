from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

from server.adapters.mcp.contracts.macro import MacroExecutionReportContract


def test_macro_align_part_with_contact_mcp_tool_returns_structured_contract(monkeypatch):
    from server.adapters.mcp.areas.scene import macro_align_part_with_contact

    class Handler:
        def align_part_with_contact(self, **kwargs):
            return {
                "status": "success",
                "macro_name": "macro_align_part_with_contact",
                "intent": "Repair 'Ear' relative to 'Head'",
                "actions_taken": [
                    {
                        "status": "applied",
                        "action": "align_part_with_contact",
                        "tool_name": "modeling_transform_object",
                    },
                    {
                        "status": "applied",
                        "action": "evaluate_attachment_outcome",
                        "tool_name": "scene_assert_contact",
                        "details": {"attachment_verdict": "seated_contact"},
                    },
                ],
                "objects_modified": [kwargs.get("part_object", "Ear")],
                "verification_recommended": [
                    {"tool_name": "scene_measure_gap", "reason": "Confirm repaired contact after nudge."}
                ],
                "requires_followup": True,
            }

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_macro_handler", lambda: Handler())

    result = asyncio.run(
        macro_align_part_with_contact(
            MagicMock(),
            part_object="Ear",
            reference_object="Head",
        )
    )

    assert isinstance(result, MacroExecutionReportContract)
    assert result.macro_name == "macro_align_part_with_contact"
    assert result.actions_taken[0].action == "align_part_with_contact"
    assert result.actions_taken[-1].details["attachment_verdict"] == "seated_contact"
