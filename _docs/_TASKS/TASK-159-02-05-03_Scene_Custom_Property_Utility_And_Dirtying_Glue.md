# TASK-159-02-05-03: Scene Custom Property Utility And Dirtying Glue

**Parent:** [TASK-159-02-05](./TASK-159-02-05_Scene_Object_Utility_Manage_And_Guided_Dirtying_Slices.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Separate custom-property read/write wrappers and their structured-delivery
runtime glue into one focused scene-utility leaf.

## Repository Touchpoints

- `server/adapters/mcp/areas/scene.py`
- likely helper module such as `server/adapters/mcp/areas/scene_object_utils.py`
- `server/adapters/mcp/session_capabilities.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`

## Current Code Anchors

- `scene_get_custom_properties(...)`
- `scene_set_custom_property(...)`

## Planned Code Shape

```python
from .scene_object_utils import execute_scene_custom_property_utility
```

## Runtime / Security Contract Notes

- keep structured custom-property delivery and read/write payload shapes stable
- preserve guided dirtying/runtime glue for the mutating custom-property wrapper
- current proof for this slice is the exact unit/contract lane because the repo
  does not yet have a dedicated Blender-backed custom-property workflow test;
  add a follow-on E2E only when such a workflow exists

## Tests To Add/Update

- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_mcp_tools_batch.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_structured_contract_delivery.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_provider_inventory.py -q`

## Docs To Update

- inherit parent docs closeout unless custom-property ownership wording changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- custom-property wrappers have a focused home
- structured delivery and guided dirtying/runtime glue remain unchanged under
  the current unit/contract proof lane

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
