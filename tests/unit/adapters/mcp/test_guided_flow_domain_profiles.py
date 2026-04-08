"""Regression tests for guided flow domain-profile selection and overlays."""

from __future__ import annotations

from dataclasses import dataclass, field

from server.adapters.mcp.session_capabilities import update_session_from_router_goal


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
