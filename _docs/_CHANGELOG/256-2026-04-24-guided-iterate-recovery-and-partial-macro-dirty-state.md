# 256. Guided iterate recovery and partial macro dirty state

Date: 2026-04-24

## Summary

Fixed two guided-flow correctness gaps:

- recoverable staged compare setup errors no longer advance the guided loop to
  `finish_or_stop`
- partial macro reports that already mutated objects now still mark guided
  spatial facts stale

## What Changed

- in `server/adapters/mcp/areas/reference.py`:
  - added setup-error detection for blocked readiness, missing matching
    references, and active-scope mismatch errors
  - preserved current guided flow state on those recoverable setup errors
    while keeping explicit truth-only handoff escalation intact
- in `server/adapters/mcp/router_helper.py`:
  - treated `status="partial"` and reports with `objects_modified` as
    successful mutations for dirty-state purposes unless the report is
    explicitly failed/blocked/error
- in `tests/unit/adapters/mcp/test_reference_images.py` and
  `tests/unit/adapters/mcp/test_context_bridge.py`:
  - added regressions for recoverable iterate setup errors and partial
    mutating macro reports

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_context_bridge.py -q -k "preserves_flow_on_recoverable_reference_setup_error or partial_mutating_macro_reports_as_dirty or falls_back_to_truth_handoff_when_vision_compare_errors or scans_all_successful_routed_steps"`
  - result on this machine: `4 passed`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_context_bridge.py tests/unit/tools/macro/test_macro_attach_part_to_surface.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py -q`
  - result on this machine: `127 passed`
- `poetry run ruff check server/adapters/mcp/areas/reference.py server/adapters/mcp/router_helper.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_context_bridge.py`
  - result on this machine: passed
- `poetry run mypy`
  - result on this machine: passed
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
  - result on this machine: passed
- `PYTHONPATH=. poetry run pytest tests/unit -q`
  - result on this machine: `3087 passed`
