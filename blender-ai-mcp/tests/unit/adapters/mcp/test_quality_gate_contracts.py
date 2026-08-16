"""Tests for goal-derived quality-gate contracts."""

from __future__ import annotations

import pytest
from server.adapters.mcp.contracts.quality_gates import (
    GateProposalContract,
    normalize_gate_plan,
    templates_for_domain_profile,
)


def _gate_by_target(plan, target_label: str):
    return next(gate for gate in plan.gates if gate.target_label == target_label)


def test_normalize_gate_plan_accepts_supported_gate_types():
    proposal = GateProposalContract(
        proposal_id="squirrel_goal",
        source="llm_goal",
        gates=[
            {
                "gate_type": "required_part",
                "label": "visible eye pair",
                "target_kind": "reference_part",
                "target_label": "eye_pair",
                "priority": "high",
                "rationale": "The reference shows two visible eyes.",
            }
        ],
    )

    plan = normalize_gate_plan(proposal, domain_profile="creature")

    eye_gate = _gate_by_target(plan, "eye_pair")
    assert eye_gate.gate_type == "required_part"
    assert eye_gate.status == "pending"
    assert eye_gate.verification_strategy == "object_existence"
    assert eye_gate.proposal_sources == ["llm_goal"]
    assert eye_gate.rationale == "The reference shows two visible eyes."
    assert eye_gate.evidence_requirements[0].evidence_kind == "scene_truth"
    assert eye_gate.evidence_refs == []
    assert any(gate.gate_type == "final_completion" for gate in plan.gates)


def test_normalize_gate_plan_rejects_unsupported_gate_types_with_warning():
    plan = normalize_gate_plan(
        {
            "source": "llm_goal",
            "gates": [
                {
                    "gate_type": "raw_blender_python",
                    "label": "run custom bpy script",
                    "target_kind": "scene",
                }
            ],
        },
        domain_profile="generic",
        templates=[],
    )

    assert plan.gates == []
    assert [warning.code for warning in plan.policy_warnings] == ["unsupported_gate_type"]


def test_normalize_gate_plan_drops_hidden_tool_names_from_correction_families():
    plan = normalize_gate_plan(
        {
            "source": "llm_goal",
            "gates": [
                {
                    "gate_type": "attachment_seam",
                    "label": "tail seated on body",
                    "target_kind": "object_pair",
                    "target_label": "tail_body",
                    "allowed_correction_families": ["scene_hide_object", "attachment_alignment"],
                }
            ],
        },
        domain_profile="creature",
        templates=[],
    )

    gate = _gate_by_target(plan, "tail_body")
    assert gate.allowed_correction_families == ["attachment_alignment"]
    assert [warning.code for warning in plan.policy_warnings] == ["hidden_tool_requirement"]


def test_normalize_gate_plan_keeps_reference_and_perception_provenance_advisory():
    plan = normalize_gate_plan(
        {
            "proposal_id": "ref-understanding-1",
            "source": "reference_understanding",
            "source_provenance": [
                {
                    "source": "reference_understanding",
                    "provider": "openrouter",
                    "model_id": "example-vision-model",
                    "vision_contract_profile": "openai_strict_json",
                    "reference_ids": ["ref_front"],
                }
            ],
            "gates": [
                {
                    "gate_type": "shape_profile",
                    "label": "curled tail silhouette",
                    "target_kind": "reference_part",
                    "target_label": "curled_tail",
                    "status": "passed",
                    "evidence_requirements": ["silhouette_analysis"],
                }
            ],
        },
        domain_profile="creature",
        templates=[],
    )

    gate = _gate_by_target(plan, "curled_tail")
    assert gate.status == "pending"
    assert gate.evidence_requirements[0].evidence_kind == "silhouette_analysis"
    assert gate.source_provenance[0].provider == "openrouter"
    assert gate.source_provenance[0].model_id == "example-vision-model"
    assert [warning.code for warning in plan.policy_warnings] == ["unsupported_completion_status"]


def test_normalize_gate_plan_rejects_raw_blender_instruction_payloads():
    plan = normalize_gate_plan(
        {
            "source": "llm_goal",
            "gates": [
                {
                    "gate_type": "required_part",
                    "label": "run bpy.ops.mesh.primitive_cube_add for a missing eye",
                    "target_kind": "reference_part",
                    "target_label": "eye_pair",
                }
            ],
        },
        domain_profile="creature",
        templates=[],
    )

    assert plan.gates == []
    assert [warning.code for warning in plan.policy_warnings] == ["raw_blender_instruction"]


@pytest.mark.parametrize(
    ("domain_profile", "expected_template_target"),
    [
        ("generic", None),
        ("creature", "body_core"),
        ("building", "roof_mass"),
    ],
)
def test_domain_templates_merge_required_gates(domain_profile, expected_template_target):
    templates = templates_for_domain_profile(domain_profile)
    plan = normalize_gate_plan({"source": "llm_goal", "gates": []}, domain_profile=domain_profile)

    assert plan.required_gate_count == len(templates)
    assert any(gate.gate_type == "final_completion" for gate in plan.gates)
    if expected_template_target:
        assert any(gate.target_label == expected_template_target for gate in plan.gates)
