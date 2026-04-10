"""Guided scope-discipline regressions for scene spatial helper tools."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import cast

from fastmcp import Context
from server.adapters.mcp.areas import scene as scene_area
from server.adapters.mcp.session_capabilities import SessionCapabilityState, set_session_capability_state
from server.adapters.mcp.session_phase import SessionPhase


@dataclass
class FakeContext:
    state: dict[str, object] = field(default_factory=dict)

    def get_state(self, key: str):
        return self.state.get(key)

    def set_state(self, key: str, value, *, serializable: bool = True) -> None:
        self.state[key] = value


def _guided_ctx() -> FakeContext:
    ctx = FakeContext()
    set_session_capability_state(
        cast(Context, ctx),
        SessionCapabilityState(
            phase=SessionPhase.BUILD,
            surface_profile="llm-guided",
            guided_flow_state={
                "flow_id": "guided_creature_flow",
                "domain_profile": "creature",
                "current_step": "establish_spatial_context",
                "completed_steps": ["understand_goal"],
                "required_checks": [],
                "required_prompts": ["guided_session_start", "reference_guided_creature_build"],
                "preferred_prompts": ["workflow_router_first"],
                "next_actions": ["run_required_checks"],
                "blocked_families": [],
                "allowed_families": ["spatial_context", "reference_context"],
                "allowed_roles": [],
                "completed_roles": [],
                "missing_roles": [],
                "required_role_groups": ["spatial_context"],
                "step_status": "blocked",
            },
        ),
    )
    return ctx


def test_scene_scope_graph_requires_explicit_scope_during_guided_spatial_gate(monkeypatch):
    monkeypatch.setattr(scene_area, "route_tool_call", lambda tool_name, params, direct_executor: direct_executor())

    class Handler:
        def get_scope_graph(self, target_object=None, target_objects=None, collection_name=None):
            return {
                "scope_kind": "scene",
                "primary_target": None,
                "object_names": [],
                "object_count": 0,
                "object_roles": [],
            }

    monkeypatch.setattr(scene_area, "get_scene_handler", lambda: Handler())

    result = scene_area.scene_scope_graph(_guided_ctx())

    assert result.payload is None
    assert result.error is not None
    assert "Provide target_object, target_objects, or collection_name" in result.error


def test_scene_relation_graph_requires_explicit_scope_during_guided_spatial_gate(monkeypatch):
    monkeypatch.setattr(scene_area, "route_tool_call", lambda tool_name, params, direct_executor: direct_executor())

    class Handler:
        def get_relation_graph(
            self,
            target_object=None,
            target_objects=None,
            collection_name=None,
            goal_hint=None,
            include_truth_payloads=False,
        ):
            return {
                "scope": {
                    "scope_kind": "scene",
                    "primary_target": None,
                    "object_names": [],
                    "object_count": 0,
                    "object_roles": [],
                },
                "summary": {"pair_count": 0},
                "pairs": [],
            }

    monkeypatch.setattr(scene_area, "get_scene_handler", lambda: Handler())

    result = scene_area.scene_relation_graph(_guided_ctx())

    assert result.payload is None
    assert result.error is not None
    assert "Provide target_object, target_objects, or collection_name" in result.error
