# 367. TASK-172 final audit drift repair

Date: 2026-05-23

## Summary

Repaired final audit drift found after the `TASK-172` closeout by tightening
stale task wording and adding the missing Streamable HTTP transport coverage
for the compare-time segmentation sidecar.

## Changes

- updated the `TASK-172` umbrella acceptance criteria so the closed family
  describes the shipped default-off compare-time localization path instead of
  stale open-work wording
- clarified that superseded `TASK-172-04` owns no active implementation proof
  lane and inherits segmentation runtime proof from earlier sidecar owner tasks
  plus the shipped `TASK-172` activation and harness lanes
- added Streamable HTTP E2E coverage for the optional compare-time segmentation
  sidecar to match the existing stdio coverage and localization transport proof
- changed incomplete localization sidecar configuration from a startup-time
  validation failure into bounded unavailable prerequisite diagnostics, so
  `VISION_LOCALIZATION_ENABLED=true` without `VISION_LOCALIZATION_ENDPOINT`
  does not block normal guided/reference flow
- applied the same non-fatal prerequisite behavior to the optional reference
  classifier and segmentation sidecar, including RU provenance diagnostics and
  compare-time segmentation unavailable notes when endpoints are missing
- corrected optional-capability inventory lifecycle reporting for reference
  classifier support so externally inherited classifiers report
  `external_runtime`, while explicit classifier sidecars still report
  `sidecar_process`

## Validation

- `git diff --check` - passed
- `poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_reference_compare_packets.py -q -k 'optional_capability_inventory or optional_localization or localization_support or optional_reference_classifier or optional_segmentation or segmentation_support'`
  - passed, 24 passed / 52 deselected
- `poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q -k 'segmentation_sidecar_transport or localization_sidecar_transport'`
  - passed, 4 passed / 16 deselected
- `poetry run pytest ./tests/unit` - passed, 3510 passed
- `poetry run python scripts/run_e2e_tests.py` - passed, 482 passed / 5 skipped
  (`tests/e2e/e2e_test_PASSED_20260523_231609.log`)
- `poetry run pre-commit run --all-files --show-diff-on-failure` - passed
