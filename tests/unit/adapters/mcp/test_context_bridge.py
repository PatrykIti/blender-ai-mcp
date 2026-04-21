"""Tests for the MCP context, session, and execution bridge."""

from __future__ import annotations

from dataclasses import dataclass, field

from server.adapters.mcp.context_utils import (
    ctx_error,
    ctx_info,
    ctx_progress,
    ctx_warning,
    get_session_phase,
    get_session_value,
    set_session_phase,
    set_session_value,
)
from server.adapters.mcp.execution_context import MCPExecutionContext
from server.adapters.mcp.execution_report import ExecutionStep, MCPExecutionReport
from server.adapters.mcp.router_helper import route_tool_call, route_tool_call_report
from server.adapters.mcp.session_capabilities import (
    SessionCapabilityState,
    get_session_capability_state,
    set_session_capability_state,
)
from server.adapters.mcp.session_phase import SessionPhase


@dataclass
class FakeContext:
    """Minimal sync Context stand-in for unit tests."""

    state: dict[str, object] = field(default_factory=dict)
    messages: list[tuple[str, str]] = field(default_factory=list)
    progress_events: list[tuple[float, float | None, str | None]] = field(default_factory=list)

    def get_state(self, key: str):
        return self.state.get(key)

    def set_state(self, key: str, value, *, serializable: bool = True) -> None:
        self.state[key] = value

    def info(self, message: str, logger_name=None, extra=None) -> None:
        self.messages.append(("info", message))

    def warning(self, message: str, logger_name=None, extra=None) -> None:
        self.messages.append(("warning", message))

    def error(self, message: str, logger_name=None, extra=None) -> None:
        self.messages.append(("error", message))

    def report_progress(self, progress: float, total: float | None = None, message: str | None = None) -> None:
        self.progress_events.append((progress, total, message))


@dataclass
class AsyncFakeContext:
    """Async Context stand-in to exercise sync bridge helpers safely."""

    messages: list[tuple[str, str]] = field(default_factory=list)
    progress_events: list[tuple[float, float | None, str | None]] = field(default_factory=list)

    async def info(self, message: str, logger_name=None, extra=None) -> None:
        self.messages.append(("info", message))

    async def warning(self, message: str, logger_name=None, extra=None) -> None:
        self.messages.append(("warning", message))

    async def error(self, message: str, logger_name=None, extra=None) -> None:
        self.messages.append(("error", message))

    async def report_progress(self, progress: float, total: float | None = None, message: str | None = None) -> None:
        self.progress_events.append((progress, total, message))


def test_session_helpers_round_trip_phase_and_values():
    """Session helpers should read and write sync Context state consistently."""

    ctx = FakeContext()

    assert get_session_phase(ctx) == "bootstrap"
    assert get_session_value(ctx, "missing", "fallback") == "fallback"

    set_session_phase(ctx, "planning")
    set_session_value(ctx, "surface_profile", "llm-guided")

    assert get_session_phase(ctx) == "planning"
    assert get_session_value(ctx, "surface_profile") == "llm-guided"


def test_context_logging_and_progress_helpers_are_best_effort():
    """Context helpers should write sync notifications and progress without throwing."""

    ctx = FakeContext()

    ctx_info(ctx, "hello")
    ctx_warning(ctx, "warn")
    ctx_error(ctx, "oops")
    ctx_progress(ctx, 1, 4, "step")

    assert ctx.messages == [("info", "hello"), ("warning", "warn"), ("error", "oops")]
    assert ctx.progress_events == [(1, 4, "step")]


def test_context_logging_and_progress_helpers_await_async_methods_without_warning():
    """Sync bridge helpers should execute async Context methods instead of leaking coroutines."""

    ctx = AsyncFakeContext()

    ctx_info(ctx, "hello")
    ctx_warning(ctx, "warn")
    ctx_error(ctx, "oops")
    ctx_progress(ctx, 1, 4, "step")

    assert ctx.messages == [("info", "hello"), ("warning", "warn"), ("error", "oops")]
    assert ctx.progress_events == [(1, 4, "step")]


