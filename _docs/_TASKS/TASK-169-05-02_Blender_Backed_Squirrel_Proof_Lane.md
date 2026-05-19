# TASK-169-05-02: Blender-Backed Squirrel Proof Lane

**Parent:** [TASK-169-05](./TASK-169-05_Squirrel_Reference_Guided_Drift_Regression_Pack.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Add one Blender-backed front+side squirrel proof lane that fails the current vertical-blockout class and proves the repaired runtime on the real guided/reference path.
**Repository Touchpoints:** `tests/e2e/vision/test_reference_guided_squirrel_quality_regression.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_understanding.py`, `server/adapters/mcp/areas/scene.py`, `_docs/_TEST_IMAGES/squirrel-front.png`, `_docs/_TEST_IMAGES/`
**Acceptance Criteria:**
- the repo has one explicit Blender-backed squirrel proof lane using front+side references
- the lane distinguishes gate progress from overall creature readability
- the old “stack of primitives with local fixes” result would fail this lane

## Implementation Notes

- keep the lane bounded and deterministic enough for the repo-supported Blender
  runner
- the proof should check more than “did compare run?” or “did some gates pass?”
- reuse the current repo squirrel front fixture and add one repo-owned side
  fixture under `_docs/_TEST_IMAGES/squirrel-side.png` if it still does not
  exist when implementation starts
- keep the deterministic oracle on current helper seams rather than prose:
  - `scene_measure_dimensions(...)`
  - `scene_assert_proportion(...)`
  - `scene_relation_graph(...)`
  - bounded stage compare evidence from `reference_compare_stage_checkpoint(...)`
- likely assertions:
  - a broad body/head/tail silhouette checkpoint was taken before later local
    repair dominates
  - deterministic bounding-box / proportion checks reject the tall stacked
    blockout class:
    - body_core height-to-depth ratio stays within one seated-creature range
    - head mass does not tower vertically above body_core beyond one bounded
      ratio
    - tail mass keeps one rear/upward placement relation relative to body_core
  - required creature relation checks such as tail/body and head/body remain
    seated while the whole-model proportions still satisfy the proof bar

## Runtime / Security Contract Notes

- the proof lane must rely on deterministic inspection/assertion and bounded
  staged compare evidence, not on a human prose verdict over screenshots
- any new squirrel side fixture added to the repo must stay within the current
  test-image/documentation policy and avoid private temp-path dependencies

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
  - `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_guided_squirrel_quality_regression.py -q`
- repo-supported Blender proof:
  - `poetry run python scripts/run_e2e_tests.py`

## Validation Category

- Blender-backed guided/reference proof
