# 252. Spatial scope errors, visibility refresh, and ortho diagnostics

Date: 2026-04-22

## Summary

Fixed three guided/runtime consistency gaps:

- `scene_scope_graph(...)` / `scene_relation_graph(...)` no longer accept an
  empty implicit whole-scene request and return an empty scope artifact
- guided spatial-check completion now reapplies FastMCP visibility as soon as
  the flow advances, so ordinary discovery clients see the unlocked surface
  immediately
- addon-side `scene.get_view_diagnostics` now preserves orthographic
  projection when mirroring standard `USER_PERSPECTIVE` views such as
  `FRONT`, `RIGHT`, and `TOP`

## What Changed

- in `server/application/services/spatial_graph.py`:
  - `build_scope_graph(...)` now rejects calls that omit
    `target_object` / `target_objects` / `collection_name` instead of
    fabricating an empty `scene` scope
- in `server/adapters/mcp/session_capabilities.py`:
  - sync and async guided spatial-check completion paths now reapply
    session visibility after persisting the updated `guided_flow_state`
- in `blender_addon/application/handlers/scene.py`:
  - temporary view-diagnostics mirror cameras now switch to `ORTHO` when the
    live 3D view is in orthographic standard-view mode
- updated public docs in:
  - `README.md`
  - `_docs/_MCP_SERVER/README.md`
  - `_docs/_ADDON/README.md`
  so the explicit-scope, visibility-refresh, and diagnostics behavior matches
  the shipped runtime

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit -q`
  - result on this machine: `3071 passed`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
  - result on this machine: passed