def test_execution_report_renders_legacy_text_for_multi_step_sequence():
    """Structured reports should still support the current string-based adapter contract."""

    report = MCPExecutionReport(
        context=MCPExecutionContext(tool_name="mesh_extrude_region", params={"move": [0, 0, 1]}),
        router_enabled=True,
        router_applied=True,
        router_disposition="corrected",
        steps=(
            ExecutionStep(tool_name="scene_set_mode", params={"mode": "EDIT"}, result="OK"),
            ExecutionStep(tool_name="mesh_extrude_region", params={"move": [0, 0, 1]}, result="Extruded"),
        ),
    )

    assert report.to_dict()["context"]["tool_name"] == "mesh_extrude_region"
    assert report.to_legacy_text() == "[Step 1: scene_set_mode] OK\n[Step 2: mesh_extrude_region] Extruded"


def test_route_tool_call_report_returns_direct_execution_when_router_disabled(monkeypatch):
    """route_tool_call_report should still build a structured report on direct execution."""

    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: False)

    report = route_tool_call_report(
        tool_name="scene_list_objects",
        params={},
        direct_executor=lambda: "['Cube']",
    )

    assert report.router_enabled is False
    assert report.router_applied is False
    assert report.router_disposition == "bypassed"
    assert report.steps[0].tool_name == "scene_list_objects"
    assert report.to_legacy_text() == "['Cube']"


def test_route_tool_call_report_bypasses_router_for_scene_utility_tools(monkeypatch):
    """Scene utility/read-side tools should not trigger pending workflow execution."""

    class FailingRouter:
        def process_llm_tool_call(self, tool_name, params, prompt):
            raise AssertionError("scene_* tools should bypass router processing")

    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: True)
    monkeypatch.setattr("server.adapters.mcp.router_helper.get_router", lambda: FailingRouter())

    report = route_tool_call_report(
        tool_name="scene_clean_scene",
        params={"keep_lights_and_cameras": True},
        direct_executor=lambda: "Scene cleaned",
    )

    assert report.router_enabled is True
    assert report.router_applied is False
    assert report.router_disposition == "bypassed"
    assert report.steps[0].result == "Scene cleaned"


def test_route_tool_call_report_exposes_guided_family_and_role_for_direct_call(monkeypatch):
    """Direct guided calls should still resolve family and role metadata in the execution context."""

    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: False)

    report = route_tool_call_report(
        tool_name="modeling_create_primitive",
        params={"primitive_type": "Sphere", "name": "Squirrel_Body", "guided_role": "body_core"},
        direct_executor=lambda: "Created Sphere named 'Squirrel_Body'",
    )

    assert report.context.guided_tool_family == "primary_masses"
    assert report.context.guided_role == "body_core"
    assert report.context.guided_role_group is None


def test_route_tool_call_report_uses_final_corrected_tool_for_guided_family_metadata(monkeypatch):
    """Corrected guided calls should resolve family metadata from the final effective tool call."""

    class Router:
        def process_llm_tool_call(self, tool_name, params, prompt):
            return [
                {
                    "tool": "macro_finish_form",
                    "params": {"target_object": "Housing"},
                }
            ]

    class Dispatcher:
        def execute(self, tool_name, params):
            assert tool_name == "macro_finish_form"
            return "Finished Housing"

    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: True)
    monkeypatch.setattr("server.adapters.mcp.router_helper.get_router", lambda: Router())
    monkeypatch.setattr("server.adapters.mcp.router_helper.get_dispatcher", lambda: Dispatcher())

    report = route_tool_call_report(
        tool_name="modeling_create_primitive",
        params={"primitive_type": "Cube", "name": "Housing"},
        direct_executor=lambda: "should not run",
    )

    assert report.router_applied is True
    assert report.context.guided_tool_family == "finish"
    assert report.steps[-1].tool_name == "macro_finish_form"


