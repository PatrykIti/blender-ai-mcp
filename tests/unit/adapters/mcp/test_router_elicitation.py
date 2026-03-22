"""Tests for router-side native elicitation integration."""

from __future__ import annotations

from dataclasses import dataclass, field

from fastmcp.server.context import AcceptedElicitation, DeclinedElicitation

from server.adapters.mcp.areas import router as router_area
from server.adapters.mcp.elicitation_contracts import build_elicitation_response_type


@dataclass
class FakeContext:
    """Minimal async Context-like object for elicitation tests."""

    response: object
    calls: list[tuple[str, object]] = field(default_factory=list)

    async def elicit(self, message: str, response_type=None):
        self.calls.append((message, response_type))
        return self.response


def test_maybe_elicit_router_answers_accepts_and_extracts_answers(monkeypatch):
    """llm-guided native elicitation should capture accepted answers."""

    monkeypatch.setattr(router_area, "get_config", lambda: type("Cfg", (), {"MCP_SURFACE_PROFILE": "llm-guided"})())

    initial = {
        "status": "needs_input",
        "workflow": "chair_workflow",
        "unresolved": [{"param": "height", "type": "float", "description": "Overall height"}],
    }
    response_type = build_elicitation_response_type(
        router_area.build_clarification_plan("chair", "chair_workflow", initial["unresolved"])
    )
    ctx = FakeContext(response=AcceptedElicitation(data=response_type(height=1.25)))

    result = __import__("asyncio").run(router_area._maybe_elicit_router_answers(ctx, "chair", initial))

    assert result["elicitation_action"] == "accept"
    assert result["elicitation_answers"] == {"height": 1.25}
    assert "clarification" in result


def test_maybe_elicit_router_answers_decline_keeps_fallback_payload(monkeypatch):
    """Declined elicitation should preserve typed fallback clarification data."""

    monkeypatch.setattr(router_area, "get_config", lambda: type("Cfg", (), {"MCP_SURFACE_PROFILE": "llm-guided"})())

    initial = {
        "status": "needs_input",
        "workflow": "chair_workflow",
        "unresolved": [{"param": "leg_style", "type": "string", "description": "Leg style"}],
    }
    ctx = FakeContext(response=DeclinedElicitation())

    result = __import__("asyncio").run(router_area._maybe_elicit_router_answers(ctx, "chair", initial))

    assert result["elicitation_action"] == "decline"
    assert "clarification" in result
