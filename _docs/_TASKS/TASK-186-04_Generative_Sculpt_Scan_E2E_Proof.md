# TASK-186-04: Generative, Sculpt, And Scan E2E Proof

**Parent:** [TASK-186](./TASK-186_Semantic_Part_Decomposition_And_Registry_Materialization.md)
**Status:** ⏳ To Do
**Priority:** 🟡 Medium
**Objective:** Prove semantic part decomposition and registry materialization on representative fixture assets before relying on live provider output.

**Repository Touchpoints:** `tests/e2e/`, `tests/fixtures/`, `scripts/run_e2e_tests.py`, `_docs/_TESTS/README.md`, `_docs/_VISION/README.md`

## Implementation Notes

- Use local fixtures first:
  - generated-style single mesh
  - sculpted organic mesh
  - scan/import-style mesh with imperfect topology
- Include at least one negative or ambiguous fixture where decomposition should
  refuse to register a part without operator confirmation.
- Record fixture provenance and keep files small enough for normal test
  workflows.

## Runtime / Security Contract Notes

- live external provider output is not required for this proof
- fixture assets must be license-safe and committed only when allowed
- E2E should use the repo-supported Blender runner

## Tests To Add/Update

- Blender-backed E2E for materialization and registry visibility
- negative E2E for ambiguous decomposition
- docs/test architecture updates if new fixture classes are added

## Docs To Update

- `_docs/_TESTS/README.md`
- `_docs/_VISION/README.md`

## Acceptance Criteria

- one fixture proves end-to-end decomposition -> materialization -> guided
  registration -> relation/inspection visibility
- one fixture proves ambiguous output does not become registry truth
- validation is recorded in the task closeout

## Validation Commands

- `git diff --check`
- `poetry run python scripts/run_e2e_tests.py`
