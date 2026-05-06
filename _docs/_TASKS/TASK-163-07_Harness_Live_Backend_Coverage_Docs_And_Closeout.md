# TASK-163-07: Harness Live Backend Coverage, Docs, And Closeout

**Status:** ✅ Done
**Priority:** 🔴 High
**Parent:** [TASK-163](./TASK-163_Vision_Orchestrator_Feedback_Strategy_Normalization_And_Optional_Perception_Adapters.md)
**Objective:** Close the umbrella with live-backend proof lanes, final docs, and board/changelog closure.
**Repository Touchpoints:** `tests/e2e/vision/`, `tests/e2e/integration/`, `tests/fixtures/vision_eval/`, `_docs/_VISION/`, `_docs/_MCP_SERVER/README.md`, `_docs/_TESTS/README.md`, `_docs/_TASKS/README.md`, `_docs/_CHANGELOG/`
**Acceptance Criteria:** at least one local and one external live RU lane are validated or explicitly recorded as intentionally skipped with a concrete reason; docs reflect the shipped compact feedback contract; board/changelog state is synchronized.

## Completion Summary

- added a real live `--mode reference-understanding` path to
  `scripts/vision_harness.py` instead of relying only on fixture-only RU mode
- validated one local and one external live RU proof lane on the shared
  squirrel reference image:
  - local: `mlx-community/Qwen3-VL-4B-Instruct-4bit`
  - external: OpenRouter `qwen/qwen3-vl-32b-instruct`
- replaced the earlier stale external closeout command that referenced
  `google/gemma-3-27b-it:free`, because that OpenRouter route now returns
  `404 No endpoints found`
- closed the previously explicit MLX blocker through
  [TASK-163-07-01](./TASK-163-07-01_Local_MLX_Reference_Understanding_JSON_Reliability.md)
- kept the wider five-class RU harness matrix as future expansion work; the
  current closeout operationalizes the squirrel proof lane that this umbrella
  actually shipped

## Coverage Vs Long Plan

Covered from `_docs/blender-ai-mcp-vision-reference-understanding-plan.md` by
`TASK-163`:

- Stage 1 reference-understanding on the existing reference/guided seam
- Stage 2 server-owned strategy apply through guided state/visibility/gate
  policy
- orchestrator-facing handoff/read model on existing surfaces
- optional deterministic visual evidence
- optional CLIP/SigLIP-style support classification seam
- optional segmentation-sidecar linkage seam

Not covered by `TASK-163` and still outside this umbrella closeout:

- explicit low-poly facet refinement stage / macro family wave
- the broader five-class RU fixture matrix as a mandatory closeout proof gate
- heavier later adapters such as GroundingDINO / OWL-ViT localization
- domain-consumer implementation tracks owned by `TASK-135-03`, `TASK-135`,
  and `TASK-140`

## Implementation Notes

- target coverage matrix for future RU harness expansion:
  - low-poly squirrel
  - smooth organic creature
  - hard-surface product
  - architectural facade
  - dental crown mockup
- current repo-supported closeout proof is operationalized only for the shared
  squirrel RU lane. If the full five-class matrix becomes mandatory before
  umbrella closure, split those additional fixture/proof lanes into explicit
  follow-on leaves before claiming that coverage.
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
- 2026-05-06: the historical local MLX blocker was split into
  [TASK-163-07-01](./TASK-163-07-01_Local_MLX_Reference_Understanding_JSON_Reliability.md)
  and resolved later the same day, so this leaf no longer stays open on that
  condition.

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

- covered by [321. TASK-163 harness closeout and MLX RU proof](../_CHANGELOG/321-2026-05-06-task-163-harness-closeout-and-mlx-ru-proof.md)

## Status / Board Update

- this leaf is now closed and no longer blocks umbrella closeout
- if future RU harness expansion revives the five-class matrix as required
  scope, track that as a new explicit follow-on instead of reopening this leaf

## Validation Commands

- `git diff --check`
- `poetry run pre-commit run --all-files --show-diff-on-failure`
- `PYTHONPATH=. poetry run pytest ./tests/unit -q`
- `poetry run python scripts/run_e2e_tests.py`
- current live RU proof commands on the shared squirrel reference image:
  - local: `poetry run python scripts/vision_harness.py --backend mlx_local --mode reference-understanding --goal "classify the attached low-poly squirrel reference for bounded Blender planning" --reference _docs/_TEST_IMAGES/squirrel-front.png --mlx-model mlx-community/Qwen3-VL-4B-Instruct-4bit`
  - external: `poetry run python scripts/vision_harness.py --backend openai_compatible_external --mode reference-understanding --goal "classify the attached low-poly squirrel reference for bounded Blender planning" --reference _docs/_TEST_IMAGES/squirrel-front.png --external-provider openrouter --external-contract-profile generic_full --openrouter-model qwen/qwen3-vl-32b-instruct --openrouter-api-key-env OPENROUTER_API_KEY`
