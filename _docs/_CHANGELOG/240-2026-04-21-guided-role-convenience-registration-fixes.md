# 240. Guided role convenience registration fixes

Date: 2026-04-21

## Summary

Fixed two regressions in the `guided_role=...` convenience path on modeling
create/transform calls:

- successful guided convenience registration now uses the real created object
  name returned by Blender/tool execution
- successful scene mutations no longer raise after the fact when no active
  guided flow exists

## What Changed

- added one small helper in `server/adapters/mcp/areas/modeling.py` that:
  - auto-registers a guided role only when `guided_flow_state` is active
  - extracts the final created object name from the canonical success string
- changed the create convenience path so it no longer falls back to the raw
  primitive token for registration when Blender returns a different default
  name such as `Suzanne` or an auto-numbered name such as `Cube.001`
- changed create/transform convenience registration so non-guided or
  pre-goal-session calls can still succeed normally without trying to persist
  guided role state afterward
- updated public README, MCP docs, and prompt docs so they now state clearly:
  - `guided_register_part(...)` is canonical
  - `guided_role=...` is convenience-only
  - convenience auto-registration requires an active guided flow

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/tools/test_mcp_area_main_paths.py tests/unit/adapters/mcp/test_search_surface.py -q -k 'guided_role or test_modeling_create_primitive or test_modeling_transform_object'`
  - result on this machine: `7 passed`
- `poetry run ruff check server/adapters/mcp/areas/modeling.py tests/unit/tools/test_mcp_area_main_paths.py tests/unit/adapters/mcp/test_search_surface.py`
  - result on this machine: passed
