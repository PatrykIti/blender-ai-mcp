"""Tests for session phase and capability state helpers."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from server.adapters.mcp.session_capabilities import (
    SessionCapabilityState,
    apply_visibility_for_session_state,
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
from server.adapters.mcp.transforms.visibility_policy import (
    GUIDED_BUILD_ESCAPE_HATCH_TOOLS,
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


def test_clear_session_goal_state_resets_goal_but_keeps_coarse_planning_phase():
    """Clearing the current goal should reset goal-scoped state but keep the session usable."""

    ctx = FakeContext()
    update_session_from_router_goal(ctx, "chair", {"status": "ready"})

    state = clear_session_goal_state(ctx)

    assert state.phase == SessionPhase.PLANNING
    assert state.goal is None
    assert state.pending_clarification is None
    assert state.policy_context is None


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
    assert any(
        name == "enable_components" and call["names"] == set(GUIDED_ENTRY_TOOLS)
        for name, call in calls[1:]
    )
    assert any(
        name == "enable_components" and call["names"] == set(GUIDED_BUILD_ESCAPE_HATCH_TOOLS)
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