def test_route_tool_call_report_fail_closes_when_guided_family_is_not_allowed(monkeypatch):
    """Guided execution policy should block a disallowed family even before direct execution runs."""

    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: False)
    monkeypatch.setattr("server.adapters.mcp.router_helper._get_active_surface_profile", lambda: "llm-guided")
    monkeypatch.setattr(
        "server.adapters.mcp.router_helper._get_active_session_state",
        lambda: SessionCapabilityState(
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
                "completed_roles": ["body_core"],
                "missing_roles": ["head_mass", "tail_mass"],
                "required_role_groups": ["primary_masses"],
                "step_status": "ready",
            },
        ),
    )

    report = route_tool_call_report(
        tool_name="macro_finish_form",
        params={"target_object": "Squirrel_Body"},
        direct_executor=lambda: "should not run",
    )

    assert report.router_disposition == "failed_closed_error"
    assert "tool family 'finish'" in str(report.error)
    assert report.context.guided_tool_family == "finish"


def test_route_tool_call_report_fail_closes_when_guided_role_is_not_allowed(monkeypatch):
    """Guided execution policy should block explicit roles that do not belong to the current step."""

    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: False)
    monkeypatch.setattr("server.adapters.mcp.router_helper._get_active_surface_profile", lambda: "llm-guided")
    monkeypatch.setattr(
        "server.adapters.mcp.router_helper._get_active_session_state",
        lambda: SessionCapabilityState(
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
                "completed_roles": ["body_core"],
                "missing_roles": ["head_mass", "tail_mass"],
                "required_role_groups": ["primary_masses"],
                "step_status": "ready",
            },
        ),
    )

    report = route_tool_call_report(
        tool_name="modeling_create_primitive",
        params={"primitive_type": "Cone", "name": "Squirrel_Ear_L", "guided_role": "ear_pair"},
        direct_executor=lambda: "should not run",
    )

    assert report.router_disposition == "failed_closed_error"
    assert "tool family 'secondary_parts'" in str(report.error)
    assert report.context.guided_tool_family == "secondary_parts"
    assert report.context.guided_role == "ear_pair"


def test_route_tool_call_report_fail_closes_when_guided_role_is_missing_for_build_family(monkeypatch):
    """Primary/secondary build tools should require semantic part roles on guided surfaces."""

    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: False)
    monkeypatch.setattr("server.adapters.mcp.router_helper._get_active_surface_profile", lambda: "llm-guided")
    monkeypatch.setattr(
        "server.adapters.mcp.router_helper._get_active_session_state",
        lambda: SessionCapabilityState(
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

    report = route_tool_call_report(
        tool_name="modeling_create_primitive",
        params={"primitive_type": "Sphere", "name": "Squirrel_Body"},
        direct_executor=lambda: "should not run",
    )

    assert report.router_disposition == "failed_closed_error"
    assert "requires an explicit semantic role" in str(report.error)
    assert report.context.guided_tool_family == "primary_masses"
    assert report.context.guided_role is None


def test_route_tool_call_report_records_guided_naming_warning_for_weak_abbreviation(monkeypatch):
    """Role-sensitive guided build calls should keep deterministic naming warnings in policy_context."""

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
                "allowed_roles": ["snout_mass", "ear_pair", "foreleg_pair", "hindleg_pair"],
                "completed_roles": ["body_core", "head_mass"],
                "missing_roles": ["snout_mass", "ear_pair", "foreleg_pair", "hindleg_pair"],
                "required_role_groups": ["secondary_parts"],
                "step_status": "ready",
            },
        ),
    )

    report = route_tool_call_report(
        tool_name="modeling_create_primitive",
        params={"primitive_type": "Cone", "name": "ForeL", "guided_role": "foreleg_pair"},
        direct_executor=lambda: "Created Cone named 'ForeL'",
    )

    assert report.router_disposition == "bypassed"
    assert report.policy_context is not None
    assert report.policy_context["guided_naming"]["status"] == "warning"
    assert "ForeLeg_L" in report.policy_context["guided_naming"]["message"]


