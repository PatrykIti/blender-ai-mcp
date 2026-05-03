# TASK-159-02-05-01: Scene Cleanup, Mode, And Active Object Utility Slices

**Parent:** [TASK-159-02-05](./TASK-159-02-05_Scene_Object_Utility_Manage_And_Guided_Dirtying_Slices.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Separate cleanup, duplicate, active-object, and mode wrappers into one focused
scene-utility leaf.

## Repository Touchpoints

- `server/adapters/mcp/areas/scene.py`
- likely helper module such as `server/adapters/mcp/areas/scene_object_utils.py`
- `server/adapters/mcp/session_capabilities.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/test_mcp_area_main_paths.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/e2e/tools/scene/test_scene_clean_scene.py`

## Current Code Anchors

- `scene_list_objects(...)`
- `scene_delete_object(...)`
- `scene_clean_scene(...)`
- `_scene_clean_scene_async(...)`
- `scene_duplicate_object(...)`
- `scene_set_active_object(...)`
- `scene_set_mode(...)`

## Planned Code Shape

```python
from .scene_object_utils import execute_scene_cleanup_and_mode_utility
```

## Runtime / Security Contract Notes

- preserve cleanup canonicalization and guided dirtying side effects
- keep current mode/active-object semantics and request-path behavior unchanged

## Tests To Add/Update

- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/test_mcp_area_main_paths.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/e2e/tools/scene/test_scene_clean_scene.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_mcp_tools_batch.py tests/unit/tools/test_mcp_area_main_paths.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/e2e/tools/scene/test_scene_clean_scene.py -q`

## Docs To Update

- inherit parent docs closeout unless cleanup/mode ownership wording changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- cleanup, duplicate, active-object, and mode wrappers have a focused home
- cleanup canonicalization and guided dirtying behavior remain unchanged

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
