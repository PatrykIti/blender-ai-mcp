# 393 - 2026-05-31 - Vision Follow-Up Closeout

## Summary

Closed the remaining promoted Vision Output Quality follow-up slices for
`TASK-177-02`, `TASK-179-02`, `TASK-180-02`, `TASK-180-03`, `TASK-180-04`,
`TASK-181-01`, `TASK-182-01`, and `TASK-182-02`, plus the `TASK-173-01`
scope-convergence slice.

## Changes

- Added compact `target_top` and `target_oblique_left` staged-capture presets
  with symbolic `view_kind` and `projection` metadata.
- Centralized calibrated per-object IoU severity thresholds and added a
  fixture-backed calibration proof.
- Persisted session-stable Set-of-Mark IDs through the guided registry and
  threaded the exact `mark_id_map` into overlays and compare packets.
- Projected optional localization sidecar candidates into reference-side mark
  provenance without changing the default-off, advisory-only sidecar boundary.
- Added typed mark correspondence, rejected-mark reporting, and one bounded
  valid-mark retry for packet compare results.
- Promoted the guided part registry to the first staged-compare scope source,
  keeping legacy focus/name clustering as fallback and exposing scope provenance
  in diagnostics.
- Added packet-scoped Critic `open_defects`, same-packet Verify
  `verify_status`, iterate-state defect carryover, synthesis preservation, and
  compact feedback notes for unresolved defects.
- Added provenance-tagged `authoritative_next_action_provenance` while keeping
  the existing `authoritative_next_actions` compatibility list.

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_capture_runtime.py tests/unit/adapters/mcp/test_vision_capture_bundle.py tests/unit/adapters/mcp/test_vision_policy.py -q` -> 37 passed
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py::test_packet_defect_tracking_assigns_packet_scoped_ids_and_verifies_prior_defects tests/unit/adapters/mcp/test_reference_compare_packets.py::test_synthesize_packet_vision_result_preserves_truncation_accounting tests/unit/adapters/mcp/test_reference_compare_packets.py::test_merge_packet_phase_results_does_not_keep_extraction_focus_after_ranking_downgrade tests/unit/adapters/mcp/test_reference_images.py::test_reference_orchestrator_feedback_tags_authoritative_next_action_provenance tests/unit/adapters/mcp/test_vision_silhouette.py::test_per_object_iou_severity_thresholds_match_calibration_fixture -q` -> 5 passed
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_capture_runtime.py tests/unit/adapters/mcp/test_vision_capture_bundle.py tests/unit/adapters/mcp/test_vision_silhouette.py tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_reference_images.py::test_reference_orchestrator_feedback_projects_runtime_policy_block tests/unit/adapters/mcp/test_reference_images.py::test_reference_orchestrator_feedback_tags_authoritative_next_action_provenance tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_vision_prompting.py -q` -> 180 passed
- `PYTHONPATH=. poetry run pytest ./tests/unit` -> 3614 passed
- `poetry run mypy` -> success
- `git diff --check` -> success
- `poetry run python scripts/run_e2e_tests.py` -> 495 passed, 5 skipped
  (`tests/e2e/e2e_test_PASSED_20260531_110143.log`)
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
  -> passed
