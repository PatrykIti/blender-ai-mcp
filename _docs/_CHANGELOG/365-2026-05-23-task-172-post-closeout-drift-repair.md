# 365. TASK-172 post-closeout drift repair

Date: 2026-05-23

## Summary

Ran a post-closeout audit of `TASK-172` and repaired the remaining runtime,
test-accounting, and task-governance drift that was left behind after the
family was marked done.

## Changes

- fixed `scripts/vision_harness.py --mode localized-support` so it no longer
  requires an unrelated primary vision backend config and now accepts
  `--references-json` without an inline `--reference` when the runtime path
  already supports that input shape
- added new harness regression coverage for:
  - the live subprocess localized-support CLI path
  - localized-support docs / contract assertions
  - compact feedback projection of `localized_support_reason`
  - localization-only `part_segmentation` fallback on early compare exits
  - router status feedback when localized support is configured
- repaired compact feedback carriers so localized-support activation and
  degradation survive the `evidence_summary` / `uncertainty_notes` budget
  instead of disappearing behind higher-volume compare evidence
- repaired `part_segmentation` fallback reporting so the shared public carrier
  now reflects localization-only runtime state instead of falling back to stale
  segmentation-only wording
- corrected `TASK-172` governance docs:
  - narrowed the umbrella dependency from the still-open `TASK-140-06`
    umbrella to the already-landed `TASK-140-06-01` / `TASK-140-06-03`
    substrate
  - removed the stale execution-order implication that `TASK-172-04` shipped as
    a live delivery step
  - replaced lingering implementation notes that still routed readers through
    superseded `TASK-172-04`
  - tightened `TASK-172-06` / changelog wording so proof-lane claims match the
    actual subprocess vs unit coverage split

## Validation

- `git diff --check`
- `poetry run pytest tests/unit/scripts/test_script_tooling.py -q -k 'localized_support'`
- `poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q -k 'localized_support_reason_and_degradation or localization_only_runtime or enabled_segmentation_sidecar_as_unavailable'`
- `poetry run pytest tests/unit/router/application/test_router_contracts.py -q -k 'localized_support_notes or reference_understanding_summary'`
- `poetry run pytest tests/e2e/vision/test_reference_understanding_fixture_only_harness.py -q -k 'localized_support'`
- `poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q -k 'localization_sidecar_transport'`
- `poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`
- `poetry run pre-commit run --all-files --show-diff-on-failure`
