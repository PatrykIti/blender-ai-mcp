# TASK-163-07: Harness Live Backend Coverage, Docs, And Closeout

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-163](./TASK-163_Vision_Orchestrator_Feedback_Strategy_Normalization_And_Optional_Perception_Adapters.md)
**Objective:** Close the umbrella with live-backend proof lanes, final docs, and board/changelog closure.
**Repository Touchpoints:** `tests/e2e/vision/`, `tests/e2e/integration/`, `tests/fixtures/vision_eval/`, `_docs/_VISION/`, `_docs/_MCP_SERVER/README.md`, `_docs/_TESTS/README.md`, `_docs/_TASKS/README.md`, `_docs/_CHANGELOG/`
**Acceptance Criteria:** at least one local and one external live RU lane are validated or explicitly recorded as intentionally skipped with a concrete reason; docs reflect the shipped compact feedback contract; board/changelog state is synchronized.

## Implementation Notes

- cover five golden classes:
  - low-poly squirrel
  - smooth organic creature
  - hard-surface product
  - architectural facade
  - dental crown mockup
- keep the low-poly domain consumer ownership with `TASK-135-03`
- `scripts/vision_harness.py` is the owner for fixture/live RU eval commands and
  proof output capture; this leaf should reuse that seam rather than inventing a
  second closeout harness

## Pseudocode

```python
run_local_ru_harness()
run_external_ru_harness()
update_docs_and_board()
record_closeout_with_real_or_explicitly_skipped_proof_lanes()
```

## Runtime / Security Contract Notes

- the closeout proof must use the repo-supported local/external RU seams, not
  ad hoc model calls
- if external provider validation is intentionally skipped, record the exact
  missing prerequisite and keep the leaf open or note the skip explicitly
- do not claim closeout from docs-only updates without the runtime proof lane

## Tests To Add/Update

- `tests/e2e/vision/test_reference_understanding_runtime_surface.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/unit/scripts/test_script_tooling.py`
- fixture additions under `tests/fixtures/vision_eval/`

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TESTS/README.md`
- `_docs/_TASKS/README.md`

## Changelog Impact

- add the final `_docs/_CHANGELOG/*` closeout entry for `TASK-163`

## Status / Board Update

- close the `TASK-163` umbrella only after this leaf records the final proof lanes
- if external live-backend validation stays intentionally skipped, record that explicitly in the closeout summary

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest ./tests/unit -q`
- `poetry run python scripts/run_e2e_tests.py`
- exact local/external RU proof pair expected for closeout:
  - local: `poetry run python scripts/vision_harness.py --fixture-only reference-understanding --backend mlx_local`
  - external: `poetry run python scripts/vision_harness.py --fixture-only reference-understanding --backend openai_compatible_external`
