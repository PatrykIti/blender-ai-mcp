"""Tests for session-scoped quality-gate proposal intake."""

from __future__ import annotations

from dataclasses import dataclass, field

from server.adapters.mcp.session_capabilities import (
    SessionCapabilityState,
    get_session_capability_state,
    ingest_quality_gate_proposal,
    mark_guided_spatial_state_stale,
    set_session_capability_state,
    update_quality_gate_plan_from_relation_graph,
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


def test_relation_graph_verification_persists_gate_status_and_blockers():
    ctx = FakeContext()
    set_session_capability_state(
        ctx,
        SessionCapabilityState(
            phase=SessionPhase.BUILD,
            goal="create a low-poly squirrel",
            surface_profile="llm-guided",
            guided_flow_state=_guided_flow_state() | {"spatial_state_version": 3},
        ),
    )
    ingest_quality_gate_proposal(
        ctx,
        {
            "source": "llm_goal",
            "gates": [
                {
                    "gate_id": "tail_body_seam",
                    "gate_type": "attachment_seam",
                    "label": "tail seated on body",
                    "target_kind": "object_pair",
                    "target_objects": ["Tail", "Body"],
                }
            ],
        },
    )

    update_quality_gate_plan_from_relation_graph(
        ctx,
        {
            "scope": {
                "scope_kind": "object_set",
                "primary_target": "Body",
                "object_names": ["Body", "Tail"],
                "object_count": 2,
            },
            "summary": {
                "pairing_strategy": "guided_spatial_pairs",
                "pair_count": 1,
                "evaluated_pairs": 1,
                "failing_pairs": 1,
                "attachment_pairs": 1,
                "support_pairs": 0,
                "symmetry_pairs": 0,
            },
            "pairs": [
                {
                    "pair_id": "tail__body",
                    "from_object": "Tail",
                    "to_object": "Body",
                    "pair_source": "required_creature_seam",
                    "relation_kinds": ["contact", "gap", "alignment", "attachment"],
                    "relation_verdicts": ["separated", "floating_gap"],
                    "gap_relation": "separated",
                    "gap_distance": 0.2,
                    "contact_passed": False,
                    "alignment_status": "aligned",
                    "aligned_axes": ["X", "Y", "Z"],
                    "measurement_basis": "bounding_box",
                    "attachment_semantics": {
                        "relation_kind": "segment_attachment",
                        "seam_kind": "tail_body",
                        "part_object": "Tail",
                        "anchor_object": "Body",
                        "required_seam": True,
                        "preferred_macro": "macro_align_part_with_contact",
                        "attachment_verdict": "floating_gap",
                    },
                }
            ],
        },
    )

    restored = get_session_capability_state(ctx)

    assert restored.gate_plan is not None
    seam = next(gate for gate in restored.gate_plan["gates"] if gate["gate_id"] == "tail_body_seam")
    assert seam["status"] == "failed"
    assert seam["status_reason"] == "relation_floating_gap"
    assert seam["verified_at_spatial_version"] == 3
    assert any(blocker["gate_id"] == "tail_body_seam" for blocker in restored.gate_plan["completion_blockers"])


def test_mutating_tool_marks_evidence_backed_gate_status_stale():
    ctx = FakeContext()
    set_session_capability_state(
        ctx,
        SessionCapabilityState(
            phase=SessionPhase.BUILD,
            goal="create a low-poly squirrel",
            surface_profile="llm-guided",
            guided_flow_state={
                **_guided_flow_state(),
                "active_target_scope": {
                    "scope_kind": "object_set",
                    "primary_target": "Body",
                    "object_names": ["Body", "Tail"],
                    "object_count": 2,
                },
                "spatial_scope_fingerprint": "scope:body-tail",
                "spatial_state_version": 3,
            },
            gate_plan={
                "plan_id": "creature_quality_gate_plan",
                "domain_profile": "creature",
                "required_gate_count": 1,
                "optional_gate_count": 0,
                "gates": [
                    {
                        "gate_id": "tail_body_seam",
                        "gate_type": "attachment_seam",
                        "label": "tail seated on body",
                        "target_kind": "object_pair",
                        "target_objects": ["Tail", "Body"],
                        "required": True,
                        "priority": "high",
                        "status": "passed",
                        "verification_strategy": "spatial_contact",
                        "allowed_correction_families": ["spatial_context", "attachment_alignment"],
                        "recommended_bounded_tools": ["scene_relation_graph"],
                        "proposal_sources": ["llm_goal"],
                        "evidence_requirements": [{"evidence_kind": "spatial_relation", "required": True}],
                        "evidence_refs": [
                            {
                                "evidence_id": "scene_relation_graph:tail__body:tail_body_seam",
                                "evidence_kind": "spatial_relation",
                                "source": "spatial_relation",
                                "authority": "authoritative",
                                "tool_name": "scene_relation_graph",
                            }
                        ],
                    }
                ],
            },
        ),
    )

    mark_guided_spatial_state_stale(ctx, tool_name="modeling_create_object", family="primary_masses")

    restored = get_session_capability_state(ctx)

    assert restored.gate_plan is not None
    gate = restored.gate_plan["gates"][0]
    assert gate["status"] == "stale"
    assert gate["status_reason"] == "scene_mutation_after_verification"
    assert gate["stale_since_spatial_version"] == 4
