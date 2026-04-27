# 264. Guided spatial scope and RPC trace hardening

Date: 2026-04-27

## Summary

Closed PR-review follow-ups around guided spatial scope identity, creature
limb heuristics, and addon RPC trace overhead.

## What Changed

- in `server/application/services/spatial_graph.py`:
  - normalized single-target `primary_target` to the canonical scoped object
    name instead of preserving padded caller input
  - restricted side/direction-only limb fallback to anatomical `fore` / `hind`
    tokens, avoiding false creature seams for non-anatomical names such as
    `front_right_window`
- in `server/adapters/mcp/session_capabilities.py` and
  `server/adapters/mcp/areas/scene.py`:
  - kept `spatial_refresh_required` checks bound to the already-active guided
    target scope instead of rebinding to a newly supplied object set
  - surfaced a mismatch message for `scene_scope_graph(...)` during refresh,
    matching the relation/view diagnostic behavior
- in `blender_addon/infrastructure/rpc_server.py`:
  - made trace-file setup degrade to no-trace mode when the trace directory is
    unavailable
  - removed per-event `fsync` from the RPC trace hot path

## Documentation

- updated `README.md`, `_docs/_MCP_SERVER/README.md`, and
  `_docs/_PROMPTS/README.md` to clarify that refresh checks must use the
  already-bound active scope
- updated `_docs/_ADDON/README.md` to document best-effort trace startup and
  non-fsync trace writes

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_spatial_graph_service.py tests/unit/adapters/rpc/test_rpc_server_edge_cases.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_scene_guided_scope_requirements.py -q`
  - result on this machine: `64 passed`
- `poetry run ruff check server/application/services/spatial_graph.py server/adapters/mcp/areas/reference.py server/adapters/mcp/session_capabilities.py server/adapters/mcp/areas/scene.py blender_addon/infrastructure/rpc_server.py tests/unit/tools/scene/test_spatial_graph_service.py tests/unit/adapters/rpc/test_rpc_server_edge_cases.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_scene_guided_scope_requirements.py`
  - result on this machine: passed
- `poetry run mypy server/application/services/spatial_graph.py server/adapters/mcp/session_capabilities.py server/adapters/mcp/areas/scene.py blender_addon/infrastructure/rpc_server.py`
  - result on this machine: passed
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --files README.md _docs/_ADDON/README.md _docs/_CHANGELOG/README.md _docs/_CHANGELOG/264-2026-04-27-guided-spatial-scope-and-rpc-trace-hardening.md _docs/_MCP_SERVER/README.md _docs/_PROMPTS/README.md blender_addon/infrastructure/rpc_server.py server/adapters/mcp/areas/reference.py server/adapters/mcp/areas/scene.py server/adapters/mcp/session_capabilities.py server/application/services/spatial_graph.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_scene_guided_scope_requirements.py tests/unit/adapters/rpc/test_rpc_server_edge_cases.py tests/unit/tools/scene/test_spatial_graph_service.py`
  - result on this machine: passed
