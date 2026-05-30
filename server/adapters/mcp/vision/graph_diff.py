# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Deterministic graph-vs-graph compare diff for reference-guided scenes.

Compares the EXPECTED part graph (roles + relations the reference implies) with
the BUILT scene graph (registered parts + the deterministic relation-graph pairs)
and reports per-node and per-edge mismatches over the fixed relation vocabulary.

Advisory structural evidence only — it surfaces which parts/relations differ from
the expected structure so the orchestrator does not have to infer it from prose;
deterministic inspection/assertion still own correctness.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal

from server.adapters.mcp.contracts.reference import (
    ReferenceGraphDiffContract,
    ReferenceGraphEdgeDeltaContract,
    ReferenceGraphNodeDeltaContract,
)

# Expected relation as (from_label, to_label, relation_kind).
ExpectedRelation = tuple[str, str, str]

NodeStatus = Literal["present", "missing", "unexpected"]
EdgeStatus = Literal["satisfied", "violated", "missing", "unknown"]


def _norm(label: object) -> str:
    return str(label or "").strip()


def _relation_satisfied(pair: Mapping[str, Any], relation_kind: str) -> bool:
    """Whether a built relation-graph pair satisfies an expected relation kind."""

    kinds = pair.get("relation_kinds")
    if isinstance(kinds, list) and relation_kind in {str(k) for k in kinds}:
        verdicts = pair.get("relation_verdicts")
        if isinstance(verdicts, list) and "fail" in {str(v) for v in verdicts}:
            return False
        return True
    if relation_kind in {"contact", "attachment", "support"} and pair.get("contact_passed") is True:
        return True
    if relation_kind == "gap" and pair.get("gap_relation") in {"separated"}:
        return True
    if relation_kind == "overlap" and pair.get("overlap_relation") in {"overlap", "contained"}:
        return True
    return False


def build_reference_graph_diff(
    *,
    expected_parts: Sequence[str],
    actual_parts: Sequence[str],
    expected_relations: Sequence[ExpectedRelation] = (),
    actual_pairs: Sequence[Mapping[str, Any]] = (),
    node_attribute_mismatches: Mapping[str, Sequence[str]] | None = None,
) -> ReferenceGraphDiffContract:
    """Build a deterministic expected-vs-built graph diff contract."""

    expected_set = [p for p in (_norm(p) for p in expected_parts) if p]
    actual_set = [p for p in (_norm(p) for p in actual_parts) if p]
    expected_lookup = set(expected_set)
    actual_lookup = set(actual_set)
    attr = {k: list(v) for k, v in (node_attribute_mismatches or {}).items()}

    node_deltas: list[ReferenceGraphNodeDeltaContract] = []
    for part in expected_set:
        node_status: NodeStatus = "present" if part in actual_lookup else "missing"
        node_deltas.append(
            ReferenceGraphNodeDeltaContract(
                target_label=part,
                status=node_status,
                attribute_mismatches=attr.get(part, []) if node_status == "present" else [],
            )
        )
    for part in actual_set:
        if part not in expected_lookup:
            node_deltas.append(
                ReferenceGraphNodeDeltaContract(target_label=part, status="unexpected", attribute_mismatches=[])
            )

    # Index built pairs by (from, to) for relation lookup.
    pair_index: dict[tuple[str, str], Mapping[str, Any]] = {}
    for pair in actual_pairs:
        key = (_norm(pair.get("from_object")), _norm(pair.get("to_object")))
        if key[0] and key[1]:
            pair_index[key] = pair

    edge_deltas: list[ReferenceGraphEdgeDeltaContract] = []
    for from_label, to_label, relation_kind in expected_relations:
        from_label, to_label, relation_kind = _norm(from_label), _norm(to_label), _norm(relation_kind)
        if not from_label or not to_label or not relation_kind:
            continue
        matched = pair_index.get((from_label, to_label)) or pair_index.get((to_label, from_label))
        edge_status: EdgeStatus
        edge_detail: str | None
        if matched is None:
            edge_status, edge_detail = "missing", "Expected relation edge has no built pair."
        elif _relation_satisfied(matched, relation_kind):
            edge_status, edge_detail = "satisfied", None
        else:
            edge_status, edge_detail = "violated", f"Built pair does not satisfy expected '{relation_kind}'."
        edge_deltas.append(
            ReferenceGraphEdgeDeltaContract(
                from_label=from_label,
                to_label=to_label,
                relation_kind=relation_kind,  # type: ignore[arg-type]
                status=edge_status,
                detail=edge_detail,
            )
        )

    return ReferenceGraphDiffContract(
        node_deltas=node_deltas,
        edge_deltas=edge_deltas,
        missing_parts=[p for p in expected_set if p not in actual_lookup],
        unexpected_parts=[p for p in actual_set if p not in expected_lookup],
    )
