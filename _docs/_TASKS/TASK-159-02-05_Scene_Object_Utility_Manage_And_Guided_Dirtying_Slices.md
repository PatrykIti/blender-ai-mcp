# TASK-159-02-05: Scene Object Utility Manage And Guided Dirtying Slices

**Parent:** [TASK-159-02](./TASK-159-02_Scene_MCP_Area_Modularization_And_Surface_Slices.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Extract standalone object-utility wrappers from `scene.py` while preserving the
current public utility surface, cleanup canonicalization, and guided dirtying
semantics.

This leaf owns the non-mega utility wrappers that currently sit between the
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

## Planned Code Shape

```python
from .scene_object_utils import (
    execute_scene_clean_scene,
    execute_scene_object_utility,
    execute_scene_camera_utility,
    execute_scene_custom_property_utility,
)
```

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

- object-utility wrappers no longer sit inline between grouped scene tools and
  the spatial-support / measure / view slices
- cleanup canonicalization and guided dirtying semantics remain stable
- public utility names and structured custom-property delivery stay unchanged
- focused unit/integration/e2e lanes still prove the same cleanup and utility
  behavior

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
