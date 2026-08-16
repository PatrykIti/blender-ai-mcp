# TASK-143-02: Relation Graph Derivation and Truth-Layer Convergence

**Parent:** [TASK-143](./TASK-143_Guided_Spatial_Scope_And_Relation_Graphs.md)
**Depends On:** [TASK-143-01](./TASK-143-01_Scope_Graph_Contract_And_Read_Only_Surface.md)
**Status:** ✅ Done
**Priority:** 🔴 High

**Completion Summary:** Completed on 2026-04-07. The repo now has one compact
relation graph builder derived from the existing truth primitives, public
`scene_relation_graph(...)` output, and shared relation semantics reused by
`truth_bundle`, `truth_followup`, and `correction_candidates` without turning
stage payloads into default graph carriers.

## Objective

Derive one compact relation graph from the existing truth primitives and align
`truth_bundle`, `truth_followup`, and `correction_candidates` with that same
relation vocabulary.

## Business Problem

The repo already computes the raw ingredients for relation reasoning, but they
are still fragmented:

- pair expansion lives inside `_truth_bundle_pairs(...)`
- relation semantics are split across gap/alignment/overlap/assert payloads
- attachment heuristics are local to `reference.py`
- stage-loop routing consumes relation-like facts without one explicit
  relation-graph artifact

At the same time, the graph cannot become a heavy all-to-all payload. The
derivation policy must stay bounded, deterministic, and truth-first.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/contracts/scene.py`
- `server/application/services/`
- `server/router/infrastructure/tools_metadata/scene/`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/scene/test_scene_measure_tools.py`
- `tests/unit/tools/scene/test_scene_assert_tools.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/e2e/tools/scene/test_scene_measure_tools.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- `_docs/LLM_GUIDE_V2.md`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`

## Acceptance Criteria

- the repo has one compact relation-graph contract derived from the current
  measure/assert truth layer
- pair expansion is goal-aware and bounded rather than permanently
  `primary_to_others` or unbounded all-to-all
- relation semantics cover the current high-value guided cases:
  - contact / gap
  - overlap
  - alignment
  - attachment
  - support or symmetry-oriented interpretation where justified
- `truth_followup` and `correction_candidates` can reuse the same relation
  vocabulary instead of carrying a parallel private semantics model
- stage compare / iterate adoption stays bounded and does not embed the full
  relation graph by default

## Docs To Update

- `_docs/LLM_GUIDE_V2.md`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/scene/test_scene_measure_tools.py`
- `tests/unit/tools/scene/test_scene_assert_tools.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/e2e/tools/scene/test_scene_measure_tools.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`

## Changelog Impact

- include in the parent `TASK-143` changelog entry when shipped

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-143-02-01](./TASK-143-02-01_Relation_Vocabulary_Bounded_Pair_Expansion_And_Graph_Builder.md) | Define the relation vocabulary, bounded pair-expansion policy, and graph builder that reuse the current truth primitives |
| 2 | [TASK-143-02-02](./TASK-143-02-02_Relation_Graph_Adoption_In_Truth_Followup_And_Stage_Loops.md) | Adopt the relation graph semantics inside truth-followup, correction candidates, and stage compare / iterate without payload bloat |

## Status / Board Update

- keep board tracking on the parent `TASK-143`
- do not promote this slice independently unless relation derivation becomes
  the only remaining TASK-143 branch
- this planning pass intentionally leaves `_docs/_TASKS/README.md` untouched
