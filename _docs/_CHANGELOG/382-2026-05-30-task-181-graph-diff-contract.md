# 382. TASK-181-02 graph-vs-graph diff contract and builder

Date: 2026-05-30

## Summary

Implemented `TASK-181-02`: a typed graph-vs-graph compare-diff contract plus a
deterministic builder that compares the EXPECTED part graph (roles + relations the
reference implies) against the BUILT scene graph (registered parts + the
deterministic relation-graph pairs) and reports per-node and per-edge mismatches
over the fixed relation vocabulary. This is the structured "which parts/relations
differ" evidence the orchestrator can read instead of inferring it from prose.

## Changes

- `server/adapters/mcp/contracts/reference.py`: added
  `ReferenceGraphNodeDeltaContract` (per-node present/missing/unexpected +
  symbolic attribute mismatches), `ReferenceGraphEdgeDeltaContract` (per-edge
  satisfied/violated/missing/unknown over `SceneRelationKindLiteral`), and
  `ReferenceGraphDiffContract` (node deltas, edge deltas, missing/unexpected
  parts). All advisory, not a truth source.
- new `server/adapters/mcp/vision/graph_diff.py`: `build_reference_graph_diff(...)`
  computes the diff from expected/actual part lists, expected relations, and the
  built relation-graph pairs; relation satisfaction reuses the same pair fields
  the relation-triplet serializer reads, and edge lookup is order-insensitive.

## Tests

- `tests/unit/adapters/mcp/test_vision_graph_diff.py`: missing/unexpected parts,
  attribute mismatches only on present nodes, edge satisfied/violated/missing, and
  order-insensitive edge lookup
- `ruff`/`mypy` clean; full `tests/unit` green

## Follow-on

`TASK-181-01` (make the part registry the canonical compare scope — the deep
guided-flow rewrite that fixes the `TASK-173` Body+Head drift) and `TASK-181-04`
(squirrel scope-drift regression lane) remain open; wiring this diff into the
staged-compare payload is a small additive follow-up once 181-01 lands.

## Research Basis

SceneVerse (arXiv:2401.09340) relation taxonomy; 3DGraphLLM (arXiv:2412.18450)
graph-structured evidence. Re-measure on `tests/fixtures/vision_eval`.
