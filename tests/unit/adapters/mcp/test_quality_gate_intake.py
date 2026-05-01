"""Tests for session-scoped quality-gate proposal intake."""

from __future__ import annotations

from dataclasses import dataclass, field

from server.adapters.mcp.session_capabilities import (
    SessionCapabilityState,
    get_session_capability_state,
    ingest_quality_gate_proposal,
    set_session_capability_state,
)
from server.adapters.mcp.session_phase import SessionPhase


@dataclass
class FakeContext:
    state: dict[str, object] = field(default_factory=dict)

    def get_state(self, key: str):
        return self.state.get(key)

    def set_state(self, key: str, value, *, serializable: bool = True):
        self.state[key] = value


def _guided_flow_state() -> dict[str, object]:
    return {
        "flow_id": "guided_creature_flow",
        "domain_profile": "creature",
        "current_step": "create_primary_masses",
        "completed_steps": [],
        "required_checks": [],
        "required_prompts": ["guided_session_start", "reference_guided_creature_build"],
        "preferred_prompts": ["workflow_router_first"],
        "next_actions": ["begin_primary_masses"],
        "blocked_families": [],
        "allowed_families": ["primary_masses"],
        "allowed_roles": ["body_core", "head_mass", "tail_mass"],
        "missing_roles": ["body_core", "head_mass"],
        "required_role_groups": ["primary_masses"],
    }


def test_gate_proposal_intake_ignores_missing_active_guided_goal():
    ctx = FakeContext()

    result = ingest_quality_gate_proposal(
        ctx,
        {
            "source": "llm_goal",
            "gates": [{"gate_type": "required_part", "label": "eye pair", "target_label": "eye_pair"}],
        },
    )

    assert result.status == "ignored"
    assert result.reason == "no_active_guided_goal"
    assert get_session_capability_state(ctx).gate_plan is None


def test_gate_proposal_intake_persists_normalized_plan_for_active_goal():
    ctx = FakeContext()
    set_session_capability_state(
        ctx,
        SessionCapabilityState(
            phase=SessionPhase.BUILD,
            goal="create a low-poly squirrel",
            surface_profile="llm-guided",
            guided_flow_state=_guided_flow_state(),
        ),
    )

    result = ingest_quality_gate_proposal(
        ctx,
        {
            "proposal_id": "squirrel-gates",
            "source": "llm_goal",
            "gates": [
                {
                    "gate_type": "symmetry_pair",
                    "label": "both eyes visible",
                    "target_kind": "reference_part",
                    "target_label": "eye_pair",
                    "status": "passed",
                }
            ],
        },
    )

    restored = get_session_capability_state(ctx)

    assert result.status == "accepted"
    assert restored.gate_plan is not None
    assert restored.gate_plan["domain_profile"] == "creature"
    eye_gate = next(gate for gate in restored.gate_plan["gates"] if gate.get("target_label") == "eye_pair")
    assert eye_gate["gate_type"] == "symmetry_pair"
    assert eye_gate["status"] == "pending"
    assert restored.gate_plan["policy_warnings"][0]["code"] == "unsupported_completion_status"


def test_gate_proposal_intake_rejects_unknown_payload_fields():
    ctx = FakeContext()
    set_session_capability_state(
        ctx,
        SessionCapabilityState(
            phase=SessionPhase.BUILD,
            goal="create a low-poly squirrel",
            surface_profile="llm-guided",
            guided_flow_state=_guided_flow_state(),
        ),
    )

    result = ingest_quality_gate_proposal(
        ctx,
        {
            "source": "llm_goal",
            "unsafe_extra": "do not accept loose payloads",
            "gates": [],
        },
    )

    assert result.status == "rejected"
    assert "unsafe_extra" in str(result.reason)
    assert get_session_capability_state(ctx).gate_plan is None
