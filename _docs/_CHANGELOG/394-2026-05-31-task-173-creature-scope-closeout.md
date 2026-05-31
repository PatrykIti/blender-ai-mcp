# 394 - 2026-05-31 - TASK-173 Creature Scope-Convergence Closeout

## Summary

Closed `TASK-173` and its remaining children:

- `TASK-173-02` shape-convergence exit criteria and inspect escalation
- `TASK-173-03` creature-packet optional localization/segmentation activation
- `TASK-173-04` squirrel proof-lane runtime evidence surfacing

## Changes

- Added a compact `shape_convergence_disposition` to iterate responses and
  feedback so clients can distinguish all-roles-present shape drift from an
  exhausted build path.
- Kept creature `checkpoint_iterate` in `continue_build` for buildable
  shape/profile/proportion blockers, while preserving truth-signal and repeated
  stagnation escalation to `inspect_validate`.
- Replaced the generic optional localized-support trigger with a
  creature-domain, appendage-packet policy that requires under-grounded truth,
  silhouette/action-hint, or unresolved-defect evidence.
- Made segmentation run only when mask support is requested directly or
  localization produced seed boxes.
- Added typed `runtime_evidence` for classifier, main vision, localization, and
  segmentation participation on compare/iterate responses, compact feedback,
  router status, and localized-support harness output.
- Extended the existing squirrel proof lane with runtime-evidence assertions
  instead of adding a duplicate squirrel regression path.

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_reference_images.py::test_reference_compare_stage_checkpoint_projects_compare_time_segmentation_sidecar_into_packets tests/unit/adapters/mcp/test_reference_images.py::test_reference_compare_stage_checkpoint_projects_localization_only_support_into_part_segmentation tests/unit/adapters/mcp/test_reference_images.py::test_reference_compare_stage_checkpoint_threads_localization_seed_boxes_into_segmentation_request tests/unit/adapters/mcp/test_reference_images.py::test_reference_compare_stage_checkpoint_keeps_available_segmentation_sidecar_advisory_only tests/unit/adapters/mcp/test_reference_images.py::test_reference_compare_stage_checkpoint_uses_shared_part_segmentation_fallback_for_localization_only_runtime tests/unit/adapters/mcp/test_reference_images.py::test_reference_iterate_stage_checkpoint_keeps_refinement_stage_for_profile_blockers tests/unit/adapters/mcp/test_reference_images.py::test_reference_iterate_stage_checkpoint_holds_checkpoint_shape_convergence tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/router/application/test_router_contracts.py -q`
  -> 74 passed
- `PYTHONPATH=. poetry run pytest ./tests/unit`
  -> 3618 passed
- `poetry run mypy`
  -> success
- `git diff --check`
  -> passed
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
  -> passed
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py::test_reference_compare_segmentation_sidecar_transport_over_stdio tests/e2e/integration/test_guided_gate_state_transport.py::test_reference_compare_segmentation_sidecar_transport_over_streamable -q`
  -> 2 passed
- `poetry run python scripts/run_e2e_tests.py`
  -> 495 passed, 5 skipped in 1081.27s
  (`tests/e2e/e2e_test_PASSED_20260531_122426.log`)
