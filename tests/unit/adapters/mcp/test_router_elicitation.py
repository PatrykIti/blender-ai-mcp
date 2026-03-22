"""Tests for router-side native elicitation integration."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from fastmcp.server.context import AcceptedElicitation, CancelledElicitation, DeclinedElicitation

from server.adapters.mcp.areas import router as router_area
from server.adapters.mcp.elicitation_contracts import build_elicitation_response_type
from server.adapters.mcp.session_capabilities import get_session_capability_state


@dataclass
class FakeContext:
    """Minimal async Context-like object for elicitation tests."""

    response: object
    calls: list[tuple[str, object]] = field(default_factory=list)
    state: dict[str, object] = field(default_factory=dict)

    async def elicit(self, message: str, response_type=None):
        self.calls.append((message, response_type))
        return self.response

    def get_state(self, key: str):
        return self.state.get(key)

    def set_state(self, key: str, value, *, serializable: bool = True):
        self.state[key] = value

    async def reset_visibility(self):
        return None

    async def enable_components(self, **kwargs):
        return None

    async def disable_components(self, **kwargs):
        return None

    async def info(self, message: str, logger_name=None, extra=None):
        return None


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


def test_router_set_goal_cancel_persists_pending_elicitation_state(monkeypatch):
    """Cancelled elicitation should keep pending state for the next request."""

    monkeypatch.setattr(router_area, "get_config", lambda: type("Cfg", (), {"MCP_SURFACE_PROFILE": "llm-guided"})())

    class Handler:
        def set_goal(self, goal, resolved_params=None):
            return {
                "status": "needs_input",
                "workflow": "chair_workflow",
                "resolved": {},
                "unresolved": [{"param": "height", "type": "float", "description": "Overall height"}],
                "resolution_sources": {},
                "message": "need height",
            }

        def clear_goal(self):
            return "cleared"

    monkeypatch.setattr(router_area, "get_router_handler", lambda: Handler())

    ctx = FakeContext(response=CancelledElicitation())
    result = asyncio.run(router_area.router_set_goal(ctx, goal="chair"))

    session = get_session_capability_state(ctx)
    assert result.status == "needs_input"
    assert result.elicitation_action == "cancel"
    assert session.pending_question_set_id is not None
    assert session.pending_workflow_name == "chair_workflow"
    assert session.last_elicitation_action == "cancel"


def test_router_set_goal_merges_partial_answers_on_followup(monkeypatch):
    """Persisted partial answers should be merged with the next resolved_params call."""

    monkeypatch.setattr(router_area, "get_config", lambda: type("Cfg", (), {"MCP_SURFACE_PROFILE": "legacy-flat"})())

    calls: list[dict[str, object] | None] = []

    class Handler:
        def set_goal(self, goal, resolved_params=None):
            calls.append(resolved_params)
            if resolved_params is None or "height" not in resolved_params:
                return {
                    "status": "needs_input",
                    "workflow": "chair_workflow",
                    "resolved": {"width": 1.0},
                    "unresolved": [{"param": "height", "type": "float", "description": "Overall height"}],
                    "resolution_sources": {"width": "user"},
                    "message": "need height",
                }
            return {
                "status": "ready",
                "workflow": "chair_workflow",
                "resolved": resolved_params,
                "unresolved": [],
                "resolution_sources": {"width": "user", "height": "user"},
                "message": "ok",
                "executed": 0,
            }

        def clear_goal(self):
            return "cleared"

    monkeypatch.setattr(router_area, "get_router_handler", lambda: Handler())

    ctx = FakeContext(response=DeclinedElicitation())
    first = asyncio.run(router_area.router_set_goal(ctx, goal="chair", resolved_params={"width": 1.0}))
    second = asyncio.run(router_area.router_set_goal(ctx, goal="chair", resolved_params={"height": 2.0}))

    assert first.status == "needs_input"
    assert second.status == "ready"
    assert calls[0] == {"width": 1.0}
    assert calls[1] == {"width": 1.0, "height": 2.0}


def test_router_set_goal_reuses_question_set_id_after_cancel(monkeypatch):
    """A cancelled clarification should reuse the same pending question-set id on retry."""

    monkeypatch.setattr(router_area, "get_config", lambda: type("Cfg", (), {"MCP_SURFACE_PROFILE": "legacy-flat"})())

    class Handler:
        def set_goal(self, goal, resolved_params=None):
            return {
                "status": "needs_input",
                "workflow": "chair_workflow",
                "resolved": {},
                "unresolved": [{"param": "height", "type": "float", "description": "Overall height"}],
                "resolution_sources": {},
                "message": "need height",
            }

        def clear_goal(self):
            return "cleared"

    monkeypatch.setattr(router_area, "get_router_handler", lambda: Handler())

    ctx = FakeContext(response=CancelledElicitation())
    first = asyncio.run(router_area.router_set_goal(ctx, goal="chair"))
    second = asyncio.run(router_area.router_set_goal(ctx, goal="chair"))

    assert first.clarification.question_set_id == second.clarification.question_set_id
