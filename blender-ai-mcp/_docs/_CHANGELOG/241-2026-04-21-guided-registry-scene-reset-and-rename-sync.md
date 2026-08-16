# 241. Guided registry scene reset and rename sync

Date: 2026-04-21

## Summary

Fixed three guided-session state drift cases that could leave the public
guided flow contract out of sync with the real Blender scene:

- `scene_clean_scene(...)` now clears guided part registration and resets the
  guided flow back to empty-scene primary bootstrap
- `guided_register_part(...)` now requires the named Blender object to exist
- successful `scene_rename_object(...)` calls now update guided part
  registration so later role-sensitive calls still recover the stored role

## What Changed

- in `server/adapters/mcp/session_capabilities.py`:
  - added real-scene existence validation for guided part registration
  - cleared `guided_part_registry` on `scene_clean_scene(...)`
  - reset clean-scene guided flows to `bootstrap_primary_workset` instead of
    carrying stale completed roles into an empty scene
  - added guided part registry rename synchronization
- in `server/adapters/mcp/router_helper.py`:
  - added a post-success rename sync hook for `scene_rename_object(...)`
- updated public docs so README and MCP docs now describe:
  - existing-object validation for `guided_register_part(...)`
  - rename-aware guided registry behavior
  - clean-scene bootstrap reset semantics

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_context_bridge.py tests/unit/adapters/mcp/test_router_elicitation.py -q -k 'scene_clean_scene or register_guided_part_role_rejects_nonexistent_scene_object or updates_guided_registry_after_scene_rename or rejects_missing_scene_object or allows_registered_object_transform_without_explicit_role'`
  - result on this machine: `5 passed`
- `poetry run ruff check server/adapters/mcp/session_capabilities.py server/adapters/mcp/router_helper.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_context_bridge.py tests/unit/adapters/mcp/test_router_elicitation.py`
  - result on this machine: passed
