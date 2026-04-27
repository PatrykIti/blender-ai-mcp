# TASK-143-02-02: Relation Graph Adoption in Truth Followup and Stage Loops

**Parent:** [TASK-143-02](./TASK-143-02_Relation_Graph_Derivation_And_Truth_Layer_Convergence.md)
**Depends On:** [TASK-143-02-01](./TASK-143-02-01_Relation_Vocabulary_Bounded_Pair_Expansion_And_Graph_Builder.md)
**Status:** ✅ Done
**Priority:** 🔴 High

**Completion Summary:** Completed on 2026-04-07. Stage compare/iterate now use
the shared spatial derivation layer internally, `truth_followup` and
`correction_candidates` carry the same relation vocabulary, and the graph
remains an explicit on-demand artifact instead of a mandatory stage payload.

## Objective

Reuse the relation-graph semantics inside `truth_followup`,
`correction_candidates`, and staged compare / iterate flows while keeping the
graph itself outside the default heavy checkpoint payload path.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/contracts/scene.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`

## Acceptance Criteria

- `truth_followup` and `correction_candidates` reuse the relation-graph
  semantics instead of maintaining a disconnected private interpretation layer
- stage compare / iterate can consume the shared relation builder internally
  without embedding the full graph by default
- if a lightweight stage-loop summary is added, it is a compact derivative of
  the graph rather than the graph payload itself
- budget-control behavior remains explicit whenever relation-derived detail is
  trimmed
- the staged truth handoff remains aligned with the existing truth-first
  boundary: vision may inform, but relation truth is still derived from
  measured/asserted state

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`

## Changelog Impact

- include in the parent `TASK-143` changelog entry when shipped

## Status / Board Update

- keep board tracking on `TASK-143`
- no `_docs/_TASKS/README.md` change in this planning pass
