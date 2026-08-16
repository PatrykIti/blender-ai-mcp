# 228. Guided spatial target binding and freshness re-arm

Date: 2026-04-09

## Summary

Completed TASK-151 so guided spatial checks are now target-bound and
freshness-aware instead of being satisfiable once and then trusted forever.

## What Changed

- added guided spatial target identity fields on `guided_flow_state`:
  - `active_target_scope`
  - `spatial_scope_fingerprint`
- added guided spatial freshness fields:
  - `spatial_state_version`
  - `spatial_state_stale`
  - `last_spatial_check_version`
  - `spatial_refresh_required`
- `scene_scope_graph(...)` now binds or rebinds the active guided target scope
  for the spatial gate
- `scene_relation_graph(...)` and `scene_view_diagnostics(...)` only complete
  the guided spatial gate when they match that active scope
- helper-only scopes such as a single `Camera` no longer satisfy a
  creature/building spatial gate by themselves
- successful guided mutations such as:
  - `scene_clean_scene(...)`
  - `modeling_create_primitive(...)`
  - `modeling_transform_object(...)`
  - bounded attachment/alignment macros
  can now mark the spatial layer stale
- guided flow can now re-arm the spatial gate with
  `next_actions=["refresh_spatial_context"]` and later clear it again after a
  fresh `scene_scope_graph(...)` + matching spatial checks
- build visibility/search now narrow back to the spatial-context surface while
  spatial refresh is pending
- updated README, MCP docs, prompt docs, task board, and TASK-151 tree to
  match the shipped contract

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_context_bridge.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py tests/e2e/integration/test_guided_streamable_spatial_support.py -q`
