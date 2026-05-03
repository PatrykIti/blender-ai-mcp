# TASK-159-03-04: Addon Scene Creation, Visibility, And Metadata Utilities

**Parent:** [TASK-159-03](./TASK-159-03_Addon_Scene_Handler_Modularization_And_Blender_Ownership_Boundaries.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Split addon creation, mode/visibility, and custom-property utilities into
focused leaves while preserving RPC behavior and Blender object-mode
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
- `tests/e2e/tools/scene/test_hide_object.py`
- `tests/e2e/tools/scene/test_show_all_objects.py`
- `tests/e2e/tools/scene/test_rename_object.py`
- `tests/e2e/tools/scene/test_isolate_object.py`
- `tests/e2e/tools/scene/test_scene_get_viewport_camera.py`
- `tests/e2e/tools/scene/test_scene_view_diagnostics.py`
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

## Pseudocode

```python
creation_leaf = ["create_light", "create_camera", "create_empty"]
mode_visibility_leaf = [
    "set_mode",
    "rename_object",
    "hide_object",
    "show_all_objects",
    "isolate_object",
]
custom_property_leaf = ["get_custom_properties", "set_custom_property"]

for rpc_method in creation_leaf + mode_visibility_leaf + custom_property_leaf:
    keep_public_scene_handler_name(rpc_method)
    move_implementation_to_focused_utility_leaf(rpc_method)

preserve_object_mode_assumptions()
preserve_existing_rpc_payloads()
```

## Implementation Notes

- Keep creation helpers separate from mode/visibility helpers so object-spawn
  defaults do not blur with mutating view-state/runtime behavior.
- Keep custom-property read/write flows on their own leaf because they are the
  only utility slice with structured metadata payload ownership.
- Preserve current object-mode assumptions and RPC payload shapes across every
  child leaf.

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-159-03-04-01](./TASK-159-03-04-01_Addon_Scene_Creation_Helper_Split.md) | Separate light/camera/empty creation helpers into one focused addon utility leaf |
| 2 | [TASK-159-03-04-02](./TASK-159-03-04-02_Addon_Scene_Mode_And_Visibility_Utility_Split.md) | Separate mode-switch, rename, visibility, and isolation helpers into one focused addon utility leaf |
| 3 | [TASK-159-03-04-03](./TASK-159-03-04-03_Addon_Scene_Custom_Property_Utility_Split.md) | Separate custom-property read/write helpers into one focused addon utility leaf |

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
- `tests/e2e/tools/scene/test_hide_object.py`
- `tests/e2e/tools/scene/test_show_all_objects.py`
- `tests/e2e/tools/scene/test_rename_object.py`
- `tests/e2e/tools/scene/test_isolate_object.py`
- `tests/e2e/tools/scene/test_scene_utility_workflow.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_mode.py tests/unit/tools/scene/test_scene_construction.py tests/unit/tools/scene/test_hide_object.py tests/unit/tools/scene/test_show_all_objects.py tests/unit/tools/scene/test_rename_object.py tests/unit/tools/scene/test_isolate_object.py tests/unit/tools/scene/test_scene_mcp_tools_batch.py tests/unit/tools/test_handler_rpc_alignment.py tests/unit/adapters/mcp/test_structured_contract_delivery.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/tools/scene/test_hide_object.py tests/e2e/tools/scene/test_show_all_objects.py tests/e2e/tools/scene/test_rename_object.py tests/e2e/tools/scene/test_isolate_object.py tests/e2e/tools/scene/test_scene_get_viewport_camera.py tests/e2e/tools/scene/test_scene_view_diagnostics.py tests/e2e/tools/scene/test_scene_utility_workflow.py -q`

## Docs To Update

- inherit parent docs closeout unless addon utility ownership wording changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- this branch is decomposed into focused creation, mode/visibility, and
  custom-property leaves instead of one broad utility pass
- RPC method names, payloads, and mode-validation errors remain stable
- structured custom-property delivery keeps the same contract under the
  dedicated unit/RPC/structured-contract proof lane of `TASK-159-03-04-03`
- focused unit/e2e lanes still prove the same creation and mode/visibility
  behavior

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
- execute this branch through the focused leaves below instead of landing all
  addon utilities in one broad pass
