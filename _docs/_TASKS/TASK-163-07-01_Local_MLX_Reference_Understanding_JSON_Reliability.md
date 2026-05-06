# TASK-163-07-01: Local MLX Reference-Understanding JSON Reliability

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-163-07](./TASK-163-07_Harness_Live_Backend_Coverage_Docs_And_Closeout.md)
**Objective:** Make the local MLX live `reference-understanding` harness lane return parseable bounded JSON so `TASK-163` can close with both local and external RU proof.
**Repository Touchpoints:** `server/adapters/mcp/vision/prompting.py`, `server/adapters/mcp/vision/parsing.py`, `server/adapters/mcp/vision/backends.py`, `scripts/vision_harness.py`, `tests/unit/adapters/mcp/test_vision_prompting.py`, `tests/unit/adapters/mcp/test_vision_parsing.py`, `tests/unit/scripts/test_script_tooling.py`, `tests/e2e/vision/test_openrouter_qwen_json_mode.py`
**Acceptance Criteria:** the local MLX RU harness lane succeeds on the shared squirrel reference image with bounded JSON; no external-provider path regresses; `TASK-163-07` can record one green local RU proof instead of a blocker note.

## Context

`TASK-163-07` now has a real live `reference-understanding` harness mode and a
green external RU proof on the squirrel reference, but the local MLX lane is
still blocked:

```text
MLX local vision runtime did not return valid JSON content.
```

That blocker is specific enough to deserve its own leaf under the closeout
track instead of being left as an implicit note in the parent task.

## Implementation Notes

- start from the exact failing command recorded in `TASK-163-07`
- keep the fix scoped to local MLX RU JSON reliability; do not widen this leaf
  into general compare-loop prompt redesign
- prefer prompt/schema/parser tightening or bounded repair over weakening the
  RU contract
- do not relax the RU path into prose acceptance; the goal is still typed JSON
- keep the external OpenRouter/Qwen RU lane stable while improving the local
  MLX path
- if the MLX model needs a smaller/cleaner RU prompt than the external path,
  keep that distinction inside the current backend/prompt owner seams instead of
  inventing a second public contract

## Pseudocode

```python
run_local_ru_harness()
capture_raw_local_ru_output()
identify_local_json_failure_shape()
tighten_local_ru_prompt_or_repair_path()
rerun_local_ru_harness()
confirm_external_ru_harness_still_passes()
```

## Runtime / Security Contract Notes

- this leaf touches local model output reliability only; it must not change the
  authority boundary of RU
- do not let repair logic accept echoed input, free-form prose, or hidden tool
  names as a successful RU payload
- any parser repair added here must stay bounded to the declared RU schema

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/scripts/test_script_tooling.py` when harness CLI/runtime behavior changes
- reuse the existing live lane in `TASK-163-07` after the unit owner lanes are green

## Docs To Update

- `TASK-163-07` progress notes and validation proof once the blocker clears
- `_docs/_VISION/README.md` only if the local-vs-external RU prompt semantics become intentionally different

## Changelog Impact

- no dedicated changelog entry by default; fold into the final `TASK-163-07`
  closeout entry unless this blocker turns into a larger standalone runtime fix

## Status / Board Update

- stays nested under `TASK-163-07`
- does not become its own board row unless the local MLX RU blocker expands
  into a broader Vision runtime reliability track

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_vision_parsing.py tests/unit/scripts/test_script_tooling.py -q`
- local RU proof lane:
  - `poetry run python scripts/vision_harness.py --backend mlx_local --mode reference-understanding --goal "classify the attached low-poly squirrel reference for bounded Blender planning" --reference _docs/_TEST_IMAGES/squirrel-front.png --mlx-model mlx-community/Qwen3-VL-4B-Instruct-4bit`
- external regression check after the local fix:
  - `poetry run python scripts/vision_harness.py --backend openai_compatible_external --mode reference-understanding --goal "classify the attached low-poly squirrel reference for bounded Blender planning" --reference _docs/_TEST_IMAGES/squirrel-front.png --external-provider openrouter --external-contract-profile generic_full --openrouter-model qwen/qwen3-vl-32b-instruct --openrouter-api-key-env OPENROUTER_API_KEY`
