"""Tests for session phase and capability state helpers."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, cast

from server.adapters.mcp.session_capabilities import (
    SessionCapabilityState,
    apply_visibility_for_session_state,
    build_guided_reference_readiness,
    clear_session_goal_state,
    get_session_capability_state,
    infer_phase_from_router_status,
    merge_resolved_params_with_session_answers,
    record_router_execution_outcome,
    update_session_from_router_goal,
)
from server.adapters.mcp.session_phase import (
    FIRST_PASS_ACTIVE_PHASES,
    SessionPhase,
    coerce_session_phase,
)
from server.adapters.mcp.session_state import get_session_value_async, set_session_value_async
from server.adapters.mcp.transforms.visibility_policy import (
    GUIDED_BUILD_ESCAPE_HATCH_TOOLS,
    GUIDED_DISCOVERY_TOOLS,
    GUIDED_ENTRY_TOOLS,
)


@dataclass
class FakeContext:
    """Minimal Context-like state store for unit tests."""

    state: dict[str, object] = field(default_factory=dict)

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


@dataclass
class AsyncStateContext:
    """Context-like object exposing async state methods."""

    state: dict[str, object] = field(default_factory=dict)

    async def get_state(self, key: str):
        return self.state.get(key)

    async def set_state(self, key: str, value, *, serializable: bool = True) -> None:
        self.state[key] = value


def test_session_phase_coercion_uses_canonical_subset_defaults():
    """Unknown values should collapse back to bootstrap instead of inventing phase labels."""

    assert coerce_session_phase(None) == SessionPhase.BOOTSTRAP
    assert coerce_session_phase("planning") == SessionPhase.PLANNING
    assert coerce_session_phase("inspect") == SessionPhase.BOOTSTRAP
    assert FIRST_PASS_ACTIVE_PHASES == (
        SessionPhase.BOOTSTRAP,
        SessionPhase.PLANNING,
        SessionPhase.BUILD,
        SessionPhase.INSPECT_VALIDATE,
    )


def test_infer_phase_from_router_status_uses_coarse_first_pass_mapping():
    """Router statuses should map onto the coarse first-pass phase set."""

    assert infer_phase_from_router_status("needs_input") == SessionPhase.PLANNING
    assert infer_phase_from_router_status("no_match") == SessionPhase.PLANNING
    assert infer_phase_from_router_status("ready") == SessionPhase.BUILD


def test_update_session_from_router_goal_persists_goal_and_clarification_state():
    """router_set_goal responses should update session state consistently."""

    ctx = FakeContext()

    state = update_session_from_router_goal(
        ctx,
        "chair",
        {
            "status": "needs_input",
            "unresolved": [{"param": "height"}],
        },
    )

    assert state.phase == SessionPhase.PLANNING
    assert state.goal == "chair"
    assert state.pending_clarification == [{"param": "height"}]
    assert get_session_capability_state(ctx).last_router_status == "needs_input"
    assert get_session_capability_state(ctx).policy_context is None


def test_update_session_from_router_goal_persists_guided_handoff():
    """Explicit guided handoff payloads should remain available in session diagnostics."""

    ctx = FakeContext()

    state = update_session_from_router_goal(
        ctx,
        "low poly squirrel",
        {
            "status": "no_match",
            "continuation_mode": "guided_manual_build",
            "phase_hint": "build",
            "guided_handoff": {
                "kind": "guided_manual_build",
                "target_phase": "build",
                "surface_profile": "llm-guided",
                "direct_tools": ["scene_create", "macro_finish_form"],
                "supporting_tools": ["reference_images", "router_get_status"],
                "discovery_tools": ["search_tools", "call_tool"],
                "workflow_import_recommended": False,
                "message": "Continue on the guided build surface.",
            },
        },
    )

    assert state.phase == SessionPhase.BUILD
    assert state.guided_handoff is not None
    assert state.guided_handoff["kind"] == "guided_manual_build"
    assert get_session_capability_state(ctx).guided_handoff["target_phase"] == "build"


def test_clear_session_goal_state_resets_goal_but_keeps_coarse_planning_phase():
    """Clearing the current goal should reset goal-scoped state but keep the session usable."""

    ctx = FakeContext()
    update_session_from_router_goal(
        ctx,
        "chair",
        {
            "status": "ready",
            "guided_handoff": {
                "kind": "guided_manual_build",
                "target_phase": "build",
                "surface_profile": "llm-guided",
                "direct_tools": ["scene_create"],
                "supporting_tools": ["router_get_status"],
                "discovery_tools": ["search_tools", "call_tool"],
                "workflow_import_recommended": False,
                "message": "Continue on the guided build surface.",
            },
        },
    )

    state = clear_session_goal_state(ctx)

    assert state.phase == SessionPhase.PLANNING
    assert state.goal is None
    assert state.pending_clarification is None
    assert state.policy_context is None
    assert state.guided_handoff is None


def test_update_session_from_router_goal_persists_policy_context():
    """Session state should keep the last explicit policy decision for operator transparency."""

    ctx = FakeContext()

    state = update_session_from_router_goal(
        ctx,
        "chair",
        {
            "status": "needs_input",
            "policy_context": {
                "decision": "ask",
                "reason": "medium confidence",
                "source": "workflow_match",
                "score": 0.7,
                "band": "medium",
                "risk": "high",
            },
        },
    )

    assert state.policy_context["decision"] == "ask"


def test_build_guided_reference_readiness_reports_pending_goal_inputs():
    """Guided reference readiness should expose goal-input blockers explicitly."""

    readiness = build_guided_reference_readiness(
        SessionCapabilityState(
            phase=SessionPhase.PLANNING,
            goal="chair",
            pending_clarification=[{"param": "height"}],
            last_router_status="needs_input",
        )
    )

    assert readiness.status == "blocked"
    assert readiness.goal == "chair"
    assert readiness.goal_input_pending is True
    assert readiness.blocking_reason == "goal_input_pending"
    assert readiness.next_action == "answer_pending_goal_questions"


def test_build_guided_reference_readiness_ignores_pending_references_from_other_goals():
    """Unrelated staged refs should not block compare/iterate on an otherwise ready goal."""

    readiness = build_guided_reference_readiness(
        SessionCapabilityState(
            phase=SessionPhase.BUILD,
            goal="table",
            last_router_status="ready",
            reference_images=[
                {
                    "reference_id": "ref_table",
                    "goal": "table",
                    "label": "table_ref",
                    "stored_path": "/tmp/table.png",
                }
            ],
            pending_reference_images=[
                {
                    "reference_id": "ref_chair",
                    "goal": "chair",
                    "label": "chair_ref",
                    "stored_path": "/tmp/chair.png",
                }
            ],
        )
    )

    assert readiness.status == "ready"
    assert readiness.compare_ready is True
    assert readiness.iterate_ready is True
    assert readiness.pending_reference_count == 0
    assert readiness.blocking_reason is None


def test_apply_visibility_for_session_state_uses_stored_surface_profile():
    """Session visibility should be derived from the persisted surface profile and phase."""

    ctx = FakeContext()
    state = SessionCapabilityState(
        phase=SessionPhase.BUILD,
        surface_profile="llm-guided",
    )

    asyncio.run(apply_visibility_for_session_state(ctx, state))

    calls = ctx.state["_visibility_calls"]
    assert calls[0] == ("reset_visibility", {})
    assert any(name == "enable_components" and call["names"] == set(GUIDED_ENTRY_TOOLS) for name, call in calls[1:])
    assert any(name == "enable_components" and call["names"] == set(GUIDED_DISCOVERY_TOOLS) for name, call in calls[1:])
    assert any(
        name == "enable_components" and call["names"] == set(GUIDED_BUILD_ESCAPE_HATCH_TOOLS)
        for name, call in calls[1:]
    )


def test_apply_visibility_for_session_state_can_use_creature_handoff_recipe():
    """Session visibility should narrow to the creature handoff recipe when one is active."""

    ctx = FakeContext()
    state = SessionCapabilityState(
        phase=SessionPhase.BUILD,
        surface_profile="llm-guided",
        guided_handoff={
            "kind": "guided_manual_build",
            "recipe_id": "low_poly_creature_blockout",
            "direct_tools": ["modeling_create_primitive", "mesh_extrude_region", "inspect_scene"],
            "supporting_tools": ["reference_images", "reference_iterate_stage_checkpoint", "router_get_status"],
            "discovery_tools": ["search_tools", "call_tool"],
            "workflow_import_recommended": False,
            "message": "Continue on the guided creature blockout surface.",
        },
    )

    asyncio.run(apply_visibility_for_session_state(ctx, state))

    calls = ctx.state["_visibility_calls"]
    assert any(
        name == "enable_components"
        and call["names"]
        == {
            "modeling_create_primitive",
            "mesh_extrude_region",
            "inspect_scene",
            "reference_images",
            "reference_iterate_stage_checkpoint",
            "router_get_status",
        }
        for name, call in calls[1:]
    )


def test_update_session_from_router_goal_persists_pending_elicitation_fields():
    """needs_input router responses should persist stable elicitation identifiers."""

    ctx = FakeContext()

    state = update_session_from_router_goal(
        ctx,
        "chair",
        {
            "status": "needs_input",
            "workflow": "chair_workflow",
            "clarification": {
                "question_set_id": "qs_test",
            },
            "elicitation_action": "cancel",
        },
        provided_answers={"width": 1.0},
    )

    assert state.pending_elicitation_id == "elic_qs_test"
    assert state.pending_workflow_name == "chair_workflow"
    assert state.pending_question_set_id == "qs_test"
    assert state.partial_answers == {"width": 1.0}
    assert state.last_elicitation_action == "cancel"


def test_update_session_from_router_goal_adopts_pending_references_only_after_goal_is_ready():
    """Pending references should stay staged across needs_input and adopt on ready for the same goal."""

    ctx = FakeContext(
        state={
            "pending_reference_images": [
                {
                    "reference_id": "ref_1",
                    "goal": "chair",
                    "label": "front_ref",
                    "stored_path": "/tmp/front.png",
                }
            ]
        }
    )

    blocked_state = update_session_from_router_goal(
        ctx,
        "chair",
        {
            "status": "needs_input",
            "workflow": "chair_workflow",
            "unresolved": [{"param": "height"}],
        },
    )
    ready_state = update_session_from_router_goal(
        ctx,
        "chair",
        {
            "status": "ready",
            "workflow": "chair_workflow",
            "resolved": {"height": 1.0},
            "unresolved": [],
            "resolution_sources": {"height": "user"},
            "message": "ok",
            "executed": 0,
        },
    )

    assert blocked_state.reference_images is None
    assert blocked_state.pending_reference_images is not None
    assert ready_state.reference_images is not None
    assert ready_state.reference_images[0]["goal"] == "chair"
    assert ready_state.pending_reference_images is None


def test_update_session_from_router_goal_deduplicates_adopted_references_by_reference_id():
    """Ready transitions should not duplicate already-active reference records."""

    ctx = FakeContext(
        state={
            "goal": "chair",
            "reference_images": [
                {
                    "reference_id": "ref_1",
                    "goal": "chair",
                    "label": "front_ref",
                    "stored_path": "/tmp/front.png",
                }
            ],
            "pending_reference_images": [
                {
                    "reference_id": "ref_1",
                    "goal": "chair",
                    "label": "front_ref_pending",
                    "stored_path": "/tmp/front.png",
                },
                {
                    "reference_id": "ref_2",
                    "goal": "chair",
                    "label": "side_ref",
                    "stored_path": "/tmp/side.png",
                },
            ],
        }
    )

    state = update_session_from_router_goal(
        ctx,
        "chair",
        {
            "status": "ready",
            "workflow": "chair_workflow",
            "resolved": {},
            "unresolved": [],
            "resolution_sources": {},
            "message": "ok",
            "executed": 0,
        },
    )

    assert state.reference_images == [
        {
            "reference_id": "ref_1",
            "goal": "chair",
            "label": "front_ref",
            "stored_path": "/tmp/front.png",
        },
        {
            "reference_id": "ref_2",
            "goal": "chair",
            "label": "side_ref",
            "stored_path": "/tmp/side.png",
        },
    ]
    assert state.pending_reference_images is None


def test_update_session_from_router_goal_keeps_goal_mismatched_pending_references_explicit():
    """Pending references intended for another goal should not silently retarget."""

    ctx = FakeContext(
        state={
            "pending_reference_images": [
                {
                    "reference_id": "ref_legacy",
                    "goal": "chair",
                    "label": "chair_ref",
                    "stored_path": "/tmp/chair.png",
                }
            ]
        }
    )

    state = update_session_from_router_goal(
        ctx,
        "table",
        {
            "status": "ready",
            "workflow": "table_workflow",
            "resolved": {},
            "unresolved": [],
            "resolution_sources": {},
            "message": "ok",
            "executed": 0,
        },
    )

    assert state.reference_images is None
    assert state.pending_reference_images is not None
    assert state.pending_reference_images[0]["goal"] == "chair"


def test_merge_resolved_params_with_session_answers_prefers_new_values():
    """Explicit follow-up answers should override older partial answers."""

    ctx = FakeContext(
        state={
            "partial_answers": {"width": 1.0, "height": 2.0},
        }
    )

    merged = merge_resolved_params_with_session_answers(ctx, {"height": 3.0, "depth": 0.5})

    assert merged == {"width": 1.0, "height": 3.0, "depth": 0.5}


def test_record_router_execution_outcome_persists_last_disposition_and_error():
    """Operational diagnostics should keep the last router execution disposition in session state."""

    ctx = FakeContext()

    state = record_router_execution_outcome(
        ctx,
        router_disposition="failed_closed_error",
        error="Router processing failed",
    )

    assert state.last_router_disposition == "failed_closed_error"
    assert state.last_router_error == "Router processing failed"
    assert get_session_capability_state(ctx).last_router_disposition == "failed_closed_error"


def test_record_router_execution_outcome_does_not_clear_goal_scoped_state_in_async_context():
    """Sync diagnostics bookkeeping must not rewrite unrelated goal/reference session state."""

    async def run() -> None:
        ctx = AsyncStateContext()
        typed_ctx = cast(Any, ctx)
        await set_session_value_async(typed_ctx, "phase", SessionPhase.BUILD.value)
        await set_session_value_async(typed_ctx, "goal", "low poly squirrel")
        await set_session_value_async(typed_ctx, "reference_images", [{"reference_id": "ref_1"}])

        record_router_execution_outcome(
            typed_ctx,
            router_disposition="direct",
            error=None,
        )

        await asyncio.sleep(0)

        assert await get_session_value_async(typed_ctx, "goal") == "low poly squirrel"
        assert await get_session_value_async(typed_ctx, "reference_images") == [{"reference_id": "ref_1"}]
        assert await get_session_value_async(typed_ctx, "last_router_disposition") == "direct"
        assert await get_session_value_async(typed_ctx, "last_router_error") is None

    asyncio.run(run())


def test_update_session_from_router_goal_clears_reference_images_when_goal_changes():
    ctx = FakeContext()
    ctx.state["reference_images"] = [{"reference_id": "ref_1"}]

    state = update_session_from_router_goal(
        ctx,
        "new_goal",
        {
            "status": "ready",
        },
    )

    assert state.reference_images is None


def test_update_session_from_router_goal_preserves_reference_images_for_same_goal():
    ctx = FakeContext()
    update_session_from_router_goal(ctx, "chair", {"status": "ready"})
    ctx.state["reference_images"] = [{"reference_id": "ref_1"}]

    state = update_session_from_router_goal(
        ctx,
        "chair",
        {
            "status": "needs_input",
            "unresolved": [{"param": "height"}],
        },
    )

    assert state.reference_images == [{"reference_id": "ref_1"}]
