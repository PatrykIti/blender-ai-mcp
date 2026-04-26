"""Tests for server-driven guided flow state helpers."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, cast

import pytest
import server.adapters.mcp.session_capabilities as session_capabilities
from server.adapters.mcp.contracts.guided_flow import GuidedFlowStateContract
from server.adapters.mcp.session_capabilities import (
    SessionCapabilityState,
    advance_guided_flow_from_iteration_async,
    bootstrap_guided_empty_scene_primary_workset_async,
    get_session_capability_state,
    mark_guided_spatial_state_stale,
    record_guided_flow_spatial_check_completion,
    register_guided_part_role,
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


def _scope(*names: str) -> dict[str, object]:
    cleaned = [name for name in names if name]
    primary = cleaned[0] if cleaned else None
    return {
        "scope_kind": "object_set" if len(cleaned) > 1 else "single_object",
        "primary_target": primary,
        "object_names": cleaned,
        "object_count": len(cleaned),
    }


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


def test_default_session_state_has_no_guided_part_registry():
    ctx = FakeContext()

    restored = get_session_capability_state(ctx)

    assert restored.guided_part_registry is None


def test_session_state_round_trips_guided_part_registry():
    ctx = FakeContext()
    state = SessionCapabilityState(
        phase=SessionPhase.BUILD,
        guided_part_registry=[
            {
                "object_name": "Squirrel_Body",
                "role": "body_core",
                "role_group": "primary_masses",
                "status": "registered",
                "created_in_step": "create_primary_masses",
            }
        ],
    )

    set_session_capability_state(ctx, state)
    restored = get_session_capability_state(ctx)

    assert restored.guided_part_registry is not None
    assert restored.guided_part_registry[0]["object_name"] == "Squirrel_Body"
    assert restored.guided_part_registry[0]["role"] == "body_core"


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
    assert state.guided_flow_state["allowed_families"] == ["spatial_context", "reference_context"]
    assert state.guided_flow_state["allowed_roles"] == []
    assert state.guided_flow_state["required_role_groups"] == ["spatial_context"]


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
    assert state.guided_flow_state["allowed_families"] == ["spatial_context"]
    assert state.guided_flow_state["allowed_roles"] == []
    assert state.guided_flow_state["required_role_groups"] == ["spatial_context"]


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
    assert state.guided_flow_state["allowed_families"] == ["primary_masses", "reference_context"]
    assert state.guided_flow_state["allowed_roles"] == ["body_core", "head_mass", "tail_mass"]
    assert state.guided_flow_state["missing_roles"] == ["body_core", "head_mass", "tail_mass"]
    assert state.guided_flow_state["required_role_groups"] == ["primary_masses"]


def test_spatial_check_completion_reapplies_visibility(monkeypatch):
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

    events: list[tuple[str, str | None]] = []

    def fake_refresh_visibility_for_session_state(_ctx, state):
        current_step = None
        if state.guided_flow_state is not None:
            current_step = str(state.guided_flow_state.get("current_step"))
        events.append(("refresh_visibility", current_step))

    monkeypatch.setattr(
        session_capabilities, "refresh_visibility_for_session_state", fake_refresh_visibility_for_session_state
    )

    record_guided_flow_spatial_check_completion(ctx, tool_name="scene_scope_graph")
    record_guided_flow_spatial_check_completion(ctx, tool_name="scene_relation_graph")
    state = record_guided_flow_spatial_check_completion(ctx, tool_name="scene_view_diagnostics")

    assert state.guided_flow_state is not None
    assert events == [
        ("refresh_visibility", "establish_spatial_context"),
        ("refresh_visibility", "establish_spatial_context"),
        ("refresh_visibility", "create_primary_masses"),
    ]


def test_guided_role_hint_registration_reapplies_visibility(monkeypatch):
    ctx = FakeContext()
    set_session_capability_state(
        ctx,
        SessionCapabilityState(
            phase=SessionPhase.BUILD,
            surface_profile="llm-guided",
            guided_flow_state={
                "flow_id": "guided_creature_flow",
                "domain_profile": "creature",
                "current_step": "create_primary_masses",
                "completed_steps": ["understand_goal", "establish_spatial_context"],
                "required_checks": [],
                "required_prompts": ["guided_session_start", "reference_guided_creature_build"],
                "preferred_prompts": ["workflow_router_first"],
                "next_actions": ["begin_primary_masses"],
                "blocked_families": [],
                "allowed_families": ["primary_masses", "reference_context"],
                "allowed_roles": ["body_core", "head_mass"],
                "completed_roles": [],
                "missing_roles": ["body_core", "head_mass"],
                "required_role_groups": ["primary_masses"],
                "step_status": "ready",
            },
        ),
    )
    events: list[tuple[str | None, bool, list[str]]] = []

    def fake_refresh_visibility_for_session_state(_ctx, state):
        flow_state = state.guided_flow_state or {}
        events.append(
            (
                str(flow_state.get("current_step")) if flow_state else None,
                bool(flow_state.get("spatial_refresh_required")),
                [str(family) for family in flow_state.get("allowed_families", [])],
            )
        )

    monkeypatch.setattr(
        session_capabilities, "refresh_visibility_for_session_state", fake_refresh_visibility_for_session_state
    )

    register_guided_part_role(ctx, object_name="Squirrel_Body", role="body_core")
    state = register_guided_part_role(ctx, object_name="Squirrel_Head", role="head_mass")

    assert state.guided_flow_state is not None
    assert state.guided_flow_state["current_step"] == "place_secondary_parts"
    assert state.guided_flow_state["spatial_refresh_required"] is True
    assert events == [
        ("create_primary_masses", False, ["primary_masses", "reference_context"]),
        ("place_secondary_parts", True, ["spatial_context", "reference_context"]),
    ]


def test_scene_view_diagnostics_unavailable_does_not_complete_guided_spatial_check(monkeypatch):
    from server.adapters.mcp.areas import scene as scene_area

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

    class Handler:
        def get_scope_graph(self, **kwargs):
            return {
                "scope_kind": "single_object",
                "primary_target": "Body",
                "object_names": ["Body"],
                "object_count": 1,
                "object_roles": [],
            }

        def get_view_diagnostics(self, **kwargs):
            return {
                "view_query": {
                    "requested_view_source": "user_perspective",
                    "resolved_view_source": None,
                    "analysis_backend": "mirrored_user_perspective",
                    "available": False,
                    "unavailable_reason": "active_user_viewport_required",
                    "state_restored": True,
                },
                "summary": {
                    "target_count": 1,
                    "visible_count": 0,
                    "partially_visible_count": 0,
                    "fully_occluded_count": 0,
                    "outside_frame_count": 0,
                    "unavailable_count": 1,
                    "centered_target_count": 0,
                    "framing_issue_count": 0,
                },
                "targets": [
                    {
                        "object_name": "Body",
                        "visibility_verdict": "unavailable",
                        "projection_status": "unavailable",
                        "unavailable_reason": "active_user_viewport_required",
                    }
                ],
            }

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_scene_handler", lambda: Handler())
    monkeypatch.setattr("server.adapters.mcp.areas.scene.route_tool_call", lambda **kwargs: kwargs["direct_executor"]())

    record_guided_flow_spatial_check_completion(ctx, tool_name="scene_scope_graph")
    record_guided_flow_spatial_check_completion(ctx, tool_name="scene_relation_graph")
    result = scene_area.scene_view_diagnostics(ctx, target_object="Body")
    state = get_session_capability_state(ctx)
    checks_by_tool = {item["tool_name"]: item["status"] for item in state.guided_flow_state["required_checks"]}

    assert result.payload is not None
    assert result.payload.view_query.available is False
    assert checks_by_tool["scene_view_diagnostics"] == "pending"
    assert state.guided_flow_state["current_step"] == "establish_spatial_context"


def test_scene_scope_graph_binds_active_target_scope_and_blocks_unrelated_spoofed_view_check():
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

    state = record_guided_flow_spatial_check_completion(
        ctx,
        tool_name="scene_scope_graph",
        resolved_scope=_scope("Squirrel_Body", "Squirrel_Head"),
    )
    spoofed = record_guided_flow_spatial_check_completion(
        ctx,
        tool_name="scene_view_diagnostics",
        resolved_scope=_scope("Camera"),
    )

    assert state.guided_flow_state is not None
    assert state.guided_flow_state["active_target_scope"]["object_names"] == ["Squirrel_Body", "Squirrel_Head"]
    assert state.guided_flow_state["spatial_scope_fingerprint"]
    assert spoofed.guided_flow_state is not None
    assert spoofed.guided_flow_state["current_step"] == "establish_spatial_context"
    checks_by_tool = {check["tool_name"]: check["status"] for check in spoofed.guided_flow_state["required_checks"]}
    assert checks_by_tool["scene_scope_graph"] == "completed"
    assert checks_by_tool["scene_view_diagnostics"] == "pending"


def test_default_cube_scope_can_bind_active_guided_target_scope_when_explicitly_requested():
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

    state = record_guided_flow_spatial_check_completion(
        ctx,
        tool_name="scene_scope_graph",
        resolved_scope={
            "scope_kind": "single_object",
            "primary_target": "Cube",
            "object_names": ["Cube"],
            "object_count": 1,
        },
    )

    assert state.guided_flow_state is not None
    assert state.guided_flow_state["active_target_scope"]["primary_target"] == "Cube"
    assert state.guided_flow_state["current_step"] == "establish_spatial_context"


def test_helper_token_scope_can_bind_active_guided_target_scope_when_explicitly_requested():
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

    state = record_guided_flow_spatial_check_completion(
        ctx,
        tool_name="scene_scope_graph",
        resolved_scope={
            "scope_kind": "single_object",
            "primary_target": "Sunflower",
            "object_names": ["Sunflower"],
            "object_count": 1,
        },
    )

    assert state.guided_flow_state is not None
    assert state.guided_flow_state["active_target_scope"]["primary_target"] == "Sunflower"


def test_helper_only_camera_scope_does_not_bind_active_guided_target_scope():
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

    state = record_guided_flow_spatial_check_completion(
        ctx,
        tool_name="scene_scope_graph",
        resolved_scope=_scope("Camera"),
    )

    assert state.guided_flow_state is not None
    assert state.guided_flow_state["active_target_scope"] is None


def test_default_collection_scope_does_not_bind_active_guided_target_scope():
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

    state = record_guided_flow_spatial_check_completion(
        ctx,
        tool_name="scene_scope_graph",
        resolved_scope={
            "scope_kind": "collection",
            "primary_target": None,
            "object_names": [],
            "object_count": 0,
            "collection_name": "Collection",
        },
    )

    assert state.guided_flow_state is not None
    assert state.guided_flow_state["active_target_scope"] is None
    assert state.guided_flow_state["current_step"] == "establish_spatial_context"


def test_non_scope_graph_cannot_bind_initial_guided_target_scope():
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

    state = record_guided_flow_spatial_check_completion(
        ctx,
        tool_name="scene_view_diagnostics",
        resolved_scope=_scope("Squirrel_Body", "Squirrel_Head"),
    )

    assert state.guided_flow_state is not None
    assert state.guided_flow_state.get("active_target_scope") is None
    assert state.guided_flow_state["current_step"] == "establish_spatial_context"
    assert {check["status"] for check in state.guided_flow_state["required_checks"]} == {"pending"}


def test_router_goal_flow_summary_uses_part_registry_for_same_goal_followup():
    ctx = FakeContext()
    set_session_capability_state(
        ctx,
        SessionCapabilityState(
            phase=SessionPhase.BUILD,
            goal="create a low-poly squirrel matching front and side reference images",
            guided_part_registry=[
                {
                    "object_name": "Squirrel_Body",
                    "role": "body_core",
                    "role_group": "primary_masses",
                    "status": "registered",
                }
            ],
        ),
    )

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
    assert state.guided_flow_state["completed_roles"] == ["body_core"]
    assert state.guided_flow_state["missing_roles"] == []


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


def test_scene_clean_scene_clears_guided_part_registry_and_returns_to_primary_bootstrap():
    ctx = FakeContext()
    set_session_capability_state(
        cast(Any, ctx),
        SessionCapabilityState(
            phase=SessionPhase.BUILD,
            goal="create a low-poly squirrel matching front and side reference images",
            guided_part_registry=[
                {
                    "object_name": "Squirrel_Body",
                    "role": "body_core",
                    "role_group": "primary_masses",
                    "status": "registered",
                },
                {
                    "object_name": "Squirrel_Head",
                    "role": "head_mass",
                    "role_group": "primary_masses",
                    "status": "registered",
                },
            ],
            guided_flow_state={
                "flow_id": "guided_creature_flow",
                "domain_profile": "creature",
                "current_step": "place_secondary_parts",
                "completed_steps": ["understand_goal", "establish_spatial_context", "create_primary_masses"],
                "active_target_scope": _scope("Squirrel_Body", "Squirrel_Head"),
                "spatial_scope_fingerprint": "scope_1",
                "spatial_state_version": 0,
                "last_spatial_check_version": 0,
                "required_checks": [],
                "required_prompts": ["guided_session_start", "reference_guided_creature_build"],
                "preferred_prompts": ["workflow_router_first"],
                "next_actions": ["begin_secondary_parts"],
                "blocked_families": [],
                "allowed_families": ["primary_masses", "secondary_parts", "attachment_alignment", "reference_context"],
                "allowed_roles": ["snout_mass", "ear_pair", "foreleg_pair", "hindleg_pair"],
                "completed_roles": ["body_core", "head_mass"],
                "missing_roles": ["snout_mass", "ear_pair", "foreleg_pair", "hindleg_pair"],
                "required_role_groups": ["secondary_parts"],
                "step_status": "ready",
            },
        ),
    )

    state = mark_guided_spatial_state_stale(
        ctx,
        tool_name="scene_clean_scene",
        family="utility",
        reason="scene_clean_scene",
    )

    assert state.guided_flow_state is not None
    assert state.guided_flow_state["current_step"] == "bootstrap_primary_workset"
    assert state.guided_flow_state["spatial_state_stale"] is False
    assert state.guided_flow_state["spatial_refresh_required"] is False
    assert state.guided_flow_state["active_target_scope"] is None
    assert state.guided_flow_state["allowed_families"] == ["primary_masses", "reference_context"]
    assert state.guided_flow_state["next_actions"] == ["create_primary_workset"]
    assert state.guided_flow_state["completed_roles"] == []
    assert state.guided_flow_state["missing_roles"] == ["body_core", "head_mass", "tail_mass"]
    assert state.guided_part_registry is None


@pytest.mark.parametrize("tool_name", ["scene_rename_object", "scene_duplicate_object"])
def test_scene_object_mutations_mark_guided_spatial_state_stale(tool_name):
    ctx = FakeContext()
    set_session_capability_state(
        ctx,
        SessionCapabilityState(
            phase=SessionPhase.BUILD,
            goal="create a low-poly squirrel matching front and side reference images",
            guided_flow_state={
                "flow_id": "guided_creature_flow",
                "domain_profile": "creature",
                "current_step": "create_primary_masses",
                "completed_steps": ["understand_goal", "establish_spatial_context"],
                "active_target_scope": _scope("Squirrel_Body", "Squirrel_Head"),
                "spatial_scope_fingerprint": "scope_1",
                "spatial_state_version": 0,
                "last_spatial_check_version": 0,
                "required_checks": [],
                "required_prompts": ["guided_session_start", "reference_guided_creature_build"],
                "preferred_prompts": ["workflow_router_first"],
                "next_actions": ["begin_primary_masses"],
                "blocked_families": [],
                "allowed_families": ["primary_masses", "reference_context"],
                "allowed_roles": ["body_core", "head_mass", "tail_mass"],
                "completed_roles": [],
                "missing_roles": ["body_core", "head_mass", "tail_mass"],
                "required_role_groups": ["primary_masses"],
                "step_status": "ready",
            },
        ),
    )

    state = mark_guided_spatial_state_stale(
        ctx,
        tool_name=tool_name,
        family="utility",
        reason=tool_name,
    )

    assert state.guided_flow_state is not None
    assert state.guided_flow_state["spatial_state_stale"] is True
    assert state.guided_flow_state["spatial_refresh_required"] is True
    assert state.guided_flow_state["allowed_families"] == ["spatial_context", "reference_context"]
    assert state.guided_flow_state["next_actions"] == ["refresh_spatial_context"]


@pytest.mark.parametrize("tool_name", ["modeling_join_objects", "modeling_separate_object"])
def test_topology_changing_modeling_ops_mark_guided_spatial_state_stale(tool_name: str):
    ctx = FakeContext()
    set_session_capability_state(
        cast(Any, ctx),
        SessionCapabilityState(
            phase=SessionPhase.BUILD,
            goal="create a low-poly squirrel matching front and side reference images",
            guided_flow_state={
                "flow_id": "guided_creature_flow",
                "domain_profile": "creature",
                "current_step": "place_secondary_parts",
                "completed_steps": ["understand_goal", "establish_spatial_context", "create_primary_masses"],
                "active_target_scope": _scope("Ear_L", "Ear_R"),
                "spatial_scope_fingerprint": "scope_ears",
                "spatial_state_version": 0,
                "last_spatial_check_version": 0,
                "required_checks": [],
                "required_prompts": ["guided_session_start", "reference_guided_creature_build"],
                "preferred_prompts": ["workflow_router_first"],
                "next_actions": ["begin_secondary_parts"],
                "blocked_families": [],
                "allowed_families": ["primary_masses", "secondary_parts", "attachment_alignment", "reference_context"],
                "allowed_roles": ["snout_mass", "ear_pair", "foreleg_pair", "hindleg_pair"],
                "completed_roles": ["body_core", "head_mass"],
                "missing_roles": ["snout_mass", "ear_pair", "foreleg_pair", "hindleg_pair"],
                "required_role_groups": ["secondary_parts"],
                "step_status": "ready",
            },
        ),
    )

    state = mark_guided_spatial_state_stale(
        cast(Any, ctx),
        tool_name=tool_name,
        family=None,
        reason=tool_name,
    )

    assert state.guided_flow_state is not None
    assert state.guided_flow_state["spatial_state_stale"] is True
    assert state.guided_flow_state["spatial_refresh_required"] is True
    assert state.guided_flow_state["allowed_families"] == ["spatial_context", "reference_context"]
    assert state.guided_flow_state["next_actions"] == ["refresh_spatial_context"]


def test_empty_scene_bootstrap_moves_guided_flow_to_primary_workset_creation():
    ctx = FakeContext()
    set_session_capability_state(
        ctx,
        SessionCapabilityState(
            phase=SessionPhase.BUILD,
            goal="create a low-poly squirrel matching front and side reference images",
            guided_flow_state={
                "flow_id": "guided_creature_flow",
                "domain_profile": "creature",
                "current_step": "establish_spatial_context",
                "completed_steps": ["understand_goal"],
                "required_checks": [
                    {
                        "check_id": "scope_graph",
                        "tool_name": "scene_scope_graph",
                        "reason": "Establish scope",
                        "status": "pending",
                        "priority": "high",
                    }
                ],
                "required_prompts": ["guided_session_start", "reference_guided_creature_build"],
                "preferred_prompts": ["workflow_router_first"],
                "next_actions": ["run_required_checks"],
                "blocked_families": ["build", "late_refinement", "finish"],
                "allowed_families": ["spatial_context", "reference_context"],
                "allowed_roles": [],
                "completed_roles": [],
                "missing_roles": [],
                "required_role_groups": ["spatial_context"],
                "step_status": "blocked",
            },
        ),
    )

    state = asyncio.run(bootstrap_guided_empty_scene_primary_workset_async(ctx))

    assert state.guided_flow_state is not None
    assert state.guided_flow_state["current_step"] == "bootstrap_primary_workset"
    assert state.guided_flow_state["required_checks"] == []
    assert state.guided_flow_state["next_actions"] == ["create_primary_workset"]
    assert state.guided_flow_state["allowed_families"] == ["primary_masses", "reference_context"]
    assert state.guided_flow_state["allowed_roles"] == ["body_core", "head_mass", "tail_mass"]


def test_stale_secondary_step_rearms_and_refresh_clear_restores_secondary_families():
    ctx = FakeContext()
    set_session_capability_state(
        ctx,
        SessionCapabilityState(
            phase=SessionPhase.BUILD,
            goal="create a low-poly squirrel matching front and side reference images",
            guided_flow_state={
                "flow_id": "guided_creature_flow",
                "domain_profile": "creature",
                "current_step": "place_secondary_parts",
                "completed_steps": ["understand_goal", "establish_spatial_context", "create_primary_masses"],
                "active_target_scope": _scope("Squirrel_Body", "Squirrel_Head"),
                "spatial_scope_fingerprint": "scope_1",
                "spatial_state_version": 0,
                "last_spatial_check_version": 0,
                "required_checks": [],
                "required_prompts": ["guided_session_start", "reference_guided_creature_build"],
                "preferred_prompts": ["workflow_router_first"],
                "next_actions": ["begin_secondary_parts"],
                "blocked_families": [],
                "allowed_families": [
                    "primary_masses",
                    "secondary_parts",
                    "attachment_alignment",
                    "reference_context",
                ],
                "allowed_roles": ["snout_mass", "ear_pair", "foreleg_pair", "hindleg_pair"],
                "completed_roles": ["body_core", "head_mass"],
                "missing_roles": ["snout_mass", "ear_pair", "foreleg_pair", "hindleg_pair"],
                "required_role_groups": ["secondary_parts"],
                "step_status": "ready",
            },
        ),
    )

    stale_state = mark_guided_spatial_state_stale(
        ctx,
        tool_name="modeling_transform_object",
        family="primary_masses",
        reason="modeling_transform_object",
    )

    assert stale_state.guided_flow_state is not None
    assert stale_state.guided_flow_state["spatial_state_version"] == 1
    assert stale_state.guided_flow_state["spatial_state_stale"] is True
    assert stale_state.guided_flow_state["spatial_refresh_required"] is True
    assert stale_state.guided_flow_state["allowed_families"] == ["spatial_context", "reference_context"]
    assert stale_state.guided_flow_state["next_actions"] == ["refresh_spatial_context"]
    assert len(stale_state.guided_flow_state["required_checks"]) == 3

    rebound = record_guided_flow_spatial_check_completion(
        ctx,
        tool_name="scene_scope_graph",
        resolved_scope=_scope("Squirrel_Body", "Squirrel_Head", "Squirrel_Ear_L"),
    )
    refreshed = record_guided_flow_spatial_check_completion(
        ctx,
        tool_name="scene_relation_graph",
        resolved_scope=_scope("Squirrel_Body", "Squirrel_Head", "Squirrel_Ear_L"),
    )
    final_state = record_guided_flow_spatial_check_completion(
        ctx,
        tool_name="scene_view_diagnostics",
        resolved_scope=_scope("Squirrel_Body", "Squirrel_Head", "Squirrel_Ear_L"),
    )

    assert rebound.guided_flow_state is not None
    assert rebound.guided_flow_state["active_target_scope"]["object_names"] == [
        "Squirrel_Body",
        "Squirrel_Ear_L",
        "Squirrel_Head",
    ]
    assert refreshed.guided_flow_state is not None
    assert refreshed.guided_flow_state["spatial_refresh_required"] is True
    assert final_state.guided_flow_state is not None
    assert final_state.guided_flow_state["current_step"] == "place_secondary_parts"
    assert final_state.guided_flow_state["spatial_state_stale"] is False
    assert final_state.guided_flow_state["spatial_refresh_required"] is False
    assert final_state.guided_flow_state["last_spatial_check_version"] == 1
    assert final_state.guided_flow_state["allowed_families"] == [
        "primary_masses",
        "secondary_parts",
        "attachment_alignment",
        "reference_context",
    ]
    assert final_state.guided_flow_state["next_actions"] == ["begin_secondary_parts"]


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
    assert state.phase == SessionPhase.INSPECT_VALIDATE
    assert state.guided_flow_state["allowed_families"] == [
        "inspect_validate",
        "spatial_context",
        "checkpoint_iterate",
        "attachment_alignment",
    ]


def test_clear_session_goal_state_clears_guided_part_registry():
    ctx = FakeContext()
    set_session_capability_state(
        ctx,
        SessionCapabilityState(
            phase=SessionPhase.BUILD,
            goal="create a low-poly squirrel matching front and side reference images",
            guided_part_registry=[
                {
                    "object_name": "Squirrel_Body",
                    "role": "body_core",
                    "role_group": "primary_masses",
                    "status": "registered",
                }
            ],
        ),
    )

    from server.adapters.mcp.session_capabilities import clear_session_goal_state

    state = clear_session_goal_state(ctx)

    assert state.guided_part_registry is None


def test_primary_mass_role_registration_advances_creature_flow_after_required_roles_complete():
    ctx = FakeContext()
    set_session_capability_state(
        ctx,
        SessionCapabilityState(
            phase=SessionPhase.BUILD,
            goal="create a low-poly squirrel matching front and side reference images",
            guided_flow_state={
                "flow_id": "guided_creature_flow",
                "domain_profile": "creature",
                "current_step": "create_primary_masses",
                "completed_steps": ["understand_goal", "establish_spatial_context"],
                "required_checks": [],
                "required_prompts": ["guided_session_start", "reference_guided_creature_build"],
                "preferred_prompts": ["workflow_router_first"],
                "next_actions": ["begin_primary_masses"],
                "blocked_families": [],
                "allowed_families": ["primary_masses", "reference_context"],
                "allowed_roles": ["body_core", "head_mass", "tail_mass"],
                "completed_roles": [],
                "missing_roles": ["body_core", "head_mass", "tail_mass"],
                "required_role_groups": ["primary_masses"],
                "step_status": "ready",
            },
        ),
    )

    first = register_guided_part_role(ctx, object_name="Squirrel_Body", role="body_core")
    second = register_guided_part_role(ctx, object_name="Squirrel_Head", role="head_mass")

    assert first.guided_flow_state is not None
    assert first.guided_flow_state["current_step"] == "create_primary_masses"
    assert first.guided_flow_state["missing_roles"] == ["head_mass", "tail_mass"]

    assert second.guided_flow_state is not None
    assert second.guided_flow_state["current_step"] == "place_secondary_parts"
    assert second.guided_flow_state["required_role_groups"] == ["secondary_parts"]
    assert second.guided_flow_state["spatial_refresh_required"] is True
    assert second.guided_flow_state["step_status"] == "blocked"
    assert second.guided_flow_state["allowed_families"] == [
        "spatial_context",
        "reference_context",
    ]
    assert second.guided_flow_state["allowed_roles"] == [
        "tail_mass",
        "snout_mass",
        "ear_pair",
        "foreleg_pair",
        "hindleg_pair",
    ]


def test_place_secondary_parts_allows_missing_primary_mass_role_on_explicit_build_call(monkeypatch):
    from server.adapters.mcp.router_helper import route_tool_call_report

    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: False)
    monkeypatch.setattr("server.adapters.mcp.router_helper._get_active_surface_profile", lambda: "llm-guided")
    monkeypatch.setattr(
        "server.adapters.mcp.router_helper._get_active_session_state",
        lambda: SessionCapabilityState(
            phase=SessionPhase.BUILD,
            guided_flow_state={
                "flow_id": "guided_creature_flow",
                "domain_profile": "creature",
                "current_step": "place_secondary_parts",
                "completed_steps": ["understand_goal", "establish_spatial_context", "create_primary_masses"],
                "required_checks": [],
                "required_prompts": ["guided_session_start", "reference_guided_creature_build"],
                "preferred_prompts": ["workflow_router_first"],
                "next_actions": ["begin_secondary_parts"],
                "blocked_families": [],
                "allowed_families": ["primary_masses", "secondary_parts", "attachment_alignment", "reference_context"],
                "allowed_roles": ["tail_mass", "snout_mass", "ear_pair", "foreleg_pair", "hindleg_pair"],
                "completed_roles": ["body_core", "head_mass"],
                "missing_roles": ["tail_mass", "snout_mass", "ear_pair", "foreleg_pair", "hindleg_pair"],
                "required_role_groups": ["secondary_parts"],
                "step_status": "ready",
            },
        ),
    )

    report = route_tool_call_report(
        tool_name="modeling_create_primitive",
        params={"primitive_type": "Sphere", "name": "Tail", "guided_role": "tail_mass"},
        direct_executor=lambda: "Created Sphere named 'Tail'",
    )

    assert report.router_disposition == "bypassed"
    assert report.context.guided_tool_family == "primary_masses"
    assert report.context.guided_role == "tail_mass"


def test_secondary_role_registration_advances_creature_flow_to_checkpoint_iterate():
    ctx = FakeContext()
    set_session_capability_state(
        ctx,
        SessionCapabilityState(
            phase=SessionPhase.BUILD,
            goal="create a low-poly squirrel matching front and side reference images",
            guided_flow_state={
                "flow_id": "guided_creature_flow",
                "domain_profile": "creature",
                "current_step": "place_secondary_parts",
                "completed_steps": ["understand_goal", "establish_spatial_context", "create_primary_masses"],
                "required_checks": [],
                "required_prompts": ["guided_session_start", "reference_guided_creature_build"],
                "preferred_prompts": ["workflow_router_first"],
                "next_actions": ["begin_secondary_parts"],
                "blocked_families": [],
                "allowed_families": ["secondary_parts", "attachment_alignment"],
                "allowed_roles": ["snout_mass", "ear_pair", "foreleg_pair", "hindleg_pair"],
                "completed_roles": ["body_core", "head_mass"],
                "missing_roles": ["snout_mass", "ear_pair", "foreleg_pair", "hindleg_pair"],
                "required_role_groups": ["secondary_parts"],
                "step_status": "ready",
            },
        ),
    )

    register_guided_part_role(ctx, object_name="Squirrel_Ears", role="ear_pair")
    register_guided_part_role(ctx, object_name="Squirrel_FrontLegs", role="foreleg_pair")
    state = register_guided_part_role(ctx, object_name="Squirrel_HindLegs", role="hindleg_pair")

    assert state.guided_flow_state is not None
    assert state.guided_flow_state["current_step"] == "checkpoint_iterate"
    assert state.guided_flow_state["spatial_refresh_required"] is True
    assert state.guided_flow_state["step_status"] == "blocked"
    assert state.guided_flow_state["required_role_groups"] == ["checkpoint_iterate"]
    assert state.guided_flow_state["allowed_families"] == [
        "spatial_context",
        "reference_context",
    ]
    assert state.guided_flow_state["allowed_roles"] == ["tail_mass", "snout_mass"]


def test_guided_part_role_registration_rejects_mismatched_role_group():
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
                "next_actions": ["begin_primary_masses"],
                "blocked_families": [],
                "allowed_families": ["primary_masses", "reference_context"],
                "allowed_roles": ["body_core", "head_mass", "tail_mass"],
                "completed_roles": [],
                "missing_roles": ["body_core", "head_mass", "tail_mass"],
                "required_role_groups": ["primary_masses"],
                "step_status": "ready",
            },
        ),
    )

    with pytest.raises(ValueError, match="belongs to role_group 'primary_masses', not 'utility'"):
        register_guided_part_role(
            ctx,
            object_name="Squirrel_Body",
            role="body_core",
            role_group="utility",
        )


def test_register_guided_part_role_stays_pure_state_update_without_scene_lookup(monkeypatch):
    ctx = FakeContext()
    set_session_capability_state(
        ctx,
        SessionCapabilityState(
            phase=SessionPhase.BUILD,
            goal="create a low-poly squirrel matching front and side reference images",
            guided_flow_state={
                "flow_id": "guided_creature_flow",
                "domain_profile": "creature",
                "current_step": "create_primary_masses",
                "completed_steps": [],
                "required_checks": [],
                "required_prompts": ["guided_session_start", "reference_guided_creature_build"],
                "preferred_prompts": ["workflow_router_first"],
                "next_actions": ["begin_primary_masses"],
                "blocked_families": [],
                "allowed_families": ["primary_masses", "reference_context"],
                "allowed_roles": ["body_core", "head_mass", "tail_mass"],
                "completed_roles": [],
                "missing_roles": ["body_core", "head_mass", "tail_mass"],
                "required_role_groups": ["primary_masses"],
                "step_status": "ready",
            },
        ),
    )
    monkeypatch.setattr(
        "server.adapters.mcp.session_capabilities._scene_object_names",
        lambda: (_ for _ in ()).throw(AssertionError("scene lookup should not run for pure state helper")),
    )

    state = register_guided_part_role(ctx, object_name="MissingBody", role="body_core")

    assert state.guided_part_registry is not None
    assert state.guided_part_registry[0]["object_name"] == "MissingBody"
    assert state.guided_flow_state is not None
    assert state.guided_flow_state["completed_roles"] == ["body_core"]


def test_pair_role_registration_requires_two_side_specific_objects_before_completion():
    ctx = FakeContext()
    set_session_capability_state(
        ctx,
        SessionCapabilityState(
            phase=SessionPhase.BUILD,
            goal="create a low-poly squirrel matching front and side reference images",
            guided_flow_state={
                "flow_id": "guided_creature_flow",
                "domain_profile": "creature",
                "current_step": "place_secondary_parts",
                "completed_steps": ["understand_goal", "establish_spatial_context", "create_primary_masses"],
                "required_checks": [],
                "required_prompts": ["guided_session_start", "reference_guided_creature_build"],
                "preferred_prompts": ["workflow_router_first"],
                "next_actions": ["begin_secondary_parts"],
                "blocked_families": [],
                "allowed_families": ["secondary_parts", "attachment_alignment"],
                "allowed_roles": ["snout_mass", "ear_pair", "foreleg_pair", "hindleg_pair"],
                "completed_roles": ["body_core", "head_mass", "tail_mass", "snout_mass"],
                "missing_roles": ["ear_pair", "foreleg_pair", "hindleg_pair"],
                "required_role_groups": ["secondary_parts"],
                "step_status": "ready",
            },
        ),
    )

    first = register_guided_part_role(ctx, object_name="Ear_L", role="ear_pair")
    second = register_guided_part_role(ctx, object_name="Ear_R", role="ear_pair")

    assert first.guided_flow_state is not None
    assert first.guided_flow_state["current_step"] == "place_secondary_parts"
    assert first.guided_flow_state["role_counts"]["ear_pair"] == 1
    assert first.guided_flow_state["role_cardinality"]["ear_pair"] == 2
    assert first.guided_flow_state["role_objects"]["ear_pair"] == ["Ear_L"]
    assert "ear_pair" in first.guided_flow_state["allowed_roles"]
    assert "ear_pair" in first.guided_flow_state["missing_roles"]
    assert "ear_pair" not in first.guided_flow_state["completed_roles"]

    assert second.guided_flow_state is not None
    assert second.guided_flow_state["role_counts"]["ear_pair"] == 2
    assert second.guided_flow_state["role_objects"]["ear_pair"] == ["Ear_L", "Ear_R"]
    assert "ear_pair" in second.guided_flow_state["completed_roles"]
    assert "ear_pair" not in second.guided_flow_state["allowed_roles"]
    assert "ear_pair" not in second.guided_flow_state["missing_roles"]


def test_checkpoint_iterate_role_summary_keeps_missing_build_roles_visible():
    ctx = FakeContext()
    set_session_capability_state(
        ctx,
        SessionCapabilityState(
            phase=SessionPhase.BUILD,
            goal="create a low-poly squirrel matching front and side reference images",
            guided_flow_state={
                "flow_id": "guided_creature_flow",
                "domain_profile": "creature",
                "current_step": "checkpoint_iterate",
                "completed_steps": [
                    "understand_goal",
                    "establish_spatial_context",
                    "create_primary_masses",
                    "place_secondary_parts",
                ],
                "active_target_scope": _scope("Squirrel_Body", "Squirrel_Head", "Squirrel_Ears"),
                "spatial_scope_fingerprint": "scope_1",
                "spatial_state_version": 0,
                "last_spatial_check_version": 0,
                "required_checks": [],
                "required_prompts": ["guided_session_start", "reference_guided_creature_build"],
                "preferred_prompts": ["workflow_router_first"],
                "next_actions": ["run_checkpoint_iterate"],
                "blocked_families": [],
                "allowed_families": ["primary_masses", "secondary_parts", "checkpoint_iterate"],
                "allowed_roles": [],
                "completed_roles": ["body_core", "head_mass", "ear_pair", "foreleg_pair", "hindleg_pair"],
                "missing_roles": [],
                "required_role_groups": ["checkpoint_iterate"],
                "step_status": "needs_checkpoint",
            },
            guided_part_registry=[
                {
                    "object_name": "Squirrel_Body",
                    "role": "body_core",
                    "role_group": "primary_masses",
                    "status": "registered",
                },
                {
                    "object_name": "Squirrel_Head",
                    "role": "head_mass",
                    "role_group": "primary_masses",
                    "status": "registered",
                },
                {
                    "object_name": "Squirrel_Ears",
                    "role": "ear_pair",
                    "role_group": "secondary_parts",
                    "status": "registered",
                },
                {
                    "object_name": "Squirrel_ForeLegs",
                    "role": "foreleg_pair",
                    "role_group": "secondary_parts",
                    "status": "registered",
                },
                {
                    "object_name": "Squirrel_HindLegs",
                    "role": "hindleg_pair",
                    "role_group": "secondary_parts",
                    "status": "registered",
                },
            ],
        ),
    )

    state = mark_guided_spatial_state_stale(
        ctx,
        tool_name="modeling_transform_object",
        family="primary_masses",
        reason="modeling_transform_object",
    )

    assert state.guided_flow_state is not None
    assert state.guided_flow_state["spatial_state_stale"] is True
    assert state.guided_flow_state["spatial_refresh_required"] is False
    assert state.guided_flow_state["allowed_roles"] == ["tail_mass", "snout_mass"]
