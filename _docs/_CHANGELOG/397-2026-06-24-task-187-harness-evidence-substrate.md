# 397. TASK-187 harness evidence substrate

Date: 2026-06-24

Started `TASK-187` with a governance substrate for trustworthy external-model
promotion evidence. No model, fallback profile, provider vocabulary, or
`VisionContractProfile` was promoted in this slice.

## Changed

- Updated `scripts/vision_harness.py` to prefer `backend.runtime_config` after
  `backend.analyze(...)` when available, so harness output reflects lazy
  OpenRouter `/models` metadata and request-policy decisions.
- Added focused unit coverage for a fake OpenRouter backend that replaces
  preflight runtime config with live capability metadata during analysis.
- Added `TASK-187-01` as a completed leaf and moved parent `TASK-187` to
  in progress.
- Documented that promotion evidence must use post-request harness
  `model_name`, `vision_contract_profile`, and `capability_summary` records.

## Validation

All validation passed on 2026-06-24:

- `PYTHONPATH=. poetry run pytest tests/unit/scripts/test_script_tooling.py -q -k 'vision_harness and (openrouter_backend_config or backend_path or capability_summary)'`
  - `6 passed, 44 deselected`
- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runner.py tests/unit/adapters/mcp/test_vision_result_types.py -q`
  - `14 passed`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
  - `3644 passed`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --files _docs/_CHANGELOG/397-2026-06-24-task-187-harness-evidence-substrate.md _docs/_TASKS/TASK-187-01_Harness_Capability_Summary_And_Evidence_Record_Substrate.md --show-diff-on-failure`
