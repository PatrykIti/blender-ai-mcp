"""Tests for model-facing router clarification on llm-guided."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from types import SimpleNamespace

import pytest
from server.adapters.mcp.areas import router as router_area
from server.adapters.mcp.session_capabilities import (
    SessionCapabilityState,
    get_session_capability_state,
    set_session_capability_state,
)
from server.adapters.mcp.session_phase import SessionPhase


@dataclass
class FakeContext:
    """Minimal async Context-like object for elicitation tests."""

    response: object
    calls: list[tuple[str, object]] = field(default_factory=list)
    state: dict[str, object] = field(default_factory=dict)
    session_id: str = "sess_test"
    transport: str = "stdio"

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

    async def warning(self, message: str, logger_name=None, extra=None):
        return None


def test_maybe_elicit_router_answers_returns_typed_clarification_without_human_prompt(monkeypatch):
    """llm-guided should keep missing workflow params model-facing by default."""

    monkeypatch.setattr(router_area, "get_config", lambda: type("Cfg", (), {"MCP_SURFACE_PROFILE": "llm-guided"})())

    initial = {
        "status": "needs_input",
        "workflow": "chair_workflow",
        "unresolved": [{"param": "height", "type": "float", "description": "Overall height"}],
    }
    ctx = FakeContext(response=object())

    result = __import__("asyncio").run(router_area._maybe_elicit_router_answers(ctx, "chair", initial))

    assert "clarification" in result
    assert "elicitation_action" not in result
    assert ctx.calls == []


def test_maybe_elicit_router_answers_keeps_workflow_confirmation_model_facing(monkeypatch):
    """workflow_confirmation remains model-facing and should not prompt the human."""

    monkeypatch.setattr(router_area, "get_config", lambda: type("Cfg", (), {"MCP_SURFACE_PROFILE": "llm-guided"})())

    initial = {
        "status": "needs_input",
        "workflow": "chair_workflow",
        "unresolved": [
            {
                "param": "workflow_confirmation",
                "type": "string",
                "description": "Confirm workflow",
                "enum": ["chair_workflow"],
                "default": "chair_workflow",
            }
        ],
    }
    ctx = FakeContext(response=object())

    result = __import__("asyncio").run(router_area._maybe_elicit_router_answers(ctx, "chair", initial))

    assert "clarification" in result
    assert ctx.calls == []
    assert "elicitation_action" not in result


def test_router_set_goal_needs_input_is_model_facing_on_llm_guided(monkeypatch):
    """llm-guided should persist pending clarification without human-first elicitation."""

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

    ctx = FakeContext(response=object())
    result = asyncio.run(router_area.router_set_goal(ctx, goal="chair"))

    session = get_session_capability_state(ctx)
    assert result.status == "needs_input"
    assert result.session_id == "sess_test"
    assert result.transport == "stdio"
    assert result.elicitation_action is None
    assert result.guided_reference_readiness is not None
    assert result.guided_reference_readiness.blocking_reason == "goal_input_pending"
    assert result.guided_reference_readiness.next_action == "answer_pending_goal_questions"
    assert session.pending_question_set_id is not None
    assert session.pending_workflow_name == "chair_workflow"
    assert session.last_elicitation_action is None


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

    ctx = FakeContext(response=object())
    first = asyncio.run(router_area.router_set_goal(ctx, goal="chair", resolved_params={"width": 1.0}))
    second = asyncio.run(router_area.router_set_goal(ctx, goal="chair", resolved_params={"height": 2.0}))

    assert first.status == "needs_input"
    assert second.status == "ready"
    assert calls[0] == {"width": 1.0}
    assert calls[1] == {"width": 1.0, "height": 2.0}


def test_router_set_goal_reuses_question_set_id_after_model_facing_retry(monkeypatch):
    """A repeated model-facing clarification should reuse the same pending question-set id."""

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

    ctx = FakeContext(response=object())
    first = asyncio.run(router_area.router_set_goal(ctx, goal="chair"))
    second = asyncio.run(router_area.router_set_goal(ctx, goal="chair"))

    assert first.clarification.question_set_id == second.clarification.question_set_id


def test_router_set_goal_accepts_explicit_workflow_confirmation(monkeypatch):
    """Explicit workflow_confirmation answers should break the medium-confidence confirmation loop."""

    monkeypatch.setattr(router_area, "get_config", lambda: type("Cfg", (), {"MCP_SURFACE_PROFILE": "legacy-flat"})())

    class Handler:
        def set_goal(self, goal, resolved_params=None):
            if resolved_params and resolved_params.get("workflow_confirmation") == "chair_workflow":
                return {
                    "status": "ready",
                    "workflow": "chair_workflow",
                    "resolved": {},
                    "unresolved": [],
                    "resolution_sources": {},
                    "message": "ok",
                    "executed": 0,
                }
            return {
                "status": "needs_input",
                "workflow": "chair_workflow",
                "resolved": {},
                "unresolved": [{"param": "workflow_confirmation", "type": "string", "description": "Confirm workflow"}],
                "resolution_sources": {},
                "message": "confirm workflow",
            }

        def clear_goal(self):
            return "cleared"

    monkeypatch.setattr(router_area, "get_router_handler", lambda: Handler())

    ctx = FakeContext(response=object())
    result = asyncio.run(
        router_area.router_set_goal(
            ctx,
            goal="chair",
            resolved_params={"workflow_confirmation": "chair_workflow"},
        )
    )

    assert result.status == "ready"


def test_router_set_goal_workflow_confirmation_stays_model_facing_on_llm_guided(monkeypatch):
    """Medium-confidence workflow confirmation should not trigger native human elicitation."""

    monkeypatch.setattr(router_area, "get_config", lambda: type("Cfg", (), {"MCP_SURFACE_PROFILE": "llm-guided"})())

    class Handler:
        def set_goal(self, goal, resolved_params=None):
            if resolved_params and resolved_params.get("workflow_confirmation") == "chair_workflow":
                return {
                    "status": "ready",
                    "workflow": "chair_workflow",
                    "resolved": {},
                    "unresolved": [],
                    "resolution_sources": {},
                    "message": "ok",
                    "executed": 0,
                }
            return {
                "status": "needs_input",
                "workflow": "chair_workflow",
                "resolved": {},
                "unresolved": [
                    {
                        "param": "workflow_confirmation",
                        "type": "string",
                        "description": "Confirm workflow",
                        "enum": ["chair_workflow"],
                        "default": "chair_workflow",
                    }
                ],
                "resolution_sources": {},
                "message": "confirm workflow",
            }

        def clear_goal(self):
            return "cleared"

    monkeypatch.setattr(router_area, "get_router_handler", lambda: Handler())

    ctx = FakeContext(response=object())
    result = asyncio.run(router_area.router_set_goal(ctx, goal="chair"))

    assert result.status == "needs_input"
    assert result.elicitation_action is None
    assert result.clarification is not None
    assert ctx.calls == []


def test_router_set_goal_no_match_with_guided_manual_continuation_bootstraps_empty_scene(monkeypatch):
    """A guided-manual no_match handoff should bootstrap primary workset creation for an empty scene."""

    monkeypatch.setattr(router_area, "get_config", lambda: type("Cfg", (), {"MCP_SURFACE_PROFILE": "llm-guided"})())
    monkeypatch.setattr(router_area, "_scene_has_meaningful_guided_objects", lambda: False)

    class Handler:
        def set_goal(self, goal, resolved_params=None):
            return {
                "status": "no_match",
                "continuation_mode": "guided_manual_build",
                "workflow": None,
                "resolved": {},
                "unresolved": [],
                "resolution_sources": {},
                "phase_hint": "build",
                "message": "Continue on the guided build surface.",
            }

        def clear_goal(self):
            return "cleared"

    monkeypatch.setattr(router_area, "get_router_handler", lambda: Handler())

    ctx = FakeContext(response=object())
    result = asyncio.run(router_area.router_set_goal(ctx, goal="low poly squirrel 3D model"))

    session = get_session_capability_state(ctx)
    assert result.status == "no_match"
    assert result.session_id == "sess_test"
    assert result.transport == "stdio"
    assert result.continuation_mode == "guided_manual_build"
    assert result.guided_handoff is not None
    assert result.guided_handoff.kind == "guided_manual_build"
    assert result.guided_handoff.recipe_id == "low_poly_creature_blockout"
    assert result.guided_handoff.target_phase == "build"
    assert result.guided_handoff.workflow_import_recommended is False
    assert "modeling_create_primitive" in result.guided_handoff.direct_tools
    assert "mesh_extrude_region" in result.guided_handoff.direct_tools
    assert "macro_finish_form" not in result.guided_handoff.direct_tools
    assert result.guided_handoff.discovery_tools == ["search_tools", "call_tool"]
    assert result.guided_reference_readiness is not None
    assert result.guided_reference_readiness.blocking_reason == "reference_images_required"
    assert result.guided_reference_readiness.next_action == "attach_reference_images"
    assert result.guided_flow_state is not None
    assert result.guided_flow_state.domain_profile == "creature"
    assert result.guided_flow_state.current_step == "bootstrap_primary_workset"
    assert result.guided_flow_state.next_actions == ["create_primary_workset"]
    assert session.phase.value == "build"
    assert session.guided_handoff is not None
    assert session.guided_handoff["kind"] == "guided_manual_build"
    assert session.guided_flow_state is not None
    assert session.guided_flow_state["domain_profile"] == "creature"
    assert session.guided_flow_state["current_step"] == "bootstrap_primary_workset"


def test_router_get_status_exposes_session_id_and_transport(monkeypatch):
    """router_get_status should surface explicit MCP session diagnostics."""

    monkeypatch.setattr(router_area, "get_config", lambda: type("Cfg", (), {"MCP_SURFACE_PROFILE": "llm-guided"})())
    monkeypatch.setattr(router_area, "get_router_status", lambda: {"enabled": True})
    monkeypatch.setattr(router_area, "_build_background_job_diagnostics", lambda: (0, {}, []))
    monkeypatch.setattr(router_area, "_build_timeout_policy_diagnostics", lambda _ctx: None)
    monkeypatch.setattr(router_area, "_build_task_runtime_diagnostics", lambda _ctx: None)
    monkeypatch.setattr(router_area, "_build_telemetry_diagnostics", lambda: None)
    monkeypatch.setattr(router_area, "_get_list_page_size", lambda _ctx: 50)
    monkeypatch.setattr(router_area, "run_repair_suggestion_assistant", lambda *args, **kwargs: None)
    monkeypatch.setattr(router_area, "to_repair_assistant_contract", lambda *args, **kwargs: None)
    monkeypatch.setattr(router_area, "_should_attach_repair_suggestion", lambda _payload: False)
    monkeypatch.setattr(
        router_area,
        "build_visibility_diagnostics",
        lambda surface_profile, phase, guided_handoff=None, guided_flow_state=None: SimpleNamespace(
            rules=(),
            visible_capability_ids=("router",),
            visible_entry_capability_ids=("router",),
            hidden_capability_ids=(),
            hidden_category_counts={},
        ),
    )

    ctx = FakeContext(response=object())

    result = asyncio.run(router_area.router_get_status(ctx))

    assert result.session_id == "sess_test"
    assert result.transport == "stdio"


def test_router_get_status_returns_guided_flow_state(monkeypatch):
    """router_get_status should mirror the active guided flow envelope from session state."""

    monkeypatch.setattr(router_area, "get_config", lambda: type("Cfg", (), {"MCP_SURFACE_PROFILE": "llm-guided"})())
    monkeypatch.setattr(router_area, "get_router_status", lambda: {"enabled": True})
    monkeypatch.setattr(router_area, "_build_background_job_diagnostics", lambda: (0, {}, []))
    monkeypatch.setattr(router_area, "_build_timeout_policy_diagnostics", lambda _ctx: None)
    monkeypatch.setattr(router_area, "_build_task_runtime_diagnostics", lambda _ctx: None)
    monkeypatch.setattr(router_area, "_build_telemetry_diagnostics", lambda: None)
    monkeypatch.setattr(router_area, "_get_list_page_size", lambda _ctx: 50)
    monkeypatch.setattr(router_area, "run_repair_suggestion_assistant", lambda *args, **kwargs: None)
    monkeypatch.setattr(router_area, "to_repair_assistant_contract", lambda *args, **kwargs: None)
    monkeypatch.setattr(router_area, "_should_attach_repair_suggestion", lambda _payload: False)
    monkeypatch.setattr(
        router_area,
        "build_visibility_diagnostics",
        lambda surface_profile, phase, guided_handoff=None, guided_flow_state=None: SimpleNamespace(
            rules=(),
            visible_capability_ids=("router",),
            visible_entry_capability_ids=("router",),
            hidden_capability_ids=(),
            hidden_category_counts={},
        ),
    )

    ctx = FakeContext(response=object())
    ctx.state["guided_flow_state"] = {
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
    }

    result = asyncio.run(router_area.router_get_status(ctx))

    assert result.guided_flow_state is not None
    assert result.guided_flow_state.domain_profile == "building"
    assert result.guided_flow_state.current_step == "establish_spatial_context"


def test_guided_register_part_updates_session_role_summary(monkeypatch):
    """guided_register_part should update the internal role registry and return refreshed guided status."""

    monkeypatch.setattr(router_area, "get_config", lambda: type("Cfg", (), {"MCP_SURFACE_PROFILE": "llm-guided"})())
    monkeypatch.setattr("server.adapters.mcp.session_capabilities._scene_object_names", lambda: {"Squirrel_Body"})
    monkeypatch.setattr(router_area, "get_router_status", lambda: {"enabled": True})
    monkeypatch.setattr(router_area, "_build_background_job_diagnostics", lambda: (0, {}, []))
    monkeypatch.setattr(router_area, "_build_timeout_policy_diagnostics", lambda _ctx: None)
    monkeypatch.setattr(router_area, "_build_task_runtime_diagnostics", lambda _ctx: None)
    monkeypatch.setattr(router_area, "_build_telemetry_diagnostics", lambda: None)
    monkeypatch.setattr(router_area, "_get_list_page_size", lambda _ctx: 50)
    monkeypatch.setattr(router_area, "run_repair_suggestion_assistant", lambda *args, **kwargs: None)
    monkeypatch.setattr(router_area, "to_repair_assistant_contract", lambda *args, **kwargs: None)
    monkeypatch.setattr(router_area, "_should_attach_repair_suggestion", lambda _payload: False)
    monkeypatch.setattr(
        router_area,
        "build_visibility_diagnostics",
        lambda surface_profile, phase, guided_handoff=None, guided_flow_state=None: SimpleNamespace(
            rules=(),
            visible_capability_ids=("router",),
            visible_entry_capability_ids=("router",),
            hidden_capability_ids=(),
            hidden_category_counts={},
        ),
    )

    ctx = FakeContext(response=object())
    set_session_capability_state(
        ctx,
        SessionCapabilityState(
            phase=SessionPhase.BUILD,
            goal="create a low-poly squirrel matching front and side reference images",
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
                "allowed_roles": ["body_core", "head_mass", "tail_mass"],
                "completed_roles": [],
                "missing_roles": ["body_core", "head_mass", "tail_mass"],
                "required_role_groups": ["primary_masses"],
                "step_status": "ready",
            },
        ),
    )

    result = asyncio.run(router_area.guided_register_part(ctx, object_name="Squirrel_Body", role="body_core"))
    session = get_session_capability_state(ctx)

    assert result.guided_flow_state is not None
    assert result.guided_flow_state.completed_roles == ["body_core"]
    assert result.guided_flow_state.missing_roles == ["head_mass", "tail_mass"]
    assert result.message == "Registered guided role 'body_core' for 'Squirrel_Body'."
    assert session.guided_part_registry is not None
    assert session.guided_part_registry[0]["object_name"] == "Squirrel_Body"
    assert result.guided_naming is not None
    assert result.guided_naming.status == "allowed"


def test_guided_register_part_returns_naming_warning_for_weak_abbreviation(monkeypatch):
    """guided_register_part should keep registration but return structured naming guidance for weak abbreviations."""

    monkeypatch.setattr(router_area, "get_config", lambda: type("Cfg", (), {"MCP_SURFACE_PROFILE": "llm-guided"})())
    monkeypatch.setattr("server.adapters.mcp.session_capabilities._scene_object_names", lambda: {"ForeL"})
    monkeypatch.setattr(router_area, "get_router_status", lambda: {"enabled": True})
    monkeypatch.setattr(router_area, "_build_background_job_diagnostics", lambda: (0, {}, []))
    monkeypatch.setattr(router_area, "_build_timeout_policy_diagnostics", lambda _ctx: None)
    monkeypatch.setattr(router_area, "_build_task_runtime_diagnostics", lambda _ctx: None)
    monkeypatch.setattr(router_area, "_build_telemetry_diagnostics", lambda: None)
    monkeypatch.setattr(router_area, "_get_list_page_size", lambda _ctx: 50)
    monkeypatch.setattr(router_area, "run_repair_suggestion_assistant", lambda *args, **kwargs: None)
    monkeypatch.setattr(router_area, "to_repair_assistant_contract", lambda *args, **kwargs: None)
    monkeypatch.setattr(router_area, "_should_attach_repair_suggestion", lambda _payload: False)
    monkeypatch.setattr(
        router_area,
        "build_visibility_diagnostics",
        lambda surface_profile, phase, guided_handoff=None, guided_flow_state=None: SimpleNamespace(
            rules=(),
            visible_capability_ids=("router",),
            visible_entry_capability_ids=("router",),
            hidden_capability_ids=(),
            hidden_category_counts={},
        ),
    )

    ctx = FakeContext(response=object())
    set_session_capability_state(
        ctx,
        SessionCapabilityState(
            phase=SessionPhase.BUILD,
            goal="create a low-poly squirrel matching front and side reference images",
            surface_profile="llm-guided",
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
                "allowed_roles": ["snout_mass", "ear_pair", "foreleg_pair", "hindleg_pair"],
                "completed_roles": ["body_core", "head_mass"],
                "missing_roles": ["snout_mass", "ear_pair", "foreleg_pair", "hindleg_pair"],
                "required_role_groups": ["secondary_parts"],
                "step_status": "ready",
            },
        ),
    )

    result = asyncio.run(router_area.guided_register_part(ctx, object_name="ForeL", role="foreleg_pair"))
    session = get_session_capability_state(ctx)

    assert result.guided_naming is not None
    assert result.guided_naming.status == "warning"
    assert "ForeLeg_L" in result.message
    assert session.guided_part_registry is not None
    assert any(item["object_name"] == "ForeL" for item in session.guided_part_registry)


def test_guided_register_part_blocks_placeholder_name_without_mutating_registry(monkeypatch):
    """guided_register_part should not mutate session state when naming policy blocks a placeholder name."""

    monkeypatch.setattr(router_area, "get_config", lambda: type("Cfg", (), {"MCP_SURFACE_PROFILE": "llm-guided"})())
    monkeypatch.setattr(router_area, "get_router_status", lambda: {"enabled": True})
    monkeypatch.setattr(router_area, "_build_background_job_diagnostics", lambda: (0, {}, []))
    monkeypatch.setattr(router_area, "_build_timeout_policy_diagnostics", lambda _ctx: None)
    monkeypatch.setattr(router_area, "_build_task_runtime_diagnostics", lambda _ctx: None)
    monkeypatch.setattr(router_area, "_build_telemetry_diagnostics", lambda: None)
    monkeypatch.setattr(router_area, "_get_list_page_size", lambda _ctx: 50)
    monkeypatch.setattr(router_area, "run_repair_suggestion_assistant", lambda *args, **kwargs: None)
    monkeypatch.setattr(router_area, "to_repair_assistant_contract", lambda *args, **kwargs: None)
    monkeypatch.setattr(router_area, "_should_attach_repair_suggestion", lambda _payload: False)
    monkeypatch.setattr(
        router_area,
        "build_visibility_diagnostics",
        lambda surface_profile, phase, guided_handoff=None, guided_flow_state=None: SimpleNamespace(
            rules=(),
            visible_capability_ids=("router",),
            visible_entry_capability_ids=("router",),
            hidden_capability_ids=(),
            hidden_category_counts={},
        ),
    )

    ctx = FakeContext(response=object())
    set_session_capability_state(
        ctx,
        SessionCapabilityState(
            phase=SessionPhase.BUILD,
            goal="create a low-poly squirrel matching front and side reference images",
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
                "allowed_roles": ["body_core", "head_mass", "tail_mass"],
                "completed_roles": [],
                "missing_roles": ["body_core", "head_mass", "tail_mass"],
                "required_role_groups": ["primary_masses"],
                "step_status": "ready",
            },
        ),
    )

    result = asyncio.run(router_area.guided_register_part(ctx, object_name="Sphere", role="body_core"))
    session = get_session_capability_state(ctx)

    assert result.guided_naming is not None
    assert result.guided_naming.status == "blocked"
    assert "Body" in result.message
    assert session.guided_part_registry is None


def test_guided_register_part_rejects_invalid_role_for_domain(monkeypatch):
    """guided_register_part should fail clearly when the requested role does not belong to the current overlay."""

    monkeypatch.setattr(router_area, "get_config", lambda: type("Cfg", (), {"MCP_SURFACE_PROFILE": "llm-guided"})())

    ctx = FakeContext(response=object())
    set_session_capability_state(
        ctx,
        SessionCapabilityState(
            phase=SessionPhase.BUILD,
            goal="create a low-poly squirrel matching front and side reference images",
            surface_profile="llm-guided",
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

    with pytest.raises(ValueError, match="Unknown guided part role 'roof_mass'"):
        asyncio.run(router_area.guided_register_part(ctx, object_name="Squirrel_Roof", role="roof_mass"))


def test_guided_register_part_rejects_missing_scene_object(monkeypatch):
    """guided_register_part should fail clearly when the requested object does not exist in Blender."""

    monkeypatch.setattr(router_area, "get_config", lambda: type("Cfg", (), {"MCP_SURFACE_PROFILE": "llm-guided"})())
    monkeypatch.setattr("server.adapters.mcp.session_capabilities._scene_object_names", lambda: {"Squirrel_Body"})

    ctx = FakeContext(response=object())
    set_session_capability_state(
        ctx,
        SessionCapabilityState(
            phase=SessionPhase.BUILD,
            goal="create a low-poly squirrel matching front and side reference images",
            surface_profile="llm-guided",
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

    with pytest.raises(ValueError, match="requires an existing Blender object named 'MissingHead'"):
        asyncio.run(router_area.guided_register_part(ctx, object_name="MissingHead", role="head_mass"))


def test_guided_register_part_fails_when_scene_validation_is_unavailable(monkeypatch):
    """guided_register_part should fail clearly when Blender scene validation is unavailable."""

    monkeypatch.setattr(router_area, "get_config", lambda: type("Cfg", (), {"MCP_SURFACE_PROFILE": "llm-guided"})())
    monkeypatch.setattr(
        "server.adapters.mcp.session_capabilities._scene_object_names",
        lambda: (_ for _ in ()).throw(
            RuntimeError(
                "Blender Error: Could not connect to Blender Addon. Is Blender running with the addon installed?"
            )
        ),
    )

    ctx = FakeContext(response=object())
    set_session_capability_state(
        ctx,
        SessionCapabilityState(
            phase=SessionPhase.BUILD,
            goal="create a low-poly squirrel matching front and side reference images",
            surface_profile="llm-guided",
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

    with pytest.raises(ValueError, match="could not validate object 'Squirrel_Body' against the Blender scene"):
        asyncio.run(router_area.guided_register_part(ctx, object_name="Squirrel_Body", role="body_core"))
