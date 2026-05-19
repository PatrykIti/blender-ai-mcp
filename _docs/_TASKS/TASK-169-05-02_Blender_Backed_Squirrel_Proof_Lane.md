# TASK-169-05-02: Blender-Backed Squirrel Proof Lane

**Parent:** [TASK-169-05](./TASK-169-05_Squirrel_Reference_Guided_Drift_Regression_Pack.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Add one Blender-backed front+side squirrel proof lane that fails the current vertical-blockout class and proves the repaired runtime on the real guided/reference path.
**Repository Touchpoints:** `tests/e2e/vision/`, `tests/e2e/integration/`, `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_understanding.py`, `server/adapters/mcp/areas/scene.py`, `_docs/_TEST_IMAGES/`
**Acceptance Criteria:**
- the repo has one explicit Blender-backed squirrel proof lane using front+side references
- the lane distinguishes gate progress from overall creature readability
- the old “stack of primitives with local fixes” result would fail this lane

## Implementation Notes

- keep the lane bounded and deterministic enough for the repo-supported Blender
  runner
- the proof should check more than “did compare run?” or “did some gates pass?”
- likely assertions:
  - broad body/head/tail silhouette checkpoint was taken before later local
    repair dominates
  - final result is not a tall stacked blockout class
  - required creature details and dominant tail/head proportions remain
    materially closer to the references than the observed failure anchor

## Tests To Add/Update

- one new Blender-backed squirrel proof under `tests/e2e/vision/`
- supporting integration assertions only if the E2E lane needs extra surfaced
  state to make the failure readable

## Docs To Update

- `_docs/_TESTS/README.md`
- `_docs/_VISION/README.md` if the new lane changes operator proof guidance

## Changelog Impact

- covered by the umbrella closeout entry when the proof lane lands

## Status / Board Update

- keep nested under `TASK-169-05`

## Validation Commands

- `git diff --check`
- focused owner lane first:
  - `PYTHONPATH=. poetry run pytest tests/e2e/vision/<new_squirrel_proof_test>.py -q`
- repo-supported Blender proof:
  - `poetry run python scripts/run_e2e_tests.py`

## Validation Category

- Blender-backed guided/reference proof
