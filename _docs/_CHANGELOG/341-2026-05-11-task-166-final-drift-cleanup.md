# 341. TASK-166 final drift cleanup

Date: 2026-05-11
Task: `TASK-166`

## Summary

- Kept compact staged compare responses joinable when
  `correction_candidates[*].vision_evidence.packet_evidence_refs` are present
  by forcing additive top-level `compare_diagnostics` to remain visible.
- Treated successful ranking-pass downgrades to `low_information` or `blocked`
  as packet uncertainty so compact responses surface the packet status and
  uncertainty note instead of hiding diagnostics.
- Forwarded the documented `VISION_SEGMENTATION_*` opt-in sidecar variables
  through `scripts/run_streamable_openrouter.sh`.
- Added unit regressions for candidate packet refs, ranking-pass downgrades,
  and Docker helper sidecar env forwarding.

## Runtime / Contract Notes

- No public MCP tool names changed.
- Clean compact single-packet responses may still omit `compare_diagnostics`
  when no packet refs or uncertainty are present.
- Candidate-level packet refs now always have a public top-level diagnostic
  packet surface to join against.
- Optional segmentation remains default-off and advisory-only.

## Validation

- `poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_reference_images.py::test_reference_compare_stage_checkpoint_emits_compact_diagnostics_for_packet_evidence_refs tests/unit/adapters/mcp/test_reference_images.py::test_reference_compare_stage_checkpoint_emits_compare_diagnostics_on_compact_ranking_downgrade tests/unit/scripts/test_script_tooling.py::test_streamable_openrouter_shell_script_contains_required_runtime_env -q`
  - passed, `15 passed`
- `poetry run pytest ./tests/unit`
  - passed outside sandbox, `3328 passed`
- `poetry run python scripts/run_e2e_tests.py`
  - passed outside sandbox, `470 passed, 3 skipped`
- `poetry run pytest tests/unit/adapters/mcp/test_reference_images.py::test_reference_compare_stage_checkpoint_emits_compact_diagnostics_for_packet_evidence_refs tests/unit/adapters/mcp/test_reference_images.py::test_reference_compare_stage_checkpoint_emits_compare_diagnostics_on_compact_ranking_downgrade -q`
  - passed after `ruff format` updated the test file, `2 passed`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
  - passed outside sandbox after the required rerun
