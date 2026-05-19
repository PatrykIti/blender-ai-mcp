# TASK-169-03-01: Creature Global Quality Hold And Final Completion Semantics

**Parent:** [TASK-169-03](./TASK-169-03_Creature_Quality_Bar_Gate_Normalization_And_Advisory_Support_Evidence.md)
**Status:** ✅ Done
**Completed:** 2026-05-19
**Priority:** 🔴 High
**Objective:** Ensure a creature run cannot present near-complete success when gate progress improved locally but the whole-animal silhouette is still globally wrong.
**Repository Touchpoints:** `server/adapters/mcp/contracts/quality_gates.py`, `server/adapters/mcp/transforms/quality_gate_verifier.py`, `server/adapters/mcp/areas/reference_feedback.py`, `server/adapters/mcp/areas/reference_truth.py`, `tests/unit/adapters/mcp/test_quality_gate_verifier.py`, `tests/e2e/vision/test_goal_derived_gate_creature_completion.py`
**Acceptance Criteria:**
- top-level completion and blocker projection can still hold a creature run in an unresolved state when global creature readability remains bad
- local seam/detail progress no longer reads as the main success signal for obviously wrong whole-creature blockouts
- the quality hold remains typed and anchored on current verifier/truth seams instead of prose-only planner judgement

## Implementation Notes

- keep authority on the existing gate/truth path from `TASK-157`
- likely seams:
  - final-completion aggregation
  - top-level blocker projection
  - creature-readable whole-model hold criteria
- this slice should define how the runtime keeps broad failure visible without
  inventing a second success rubric parallel to the current gate plan

## Pseudocode

```python
if local_gate_progress_high(gate_plan) and global_creature_readability_unresolved(truth_followup, compare_result):
    gate_plan = hold_final_completion(gate_plan, reason="global_creature_quality_unresolved")
```

## Runtime / Security Contract Notes

- keep the hold condition deterministic and typed; do not rely on raw prose
  confidence
- do not let optional support evidence alone assert whole-creature pass/fail

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_quality_gate_verifier.py`
- `tests/e2e/vision/test_goal_derived_gate_creature_completion.py`

## Docs To Update

- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`

## Changelog Impact

- add/update the historical `_docs/_CHANGELOG/*` entry when this slice lands

## Completion Summary

- final creature completion remains blocked on unresolved required creature
  gates and seam/profile blockers instead of overclaiming success from local
  gate progress alone
- deterministic verifier and Blender-backed creature completion proof already
  keep the whole-model state visible through `completion_blockers` and
  `final_completion`

## Status / Board Update

- closed with parent `TASK-169-03`

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_verifier.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_goal_derived_gate_creature_completion.py -q`

## Validation Category

- global-quality hold semantics proof
