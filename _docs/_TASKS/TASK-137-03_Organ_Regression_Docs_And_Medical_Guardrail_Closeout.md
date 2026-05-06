# TASK-137-03: Organ Regression, Docs, And Medical Guardrail Closeout

**Status:** ⏳ To Do
**Priority:** 🟠 High
**Parent:** [TASK-137](./TASK-137_Anatomy_Aware_Reference_Guided_Organ_Reconstruction.md)
**Depends On:** [TASK-137-01](./TASK-137-01_Organ_Domain_Boundary_Vocabulary_And_Fidelity_Tiers.md), [TASK-137-02](./TASK-137-02_Guided_Organ_Loop_Relation_Semantics_And_Bounded_Surface.md)
**Objective:** Lock the first organ domain slice with regression, docs, and explicit proof that the product boundary stays non-clinical.
**Repository Touchpoints:** future `tests/e2e/vision/test_guided_organ_reconstruction.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `_docs/_PROMPTS/README.md`, likely new `_docs/_PROMPTS/REFERENCE_GUIDED_ORGAN_BUILD.md`, `_docs/_VISION/README.md`, `_docs/_MCP_SERVER/README.md`, `_docs/_TESTS/README.md`, `_docs/_TASKS/README.md`, `_docs/_CHANGELOG/`
**Acceptance Criteria:** the first organ E2E lane proves staged organ blockers on the live transport surface; docs and changelog state explicit non-clinical limits; operator guidance does not overclaim what the domain can do.

## Implementation Notes

- keep the first regression pack small and focused on one or two bounded organ
  scenarios
- include explicit negative checks for overclaiming, such as diagnosis or
  patient-specific interpretation language
- document the domain boundary only after the runtime surface actually enforces
  it

## Pseudocode

```python
run_unit_owner_lanes_for_organ_contract()
run_transport_lane_for_staged_gate_reporting()
run_first_bounded_organ_e2e_lane()
audit_docs_for_non_clinical_boundary_consistency()
```

## Runtime / Security Contract Notes

- do not close this slice without explicit docs/runtime alignment on the
  non-clinical boundary
- proof should use the existing transport/runtime seams, not docs-only review
- once the first dedicated organ E2E lane exists, final runtime closeout should
  use the repo-supported Blender runner `poetry run python scripts/run_e2e_tests.py`
  instead of treating one ad hoc pytest invocation as sufficient

## Tests To Add/Update

- future `tests/e2e/vision/test_guided_organ_reconstruction.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`

## Docs To Update

- `_docs/_PROMPTS/README.md`
- likely new `_docs/_PROMPTS/REFERENCE_GUIDED_ORGAN_BUILD.md`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TESTS/README.md`
- `_docs/_TASKS/README.md`
- `_docs/_CHANGELOG/README.md`

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry when the first organ regression/docs
  closeout ships.

## Validation Commands

- `git diff --check`
- `poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `poetry run python scripts/run_e2e_tests.py`
