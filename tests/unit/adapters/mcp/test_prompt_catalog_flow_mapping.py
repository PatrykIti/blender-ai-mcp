"""Tests for domain/step prompt bundle mapping in guided flow state."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from server.adapters.mcp.session_capabilities import (
    SessionCapabilityState,
    advance_guided_flow_from_iteration_async,
    set_session_capability_state,
    update_session_from_router_goal,
)
from server.adapters.mcp.session_phase import SessionPhase


@dataclass
class FakeContext:
    state: dict[str, object] = field(default_factory=dict)

    def get_state(self, key: str):
        return self.state.get(key)

    def set_state(self, key: str, value, *, serializable: bool = True):
        self.state[key] = value


def test_generic_flow_bundle_stays_minimal():
    ctx = FakeContext()

    state = update_session_from_router_goal(
        ctx,
        "block out a generic hard-surface housing",
        {
            "status": "ready",
            "phase_hint": "build",
            "guided_handoff": {
                "kind": "guided_manual_build",
                "target_phase": "build",
                "surface_profile": "llm-guided",
                "direct_tools": ["scene_create"],
                "supporting_tools": ["scene_scope_graph", "scene_relation_graph", "scene_view_diagnostics"],
                "discovery_tools": ["search_tools", "call_tool"],
                "workflow_import_recommended": False,
                "message": "Continue on the guided build surface.",
            },
        },
        surface_profile="llm-guided",
    )

    assert state.guided_flow_state is not None
    assert state.guided_flow_state["required_prompts"] == ["guided_session_start"]
    assert state.guided_flow_state["preferred_prompts"] == ["workflow_router_first"]


def test_creature_flow_bundle_includes_creature_prompt():
    ctx = FakeContext()

    state = update_session_from_router_goal(
        ctx,
        "create a low-poly squirrel matching front and side reference images",
        {
            "status": "ready",
            "phase_hint": "build",
            "guided_handoff": {
                "kind": "guided_manual_build",
                "recipe_id": "low_poly_creature_blockout",
                "target_phase": "build",
                "surface_profile": "llm-guided",
                "direct_tools": ["modeling_create_primitive"],
                "supporting_tools": ["scene_scope_graph", "scene_relation_graph", "scene_view_diagnostics"],
                "discovery_tools": ["search_tools", "call_tool"],
                "workflow_import_recommended": False,
                "message": "Continue on the guided creature blockout surface.",
            },
        },
        surface_profile="llm-guided",
    )

    assert state.guided_flow_state is not None
    assert state.guided_flow_state["required_prompts"] == [
        "guided_session_start",
        "reference_guided_creature_build",
    ]
    assert state.guided_flow_state["preferred_prompts"] == ["workflow_router_first"]


def test_understand_goal_step_adds_recommended_prompts_as_preferred_bundle():
    ctx = FakeContext()

    state = update_session_from_router_goal(
        ctx,
        "block out a generic hard-surface housing",
        {
            "status": "needs_input",
            "phase_hint": "planning",
            "guided_handoff": {
                "kind": "guided_manual_build",
                "target_phase": "build",
                "surface_profile": "llm-guided",
                "direct_tools": ["scene_create"],
                "supporting_tools": ["scene_scope_graph", "scene_view_diagnostics"],
                "discovery_tools": ["search_tools", "call_tool"],
                "workflow_import_recommended": False,
                "message": "Need more detail before the guided build surface can continue.",
            },
        },
        surface_profile="llm-guided",
    )

    assert state.guided_flow_state is not None
    assert state.guided_flow_state["current_step"] == "understand_goal"
    assert state.guided_flow_state["preferred_prompts"] == ["workflow_router_first", "recommended_prompts"]


def test_iteration_keeps_creature_bundle_when_switching_to_inspect_validate():
    ctx = FakeContext()
    set_session_capability_state(
        ctx,
        SessionCapabilityState(
            phase=SessionPhase.BUILD,
            guided_flow_state={
                "flow_id": "guided_creature_flow",
                "domain_profile": "creature",
                "current_step": "create_primary_masses",
                "completed_steps": ["understand_goal", "establish_spatial_context"],
                "required_checks": [],
                "required_prompts": ["guided_session_start", "reference_guided_creature_build"],
                "preferred_prompts": ["workflow_router_first"],
                "next_actions": ["continue_build"],
                "blocked_families": [],
                "step_status": "ready",
            },
        ),
    )

    state = asyncio.run(advance_guided_flow_from_iteration_async(ctx, loop_disposition="inspect_validate"))

    assert state.guided_flow_state is not None
    assert state.guided_flow_state["current_step"] == "inspect_validate"
    assert state.guided_flow_state["required_prompts"] == [
        "guided_session_start",
        "reference_guided_creature_build",
    ]
