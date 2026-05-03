# TASK-159-03: Addon Scene Handler Modularization And Blender Ownership Boundaries

**Parent:** [TASK-159](./TASK-159_Modularize_Oversized_Guided_Runtime_And_Scene_Owner_Files.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Split `blender_addon/application/handlers/scene.py` into clearer Blender-owned
responsibility slices for:

- inspection
- measure_assert
- viewport
- world/render

while preserving the current `SceneHandler` RPC method surface and main-thread
Blender safety model.

## Business Problem

The addon `SceneHandler` is the Blender truth owner for many unrelated
behaviors:

- hierarchy / bbox / origin reads
- scene object lifecycle helpers
- viewport capture and diagnostics
- measure/assert semantics
- world/render configuration
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
| 1 | [TASK-159-03-01](./TASK-159-03-01_Addon_Scene_Inspection_And_Topology_Split.md) | Extract inspection/topology helpers while preserving Blender-truth reads and object lifecycle helpers |
| 2 | [TASK-159-03-02](./TASK-159-03-02_Addon_Scene_Measure_Assert_And_RPC_Parity.md) | Separate measure/assert helpers and keep server-addon RPC contracts aligned |
| 3 | [TASK-159-03-03](./TASK-159-03-03_Addon_Scene_Viewport_World_Render_And_Registration.md) | Extract viewport/world/render helpers and prove registration plus roundtrip parity stay intact |

## Tests To Add/Update

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

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/addon/test_addon_registration.py tests/unit/tools/scene/test_scene_measure_tools.py tests/unit/tools/scene/test_scene_assert_tools.py tests/unit/tools/scene/test_scene_configure_handler.py tests/unit/tools/scene/test_scene_inspect_mesh_topology.py tests/unit/tools/scene/test_viewport_control.py tests/unit/tools/test_handler_rpc_alignment.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/tools/scene/test_scene_measure_tools.py tests/e2e/tools/scene/test_scene_assert_tools.py tests/e2e/tools/scene/test_scene_configure_roundtrip.py tests/e2e/tools/scene/test_scene_view_diagnostics.py -q`

## Docs To Update

- `_docs/_ADDON/README.md` if the internal owner map is documented explicitly
- `_docs/_TASKS/README.md` only when the task status changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- addon `SceneHandler` no longer directly owns all inspection, measure/assert,
  viewport, and world/render logic in one file
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
