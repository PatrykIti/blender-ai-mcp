# 259. Guided role-hint visibility refresh

Date: 2026-04-24

## Summary

Kept the native FastMCP tool surface synchronized after guided role-hint
registration advances the guided flow state.

## What Changed

- in `server/adapters/mcp/session_capabilities.py`:
  - refresh session visibility after sync `register_guided_part_role(...)`
    stores an updated guided flow state
  - keep the sync visibility refresh wrapper best-effort for non-native test
    contexts that do not expose FastMCP visibility methods
- in `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`:
  - added a regression covering role-hint registration from visible build tools
    reapplying visibility when primary role completion moves the session into a
    spatial-refresh-gated step

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py tests/unit/tools/test_mcp_area_main_paths.py -q`
  - result on this machine: `56 passed`
- `poetry run ruff check server/adapters/mcp/session_capabilities.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
  - result on this machine: passed
- `poetry run mypy`
  - result on this machine: passed
- `PYTHONPATH=. poetry run pytest tests/unit -q`
  - result on this machine: `3093 passed`