def test_route_tool_call_report_blocks_third_object_for_completed_pair_role(monkeypatch):
    """Pair roles should allow two siblings but block over-cardinality calls."""

    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: False)
    monkeypatch.setattr("server.adapters.mcp.router_helper._get_active_surface_profile", lambda: "llm-guided")
    monkeypatch.setattr(
        "server.adapters.mcp.router_helper._get_active_session_state",
        lambda: SessionCapabilityState(
            phase=SessionPhase.BUILD,
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
                "required_checks": [],
                "required_prompts": ["guided_session_start", "reference_guided_creature_build"],
                "preferred_prompts": ["workflow_router_first"],
                "next_actions": ["run_checkpoint_iterate"],
                "blocked_families": [],
                "allowed_families": ["primary_masses", "secondary_parts", "checkpoint_iterate"],
                "allowed_roles": ["foreleg_pair", "hindleg_pair"],
                "completed_roles": ["body_core", "head_mass", "tail_mass", "snout_mass", "ear_pair"],
                "missing_roles": ["foreleg_pair", "hindleg_pair"],
                "required_role_groups": ["checkpoint_iterate"],
                "role_counts": {"ear_pair": 2},
                "role_cardinality": {"ear_pair": 2},
                "role_objects": {"ear_pair": ["Ear_L", "Ear_R"]},
                "step_status": "needs_checkpoint",
            },
        ),
    )

    report = route_tool_call_report(
        tool_name="modeling_create_primitive",
        params={"primitive_type": "Cone", "name": "Ear_Center", "guided_role": "ear_pair"},
        direct_executor=lambda: "should not run",
    )

    assert report.router_disposition == "failed_closed_error"
    assert "Guided execution blocked role 'ear_pair'" in str(report.error)
    assert report.context.guided_role == "ear_pair"


def test_route_tool_call_report_blocks_placeholder_name_for_role_sensitive_build(monkeypatch):
    """Role-sensitive guided build calls should fail closed on placeholder names."""

    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: False)
    monkeypatch.setattr("server.adapters.mcp.router_helper._get_active_surface_profile", lambda: "llm-guided")
    monkeypatch.setattr(
        "server.adapters.mcp.router_helper._get_active_session_state",
        lambda: SessionCapabilityState(
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

    report = route_tool_call_report(
        tool_name="modeling_create_primitive",
        params={"primitive_type": "Sphere", "name": "Sphere", "guided_role": "body_core"},
        direct_executor=lambda: "should not run",
    )

    assert report.router_disposition == "failed_closed_error"
    assert "Guided naming blocked object name 'Sphere'" in str(report.error)
    assert report.policy_context is not None
    assert report.policy_context["guided_naming"]["status"] == "blocked"


def test_route_tool_call_report_allows_registered_object_transform_without_explicit_role(monkeypatch):
    """A previously registered object should not need guided_role repeated on every transform call."""

    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: False)
    monkeypatch.setattr("server.adapters.mcp.router_helper._get_active_surface_profile", lambda: "llm-guided")
    monkeypatch.setattr(
        "server.adapters.mcp.router_helper._get_active_session_state",
        lambda: SessionCapabilityState(
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
                "completed_roles": ["body_core"],
                "missing_roles": ["head_mass", "tail_mass"],
                "required_role_groups": ["primary_masses"],
                "step_status": "ready",
            },
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

    report = route_tool_call_report(
        tool_name="modeling_transform_object",
        params={"name": "Squirrel_Body", "scale": [0.9, 0.8, 1.2]},
        direct_executor=lambda: "Transformed object 'Squirrel_Body'",
    )

    assert report.router_disposition == "bypassed"
    assert report.context.guided_role == "body_core"
    assert report.steps[0].result == "Transformed object 'Squirrel_Body'"


def test_route_tool_call_updates_guided_registry_after_scene_rename(monkeypatch):
    """Successful scene renames should keep guided part registration aligned with the new object name."""

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
                "completed_roles": ["body_core"],
                "missing_roles": ["head_mass", "tail_mass"],
                "required_role_groups": ["primary_masses"],
                "step_status": "ready",
            },
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

    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: False)
    monkeypatch.setattr("server.adapters.mcp.router_helper._get_active_context", lambda: ctx)
    monkeypatch.setattr("server.adapters.mcp.session_capabilities._scene_object_names", lambda: {"Body"})
    monkeypatch.setattr(
        "server.adapters.mcp.router_helper._get_active_session_state",
        lambda: get_session_capability_state(ctx),
    )

    result = route_tool_call(
        tool_name="scene_rename_object",
        params={"old_name": "Squirrel_Body", "new_name": "Body"},
        direct_executor=lambda: "Renamed 'Squirrel_Body' to 'Body'",
    )
    report = route_tool_call_report(
        tool_name="modeling_transform_object",
        params={"name": "Body", "scale": [0.9, 0.8, 1.2]},
        direct_executor=lambda: "Transformed object 'Body'",
    )
    state = get_session_capability_state(ctx)

    assert result == "Renamed 'Squirrel_Body' to 'Body'"
    assert state.guided_part_registry is not None
    assert state.guided_part_registry[0]["object_name"] == "Body"
    assert report.context.guided_role == "body_core"


