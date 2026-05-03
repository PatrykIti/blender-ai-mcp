# TASK-159-03-04-03: Addon Scene Custom Property Utility Split

**Parent:** [TASK-159-03-04](./TASK-159-03-04_Addon_Scene_Creation_Visibility_And_Metadata_Utilities.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Separate custom-property read/write helpers into one focused addon utility leaf.

## Repository Touchpoints

- `blender_addon/application/handlers/scene.py`
- likely helper module such as `blender_addon/application/handlers/scene_utility_mixin.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/e2e/tools/scene/test_scene_utility_workflow.py`

## Current Code Anchors

- `SceneHandler.get_custom_properties(...)`
- `SceneHandler.set_custom_property(...)`

## Planned Code Shape

```python
class SceneHandler(SceneCustomPropertyUtilityMixin, ...):
    pass
```

## Runtime / Security Contract Notes

- keep custom-property read/write payloads and structured delivery stable

## Tests To Add/Update

- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/e2e/tools/scene/test_scene_utility_workflow.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_mcp_tools_batch.py tests/unit/tools/test_handler_rpc_alignment.py tests/unit/adapters/mcp/test_structured_contract_delivery.py tests/e2e/tools/scene/test_scene_utility_workflow.py -q`

## Docs To Update

- inherit parent docs closeout unless custom-property ownership wording changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- custom-property helpers have a focused home
- structured delivery and payload semantics remain unchanged

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
