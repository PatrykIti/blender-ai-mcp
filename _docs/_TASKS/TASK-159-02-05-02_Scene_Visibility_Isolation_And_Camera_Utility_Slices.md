# TASK-159-02-05-02: Scene Visibility, Isolation, And Camera Utility Slices

**Parent:** [TASK-159-02-05](./TASK-159-02-05_Scene_Object_Utility_Manage_And_Guided_Dirtying_Slices.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Separate rename, visibility, isolation, and camera wrappers into one focused
scene-utility leaf.

## Repository Touchpoints

- `server/adapters/mcp/areas/scene.py`
- likely helper module such as `server/adapters/mcp/areas/scene_object_utils.py`
- `server/adapters/mcp/session_capabilities.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_camera_orbit.py`
- `tests/unit/tools/scene/test_camera_focus.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/e2e/tools/scene/test_camera_orbit.py`
- `tests/e2e/tools/scene/test_camera_focus.py`
- `tests/e2e/tools/scene/test_scene_utility_workflow.py`

## Current Code Anchors

- `scene_rename_object(...)`
- `scene_hide_object(...)`
- `scene_show_all_objects(...)`
- `scene_isolate_object(...)`
- `scene_camera_orbit(...)`
- `scene_camera_focus(...)`

## Planned Code Shape

```python
from .scene_object_utils import execute_scene_visibility_and_camera_utility
```

## Runtime / Security Contract Notes

- preserve current visibility/isolation semantics and camera utility behavior
- keep guided dirtying and visibility-refresh behavior unchanged for mutating wrappers

## Tests To Add/Update

- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_camera_orbit.py`
- `tests/unit/tools/scene/test_camera_focus.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/e2e/tools/scene/test_camera_orbit.py`
- `tests/e2e/tools/scene/test_camera_focus.py`
- `tests/e2e/tools/scene/test_scene_utility_workflow.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_mcp_tools_batch.py tests/unit/tools/scene/test_camera_orbit.py tests/unit/tools/scene/test_camera_focus.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/e2e/tools/scene/test_camera_orbit.py tests/e2e/tools/scene/test_camera_focus.py tests/e2e/tools/scene/test_scene_utility_workflow.py -q`

## Docs To Update

- inherit parent docs closeout unless visibility/camera ownership wording changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- visibility, isolation, rename, and camera wrappers have a focused home
- current visibility/camera behavior and guided dirtying side effects remain unchanged

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
