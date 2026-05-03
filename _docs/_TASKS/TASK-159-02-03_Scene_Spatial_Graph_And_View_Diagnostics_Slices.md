# TASK-159-02-03: Scene Spatial Graph And View Diagnostics Slices

**Parent:** [TASK-159-02](./TASK-159-02_Scene_MCP_Area_Modularization_And_Surface_Slices.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Separate spatial-graph and view-diagnostics helpers from `scene.py` while
preserving the guided spatial-support surface and its current visibility rules.

## Repository Touchpoints

- `server/adapters/mcp/areas/scene.py`
- likely new helper modules such as:
  - `server/adapters/mcp/areas/scene_spatial_graph.py`
  - `server/adapters/mcp/areas/scene_view.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/tools/scene/test_scene_view_diagnostics.py`

## Current Code Anchors

- `scene_scope_graph(...)`
- `_scene_scope_graph_async(...)`
- `scene_relation_graph(...)`
- `_scene_relation_graph_async(...)`
- `scene_view_diagnostics(...)`
- `_scene_view_diagnostics_async(...)`

## Planned Code Shape

```python
from .scene_spatial_graph import execute_scope_graph, execute_relation_graph
from .scene_view import execute_view_diagnostics
```

## Runtime / Security Contract Notes

- keep guided scope requirements, visibility-refresh expectations, and typed
  support-tool contracts unchanged
- preserve read-only posture for the spatial-support tools
- do not alter when these tools become visible or how search surfaces discover
  them on `llm-guided`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/tools/scene/test_scene_view_diagnostics.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_search_surface.py tests/e2e/tools/scene/test_scene_view_diagnostics.py -q`

## Docs To Update

- inherit parent docs closeout unless guided spatial-support ownership wording
  changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- spatial-graph and view-diagnostics helpers have explicit homes outside the
  monolith
- guided visibility and search still surface the same spatial-support tools
- typed view-diagnostics and graph contracts remain unchanged

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
