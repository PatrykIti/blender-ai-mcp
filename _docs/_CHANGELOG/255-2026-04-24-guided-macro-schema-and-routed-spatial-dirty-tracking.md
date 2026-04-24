# 255. Guided macro schema and routed spatial dirty tracking

Date: 2026-04-24

## Summary

Fixed two guided repair correctness gaps:

- bounded mesh-surface nudge guidance now uses the public macro action status
  vocabulary when a nudge is intentionally skipped because it exceeds
  `max_mesh_nudge`
- router-corrected multi-step executions now scan successful routed steps for
  spatial mutations instead of checking only the final step

## What Changed

- in `server/application/tool_handlers/macro_handler.py`:
  - changed the over-limit `mesh_surface_gap_nudge` action record from invalid
    `status="blocked"` to contract-valid `status="skipped"`
- in `server/adapters/mcp/session_capabilities.py`:
  - exposed one shared predicate for deciding whether a successful operation
    invalidates guided spatial facts
- in `server/adapters/mcp/router_helper.py`:
  - marked guided spatial state stale from the first successful routed step
    that can dirty spatial context, even if the final routed step is a
    material or other non-spatial operation
- in `tests/unit/tools/macro/test_macro_attach_part_to_surface.py` and
  `tests/unit/adapters/mcp/test_context_bridge.py`:
  - added regressions for contract-valid skipped mesh nudge guidance and
    multi-step routed spatial dirty tracking

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/tools/macro/test_macro_attach_part_to_surface.py tests/unit/adapters/mcp/test_context_bridge.py -q -k "mesh_nudge_exceeds_limit or guided_spatial_dirty_tracking_scans_all_successful_routed_steps"`
  - result on this machine: `2 passed`
- `PYTHONPATH=. poetry run pytest tests/unit/tools/macro/test_macro_attach_part_to_surface.py tests/unit/adapters/mcp/test_context_bridge.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py -q`
  - result on this machine: `66 passed`
- `poetry run ruff check server/application/tool_handlers/macro_handler.py server/adapters/mcp/router_helper.py server/adapters/mcp/session_capabilities.py tests/unit/tools/macro/test_macro_attach_part_to_surface.py tests/unit/adapters/mcp/test_context_bridge.py`
  - result on this machine: passed
- `poetry run mypy`
  - result on this machine: passed
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
  - result on this machine: passed
- `PYTHONPATH=. poetry run pytest tests/unit -q`
  - result on this machine: `3085 passed`
