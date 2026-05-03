# TASK-159-03: Addon Scene Handler Modularization And Blender Ownership Boundaries

**Parent:** [TASK-159](./TASK-159_Modularize_Oversized_Guided_Runtime_And_Scene_Owner_Files.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Split `blender_addon/application/handlers/scene.py` into clearer Blender-owned
responsibility slices for:

- scene lifecycle / context / structural reads
- measure_assert
- viewport / camera
- world / render / color management
- creation / visibility / metadata utilities

while preserving the current `SceneHandler` RPC method surface and main-thread
Blender safety model.

## Business Problem

The addon `SceneHandler` is the Blender truth owner for many unrelated
behaviors:

- hierarchy / bbox / origin reads
- scene object lifecycle helpers
- scene creation and mode/context helpers
- viewport capture and diagnostics
- camera utility helpers
- measure/assert semantics
- world/render/color-management configuration
- object metadata / custom-property helpers
- topology inspection helpers

The public server depends on this handler as one stable RPC-backed truth owner,
which is correct. The problem is that future Blender-side work now lands in one
large class with many unrelated edit zones.

That increases the chance that:

- a viewport change accidentally regresses measure/assert logic
- a render/world change becomes harder to review because the file also owns
  object CRUD and bbox helpers
- new Blender truth features land in the wrong place because no smaller owner
  boundary exists

## Repository Touchpoints

- `blender_addon/application/handlers/scene.py`
- likely new sibling modules such as:
  - `scene_inspection_mixin.py`
  - `scene_measure_assert_mixin.py`
  - `scene_viewport_mixin.py`
  - `scene_world_render_mixin.py`
  - `scene_utility_mixin.py`
- `blender_addon/__init__.py` if registration wiring needs import-path updates
- `blender_addon/infrastructure/rpc_server.py`
- `server/application/tool_handlers/scene_handler.py`
- `tests/unit/addon/test_addon_registration.py`
- `tests/unit/tools/scene/test_scene_measure_tools.py`
- `tests/unit/tools/scene/test_scene_assert_tools.py`
- `tests/unit/tools/scene/test_scene_configure_handler.py`
- `tests/unit/tools/scene/test_scene_inspect_mesh_topology.py`
- `tests/unit/tools/scene/test_viewport_control.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/e2e/tools/scene/test_scene_measure_tools.py`
- `tests/e2e/tools/scene/test_scene_assert_tools.py`
- `tests/e2e/tools/scene/test_scene_configure_roundtrip.py`
- `tests/e2e/tools/scene/test_scene_view_diagnostics.py`

## Implementation Notes

- Keep `SceneHandler` as the public addon handler class used by RPC
  registration.
- Prefer mixins or helper modules so the public RPC method names stay stable.
- Preserve Blender main-thread and evaluated-mesh safety patterns.
- Keep Blender-specific logic inside addon modules; do not migrate it into
  server services during this task.
- Preserve current shared helper behavior for bbox, rounding, assertion payload
  shaping, and viewport-state restoration unless a separate bugfix requires
  change.
- Treat world/render and `node_graph_handoff` shaping as contract-sensitive
  internals even if the public class name stays the same.

## Pseudocode

```python
from .scene_inspection_mixin import SceneInspectionMixin
from .scene_measure_assert_mixin import SceneMeasureAssertMixin
from .scene_viewport_mixin import SceneViewportMixin
from .scene_world_render_mixin import SceneWorldRenderMixin

class SceneHandler(
    SceneInspectionMixin,
    SceneMeasureAssertMixin,
    SceneViewportMixin,
    SceneWorldRenderMixin,
):
    pass
```

## Runtime / Security Contract Notes

- Preserve current RPC method names and payload shapes.
- Preserve current safe use of Blender state, evaluated meshes, and temporary
  view/camera mutations.
- Preserve addon registration wiring and current scene-tool handler alignment
  across `blender_addon/__init__.py`, RPC registration, and the server-side
  `SceneToolHandler`.
- Do not move blocking or Blender-context-sensitive work into background
  patterns that violate the addon's current main-thread model.

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-159-03-01](./TASK-159-03-01_Addon_Scene_Inspection_And_Topology_Split.md) | Extract scene lifecycle/context/structural-read helpers together with inspection/topology ownership while preserving Blender-truth reads |
| 2 | [TASK-159-03-02](./TASK-159-03-02_Addon_Scene_Measure_Assert_And_RPC_Parity.md) | Separate measure/assert helpers and keep server-addon RPC contracts aligned |
| 3 | [TASK-159-03-03](./TASK-159-03-03_Addon_Scene_Viewport_World_Render_And_Registration.md) | Extract viewport/camera/world/render/color-management helpers and prove registration plus roundtrip parity stay intact |
| 4 | [TASK-159-03-04](./TASK-159-03-04_Addon_Scene_Creation_Visibility_And_Metadata_Utilities.md) | Separate scene creation, mode-switch, visibility, and custom-property utilities without drifting RPC behavior or object-mode assumptions |

