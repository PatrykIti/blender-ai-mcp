"""Tests for deterministic quality-gate verifier helpers."""

from __future__ import annotations

from server.adapters.mcp.contracts.quality_gates import GatePlanContract, normalize_gate_plan
from server.adapters.mcp.transforms.quality_gate_verifier import verify_gate_plan_with_relation_graph


def _relation_graph_pair(
    *,
    verdict: str,
    relation_kind: str = "segment_attachment",
    pair_id: str = "tail__body",
) -> dict[str, object]:
    return {
        "pair_id": pair_id,
        "from_object": "Tail",
        "to_object": "Body",
        "pair_source": "required_creature_seam",
        "relation_kinds": ["contact", "gap", "alignment", "attachment"],
        "relation_verdicts": ["floating_gap"] if verdict == "floating_gap" else [verdict],
        "gap_relation": "separated" if verdict == "floating_gap" else "contact",
        "gap_distance": 0.25 if verdict == "floating_gap" else 0.0,
        "overlap_relation": "overlap" if verdict == "intersecting" else "disjoint",
        "contact_passed": verdict == "seated_contact",
        "alignment_status": "misaligned" if verdict == "misaligned_attachment" else "aligned",
        "aligned_axes": ["X", "Y", "Z"],
        "measurement_basis": "bounding_box",
        "attachment_semantics": {
            "relation_kind": relation_kind,
            "seam_kind": "tail_body",
            "part_object": "Tail",
            "anchor_object": "Body",
            "required_seam": True,
            "preferred_macro": "macro_align_part_with_contact",
            "attachment_verdict": verdict,
        },
    }


def _relation_graph(pairs: list[dict[str, object]]) -> dict[str, object]:
    return {
        "scope": {
            "scope_kind": "object_set",
            "primary_target": "Body",
            "object_names": ["Body", "Tail", "Eye_L", "Eye_R"],
            "object_count": 4,
        },
        "summary": {
            "pairing_strategy": "guided_spatial_pairs",
            "pair_count": len(pairs),
            "evaluated_pairs": len(pairs),
            "failing_pairs": 0,
            "attachment_pairs": len(pairs),
            "support_pairs": 0,
            "symmetry_pairs": 0,
        },
        "pairs": pairs,
    }


def _gate(plan: GatePlanContract, gate_id: str):
    return next(gate for gate in plan.gates if gate.gate_id == gate_id)


def test_required_part_gate_passes_from_scene_scope_name_evidence():
    plan = normalize_gate_plan(
        {
            "source": "llm_goal",
            "gates": [
                {
                    "gate_id": "eyes_required",
                    "gate_type": "required_part",
                    "label": "eye pair is present",
                    "target_kind": "reference_part",
                    "target_label": "eye_pair",
                }
            ],
        },
        domain_profile="generic",
        templates=[],
    )

    updated = verify_gate_plan_with_relation_graph(plan, _relation_graph([]), spatial_state_version=2)

    gate = _gate(updated, "eyes_required")
    assert gate.status == "passed"
    assert gate.evidence_refs[0].evidence_kind == "scene_truth"
    assert gate.evidence_refs[0].authority == "authoritative"
    assert updated.completion_blockers == []


def test_attachment_gate_fails_floating_gap_with_bounded_repair_tools():
    plan = normalize_gate_plan(
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
        domain_profile="generic",
    )

    updated = verify_gate_plan_with_relation_graph(
        plan, _relation_graph([_relation_graph_pair(verdict="floating_gap")])
    )

    seam = _gate(updated, "tail_body_seam")
    final = _gate(updated, "final_completion")
    assert seam.status == "failed"
    assert seam.status_reason == "relation_floating_gap"
    assert seam.evidence_refs[0].source == "spatial_relation"
    assert "macro_align_part_with_contact" in seam.recommended_bounded_tools
    assert final.status == "blocked"
    assert any(blocker.gate_id == "tail_body_seam" for blocker in updated.completion_blockers)


def test_intersecting_attachment_passes_only_when_gate_policy_allows_embedded_seam():
    relation_graph = _relation_graph(
        [_relation_graph_pair(verdict="intersecting", relation_kind="embedded_attachment")]
    )
    strict_plan = normalize_gate_plan(
        {
            "source": "llm_goal",
            "gates": [
                {
                    "gate_id": "snout_head_seam",
                    "gate_type": "attachment_seam",
                    "label": "snout seated on head",
                    "target_kind": "object_pair",
                    "target_objects": ["Tail", "Body"],
                }
            ],
        },
        domain_profile="generic",
        templates=[],
    )
    embedded_plan = normalize_gate_plan(
        {
            "source": "llm_goal",
            "gates": [
                {
                    "gate_id": "snout_head_seam",
                    "gate_type": "attachment_seam",
                    "label": "snout embedded in head",
                    "target_kind": "object_pair",
                    "target_objects": ["Tail", "Body"],
                    "allow_embedded_intersection": True,
                }
            ],
        },
        domain_profile="generic",
        templates=[],
    )

    strict = verify_gate_plan_with_relation_graph(strict_plan, relation_graph)
    embedded = verify_gate_plan_with_relation_graph(embedded_plan, relation_graph)

    assert _gate(strict, "snout_head_seam").status == "failed"
    assert _gate(strict, "snout_head_seam").status_reason == "relation_intersecting_not_allowed"
    assert _gate(embedded, "snout_head_seam").status == "passed"


def test_support_contact_gate_uses_support_semantics_as_authoritative_truth():
    plan = normalize_gate_plan(
        {
            "source": "llm_goal",
            "gates": [
                {
                    "gate_id": "body_base_support",
                    "gate_type": "support_contact",
                    "label": "body supported by base",
                    "target_kind": "object_pair",
                    "target_objects": ["Body", "Base"],
                }
            ],
        },
        domain_profile="generic",
        templates=[],
    )
    relation_graph = {
        "scope": {
            "scope_kind": "object_set",
            "primary_target": "Body",
            "object_names": ["Body", "Base"],
            "object_count": 2,
        },
        "summary": {
            "pairing_strategy": "guided_spatial_pairs",
            "pair_count": 1,
            "evaluated_pairs": 1,
            "failing_pairs": 0,
            "attachment_pairs": 0,
            "support_pairs": 1,
            "symmetry_pairs": 0,
        },
        "pairs": [
            {
                "pair_id": "body__base",
                "from_object": "Body",
                "to_object": "Base",
                "pair_source": "support_candidate",
                "relation_kinds": ["contact", "gap", "support"],
                "relation_verdicts": ["contact", "supported"],
                "gap_relation": "contact",
                "gap_distance": 0.0,
                "contact_passed": True,
                "alignment_status": "aligned",
                "aligned_axes": ["X", "Y", "Z"],
                "measurement_basis": "bounding_box",
                "support_semantics": {
                    "supported_object": "Body",
                    "support_object": "Base",
                    "axis": "Z",
                    "verdict": "supported",
                },
            }
        ],
    }

    updated = verify_gate_plan_with_relation_graph(plan, relation_graph)

    support = _gate(updated, "body_base_support")
    assert support.status == "passed"
    assert support.evidence_refs[0].verdict == "supported"
    assert updated.completion_blockers == []
