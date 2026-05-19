# TASK-169-03: Creature Quality Bar, Gate Normalization, And Advisory Support Evidence

**Parent:** [TASK-169](./TASK-169_Reference_Guided_Quality_Drift_Regression_And_Runtime_Authority.md)
**Status:** ✅ Done
**Completed:** 2026-05-19
**Priority:** 🔴 High
**Objective:** Align creature gate progress, reference-part normalization, and optional support evidence so visually bad blockouts cannot present as nearly complete runs.
**Repository Touchpoints:** `server/adapters/mcp/contracts/quality_gates.py`, `server/adapters/mcp/transforms/quality_gate_verifier.py`, `server/adapters/mcp/vision/reference_gates.py`, `server/adapters/mcp/vision/parsing.py`, `server/adapters/mcp/areas/reference_feedback.py`, `server/adapters/mcp/areas/reference_truth.py`, `server/adapters/mcp/vision/reference_support.py`, `tests/unit/adapters/mcp/test_quality_gate_verifier.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/e2e/vision/test_goal_derived_gate_creature_completion.py`
**Acceptance Criteria:**
- creature runs cannot look globally wrong while still presenting high gate-progress as the primary success signal
- reference-target drift such as `ears` vs `ear_pair` is normalized on current owner seams instead of leaking into runtime ambiguity
- optional classifier/segmentation evidence remains advisory-only and default-off, but the task documents and tests when that support should improve creature localization

## Execution Structure

| Order | Task | Purpose |
|------|------|---------|
| 1 | [TASK-169-03-01](./TASK-169-03-01_Creature_Global_Quality_Hold_And_Final_Completion_Semantics.md) | Hold final-completion and top-level success projection on a stronger whole-creature quality bar |
| 2 | [TASK-169-03-02](./TASK-169-03-02_Creature_Reference_Target_Normalization_For_Paired_Details.md) | Normalize frequent creature reference targets such as `ears` into the shipped role/gate vocabulary |
| 3 | [TASK-169-03-03](./TASK-169-03-03_Advisory_Support_Evidence_Projection_For_Creature_Localization.md) | Clarify where optional classifier and segmentation support can improve creature localization without becoming authority |

## Implementation Notes

- reuse the shipped gate owners from `TASK-157` and the creature consumer path
  from `TASK-135`; do not invent a second completion rubric
- this subtask is now the small execution umbrella for three narrower seams:
  global-quality hold semantics, paired-detail target normalization, and
  advisory support-evidence projection
- keep optional support evidence on existing seams:
  - RU-side classifier/segmentation support from `reference_support.py`
  - compare-time `part_segmentation` from staged compare packets
- this slice should not simply “turn segmentation on”; it should make the
  runtime better when that support exists and still sane when it does not

## Pseudocode

```python
normalized_target = normalize_creature_reference_target(gate.target_label)
gate = gate.model_copy(update={"target_label": normalized_target})

if global_creature_readability_unresolved(gate_plan, truth_followup, compare_result):
    gate_plan = hold_final_completion_on_global_quality(gate_plan)
```

## Runtime / Security Contract Notes

- optional support evidence remains advisory-only and must not pass gates on its
  own
- target normalization must stay explicit and typed; do not create fuzzy
  semantic matching in the verifier
- keep gate status authority on the existing truth/verifier path

## Tests To Add/Update

- proof ownership is split across the child tasks below

## Docs To Update

- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`

## Changelog Impact

- add/update the historical `_docs/_CHANGELOG/*` entry when this slice lands

## Completion Summary

- creature completion stays blocked on the shipped deterministic gate/truth
  path when required creature roles or seam/profile conditions remain
  unresolved
- paired-detail target labels and gate-only `eye_pair` semantics are already
  normalized on the current guided/reference surfaces
- optional classifier and segmentation support remain default-off and
  advisory-only across RU-side and compare-time projection

## Status / Board Update

- closed with parent `TASK-169`

## Validation Commands

- `git diff --check`
- focused validation is owned by the child tasks below

## Validation Category

- gate/verifier and creature runtime proof
