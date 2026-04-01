from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

from server.adapters.mcp.contracts.macro import MacroExecutionReportContract


def test_macro_finish_form_mcp_tool_returns_structured_contract(monkeypatch):
    from server.adapters.mcp.areas.modeling import _macro_finish_form_impl

    class Handler:
        def finish_form(self, **kwargs):
            return {
                "status": "success",
                "macro_name": "macro_finish_form",
                "intent": "apply rounded_housing finishing preset",
                "actions_taken": [
                    {"status": "applied", "action": "add_bevel_finish", "tool_name": "modeling_add_modifier"}
                ],
                "objects_modified": [kwargs.get("target_object", "BodyShell")],
                "verification_recommended": [{"tool_name": "inspect_scene", "reason": "Verify the finishing stack."}],
                "requires_followup": True,
            }

    monkeypatch.setattr("server.adapters.mcp.areas.modeling.get_macro_handler", lambda: Handler())

    result = asyncio.run(
        _macro_finish_form_impl(
            MagicMock(),
            target_object="BodyShell",
            preset="rounded_housing",
        )
    )

    assert isinstance(result, MacroExecutionReportContract)
    assert result.macro_name == "macro_finish_form"
    assert result.actions_taken[0].action == "add_bevel_finish"
