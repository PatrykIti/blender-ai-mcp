# TASK-173-02: Shape Convergence Exit Criteria And Inspect-Validate Escalation

**Parent:** [TASK-173](./TASK-173_Reference_Guided_Creature_Scope_Convergence_And_Optional_Grounding_Followups.md)
**Status:** ✅ Done
**Priority:** 🔴 High
**Follow-on After:** [TASK-171-01](./TASK-171-01_Buildable_Gate_Escalation_And_Stage_Prerequisite_Repair.md), [TASK-169-03-01](./TASK-169-03-01_Creature_Global_Quality_Hold_And_Final_Completion_Semantics.md)
**Objective:** Repair the creature loop so semantic role completion no longer outranks silhouette/proportion convergence, and make the `build` -> `checkpoint_iterate` -> `inspect_validate` escalation depend on explicit shape and gate criteria instead of “all parts exist”.
**Repository Touchpoints:** `server/adapters/mcp/session_capabilities_flow.py`, `server/adapters/mcp/session_capabilities_registry.py`, `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_compare_packets.py`, `server/adapters/mcp/areas/reference_feedback.py`, `server/adapters/mcp/areas/reference_truth.py`, `server/adapters/mcp/contracts/quality_gates.py`, `server/adapters/mcp/transforms/quality_gate_verifier.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_quality_gate_verifier.py`, `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/e2e/integration/test_guided_inspect_validate_handoff.py`, `tests/e2e/vision/test_goal_derived_gate_creature_completion.py`
**Acceptance Criteria:**
- all required creature roles existing is not enough to leave the build-oriented convergence path when whole-assembly shape drift is still dominant
- `inspect_validate` activates only after explicit escalation conditions such as resolved buildable parts plus remaining truth/view blockers, repeated stagnation, or documented non-buildable failures
- compact iterate output can distinguish “all roles exist but the creature still does not match the target shape” from “the build path is exhausted”

## Implementation Notes

- the latest squirrel result proved the current policy can build every major
  role yet still produce a primitive blockout
- whole-assembly mismatch remained obvious in capture:
  - box body
  - cube head
  - spike ears
  - detached coarse tail/legs
- the loop therefore needs a shape-convergence contract that survives semantic
  completion:
  - silhouette drift
  - aspect-ratio drift
  - unresolved upper-profile broadening
  - unresolved assembly-scale packet blockers
- escalation ownership is split:
  - `reference_iterate_stage_checkpoint(...)` and staged compare determine the
    current failure class
  - `session_capabilities_registry.py` applies the resulting step / phase move
  - verifier/truth seams keep the final gate authority
- keep deterministic truth and packet metrics as the authority; do not turn
  VLM prose into the actual exit gate

## Pseudocode

```python
all_roles_present = required_roles_satisfied(guided_flow_state)
shape_converged = assembled_shape_metrics_within_bounds(compare_diagnostics, gate_plan)
buildable_failures = unresolved_buildable_gate_blockers(gate_plan)

if not all_roles_present:
    return continue_build()
if not shape_converged and buildable_failures:
    return continue_build_with_shape_focus()
if not shape_converged and not build_path_exhausted():
    return checkpoint_iterate_again()
if hard_truth_or_view_blocker():
    return inspect_validate()
```

## Runtime / Security Contract Notes

- shape-convergence checks must remain bounded, deterministic, and auditable
- do not let optional classifier or segmentation output mark convergence
- escalation policy must remain fail-closed; if evidence is missing, prefer a
  bounded re-check over a false “done”

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_quality_gate_verifier.py`
- `tests/unit/adapters/mcp/test_reference_compare_packets.py`
- `tests/e2e/integration/test_guided_inspect_validate_handoff.py`
- `tests/e2e/vision/test_goal_derived_gate_creature_completion.py`

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Changelog Impact

- add/update the historical `_docs/_CHANGELOG/*` entry when this slice lands

## Status / Board Update

- board tracking is closed on umbrella `TASK-173`
- no separate promoted board-row change is expected for this subtask unless it
  later becomes a standalone follow-on

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/adapters/mcp/test_reference_compare_packets.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_inspect_validate_handoff.py tests/e2e/vision/test_goal_derived_gate_creature_completion.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`

## Validation Category

- shape-convergence and escalation-policy proof

## Completion Summary

Completed on 2026-05-31. `reference_iterate_stage_checkpoint(...)` now
distinguishes a creature run where all semantic roles exist but
whole-assembly shape/profile drift still has a bounded build lane from a
build path that is exhausted. Shape/profile/proportion blockers can keep
`checkpoint_iterate` in `continue_build` and advance toward
`refine_low_poly_forms`; high-priority truth findings and repeated stagnation
still escalate to `inspect_validate`.

Validation evidence is recorded in changelog entry `394`.
