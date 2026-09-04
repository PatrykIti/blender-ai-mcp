from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

from server.adapters.mcp.contracts.macro import MacroExecutionReportContract


def test_macro_cutout_recess_mcp_tool_returns_structured_contract(monkeypatch):
    from server.adapters.mcp.areas.modeling import _macro_cutout_recess_impl

    class Handler:
        def cutout_recess(self, **kwargs):
            return {
                "status": "success",
                "macro_name": "macro_cutout_recess",
                "intent": "recess cutout on BodyShell",
                "actions_taken": [
                    {"status": "applied", "action": "create_cutter", "tool_name": "modeling_create_primitive"}
                ],
                "objects_modified": ["BodyShell"],
                "verification_recommended": [
                    {
                        "tool_name": "inspect_scene",
                        "reason": "Verify the target object after the boolean cutout operation.",
                    }
                ],
                "requires_followup": True,
            }

    monkeypatch.setattr("server.adapters.mcp.areas.modeling.get_macro_handler", lambda: Handler())

    result = asyncio.run(
        _macro_cutout_recess_impl(
            MagicMock(),
            target_object="BodyShell",
            width=0.8,
            height=1.2,
            depth=0.2,
        )
    )

    assert isinstance(result, MacroExecutionReportContract)
    assert result.macro_name == "macro_cutout_recess"
    assert result.actions_taken[0].action == "create_cutter"


def test_macro_cutout_recess_mcp_tool_uses_async_route_helper(monkeypatch):
    from server.adapters.mcp.areas.modeling import _macro_cutout_recess_impl

    calls: list[str] = []
    routed_report = MacroExecutionReportContract(
        status="success",
        macro_name="macro_cutout_recess",
        intent="recess cutout on BodyShell",
        actions_taken=[],
        objects_modified=["BodyShell"],
        requires_followup=True,
    )

    def route_tool_call(*args, **kwargs):
        raise AssertionError("async macro tool should not call the sync route helper")

    async def route_tool_call_async(ctx, **kwargs):
        calls.append(kwargs["tool_name"])
        return routed_report

    monkeypatch.setattr("server.adapters.mcp.areas.modeling.route_tool_call", route_tool_call)
    monkeypatch.setattr("server.adapters.mcp.areas.modeling.route_tool_call_async", route_tool_call_async)

    result = asyncio.run(
        _macro_cutout_recess_impl(
            MagicMock(),
            target_object="BodyShell",
            width=0.8,
            height=1.2,
            depth=0.2,
        )
    )

    assert result is routed_report
    assert calls == ["macro_cutout_recess"]
