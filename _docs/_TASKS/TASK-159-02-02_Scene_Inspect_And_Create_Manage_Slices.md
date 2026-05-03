# TASK-159-02-02: Scene Context, Inspect, Snapshot, And Core Create Manage Slices

**Parent:** [TASK-159-02](./TASK-159-02_Scene_MCP_Area_Modularization_And_Surface_Slices.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Extract scene context, structured inspect, snapshot/structural-read, and grouped
create/configure helper clusters so the public wrappers stay readable without
changing the current mega-tool behavior.

This leaf owns the read-heavy scene surface plus the grouped
`scene_create(...)` / `scene_configure(...)` mega tools. Standalone object
utility wrappers such as cleanup, rename, visibility, camera utility, and
custom-property operations move under [TASK-159-02-05](./TASK-159-02-05_Scene_Object_Utility_Manage_And_Guided_Dirtying_Slices.md).

## Repository Touchpoints

- `server/adapters/mcp/areas/scene.py`
- likely new helper modules such as:
  - `server/adapters/mcp/areas/scene_inspect.py`
  - `server/adapters/mcp/areas/scene_manage.py`
- `server/adapters/mcp/contracts/scene.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_scene_context_mega.py`
- `tests/unit/tools/scene/test_scene_state_assistants.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`

## Current Code Anchors

- `scene_context(...)`
- `_scene_get_mode(...)`
- `_scene_list_selection(...)`
- `scene_inspect(...)`
- `scene_snapshot_state(...)`
- `scene_compare_snapshot(...)`
- `scene_get_hierarchy(...)`
- `scene_get_bounding_box(...)`
- `scene_get_origin_info(...)`
- `scene_create(...)`
- `scene_configure(...)`
- `_scene_inspect_object(...)`
- `_scene_create_light(...)`
- `_scene_create_camera(...)`

## Planned Code Shape

```python
from .scene_inspect import execute_scene_inspect
from .scene_manage import (
    execute_scene_context,
    execute_scene_snapshot_state,
    execute_scene_compare_snapshot,
    execute_scene_structural_read,
    execute_scene_create,
    execute_scene_configure,
)
```

## Runtime / Security Contract Notes

- keep current request validation, assistant-summary plumbing, and structured
  scene contracts intact
- preserve current read/write mode expectations for context/inspect/snapshot
  reads vs grouped create/configure writes
- keep mega-tool wrapper semantics and response shapes stable

## Tests To Add/Update

- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_scene_context_mega.py`
- `tests/unit/tools/scene/test_scene_state_assistants.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_mcp_tools_batch.py tests/unit/tools/scene/test_scene_context_mega.py tests/unit/tools/scene/test_scene_state_assistants.py tests/unit/tools/scene/test_scene_contracts.py tests/unit/tools/test_handler_rpc_alignment.py tests/unit/adapters/mcp/test_structured_contract_delivery.py -q`

## Docs To Update

- inherit parent docs closeout unless inspect/create ownership wording changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- scene context, inspect, snapshot/structural-read, and grouped
  create/configure helpers no longer live as one inline cluster inside
  `scene.py`
- current scene contracts, assistant-summary hooks, and mega-tool wrappers
  remain stable
- unit tests still prove the same context/inspect/snapshot/create/configure
  behavior

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
