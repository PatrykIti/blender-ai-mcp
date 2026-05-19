# TASK-169-03: Creature Quality Bar, Gate Normalization, And Advisory Support Evidence

**Parent:** [TASK-169](./TASK-169_Reference_Guided_Quality_Drift_Regression_And_Runtime_Authority.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Align creature gate progress, reference-part normalization, and optional support evidence so visually bad blockouts cannot present as nearly complete runs.
**Repository Touchpoints:** `server/adapters/mcp/contracts/quality_gates.py`, `server/adapters/mcp/transforms/quality_gate_verifier.py`, `server/adapters/mcp/vision/reference_gates.py`, `server/adapters/mcp/vision/parsing.py`, `server/adapters/mcp/areas/reference_feedback.py`, `server/adapters/mcp/areas/reference_truth.py`, `server/adapters/mcp/vision/reference_support.py`, `tests/unit/adapters/mcp/test_quality_gate_verifier.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/e2e/vision/test_goal_derived_gate_creature_completion.py`
**Acceptance Criteria:**
- creature runs cannot look globally wrong while still presenting high gate-progress as the primary success signal
- reference-target drift such as `ears` vs `ear_pair` is normalized on current owner seams instead of leaking into runtime ambiguity
- optional classifier/segmentation evidence remains advisory-only and default-off, but the task documents and tests when that support should improve creature localization

## Implementation Notes

- reuse the shipped gate owners from `TASK-157` and the creature consumer path
  from `TASK-135`; do not invent a second completion rubric
- likely work items:
  - normalize frequent creature target labels from RU/reference proposals into
    the current role/gate vocabulary
  - ensure final-completion and top-level blocker projection still reflect
    whole-creature unreadability when only local detail/seam gates improved
  - decide where an optional advisory silhouette/profile gate or broad
    proportion gate belongs on the current generic gate vocabulary
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

- `tests/unit/adapters/mcp/test_quality_gate_verifier.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/e2e/vision/test_goal_derived_gate_creature_completion.py`

## Docs To Update

- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`

## Changelog Impact

- add/update the historical `_docs/_CHANGELOG/*` entry when this slice lands

## Status / Board Update

- keep nested under `TASK-169`

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_goal_derived_gate_creature_completion.py -q`

## Validation Category

- gate/verifier and creature runtime proof
