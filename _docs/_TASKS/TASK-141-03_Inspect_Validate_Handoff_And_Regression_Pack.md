# TASK-141-03: `inspect_validate` Handoff and Regression Pack

**Parent:** [TASK-141](./TASK-141_Guided_Creature_Run_Contract_And_Schema_Drift_Hardening.md)
**Depends On:** [TASK-141-01](./TASK-141-01_Guided_Call_Path_Compatibility_And_Public_Contract_Ergonomics.md), [TASK-141-02](./TASK-141-02_Creature_Build_Signature_Cues_And_Discovery_Surface_Alignment.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Turn `loop_disposition="inspect_validate"` into one explicit stop-and-check
operator branch and make the same truth-first takeover happen when staged
compare degrades or fails during a real guided creature run.

## Business Problem

The runtime already exposes `inspect_validate`, but the first real creature
runs still relied too much on operator improvisation after the loop hit a
truth-heavy or degraded-compare state.

The product gap is not just the field value itself. It is the missing
end-to-end story for what happens next when:

- `loop_disposition == "inspect_validate"`
- deterministic truth findings stay high-priority
- or the vision compare path is unavailable and the operator must keep moving on
  truth tools alone

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/test_guided_inspect_validate_handoff.py`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`

## Acceptance Criteria

- `inspect_validate` is documented as a true stop-and-check branch, not a soft
  prose hint
- loop-facing runtime messaging tells the operator to switch from free-form
  modeling to inspect/measure/assert when that disposition is returned
- docs and examples prioritize the same inspect/measure/assert next-step story
- degraded compare / truth-only handoff follows the same truth-first story
  instead of dumping the session back into ad hoc modeling
- focused regression coverage protects the squirrel-run handoff shapes that
  motivated this follow-on

## Docs To Update

- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/test_guided_inspect_validate_handoff.py`

## Changelog Impact

- include in the parent `TASK-141` changelog entry when shipped

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-141-03-01](./TASK-141-03-01_Inspect_Validate_Stop_And_Check_Operator_Story.md) | Align runtime messaging and prompt/docs guidance to one explicit inspect/measure/assert handoff story for both `inspect_validate` and degraded compare |
| 2 | [TASK-141-03-02](./TASK-141-03-02_Squirrel_Run_Regression_Pack_For_Guided_Contract_Drift.md) | Add focused regression coverage for the squirrel-run contract-drift, compare-degradation, and truth-first handoff shapes |

## Status / Board Update

- keep board tracking on the parent `TASK-141`
- do not promote this subtask independently unless the handoff/regression pack
  becomes the only remaining open slice
