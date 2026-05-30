"""TASK-181-04 regression lane: the scene-graph evidence must expose the
whole-creature scope, not collapse to Body + Head.

This is the deterministic, unit-level guard for the squirrel scope-drift failure
class (TASK-173): even when compare narrows toward Body + Head, the relation-graph
serialization and the expected-vs-built graph diff must still surface the
appendage parts (tail, ears, legs) as missing/under-related so whole-assembly
convergence cannot silently lose precedence. The live end-to-end proof stays in
tests/e2e/vision/test_reference_guided_squirrel_quality_regression.py.
"""

from __future__ import annotations

from server.adapters.mcp.vision.graph_diff import build_reference_graph_diff
from server.adapters.mcp.vision.prompting import serialize_relation_triplets

_SQUIRREL_PARTS = ["Body", "Head", "Tail", "EarL", "EarR", "LegFL", "LegFR", "LegBL", "LegBR"]


def test_graph_diff_flags_appendages_missing_when_only_body_head_built():
    # The classic drift: only Body + Head exist; the appendages are absent.
    diff = build_reference_graph_diff(
        expected_parts=_SQUIRREL_PARTS,
        actual_parts=["Body", "Head"],
        expected_relations=[
            ("Tail", "Body", "attachment"),
            ("EarL", "Head", "attachment"),
            ("EarR", "Head", "attachment"),
        ],
        actual_pairs=[{"from_object": "Head", "to_object": "Body", "contact_passed": True}],
    )
    # Every appendage is reported missing — the loop cannot read this as "done".
    assert set(diff.missing_parts) == {"Tail", "EarL", "EarR", "LegFL", "LegFR", "LegBL", "LegBR"}
    # The expected appendage-attachment edges are missing, not satisfied.
    edge_status = {(e.from_label, e.to_label): e.status for e in diff.edge_deltas}
    assert edge_status[("Tail", "Body")] == "missing"
    assert edge_status[("EarL", "Head")] == "missing"
    assert edge_status[("EarR", "Head")] == "missing"


def test_relation_triplets_surface_whole_assembly_not_just_body_head():
    # A healthy whole-creature relation graph serializes the appendage relations,
    # so the prompt scope is the whole assembly rather than just Body + Head.
    pairs = [
        {"from_object": "Head", "to_object": "Body", "contact_passed": True},
        {"from_object": "Tail", "to_object": "Body", "relation_kinds": ["attachment"]},
        {"from_object": "EarL", "to_object": "Head", "relation_kinds": ["attachment"]},
        {"from_object": "LegFL", "to_object": "Body", "relation_kinds": ["support"]},
    ]
    triplets = serialize_relation_triplets(pairs)
    subjects = {t.split(" ")[0] for t in triplets}
    # Appendages appear as relation subjects, not just Body/Head.
    assert {"Tail", "EarL", "LegFL"} <= subjects


def test_graph_diff_clean_when_whole_creature_built_and_attached():
    diff = build_reference_graph_diff(
        expected_parts=_SQUIRREL_PARTS,
        actual_parts=_SQUIRREL_PARTS,
        expected_relations=[("Tail", "Body", "attachment"), ("EarL", "Head", "attachment")],
        actual_pairs=[
            {"from_object": "Tail", "to_object": "Body", "relation_kinds": ["attachment"]},
            {"from_object": "EarL", "to_object": "Head", "relation_kinds": ["attachment"]},
        ],
    )
    assert diff.missing_parts == []
    assert diff.unexpected_parts == []
    assert all(e.status == "satisfied" for e in diff.edge_deltas)
