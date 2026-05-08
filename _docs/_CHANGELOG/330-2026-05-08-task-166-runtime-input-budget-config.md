# 330. TASK-166 runtime input-budget config

Date: 2026-05-08

## Summary

- moved the staged compare input-character budget off the hard-coded
  `VISION_ASSIST_POLICY.max_input_chars` path and into runtime-owned
  `VISION_MAX_INPUT_CHARS`
- threaded that runtime value through:
  - infrastructure `Config`
  - `VisionRuntimeConfig`
  - `build_vision_runtime_config(...)`
  - bounded `vision_assist` runner rejection for `input_budget_exceeded`
  - staged compare truth trimming and top-level `budget_control.max_input_chars`
- updated operator launch/config examples so local and Docker-guided profiles
  expose the same input-budget knob next to the existing image/token limits

## Runtime / Contract Notes

- `VISION_MAX_INPUT_CHARS` now owns the compare input-character limit with the
  same safe default value of `12000`.
- Runner rejection and staged compare projection now consume the same resolved
  limit, so public `budget_control.max_input_chars` no longer drifts from
  runner enforcement.
- This slice does not yet add richer configured-vs-effective diagnostics or new
  fail-safe clipping metadata; that follow-on remains under `TASK-166-05-02`.

## Validation

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runner.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/scripts/test_script_tooling.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`
