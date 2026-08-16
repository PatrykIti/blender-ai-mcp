# TASK-143-02-01: Relation Vocabulary, Bounded Pair Expansion, and Graph Builder

**Parent:** [TASK-143-02](./TASK-143-02_Relation_Graph_Derivation_And_Truth_Layer_Convergence.md)
**Status:** ✅ Done
**Priority:** 🔴 High

**Completion Summary:** Completed on 2026-04-07. Added a shared bounded
relation builder that derives pair state from `scene_measure_gap`,
`scene_measure_alignment`, `scene_measure_overlap`, and `scene_assert_contact`,
with explicit attachment/support/symmetry interpretations where justified.

## Objective

Define one bounded relation vocabulary and pair-expansion policy, then build
the relation graph from the current scene truth primitives instead of prompt
heuristics.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/contracts/scene.py`
- `server/application/services/`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/scene/test_scene_measure_tools.py`
- `tests/unit/tools/scene/test_scene_assert_tools.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/e2e/tools/scene/test_scene_measure_tools.py`
- `_docs/LLM_GUIDE_V2.md`

## Acceptance Criteria

- the relation vocabulary is explicit, typed, and bounded
- pair-expansion policy can go beyond the current anchor-only list when the
  goal/scope requires it, but stays budget-safe and deterministic
- the builder reuses current truth primitives such as:
  - `scene_measure_gap`
  - `scene_measure_alignment`
  - `scene_measure_overlap`
  - `scene_assert_contact`
- relation derivation keeps provenance from the underlying measured/asserted
  state
- if one missing stable Blender fact is discovered during implementation, it is
  isolated as an explicit follow-on atomic/tool requirement instead of being
  hidden inside a vague graph payload

## Docs To Update

- `_docs/LLM_GUIDE_V2.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/scene/test_scene_measure_tools.py`
- `tests/unit/tools/scene/test_scene_assert_tools.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/e2e/tools/scene/test_scene_measure_tools.py`

## Changelog Impact

- include in the parent `TASK-143` changelog entry when shipped

## Status / Board Update

- keep board tracking on `TASK-143`
- no `_docs/_TASKS/README.md` change in this planning pass
