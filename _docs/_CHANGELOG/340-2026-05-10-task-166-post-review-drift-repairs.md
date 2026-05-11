# 340. TASK-166 post-review drift repairs

Date: 2026-05-10
Task: `TASK-166`

## Summary

- Fixed packet reference selection so a view-specific generic reference is
  preferred over a target-specific fallback from another view when a packet has
  no target-specific reference for its own view.
- Fixed compare-time segmentation sidecar normalization so enabled sidecars that
  return no bounded `parts` report `part_segmentation.status="unavailable"`
  instead of projecting an empty available support envelope.
- Added unit regressions for the view-specific generic fallback and empty
  sidecar result semantics.
- Added stdio transport coverage proving enabled compare-time segmentation
  sidecar output is serialized through the existing
  `reference_compare_stage_checkpoint` flow as advisory `part_segmentation` and
  packet-local `support_evidence`.

## Runtime / Contract Notes

- No public MCP tool names changed.
- The sidecar remains default-off, advisory-only, and outside deterministic
  verifier authority.
- Empty sidecar results now match the documented MCP surface behavior:
  unavailable advisory evidence, no packet-local part-segmentation support
  evidence.

## Validation

- `poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py::test_build_compare_packets_prefers_generic_view_over_target_any_view_fallback tests/unit/adapters/mcp/test_reference_compare_packets.py::test_collect_compare_time_segmentation_support_treats_empty_parts_as_unavailable tests/e2e/integration/test_guided_gate_state_transport.py::test_reference_compare_segmentation_sidecar_transport_over_stdio -q`
  - passed, `3 passed`
- `poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_reference_images.py::test_reference_compare_stage_checkpoint_projects_compare_time_segmentation_sidecar_into_packets tests/unit/adapters/mcp/test_reference_images.py::test_reference_compare_stage_checkpoint_keeps_available_segmentation_sidecar_advisory_only tests/unit/adapters/mcp/test_reference_images.py::test_reference_compare_stage_checkpoint_reports_enabled_segmentation_sidecar_as_unavailable tests/e2e/integration/test_guided_gate_state_transport.py -q`
  - passed, `24 passed, 8 skipped`
- `poetry run pytest ./tests/unit`
  - passed outside sandbox, `3326 passed`
- `poetry run python scripts/run_e2e_tests.py`
  - passed outside sandbox, `470 passed, 3 skipped`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
  - passed outside sandbox