def test_route_tool_call_removes_guided_registry_entries_after_join(monkeypatch):
    """Joining registered parts should drop stale source registrations until the result is re-registered."""

    ctx = FakeContext()
    set_session_capability_state(
        ctx,
        SessionCapabilityState(
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
                "allowed_roles": ["snout_mass", "ear_pair", "foreleg_pair", "hindleg_pair"],
                "completed_roles": ["body_core", "head_mass", "ear_pair"],
                "missing_roles": ["snout_mass", "foreleg_pair", "hindleg_pair"],
                "required_role_groups": ["secondary_parts"],
                "step_status": "ready",
            },
            guided_part_registry=[
                {
                    "object_name": "Ear_L",
                    "role": "ear_pair",
                    "role_group": "secondary_parts",
                    "status": "registered",
                },
                {
                    "object_name": "Ear_R",
                    "role": "ear_pair",
                    "role_group": "secondary_parts",
                    "status": "registered",
                },
            ],
        ),
    )

    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: False)
    monkeypatch.setattr("server.adapters.mcp.router_helper._get_active_context", lambda: ctx)

    result = route_tool_call(
        tool_name="modeling_join_objects",
        params={"object_names": ["Ear_L", "Ear_R"]},
        direct_executor=lambda: "Objects Ear_L, Ear_R joined into 'Ear_R'. Joined count: 2",
    )
    state = get_session_capability_state(ctx)

    assert result == "Objects Ear_L, Ear_R joined into 'Ear_R'. Joined count: 2"
    assert state.guided_part_registry is None
    assert state.guided_flow_state is not None
    assert "ear_pair" not in state.guided_flow_state["completed_roles"]


