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
                    {"status": "applied", "action": "attach_part_to_surface", "tool_name": "modeling_transform_object"},
                    {
                        "status": "applied",
                        "action": "evaluate_attachment_outcome",
                        "tool_name": "scene_assert_contact",
                        "details": {"attachment_verdict": "seated_contact"},
                    },
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
            align_mode="none",
        )
    )

    assert isinstance(result, MacroExecutionReportContract)
    assert result.macro_name == "macro_attach_part_to_surface"
    assert result.actions_taken[0].action == "attach_part_to_surface"
    assert result.actions_taken[-1].details["attachment_verdict"] == "seated_contact"


def test_macro_attach_part_to_surface_mcp_preserves_routed_partial_report_with_error(monkeypatch):
    from server.adapters.mcp.areas.scene import macro_attach_part_to_surface

    partial_report = {
        "status": "partial",
        "macro_name": "macro_attach_part_to_surface",
        "intent": "Attach 'Ear' to 'Head'",
        "actions_taken": [
            {
                "status": "applied",
                "action": "bounded_mesh_surface_nudge",
                "tool_name": "modeling_transform_object",
                "details": {"delta": [0.05, 0.0, 0.0]},
            },
            {
                "status": "applied",
                "action": "evaluate_attachment_outcome",
                "tool_name": "scene_assert_contact",
                "details": {"attachment_verdict": "floating_gap"},
            },
        ],
        "objects_modified": ["Ear"],
        "verification_recommended": [
            {"tool_name": "scene_measure_gap", "reason": "Confirm the remaining mesh-surface gap."}
        ],
        "requires_followup": True,
        "error": "The bounded seating move completed, but the pair is still not seated/attached correctly.",
    }

    async def route_tool_call_async(*args, **kwargs):
        return partial_report

    monkeypatch.setattr("server.adapters.mcp.areas.scene.route_tool_call_async", route_tool_call_async)

    result = asyncio.run(
        macro_attach_part_to_surface(
            MagicMock(),
            part_object="Ear",
            surface_object="Head",
            surface_axis="X",
        )
    )

    assert result.status == "partial"
    assert result.error == partial_report["error"]
    assert result.objects_modified == ["Ear"]
    assert result.requires_followup is True
    assert result.actions_taken[0].action == "bounded_mesh_surface_nudge"
    assert result.actions_taken[-1].details["attachment_verdict"] == "floating_gap"
    assert result.verification_recommended[0].tool_name == "scene_measure_gap"


def test_macro_attach_part_to_surface_mcp_tool_accepts_none_alignment(monkeypatch):
    from server.adapters.mcp.areas.scene import macro_attach_part_to_surface

    captured = {}

    class Handler:
        def attach_part_to_surface(self, **kwargs):
            captured.update(kwargs)
            return {
                "status": "success",
                "macro_name": "macro_attach_part_to_surface",
                "intent": "Attach while preserving offsets",
                "actions_taken": [],
                "objects_modified": [kwargs["part_object"]],
                "requires_followup": True,
            }

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_macro_handler", lambda: Handler())

    result = asyncio.run(
        macro_attach_part_to_surface(
            MagicMock(),
            part_object="ForeLeg_L",
            surface_object="Body",
            surface_axis="Y",
            surface_side="positive",
            align_mode="none",
        )
    )

    assert result.status == "success"
    assert captured["align_mode"] == "none"
