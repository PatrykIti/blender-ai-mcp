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

## Progress Notes

- 2026-05-06: local MLX RU reliability is now tracked explicitly as
  [TASK-163-07-01](./TASK-163-07-01_Local_MLX_Reference_Understanding_JSON_Reliability.md)
  so the remaining closeout blocker has a concrete owner seam and validation lane.
- 2026-05-06: `scripts/vision_harness.py` now exposes a real live
  `--mode reference-understanding` path instead of only the providerless
  fixture-only RU mode.
- 2026-05-06: external live RU proof on the repo-local squirrel reference is
  green with:
  - backend: `openai_compatible_external`
  - provider: `openrouter`
  - model: `qwen/qwen3-vl-32b-instruct`
- 2026-05-06: the exact historical external proof command in this task file is
  currently stale because OpenRouter now returns `404 No endpoints found` for
  `google/gemma-3-27b-it:free`.
- 2026-05-06: local live RU proof is still blocked on the current MLX path:
  `mlx-community/Qwen3-VL-4B-Instruct-4bit` returned
  `MLX local vision runtime did not return valid JSON content.` on the live RU
  harness mode, so the umbrella should stay open until that lane is either
  fixed or explicitly waived with scope-owner approval.

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
- current live RU proof commands on the shared squirrel reference image:
  - local: `poetry run python scripts/vision_harness.py --backend mlx_local --mode reference-understanding --goal "classify the attached low-poly squirrel reference for bounded Blender planning" --reference _docs/_TEST_IMAGES/squirrel-front.png --mlx-model mlx-community/Qwen3-VL-4B-Instruct-4bit`
  - external: `poetry run python scripts/vision_harness.py --backend openai_compatible_external --mode reference-understanding --goal "classify the attached low-poly squirrel reference for bounded Blender planning" --reference _docs/_TEST_IMAGES/squirrel-front.png --external-provider openrouter --external-contract-profile generic_full --openrouter-model qwen/qwen3-vl-32b-instruct --openrouter-api-key-env OPENROUTER_API_KEY`
