"""Regression tests for guided flow domain-profile selection and overlays."""

from __future__ import annotations

from dataclasses import dataclass, field

from server.adapters.mcp.session_capabilities import (
    SessionCapabilityState,
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


def test_generic_goal_uses_generic_flow_profile():
    ctx = FakeContext()

    state = update_session_from_router_goal(
        ctx,
        "block out a simple desk lamp housing",
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
    assert state.guided_flow_state["domain_profile"] == "generic"
    assert [check["tool_name"] for check in state.guided_flow_state["required_checks"]] == [
        "scene_scope_graph",
        "scene_relation_graph",
        "scene_view_diagnostics",
    ]
    assert state.guided_flow_state["required_role_groups"] == ["spatial_context"]


def test_generic_goal_with_plan_verb_does_not_select_building_profile():
    ctx = FakeContext()

    state = update_session_from_router_goal(
        ctx,
        "plan a simple desk lamp housing",
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
    assert state.guided_flow_state["domain_profile"] == "generic"


def test_creature_recipe_forces_creature_profile_even_without_goal_keywords():
    ctx = FakeContext()

    state = update_session_from_router_goal(
        ctx,
        "assemble the model from the provided references",
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
    assert state.guided_flow_state["required_prompts"] == [
        "guided_session_start",
        "reference_guided_creature_build",
    ]
    assert state.guided_flow_state["required_role_groups"] == ["spatial_context"]


def test_building_goal_uses_building_overlay_specific_checks():
    ctx = FakeContext()

    state = update_session_from_router_goal(
        ctx,
        "rebuild a watchtower facade with roof and windows from front and side references",
        {
            "status": "ready",
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

    assert state.guided_flow_state is not None
    assert state.guided_flow_state["domain_profile"] == "building"
    assert [check["tool_name"] for check in state.guided_flow_state["required_checks"]] == [
        "scene_scope_graph",
        "scene_view_diagnostics",
    ]
    assert state.guided_flow_state["required_role_groups"] == ["spatial_context"]


def test_building_flow_primary_roles_require_footprint_main_volume_and_wall_shell_before_advancing():
    ctx = FakeContext()
    set_session_capability_state(
        ctx,
        SessionCapabilityState(
            phase=SessionPhase.BUILD,
            goal="rebuild a watchtower facade with roof and windows from front and side references",
            guided_flow_state={
                "flow_id": "guided_building_flow",
                "domain_profile": "building",
                "current_step": "create_primary_masses",
                "completed_steps": ["understand_goal", "establish_spatial_context"],
                "required_checks": [],
                "required_prompts": ["guided_session_start", "reference_guided_architecture_build"],
                "preferred_prompts": ["workflow_router_first"],
                "next_actions": ["begin_primary_masses"],
                "blocked_families": [],
                "allowed_families": ["primary_masses"],
                "allowed_roles": ["footprint_mass", "main_volume", "wall_shell"],
                "completed_roles": [],
                "missing_roles": ["footprint_mass", "main_volume", "wall_shell"],
                "required_role_groups": ["primary_masses"],
                "step_status": "ready",
            },
        ),
    )

    first = register_guided_part_role(ctx, object_name="Tower_Footprint", role="footprint_mass")
    second = register_guided_part_role(ctx, object_name="Tower_MainVolume", role="main_volume")
    third = register_guided_part_role(ctx, object_name="Tower_WallShell", role="wall_shell")

    assert first.guided_flow_state is not None
    assert first.guided_flow_state["current_step"] == "create_primary_masses"
    assert first.guided_flow_state["missing_roles"] == ["main_volume", "wall_shell"]

    assert second.guided_flow_state is not None
    assert second.guided_flow_state["current_step"] == "create_primary_masses"
    assert second.guided_flow_state["missing_roles"] == ["wall_shell"]

    assert third.guided_flow_state is not None
    assert third.guided_flow_state["current_step"] == "place_secondary_parts"
    assert third.guided_flow_state["required_role_groups"] == ["secondary_parts"]
    assert third.guided_flow_state["spatial_refresh_required"] is True
    assert third.guided_flow_state["step_status"] == "blocked"
    assert third.guided_flow_state["allowed_families"] == ["spatial_context"]
    assert [check["tool_name"] for check in third.guided_flow_state["required_checks"]] == [
        "scene_scope_graph",
        "scene_view_diagnostics",
    ]
    assert third.guided_flow_state["next_actions"] == ["refresh_spatial_context"]
    assert third.guided_flow_state["allowed_roles"] == [
        "facade_opening",
        "opening_grid",
        "support_element",
        "roof_mass",
        "detail_element",
    ]


def test_building_flow_secondary_roles_advance_to_checkpoint_iterate():
    ctx = FakeContext()
    set_session_capability_state(
        ctx,
        SessionCapabilityState(
            phase=SessionPhase.BUILD,
            goal="rebuild a watchtower facade with roof and windows from front and side references",
            guided_flow_state={
                "flow_id": "guided_building_flow",
                "domain_profile": "building",
                "current_step": "place_secondary_parts",
                "completed_steps": ["understand_goal", "establish_spatial_context", "create_primary_masses"],
                "required_checks": [],
                "required_prompts": ["guided_session_start", "reference_guided_architecture_build"],
                "preferred_prompts": ["workflow_router_first"],
                "next_actions": ["begin_secondary_parts"],
                "blocked_families": [],
                "allowed_families": ["secondary_parts"],
                "allowed_roles": ["facade_opening", "opening_grid", "support_element", "roof_mass", "detail_element"],
                "completed_roles": ["footprint_mass", "main_volume", "wall_shell"],
                "missing_roles": ["facade_opening", "opening_grid", "support_element", "roof_mass", "detail_element"],
                "required_role_groups": ["secondary_parts"],
                "step_status": "ready",
            },
        ),
    )

    register_guided_part_role(ctx, object_name="Tower_WindowCuts", role="facade_opening")
    register_guided_part_role(ctx, object_name="Tower_Buttresses", role="support_element")
    state = register_guided_part_role(ctx, object_name="Tower_Roof", role="roof_mass")

    assert state.guided_flow_state is not None
    assert state.guided_flow_state["current_step"] == "checkpoint_iterate"
    assert state.guided_flow_state["spatial_refresh_required"] is True
    assert state.guided_flow_state["step_status"] == "blocked"
    assert state.guided_flow_state["allowed_families"] == ["spatial_context"]
    assert [check["tool_name"] for check in state.guided_flow_state["required_checks"]] == [
        "scene_scope_graph",
        "scene_view_diagnostics",
    ]
    assert state.guided_flow_state["next_actions"] == ["refresh_spatial_context"]
    assert state.guided_flow_state["required_role_groups"] == ["checkpoint_iterate"]
