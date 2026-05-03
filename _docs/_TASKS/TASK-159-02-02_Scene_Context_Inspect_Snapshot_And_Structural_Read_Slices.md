# TASK-159-02-02: Scene Context, Inspect, Snapshot, And Structural Read Slices

**Parent:** [TASK-159-02](./TASK-159-02_Scene_MCP_Area_Modularization_And_Surface_Slices.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Extract scene context, structured inspect, snapshot/compare, and
structural-read helper clusters so the public wrappers stay readable without
changing the current read-heavy scene behavior.

This leaf owns the read-heavy scene surface:

- `scene_context(...)`
- `scene_inspect(...)`
- `scene_snapshot_state(...)`
- `scene_compare_snapshot(...)`
- `scene_get_hierarchy(...)`
- `scene_get_bounding_box(...)`
- `scene_get_origin_info(...)`

Grouped `scene_create(...)` / `scene_configure(...)` mega tools move under
[TASK-159-02-07](./TASK-159-02-07_Scene_Grouped_Create_And_Configure_Mega_Tool_Split.md).
Standalone object-utility wrappers such as cleanup, rename, visibility, camera
utility, and custom-property operations stay under
[TASK-159-02-05](./TASK-159-02-05_Scene_Object_Utility_Manage_And_Guided_Dirtying_Slices.md).

## Repository Touchpoints

- `server/adapters/mcp/areas/scene.py`
- likely new helper modules such as:
  - `server/adapters/mcp/areas/scene_inspect.py`
  - `server/adapters/mcp/areas/scene_state_reads.py`
- `server/adapters/mcp/contracts/scene.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_scene_context_mega.py`
- `tests/unit/tools/scene/test_scene_state_assistants.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/e2e/tools/scene/test_snapshot_tools.py`

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
- `_scene_inspect_object(...)`

## Planned Code Shape

```python
from .scene_inspect import execute_scene_inspect
from .scene_state_reads import (
    execute_scene_context,
    execute_scene_snapshot_state,
    execute_scene_compare_snapshot,
    execute_scene_structural_read,
)
```

## Runtime / Security Contract Notes

- keep current request validation, assistant-summary plumbing, and structured
  scene contracts intact
- preserve current read-only semantics and `assistant_summary` behavior for
  context/inspect/snapshot/hierarchy/bbox/origin flows
- keep grouped create/configure routing out of scope for this leaf so the
  read-heavy branch remains one focused extraction pass

## Tests To Add/Update

- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_scene_context_mega.py`
- `tests/unit/tools/scene/test_scene_state_assistants.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/e2e/tools/scene/test_snapshot_tools.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_mcp_tools_batch.py tests/unit/tools/scene/test_scene_context_mega.py tests/unit/tools/scene/test_scene_state_assistants.py tests/unit/tools/scene/test_scene_contracts.py tests/unit/tools/test_handler_rpc_alignment.py tests/unit/adapters/mcp/test_structured_contract_delivery.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/tools/scene/test_snapshot_tools.py -q`

## Docs To Update

- inherit parent docs closeout unless inspect/create ownership wording changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- scene context, inspect, snapshot/compare, and structural-read helpers no
  longer live as one inline cluster inside `scene.py`
- current scene contracts, assistant-summary hooks, and read-heavy wrappers
  remain stable
- unit plus snapshot E2E lanes still prove the same context/inspect/snapshot
  behavior

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
- keep grouped create/configure work on `TASK-159-02-07` instead of stretching
  this leaf beyond one read-heavy implementation pass
