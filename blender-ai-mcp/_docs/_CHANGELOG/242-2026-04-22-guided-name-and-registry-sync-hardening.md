# 242. Guided name and registry sync hardening

Date: 2026-04-22

## Summary

Hardened guided-session state against three more scene/state drift cases:

- guided create with `guided_role=...` now requires an explicit semantic name
  before mutation
- object renames now re-arm guided spatial checks because target-scope
  fingerprints are name-based
- join/separate operations now remove stale guided part registrations instead
  of leaving old role state behind

## What Changed

- in `server/adapters/mcp/areas/modeling.py`:
  - blocked `modeling_create_primitive(guided_role=...)` when no explicit
    semantic `name` is provided on an active guided flow
- in `server/adapters/mcp/session_capabilities.py`:
  - marked `scene_rename_object` as a guided spatial-dirty mutation
  - added removal of guided part registrations after destructive
    identity/topology changes
- in `server/adapters/mcp/router_helper.py`:
  - extended post-success guided registry sync from rename-only behavior to:
    - `scene_rename_object(...)`
    - `modeling_join_objects(...)`
    - `modeling_separate_object(...)`
- updated public docs so README and MCP docs now describe:
  - explicit-name requirement for guided create
  - rename-triggered spatial refresh
  - re-registration expectations after join/separate

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/tools/test_mcp_area_main_paths.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_context_bridge.py -q -k 'explicit_name_for_guided_role or rejects_guided_role_without_explicit_name or scene_rename_object_marks_guided_spatial_state_stale or removes_guided_registry_entries_after_join or removes_guided_registry_entry_after_separate'`
  - result on this machine: `5 passed`
- `poetry run ruff check server/adapters/mcp/areas/modeling.py server/adapters/mcp/session_capabilities.py server/adapters/mcp/router_helper.py tests/unit/tools/test_mcp_area_main_paths.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_context_bridge.py`
  - result on this machine: passed
