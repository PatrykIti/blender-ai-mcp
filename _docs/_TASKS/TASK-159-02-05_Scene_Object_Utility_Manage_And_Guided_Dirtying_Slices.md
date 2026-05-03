# TASK-159-02-05: Scene Object Utility Manage And Guided Dirtying Slices

**Parent:** [TASK-159-02](./TASK-159-02_Scene_MCP_Area_Modularization_And_Surface_Slices.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Split the standalone object-utility branch from `scene.py` into focused
cleanup/mode, visibility/camera, and custom-property leaves while preserving
the current public utility surface, cleanup canonicalization, and guided
dirtying semantics.

This subtask owns the non-mega utility wrappers that currently sit between the
grouped scene tools and the spatial-support slices:

- object listing and cleanup
- duplicate / active-object / mode utility
- rename / visibility / isolation utility
- camera orbit/focus utility
- custom-property read/write utility

## Repository Touchpoints

- `server/adapters/mcp/areas/scene.py`
- likely new helper module such as `server/adapters/mcp/areas/scene_object_utils.py`
- `server/adapters/mcp/session_capabilities.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/test_mcp_area_main_paths.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/e2e/tools/scene/test_scene_clean_scene.py`
- `tests/e2e/tools/scene/test_scene_utility_workflow.py`

## Current Code Anchors

- `scene_list_objects(...)`
- `scene_delete_object(...)`
- `scene_clean_scene(...)`
- `_scene_clean_scene_async(...)`
- `scene_duplicate_object(...)`
- `scene_set_active_object(...)`
- `scene_set_mode(...)`
- `scene_rename_object(...)`
- `scene_hide_object(...)`
- `scene_show_all_objects(...)`
- `scene_isolate_object(...)`
- `scene_camera_orbit(...)`
- `scene_camera_focus(...)`
- `scene_get_custom_properties(...)`
- `scene_set_custom_property(...)`

## Pseudocode

```python
cleanup_mode_leaf = [
    "scene_list_objects",
    "scene_delete_object",
    "scene_clean_scene",
    "scene_duplicate_object",
    "scene_set_active_object",
    "scene_set_mode",
]
visibility_camera_leaf = [
    "scene_rename_object",
    "scene_hide_object",
    "scene_show_all_objects",
    "scene_isolate_object",
    "scene_camera_orbit",
    "scene_camera_focus",
]
custom_property_leaf = [
    "scene_get_custom_properties",
    "scene_set_custom_property",
]

for wrapper in cleanup_mode_leaf + visibility_camera_leaf + custom_property_leaf:
    keep_public_scene_wrapper_name(wrapper)
    delegate_to_focused_object_utility_leaf(wrapper)
    preserve_guided_dirtying_side_effects(wrapper)
```

## Implementation Notes

- Keep cleanup/mode helpers separate from visibility/camera helpers so
  state-reset semantics do not blur with framing/navigation utilities.
- Keep custom-property read/write flows on their own focused leaf; they are the
  only object-utility wrappers with structured metadata payload ownership.
- Preserve guided dirtying, registry-reset, and visibility-refresh behavior
  across every child leaf instead of centralizing new bypass helpers here.

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-159-02-05-01](./TASK-159-02-05-01_Scene_Cleanup_Mode_And_Active_Object_Utility_Slices.md) | Separate object listing/deletion, cleanup, duplicate, active-object, and mode wrappers into one focused utility leaf |
| 2 | [TASK-159-02-05-02](./TASK-159-02-05-02_Scene_Visibility_Isolation_And_Camera_Utility_Slices.md) | Separate rename, visibility, isolation, and camera helpers into one focused utility leaf |
| 3 | [TASK-159-02-05-03](./TASK-159-02-05-03_Scene_Custom_Property_Utility_And_Dirtying_Glue.md) | Separate custom-property read/write wrappers and their structured delivery/runtime glue into one focused leaf |

## Runtime / Security Contract Notes

- keep `scene_clean_scene` canonicalization for
  `keep_lights_and_cameras` vs legacy split flags unchanged
- preserve current guided dirtying, registry-reset, and visibility-refresh
  side effects for cleanup and object-mutating utility wrappers
- preserve current object-mode and camera-utility semantics; do not silently
  move these wrappers onto a bypass path that skips the request-path bridge
- keep structured custom-property delivery and read/write payload shapes stable

## Tests To Add/Update

- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/test_mcp_area_main_paths.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/e2e/tools/scene/test_scene_clean_scene.py`
- `tests/e2e/tools/scene/test_scene_utility_workflow.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_mcp_tools_batch.py tests/unit/tools/test_mcp_area_main_paths.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_provider_inventory.py tests/unit/adapters/mcp/test_structured_contract_delivery.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/tools/scene/test_scene_clean_scene.py tests/e2e/tools/scene/test_scene_utility_workflow.py -q`

## Docs To Update

- inherit parent docs closeout unless utility-surface ownership wording changes
  in `_docs/_MCP_SERVER/README.md` or `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- this branch is decomposed into focused cleanup/mode, visibility/camera, and
  custom-property leaves instead of one oversized utility pass
- cleanup canonicalization and guided dirtying semantics remain stable
- public utility names and structured custom-property delivery stay unchanged
- focused unit/integration/e2e lanes still prove the same cleanup and utility
  behavior

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
- execute this branch through the focused leaves below instead of landing all
  object utilities in one oversized pass
