# 339. TASK-166 post-closeout coverage hardening

Date: 2026-05-10
Task: `TASK-166`

## Summary

- Added missing owner-lane proof for stable staged compare packet ids across
  retry-equivalent scheduler inputs and extraction/ranking retry requests.
- Added explicit `VISION_MAX_IMAGES=1` uncertainty coverage so impossible
  packet scheduling blocks packet execution instead of silently degrading.
- Added advisory-only compare-time segmentation coverage proving
  `part_segmentation` support evidence does not emit correction candidates by
  itself.
- Added compare/iterate contract parity coverage for full configured,
  effective, and fail-safe `budget_control` diagnostics.
- Added a Blender-runner E2E scheduler lane with deterministic staged captures
  for six-reference packet scheduling under
  `tests/e2e/vision/test_reference_stage_multi_reference_scaling.py`.

## Runtime / Contract Notes

- No public MCP tool names or payload semantics changed.
- The patch hardens TASK-166 test and documentation coverage for already
  shipped staged compare behavior.

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
  - passed, `140 passed`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
  - passed, `3324 passed`
- `poetry run python scripts/run_e2e_tests.py`
  - first full run exposed the existing stdio init timeout flake in
    `test_stdio_transport_e2e_keeps_same_session_id_across_calls_in_one_client`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_mcp_transport_modes.py::test_stdio_transport_e2e_keeps_same_session_id_across_calls_in_one_client -q`
  - passed, `1 passed`
- `poetry run python scripts/run_e2e_tests.py`
  - passed on rerun, `469 passed, 3 skipped`
- post-clean-pass drift fix reran `poetry run python scripts/run_e2e_tests.py`
  - first strengthened exact-reference assertion used sequential expected ids
    and failed; the test now compares the ids returned by `reference_images`
  - passed after the assertion fix, `469 passed, 3 skipped`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
  - passed