## Tests To Add/Update

- `tests/unit/addon/test_addon_registration.py`
- `tests/unit/tools/scene/test_scene_mode.py`
- `tests/unit/tools/scene/test_scene_get_mode_handler.py`
- `tests/unit/tools/scene/test_scene_measure_tools.py`
- `tests/unit/tools/scene/test_scene_assert_tools.py`
- `tests/unit/tools/scene/test_scene_construction.py`
- `tests/unit/tools/scene/test_scene_configure_handler.py`
- `tests/unit/tools/scene/test_scene_inspect_mesh_topology.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_camera_orbit.py`
- `tests/unit/tools/scene/test_camera_focus.py`
- `tests/unit/tools/scene/test_hide_object.py`
- `tests/unit/tools/scene/test_show_all_objects.py`
- `tests/unit/tools/scene/test_rename_object.py`
- `tests/unit/tools/scene/test_isolate_object.py`
- `tests/unit/tools/scene/test_viewport_control.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/e2e/tools/scene/test_scene_measure_tools.py`
- `tests/e2e/tools/scene/test_scene_assert_tools.py`
- `tests/e2e/tools/scene/test_scene_clean_scene.py`
- `tests/e2e/tools/scene/test_scene_utility_workflow.py`
- `tests/e2e/tools/scene/test_scene_configure_roundtrip.py`
- `tests/e2e/tools/scene/test_camera_orbit.py`
- `tests/e2e/tools/scene/test_camera_focus.py`
- `tests/e2e/tools/scene/test_hide_object.py`
- `tests/e2e/tools/scene/test_show_all_objects.py`
- `tests/e2e/tools/scene/test_rename_object.py`
- `tests/e2e/tools/scene/test_isolate_object.py`
- `tests/e2e/tools/scene/test_scene_view_diagnostics.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/addon/test_addon_registration.py tests/unit/tools/scene/test_scene_mode.py tests/unit/tools/scene/test_scene_get_mode_handler.py tests/unit/tools/scene/test_scene_measure_tools.py tests/unit/tools/scene/test_scene_assert_tools.py tests/unit/tools/scene/test_scene_construction.py tests/unit/tools/scene/test_scene_configure_handler.py tests/unit/tools/scene/test_scene_inspect_mesh_topology.py tests/unit/tools/scene/test_scene_mcp_tools_batch.py tests/unit/tools/scene/test_camera_orbit.py tests/unit/tools/scene/test_camera_focus.py tests/unit/tools/scene/test_hide_object.py tests/unit/tools/scene/test_show_all_objects.py tests/unit/tools/scene/test_rename_object.py tests/unit/tools/scene/test_isolate_object.py tests/unit/tools/scene/test_viewport_control.py tests/unit/tools/test_handler_rpc_alignment.py tests/unit/adapters/mcp/test_structured_contract_delivery.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/tools/scene/test_scene_measure_tools.py tests/e2e/tools/scene/test_scene_assert_tools.py tests/e2e/tools/scene/test_scene_clean_scene.py tests/e2e/tools/scene/test_scene_utility_workflow.py tests/e2e/tools/scene/test_scene_configure_roundtrip.py tests/e2e/tools/scene/test_camera_orbit.py tests/e2e/tools/scene/test_camera_focus.py tests/e2e/tools/scene/test_hide_object.py tests/e2e/tools/scene/test_show_all_objects.py tests/e2e/tools/scene/test_rename_object.py tests/e2e/tools/scene/test_isolate_object.py tests/e2e/tools/scene/test_scene_view_diagnostics.py -q`

## Docs To Update

- `_docs/_ADDON/README.md` if the internal owner map is documented explicitly
- `_docs/_TASKS/README.md` only when the task status changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- addon `SceneHandler` no longer directly owns all lifecycle/context,
  inspection, measure/assert, viewport/camera, world/render/color-management,
  and creation/utility logic in one file
- the public RPC-backed addon surface remains stable
- addon registration wiring and server-side scene handler alignment remain
  stable
- Blender truth behavior and viewport behavior keep their current safety model
- targeted unit and Blender-backed e2e lanes prove no addon-scene regression

## Status / Board Update

- keep promoted tracking on the parent `TASK-159`
- execute this subtask through the leaves below so registration/RPC/world-render
  boundaries can be verified independently
- do not promote this slice independently unless it becomes the only remaining
  open branch in the family
