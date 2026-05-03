# TASK-159-02-02: Scene Inspect And Create Manage Slices

**Parent:** [TASK-159-02](./TASK-159-02_Scene_MCP_Area_Modularization_And_Surface_Slices.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Extract scene inspect and create/manage helper clusters so the public wrappers
stay readable without changing the current mega-tool behavior.

## Repository Touchpoints

- `server/adapters/mcp/areas/scene.py`
- likely new helper modules such as:
  - `server/adapters/mcp/areas/scene_inspect.py`
  - `server/adapters/mcp/areas/scene_manage.py`
- `server/adapters/mcp/contracts/scene.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_scene_context_mega.py`
- `tests/unit/tools/scene/test_scene_contracts.py`

## Current Code Anchors

- `scene_context(...)`
- `scene_inspect(...)`
- `scene_create(...)`
- `scene_configure(...)`
- `_scene_inspect_object(...)`
- `_scene_create_light(...)`
- `_scene_create_camera(...)`

## Planned Code Shape

```python
from .scene_inspect import execute_scene_inspect
from .scene_manage import execute_scene_create, execute_scene_configure
```

## Runtime / Security Contract Notes

- keep current request validation and structured scene contracts intact
- preserve current read/write mode expectations for inspect vs create/configure
- keep mega-tool wrapper semantics and response shapes stable

## Tests To Add/Update

- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_scene_context_mega.py`
- `tests/unit/tools/scene/test_scene_contracts.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_mcp_tools_batch.py tests/unit/tools/scene/test_scene_context_mega.py tests/unit/tools/scene/test_scene_contracts.py -q`

## Docs To Update

- inherit parent docs closeout unless inspect/create ownership wording changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- inspect and create/manage helpers no longer live as one inline cluster inside
  `scene.py`
- current scene contracts and mega-tool wrappers remain stable
- unit tests still prove the same inspect/create/configure behavior

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
