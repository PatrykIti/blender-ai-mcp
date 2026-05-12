"""
E2E-style router tests for guided manual-build handoff after no-match.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field, replace

from server.adapters.mcp.areas.router import router_get_status, router_set_goal
from server.adapters.mcp.sampling.result_types import (
    AssistantBudgetContract,
    AssistantRunResult,
    RepairSuggestionContract,
)
from server.adapters.mcp.session_capabilities import get_session_capability_state, set_session_capability_state
from server.adapters.mcp.transforms.visibility_policy import GUIDED_SPATIAL_CONTEXT_DIRECT_TOOLS
from server.application.tool_handlers.router_handler import RouterToolHandler


def test_router_set_goal_meta_capture_build_request_returns_guided_manual_no_match(router, clean_scene):
    """Meta capture/build goals should hand off into guided manual build instead of irrelevant workflow routing."""

    handler = RouterToolHandler(router=router, enabled=True)

    result = handler.set_goal(
        "squirrel vision test - 3 progressive screenshots: head blockout, face features, full body - low poly squirrel with consistent camera"
    )

    assert result["status"] == "no_match"
    assert result["continuation_mode"] == "guided_manual_build"
    assert result["workflow"] is None
    assert result["phase_hint"] == "build"
    assert "guided build surface" in result["message"]
    assert router.get_pending_workflow() is None


def test_router_set_goal_reference_guided_squirrel_returns_guided_manual_no_match(router, clean_scene):
    """Reference-guided squirrel build goals should hand off into guided manual build."""

    handler = RouterToolHandler(router=router, enabled=True)

    result = handler.set_goal("create a low-poly squirrel matching front and side reference images")

    assert result["status"] == "no_match"
    assert result["continuation_mode"] == "guided_manual_build"
    assert result["workflow"] is None
    assert result["phase_hint"] == "build"
    assert "reference-guided manual build request" in result["message"]
    assert router.get_pending_workflow() is None


def test_router_set_goal_reference_guided_architecture_returns_guided_manual_no_match(router, clean_scene):
    """Plan/elevation architecture reconstruction should enter the bounded architecture handoff."""

    handler = RouterToolHandler(router=router, enabled=True)

    result = handler.set_goal("rebuild a tower facade from the front elevation and floor plan references")

    assert result["status"] == "no_match"
    assert result["continuation_mode"] == "guided_manual_build"
    assert result["workflow"] is None
    assert result["phase_hint"] == "build"
    assert "reference-guided architecture reconstruction request" in result["message"]
    assert router.get_pending_workflow() is None


def test_guided_manual_goal_suppresses_heuristic_workflow_trigger_for_direct_transform(router, clean_scene):
    """A no-match guided manual goal should not let ordinary direct transforms trigger unrelated workflows."""

    handler = RouterToolHandler(router=router, enabled=True)
    result = handler.set_goal("create a low-poly squirrel matching front and side reference images")

    assert result["status"] == "no_match"
    assert result["continuation_mode"] == "guided_manual_build"
    assert router.get_pending_workflow() is None

    corrected = router.process_llm_tool_call(
        "modeling_transform_object",
        {"name": "AcornCap", "scale": [1.0, 1.0, 0.06]},
    )

    assert corrected == [
        {
            "tool": "modeling_transform_object",
            "params": {"name": "AcornCap", "scale": [1.0, 1.0, 0.06]},
        }
    ]


@dataclass
class FakeAsyncContext:
    state: dict[str, object] = field(default_factory=dict)
    request_id: str = "req_creature_handoff"
    session_id: str = "sess_creature_handoff"
    transport: str = "stdio"

    def get_state(self, key: str):
        return self.state.get(key)

    def set_state(self, key: str, value, *, serializable: bool = True) -> None:
        self.state[key] = value

    async def reset_visibility(self) -> None:
        self.state["_visibility_calls"] = [("reset_visibility", {})]

    async def enable_components(self, **kwargs) -> None:
        calls = self.state.setdefault("_visibility_calls", [])
        assert isinstance(calls, list)
        calls.append(("enable_components", kwargs))

    async def disable_components(self, **kwargs) -> None:
        calls = self.state.setdefault("_visibility_calls", [])
        assert isinstance(calls, list)
        calls.append(("disable_components", kwargs))

    def info(self, message, logger_name=None, extra=None):
        return None


def test_router_area_reference_guided_creature_goal_persists_creature_recipe_handoff(router, clean_scene, monkeypatch):
    """The MCP-area goal flow should persist the creature handoff recipe and re-expose it via router_get_status."""

    ctx = FakeAsyncContext()
    handler = RouterToolHandler(router=router, enabled=True)

    monkeypatch.setattr("server.adapters.mcp.areas.router.get_router_handler", lambda: handler)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.router.get_config",
        lambda: type("Cfg", (), {"MCP_SURFACE_PROFILE": "llm-guided"})(),
    )
    monkeypatch.setattr("server.adapters.mcp.areas.router._should_attach_repair_suggestion", lambda payload: False)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.router.run_repair_suggestion_assistant",
        lambda ctx, diagnostics: AssistantRunResult(
            status="unavailable",
            assistant_name="repair_suggester",
            message="disabled in test",
            budget=AssistantBudgetContract(max_input_chars=1, max_messages=1, max_tokens=1, tool_budget=0),
            capability_source="unavailable",
            result=RepairSuggestionContract(summary="n/a", actions=[]),
        ),
    )

    result = asyncio.run(
        router_set_goal(
            ctx,
            goal="create a low-poly creature matching front and side reference images",
        )
    )

    assert result.status == "no_match"
    assert result.guided_handoff is not None
    assert result.guided_handoff.recipe_id == "low_poly_creature_blockout"
    assert result.guided_flow_state is not None
    assert result.guided_flow_state.domain_profile == "creature"
    assert result.guided_flow_state.current_step == "establish_spatial_context"
    assert "modeling_create_primitive" in result.guided_handoff.direct_tools
    assert "mesh_extrude_region" in result.guided_handoff.direct_tools
    assert "macro_finish_form" not in result.guided_handoff.direct_tools

    status = asyncio.run(router_get_status(ctx))

    assert status.current_goal == "create a low-poly creature matching front and side reference images"
    assert status.current_phase == "build"
    assert status.guided_handoff is not None
    assert status.guided_handoff.recipe_id == "low_poly_creature_blockout"
    assert status.guided_flow_state is not None
    assert status.guided_flow_state.domain_profile == "creature"
    assert status.guided_flow_state.current_step == "establish_spatial_context"
    assert any(
        rule.get("names") == set(GUIDED_SPATIAL_CONTEXT_DIRECT_TOOLS)
        for rule in status.visibility_rules or []
        if rule.get("components") == {"tool"}
    )

    current_state = get_session_capability_state(ctx)
    assert current_state.guided_flow_state is not None
    set_session_capability_state(
        ctx,
        replace(
            current_state,
            guided_flow_state={
                **current_state.guided_flow_state,
                "current_step": "place_secondary_parts",
                "spatial_refresh_required": True,
                "required_checks": [
                    {
                        "check_id": "scope",
                        "tool_name": "scene_scope_graph",
                        "reason": "refresh scope",
                        "status": "pending",
                    },
                    {
                        "check_id": "relation",
                        "tool_name": "scene_relation_graph",
                        "reason": "refresh relations",
                        "status": "pending",
                    },
                ],
                "allowed_families": ["spatial_context", "reference_context"],
                "next_actions": ["refresh_spatial_context"],
            },
        ),
    )

    stale_status = asyncio.run(router_get_status(ctx))

    assert stale_status.guided_handoff is not None
    assert "modeling_create_primitive" in stale_status.guided_handoff.direct_tools
    assert stale_status.guided_flow_state is not None
    assert stale_status.guided_flow_state.spatial_refresh_required is True
    assert stale_status.guided_flow_state.next_actions == ["refresh_spatial_context"]
    assert any(
        rule.get("names") == set(GUIDED_SPATIAL_CONTEXT_DIRECT_TOOLS)
        for rule in stale_status.visibility_rules or []
        if rule.get("components") == {"tool"}
    )


def test_router_area_reference_guided_architecture_goal_persists_architecture_recipe_handoff(
    router, clean_scene, monkeypatch
):
    """The MCP-area goal flow should persist the architecture recipe and building guided flow profile."""

    ctx = FakeAsyncContext()
    handler = RouterToolHandler(router=router, enabled=True)

    monkeypatch.setattr("server.adapters.mcp.areas.router.get_router_handler", lambda: handler)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.router.get_config",
        lambda: type("Cfg", (), {"MCP_SURFACE_PROFILE": "llm-guided"})(),
    )
    monkeypatch.setattr("server.adapters.mcp.areas.router._should_attach_repair_suggestion", lambda payload: False)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.router.run_repair_suggestion_assistant",
        lambda ctx, diagnostics: AssistantRunResult(
            status="unavailable",
            assistant_name="repair_suggester",
            message="disabled in test",
            budget=AssistantBudgetContract(max_input_chars=1, max_messages=1, max_tokens=1, tool_budget=0),
            capability_source="unavailable",
            result=RepairSuggestionContract(summary="n/a", actions=[]),
        ),
    )

    result = asyncio.run(
        router_set_goal(
            ctx,
            goal="rebuild a tower facade from the front elevation and floor plan references",
        )
    )

    assert result.status == "no_match"
    assert result.guided_handoff is not None
    assert result.guided_handoff.recipe_id == "reference_guided_architecture_build"
    assert "macro_cutout_recess" in result.guided_handoff.direct_tools
    assert "macro_place_supported_pair" in result.guided_handoff.direct_tools
    assert result.guided_flow_state is not None
    assert result.guided_flow_state.domain_profile == "building"
    assert result.guided_flow_state.required_prompts == [
        "guided_session_start",
        "reference_guided_architecture_build",
    ]

    status = asyncio.run(router_get_status(ctx))

    assert status.current_goal == "rebuild a tower facade from the front elevation and floor plan references"
    assert status.current_phase == "build"
    assert status.guided_handoff is not None
    assert status.guided_handoff.recipe_id == "reference_guided_architecture_build"
    assert status.guided_flow_state is not None
    assert status.guided_flow_state.domain_profile == "building"
