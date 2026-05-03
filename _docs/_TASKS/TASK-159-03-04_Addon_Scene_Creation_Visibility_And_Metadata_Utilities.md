# TASK-159-03-04: Addon Scene Creation, Visibility, And Metadata Utilities

**Parent:** [TASK-159-03](./TASK-159-03_Addon_Scene_Handler_Modularization_And_Blender_Ownership_Boundaries.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Separate creation, mode-switch, visibility, and custom-property utility helpers
from addon `SceneHandler` while preserving RPC behavior and Blender object-mode
assumptions.

## Repository Touchpoints

- `blender_addon/application/handlers/scene.py`
- likely helper module such as `blender_addon/application/handlers/scene_utility_mixin.py`
- `server/application/tool_handlers/scene_handler.py`
- `tests/unit/tools/scene/test_scene_mode.py`
- `tests/unit/tools/scene/test_scene_construction.py`
- `tests/unit/tools/scene/test_hide_object.py`
- `tests/unit/tools/scene/test_show_all_objects.py`
- `tests/unit/tools/scene/test_rename_object.py`
- `tests/unit/tools/scene/test_isolate_object.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/e2e/tools/scene/test_scene_utility_workflow.py`

## Current Code Anchors

- `SceneHandler.create_light(...)`
- `SceneHandler.create_camera(...)`
- `SceneHandler.create_empty(...)`
- `SceneHandler.set_mode(...)`
- `SceneHandler.rename_object(...)`
- `SceneHandler.hide_object(...)`
- `SceneHandler.show_all_objects(...)`
- `SceneHandler.isolate_object(...)`
- `SceneHandler.get_custom_properties(...)`
- `SceneHandler.set_custom_property(...)`

## Planned Code Shape

```python
class SceneHandler(SceneUtilityMixin, ...):
    pass
```

## Runtime / Security Contract Notes

- preserve current object-mode assumptions and validation errors for
  `set_mode(...)`
- preserve current creation helper payloads and default handling for
  light/camera/empty operations
- preserve current viewport/render visibility side effects for hide/show/isolate
- keep custom-property read/write payloads and structured delivery stable

## Tests To Add/Update

- `tests/unit/tools/scene/test_scene_mode.py`
- `tests/unit/tools/scene/test_scene_construction.py`
- `tests/unit/tools/scene/test_hide_object.py`
- `tests/unit/tools/scene/test_show_all_objects.py`
- `tests/unit/tools/scene/test_rename_object.py`
- `tests/unit/tools/scene/test_isolate_object.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/e2e/tools/scene/test_scene_utility_workflow.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_mode.py tests/unit/tools/scene/test_scene_construction.py tests/unit/tools/scene/test_hide_object.py tests/unit/tools/scene/test_show_all_objects.py tests/unit/tools/scene/test_rename_object.py tests/unit/tools/scene/test_isolate_object.py tests/unit/tools/scene/test_scene_mcp_tools_batch.py tests/unit/tools/test_handler_rpc_alignment.py tests/unit/adapters/mcp/test_structured_contract_delivery.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/tools/scene/test_scene_utility_workflow.py -q`

## Docs To Update

- inherit parent docs closeout unless addon utility ownership wording changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- creation, mode-switch, visibility, and custom-property helpers no longer
  share one edit zone with inspection, viewport, or world/render internals
- RPC method names, payloads, and mode-validation errors remain stable
- structured custom-property delivery keeps the same contract
- focused unit/e2e lanes still prove the same utility behavior

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
