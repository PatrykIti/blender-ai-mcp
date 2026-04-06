# TASK-144-01-02: Blender View Projection Runtime And Frame Coverage

**Parent:** [TASK-144-01](./TASK-144-01_Projection_View_Space_Contract_And_Runtime_Foundation.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High  
**Depends On:** [TASK-144-01-01](./TASK-144-01-01_View_Query_Selector_And_Projection_Contract.md)

## Objective

Implement the Blender-side runtime helper that resolves the new view query
contract against:

- explicit scene cameras
- the live `USER_PERSPECTIVE`
- the current bounded focus/orbit/standard-view semantics already used by the
  capture stack

and returns deterministic projection plus frame-coverage facts.

## Implementation Direction

- keep projection/frame math in `blender_addon/application/handlers/scene.py`
  so the source of truth remains inside Blender
- transport the result through the existing scene RPC/application layers
- reuse current reversible state helpers and capture-runtime restoration
  semantics where possible
- treat this as a read-only runtime helper; do not require heavy geometry
  libraries for the first shipped version

## Repository Touchpoints

- `server/application/tool_handlers/scene_handler.py`
- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/vision/capture_runtime.py`
- `blender_addon/application/handlers/scene.py`
- `blender_addon/__init__.py`
- `blender_addon/infrastructure/rpc_server.py`
- `tests/unit/tools/scene/test_view_state.py`
- `tests/unit/tools/scene/test_viewport_control.py`
- `tests/unit/tools/scene/test_camera_focus.py`
- `tests/unit/tools/scene/test_camera_orbit.py`
- `tests/e2e/tools/scene/test_scene_get_viewport.py`
- `tests/e2e/tools/scene/test_scene_get_viewport_camera.py`
- `tests/e2e/tools/scene/test_camera_focus.py`
- `tests/e2e/tools/scene/test_camera_orbit.py`

## Acceptance Criteria

- the runtime can resolve projection/frame facts for named-camera and
  `USER_PERSPECTIVE` queries
- the runtime stays consistent with current focus/orbit/isolation/view-restore
  semantics
- frame coverage and off-frame cases are reported deterministically from
  Blender-side state, not guessed from rendered images
- the helper remains read-only and baseline-friendly for v1

## Docs To Update

- `_docs/_ADDON/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TESTS/README.md`

## Tests To Add/Update

- `tests/unit/tools/scene/test_view_state.py`
- `tests/unit/tools/scene/test_viewport_control.py`
- `tests/unit/tools/scene/test_camera_focus.py`
- `tests/unit/tools/scene/test_camera_orbit.py`
- `tests/e2e/tools/scene/test_scene_get_viewport.py`
- `tests/e2e/tools/scene/test_scene_get_viewport_camera.py`
- `tests/e2e/tools/scene/test_camera_focus.py`
- `tests/e2e/tools/scene/test_camera_orbit.py`

## Changelog Impact

- include in the parent TASK-144 changelog entry when shipped

## Status / Board Update

- this leaf owns the Blender/runtime implementation side of the TASK-144
  projection seam
- `_docs/_TASKS/README.md` remains unchanged in this planning pass per operator
  constraint
