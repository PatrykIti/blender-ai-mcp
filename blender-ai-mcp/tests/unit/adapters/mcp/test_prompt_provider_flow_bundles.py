"""Tests for guided-flow prompt bundle exposure on the public prompt provider."""

from __future__ import annotations

import asyncio

from server.adapters.mcp.prompts import provider as prompt_provider
from server.adapters.mcp.prompts.rendering import render_recommended_prompts
from server.adapters.mcp.session_capabilities import SessionCapabilityState
from server.adapters.mcp.session_phase import SessionPhase


class FakePromptTarget:
    def __init__(self) -> None:
        self.prompts: dict[str, object] = {}

    def prompt(self, fn=None, *, name: str, **kwargs):
        self.prompts[name] = fn
        return fn


def test_render_recommended_prompts_includes_flow_bundle_sections():
    result = render_recommended_prompts(
        surface_profile="llm-guided",
        phase="build",
        goal="create a low-poly squirrel matching front and side reference images",
        guided_flow_state={
            "flow_id": "guided_creature_flow",
            "domain_profile": "creature",
            "current_step": "establish_spatial_context",
            "required_prompts": ["guided_session_start", "reference_guided_creature_build"],
            "preferred_prompts": ["workflow_router_first"],
        },
    )

    message = result.messages[0].content.text

    assert "## Required prompt bundle" in message
    assert "## Preferred prompt bundle" in message
    assert "domain `creature`" in message
    assert "step `establish_spatial_context`" in message
    assert result.meta["required_prompt_names"] == ["guided_session_start", "reference_guided_creature_build"]
    assert result.meta["preferred_prompt_names"] == ["workflow_router_first"]


def test_recommended_prompts_provider_reads_guided_flow_state_from_session(monkeypatch):
    target = FakePromptTarget()
    prompt_provider.register_prompt_assets(target)

    async def fake_get_session_capability_state_async(_ctx):
        return SessionCapabilityState(
            phase=SessionPhase.BUILD,
            goal="rebuild a tower facade from front and side references",
            surface_profile="llm-guided",
            guided_flow_state={
                "flow_id": "guided_building_flow",
                "domain_profile": "building",
                "current_step": "establish_spatial_context",
                "completed_steps": [],
                "required_checks": [],
                "required_prompts": ["guided_session_start"],
                "preferred_prompts": ["workflow_router_first"],
                "next_actions": ["run_required_checks"],
                "blocked_families": ["build"],
                "step_status": "blocked",
            },
        )

    monkeypatch.setattr(prompt_provider, "get_session_capability_state_async", fake_get_session_capability_state_async)
    render_fn = target.prompts["recommended_prompts"]

    result = asyncio.run(render_fn(ctx=object()))
    message = result.messages[0].content.text

    assert "domain `building`" in message
    assert "step `establish_spatial_context`" in message
    assert result.meta["domain_profile"] == "building"
    assert result.meta["required_prompt_names"] == ["guided_session_start"]
