"""Tests for server-driven guided flow state helpers."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

import pytest
from server.adapters.mcp.contracts.guided_flow import GuidedFlowStateContract
from server.adapters.mcp.session_capabilities import (
    SessionCapabilityState,
    advance_guided_flow_from_iteration_async,
    get_session_capability_state,
    record_guided_flow_spatial_check_completion,
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

    async def reset_visibility(self) -> None:
        return None

    async def enable_components(self, **kwargs) -> None:
        return None

    async def disable_components(self, **kwargs) -> None:
        return None


def test_session_state_round_trips_guided_flow_state():
    ctx = FakeContext()
    state = SessionCapabilityState(
        phase=SessionPhase.PLANNING,
        guided_flow_state={
            "flow_id": "guided_generic_flow",
            "domain_profile": "generic",
            "current_step": "establish_spatial_context",
            "completed_steps": [],
            "required_checks": [
                {
                    "check_id": "scope_graph",
                    "tool_name": "scene_scope_graph",
                    "reason": "Establish the structural anchor and active object scope before broad edits.",
                    "status": "pending",
                    "priority": "high",
                }
            ],
            "required_prompts": ["guided_session_start"],
            "preferred_prompts": ["workflow_router_first"],
            "next_actions": ["run_required_checks"],
            "blocked_families": ["build", "late_refinement", "finish"],
            "allowed_families": ["spatial_context", "reference_context"],
            "step_status": "blocked",
        },
    )
    set_session_capability_state(ctx, state)

    restored = get_session_capability_state(ctx)
    assert restored.guided_flow_state is not None
    assert restored.guided_flow_state["current_step"] == "establish_spatial_context"
    assert restored.guided_flow_state["required_checks"][0]["tool_name"] == "scene_scope_graph"
    assert restored.guided_flow_state["allowed_families"] == ["spatial_context", "reference_context"]


def test_guided_flow_contract_accepts_allowed_families():
    contract = GuidedFlowStateContract(
        flow_id="guided_generic_flow",
        domain_profile="generic",
        current_step="create_primary_masses",
        allowed_families=["primary_masses", "reference_context"],
    )

    assert contract.allowed_families == ["primary_masses", "reference_context"]


def test_guided_flow_contract_rejects_unknown_allowed_family():
    with pytest.raises(Exception, match="allowed_families"):
        GuidedFlowStateContract(
            flow_id="guided_generic_flow",
            domain_profile="generic",
            current_step="create_primary_masses",
            allowed_families=["definitely_not_a_family"],
        )


def test_router_goal_creature_initializes_guided_flow_state():
    ctx = FakeContext()

    state = update_session_from_router_goal(
        ctx,
        "create a low-poly squirrel matching front and side reference images",
        {
            "status": "no_match",
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
    assert state.guided_flow_state["domain_profile"] == "creature"
    assert state.guided_flow_state["current_step"] == "establish_spatial_context"
    assert state.guided_flow_state["required_prompts"] == [
        "guided_session_start",
        "reference_guided_creature_build",
    ]


def test_router_goal_building_initializes_guided_flow_state():
    ctx = FakeContext()

    state = update_session_from_router_goal(
        ctx,
        "rebuild a low-poly tower facade from front and side references",
        {
            "status": "no_match",
            "phase_hint": "build",
            "guided_handoff": {
                "kind": "guided_manual_build",
                "target_phase": "build",
                "surface_profile": "llm-guided",
                "direct_tools": ["scene_create"],
                "supporting_tools": ["scene_scope_graph", "scene_view_diagnostics"],
                "discovery_tools": ["search_tools", "call_tool"],
                "workflow_import_recommended": False,
                "message": "Continue on the guided build surface.",
            },
        },
        surface_profile="llm-guided",
    )

    assert state.guided_flow_state is not None
    assert state.guided_flow_state["domain_profile"] == "building"
    assert state.guided_flow_state["required_prompts"] == ["guided_session_start"]
    assert [check["tool_name"] for check in state.guided_flow_state["required_checks"]] == [
        "scene_scope_graph",
        "scene_view_diagnostics",
    ]


def test_router_goal_ready_followup_advances_from_understand_goal_to_spatial_context():
    ctx = FakeContext()

    blocked_state = update_session_from_router_goal(
        ctx,
        "create a low-poly squirrel matching front and side reference images",
        {
            "status": "needs_input",
            "phase_hint": "planning",
            "guided_handoff": {
                "kind": "guided_manual_build",
                "recipe_id": "low_poly_creature_blockout",
                "target_phase": "build",
                "surface_profile": "llm-guided",
                "direct_tools": ["modeling_create_primitive"],
                "supporting_tools": ["scene_scope_graph", "scene_relation_graph", "scene_view_diagnostics"],
                "discovery_tools": ["search_tools", "call_tool"],
                "workflow_import_recommended": False,
                "message": "Need one more goal answer before starting the guided build surface.",
            },
        },
        surface_profile="llm-guided",
    )
    ready_state = update_session_from_router_goal(
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

    assert blocked_state.guided_flow_state is not None
    assert blocked_state.guided_flow_state["current_step"] == "understand_goal"
    assert ready_state.guided_flow_state is not None
    assert ready_state.guided_flow_state["current_step"] == "establish_spatial_context"
    assert ready_state.guided_flow_state["completed_steps"] == ["understand_goal"]
    assert ready_state.guided_flow_state["required_checks"][0]["tool_name"] == "scene_scope_graph"


def test_spatial_check_completion_advances_flow_to_primary_masses():
    ctx = FakeContext()
    update_session_from_router_goal(
        ctx,
        "create a low-poly squirrel matching front and side reference images",
        {
            "status": "no_match",
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

    record_guided_flow_spatial_check_completion(ctx, tool_name="scene_scope_graph")
    record_guided_flow_spatial_check_completion(ctx, tool_name="scene_relation_graph")
    state = record_guided_flow_spatial_check_completion(ctx, tool_name="scene_view_diagnostics")

    assert state.guided_flow_state is not None
    assert state.guided_flow_state["current_step"] == "create_primary_masses"
    assert state.guided_flow_state["required_checks"] == []
    assert state.guided_flow_state["blocked_families"] == []


def test_building_flow_advances_after_scope_and_view_checks_only():
    ctx = FakeContext()
    update_session_from_router_goal(
        ctx,
        "rebuild a low-poly tower facade from front and side references",
        {
            "status": "no_match",
            "phase_hint": "build",
            "guided_handoff": {
                "kind": "guided_manual_build",
                "target_phase": "build",
                "surface_profile": "llm-guided",
                "direct_tools": ["scene_create"],
                "supporting_tools": ["scene_scope_graph", "scene_view_diagnostics"],
                "discovery_tools": ["search_tools", "call_tool"],
                "workflow_import_recommended": False,
                "message": "Continue on the guided building surface.",
            },
        },
        surface_profile="llm-guided",
    )

    record_guided_flow_spatial_check_completion(ctx, tool_name="scene_scope_graph")
    state = record_guided_flow_spatial_check_completion(ctx, tool_name="scene_view_diagnostics")

    assert state.guided_flow_state is not None
    assert state.guided_flow_state["domain_profile"] == "building"
    assert state.guided_flow_state["current_step"] == "create_primary_masses"
    assert state.guided_flow_state["completed_steps"] == ["establish_spatial_context"]


def test_iteration_can_move_flow_into_inspect_validate():
    ctx = FakeContext()
    set_session_capability_state(
        ctx,
        SessionCapabilityState(
            phase=SessionPhase.BUILD,
            guided_flow_state={
                "flow_id": "guided_creature_flow",
                "domain_profile": "creature",
                "current_step": "create_primary_masses",
                "completed_steps": ["establish_spatial_context"],
                "required_checks": [],
                "required_prompts": ["guided_session_start", "reference_guided_creature_build"],
                "preferred_prompts": ["workflow_router_first"],
                "next_actions": ["continue_build"],
                "blocked_families": [],
                "step_status": "ready",
            },
        ),
    )

    state = asyncio.run(
        advance_guided_flow_from_iteration_async(
            ctx,
            loop_disposition="inspect_validate",
        )
    )

    assert state.guided_flow_state is not None
    assert state.guided_flow_state["current_step"] == "inspect_validate"
    assert state.guided_flow_state["step_status"] == "needs_validation"
