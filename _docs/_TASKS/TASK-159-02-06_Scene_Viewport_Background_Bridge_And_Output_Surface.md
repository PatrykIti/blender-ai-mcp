# TASK-159-02-06: Scene Viewport Background Bridge And Output Surface

**Parent:** [TASK-159-02](./TASK-159-02_Scene_MCP_Area_Modularization_And_Surface_Slices.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Separate the public viewport capture/output path from `scene.py` so
`scene_get_viewport(...)` has an explicit owner for output formatting,
task-mode/addon background execution, and viewport-vs-camera capture semantics.

This leaf owns the MCP-facing viewport surface. Blender/runtime viewport
behavior inside addon `SceneHandler` stays owned by
[TASK-159-03-03](./TASK-159-03-03_Addon_Scene_Viewport_World_Render_And_Registration.md).

## Repository Touchpoints

- `server/adapters/mcp/areas/scene.py`
- likely new helper module such as `server/adapters/mcp/areas/scene_viewport.py`
- `tests/unit/tools/scene/test_mcp_viewport_output.py`
- `tests/unit/adapters/mcp/test_task_mode_tools.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`
- `tests/unit/adapters/mcp/test_provider_versions.py`
- `tests/e2e/tools/scene/test_scene_get_viewport.py`
- `tests/e2e/tools/scene/test_scene_get_viewport_camera.py`

## Current Code Anchors

- `_format_viewport_output(...)`
- `scene_get_viewport(...)`
- task-mode viewport path covered by `tests/unit/adapters/mcp/test_task_mode_tools.py`

## Planned Code Shape

```python
from .scene_viewport import execute_scene_get_viewport, format_viewport_output

async def scene_get_viewport(ctx, ...):
    return await execute_scene_get_viewport(ctx, ...)
```

## Runtime / Security Contract Notes

- preserve the public `scene_get_viewport(...)` tool name, docstring, versions,
  and manifest/provider exposure
- preserve `USER_PERSPECTIVE` vs named-camera semantics, output-mode behavior,
  and task-mode timeout/cancellation handling
- do not bypass the current addon background bridge for task-mode captures
- keep viewport output delivery behavior identical for `IMAGE`, `BASE64`,
  `FILE`, and `MARKDOWN`

## Tests To Add/Update

- `tests/unit/tools/scene/test_mcp_viewport_output.py`
- `tests/unit/adapters/mcp/test_task_mode_tools.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`
- `tests/unit/adapters/mcp/test_provider_versions.py`
- `tests/e2e/tools/scene/test_scene_get_viewport.py`
- `tests/e2e/tools/scene/test_scene_get_viewport_camera.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_mcp_viewport_output.py tests/unit/adapters/mcp/test_task_mode_tools.py tests/unit/adapters/mcp/test_public_surface_docs.py tests/unit/adapters/mcp/test_provider_inventory.py tests/unit/adapters/mcp/test_provider_versions.py tests/e2e/tools/scene/test_scene_get_viewport.py tests/e2e/tools/scene/test_scene_get_viewport_camera.py -q`

## Docs To Update

- inherit parent docs closeout unless viewport capture ownership wording changes
  in `_docs/_MCP_SERVER/README.md` or `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- `scene_get_viewport(...)` no longer survives as an undocumented facade
  remainder in `scene.py`
- output-mode formatting plus task-mode/addon background capture flow have a
  clear home outside the monolith
- the public viewport surface keeps the same tool name, version policy,
  inventory presence, and output behavior
- targeted unit and Blender-backed viewport regressions still prove the same
  capture semantics

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