def test_route_tool_call_removes_guided_registry_entry_after_separate(monkeypatch):
    """Separating a registered object should drop the stale source registration."""

    ctx = FakeContext()
    set_session_capability_state(
        ctx,
        SessionCapabilityState(
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
                "allowed_roles": ["snout_mass", "ear_pair", "foreleg_pair", "hindleg_pair"],
                "completed_roles": ["body_core", "head_mass", "ear_pair"],
                "missing_roles": ["snout_mass", "foreleg_pair", "hindleg_pair"],
                "required_role_groups": ["secondary_parts"],
                "step_status": "ready",
            },
            guided_part_registry=[
                {
                    "object_name": "Squirrel_Ears",
                    "role": "ear_pair",
                    "role_group": "secondary_parts",
                    "status": "registered",
                }
            ],
        ),
    )

    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: False)
    monkeypatch.setattr("server.adapters.mcp.router_helper._get_active_context", lambda: ctx)

    result = route_tool_call(
        tool_name="modeling_separate_object",
        params={"name": "Squirrel_Ears", "type": "LOOSE"},
        direct_executor=lambda: "['Ear_L', 'Ear_R']",
    )
    state = get_session_capability_state(ctx)

    assert result == "['Ear_L', 'Ear_R']"
    assert state.guided_part_registry is None
    assert state.guided_flow_state is not None
    assert "ear_pair" not in state.guided_flow_state["completed_roles"]


def test_route_tool_call_report_allows_registered_primary_object_transform_during_secondary_step(monkeypatch):
    """A previously registered primary object should remain transformable during secondary steps."""

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
            guided_part_registry=[
                {
                    "object_name": "Squirrel_Head",
                    "role": "head_mass",
                    "role_group": "primary_masses",
                    "status": "registered",
                }
            ],
        ),
    )

    report = route_tool_call_report(
        tool_name="modeling_transform_object",
        params={"name": "Squirrel_Head", "scale": [1.1, 0.9, 0.95]},
        direct_executor=lambda: "Transformed object 'Squirrel_Head'",
    )

    assert report.router_disposition == "bypassed"
    assert report.context.guided_tool_family == "primary_masses"
    assert report.context.guided_role == "head_mass"


def test_route_tool_call_report_keeps_collection_manage_as_utility_even_for_registered_objects(monkeypatch):
    """Workset/housekeeping operations should not inherit role-group blocking from the moved object."""

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
            guided_part_registry=[
                {
                    "object_name": "Squirrel_Head",
                    "role": "head_mass",
                    "role_group": "primary_masses",
                    "status": "registered",
                }
            ],
        ),
    )

    report = route_tool_call_report(
        tool_name="collection_manage",
        params={"action": "move_object", "collection_name": "Squirrel", "object_name": "Squirrel_Head"},
        direct_executor=lambda: "Moved 'Squirrel_Head' to 'Squirrel' (was in: Collection)",
    )

    assert report.router_disposition == "bypassed"
    assert report.context.guided_tool_family == "utility"
    assert report.steps[0].result.startswith("Moved 'Squirrel_Head'")


def test_route_tool_call_marks_guided_spatial_state_stale_after_successful_transform(monkeypatch):
    """Successful guided build mutations should dirty the spatial layer for later re-arm logic."""

    from fastmcp.server.context import _current_context

    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: False)
    monkeypatch.setattr("server.adapters.mcp.router_helper._get_active_surface_profile", lambda: "llm-guided")

    ctx = FakeContext()
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
                "active_target_scope": {
                    "scope_kind": "object_set",
                    "primary_target": "Squirrel_Body",
                    "object_names": ["Squirrel_Body", "Squirrel_Head"],
                    "object_count": 2,
                },
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
                "completed_roles": ["body_core"],
                "missing_roles": ["head_mass", "tail_mass"],
                "required_role_groups": ["primary_masses"],
                "step_status": "ready",
            },
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

    token = _current_context.set(ctx)
    try:
        result = route_tool_call(
            tool_name="modeling_transform_object",
            params={"name": "Squirrel_Body", "scale": [0.9, 0.8, 1.2]},
            direct_executor=lambda: "Transformed object 'Squirrel_Body'",
        )
    finally:
        _current_context.reset(token)

    state = get_session_capability_state(ctx)

    assert result == "Transformed object 'Squirrel_Body'"
    assert state.guided_flow_state is not None
    assert state.guided_flow_state["spatial_state_version"] == 1
    assert state.guided_flow_state["spatial_state_stale"] is True
    assert state.guided_flow_state["spatial_refresh_required"] is False
