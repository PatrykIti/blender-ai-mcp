"""Tests for the deterministic graph-vs-graph compare diff."""

from __future__ import annotations

from server.adapters.mcp.vision.graph_diff import build_reference_graph_diff


def test_graph_diff_reports_missing_and_unexpected_parts():
    diff = build_reference_graph_diff(
        expected_parts=["Body", "Head", "Tail"],
        actual_parts=["Body", "Head", "Antenna"],
    )
    assert diff.missing_parts == ["Tail"]
    assert diff.unexpected_parts == ["Antenna"]
    statuses = {n.target_label: n.status for n in diff.node_deltas}
    assert statuses == {"Body": "present", "Head": "present", "Tail": "missing", "Antenna": "unexpected"}


def test_graph_diff_node_attribute_mismatches_only_for_present_nodes():
    diff = build_reference_graph_diff(
        expected_parts=["Head", "Tail"],
        actual_parts=["Head"],
        node_attribute_mismatches={"Head": ["profile too round"], "Tail": ["ignored"]},
    )
    head = next(n for n in diff.node_deltas if n.target_label == "Head")
    tail = next(n for n in diff.node_deltas if n.target_label == "Tail")
    assert head.attribute_mismatches == ["profile too round"]
    assert tail.attribute_mismatches == []  # missing node carries no attribute mismatches


def test_graph_diff_edge_satisfied_violated_and_missing():
    actual_pairs = [
        {"from_object": "Head", "to_object": "Body", "contact_passed": True},
        {"from_object": "Tail", "to_object": "Body", "relation_kinds": ["contact"], "relation_verdicts": ["fail"]},
    ]
    diff = build_reference_graph_diff(
        expected_parts=["Head", "Tail", "Ear", "Body"],
        actual_parts=["Head", "Tail", "Ear", "Body"],
        expected_relations=[
            ("Head", "Body", "contact"),  # satisfied via contact_passed
            ("Tail", "Body", "contact"),  # violated (verdict fail)
            ("Ear", "Body", "contact"),  # missing (no pair)
        ],
        actual_pairs=actual_pairs,
    )
    by_edge = {(e.from_label, e.to_label): e.status for e in diff.edge_deltas}
    assert by_edge[("Head", "Body")] == "satisfied"
    assert by_edge[("Tail", "Body")] == "violated"
    assert by_edge[("Ear", "Body")] == "missing"


def test_graph_diff_edge_lookup_is_order_insensitive():
    diff = build_reference_graph_diff(
        expected_parts=["EarL", "EarR"],
        actual_parts=["EarL", "EarR"],
        expected_relations=[("EarL", "EarR", "symmetry")],
        actual_pairs=[{"from_object": "EarR", "to_object": "EarL", "relation_kinds": ["symmetry"]}],
    )
    assert diff.edge_deltas[0].status == "satisfied"
