# TASK-144-01: Projection / View-Space Contract And Runtime Foundation

**Parent:** [TASK-144](./TASK-144_Camera_Aware_View_Graph_And_Visibility_Diagnostics.md)
**Status:** ✅ Done
**Priority:** 🔴 High
**Depends On:** [TASK-121-03-03](./TASK-121-03-03_Camera_Faithful_Viewport_Capture_Semantics.md), [TASK-121-03-04](./TASK-121-03-04_User_View_Manipulation_For_Viewport_Capture.md), [TASK-121-03-05](./TASK-121-03-05_Render_Visibility_Consistency_For_Viewport_Capture.md)

**Completion Summary:** Completed on 2026-04-07. Landed the typed
view-space foundation for TASK-144: the repo now has one explicit view query
contract and one Blender-backed runtime seam for projected extent, frame
coverage, and view-source provenance across named cameras and bounded
`USER_PERSPECTIVE` flows.

## Objective

Create one explicit typed view-space foundation that can answer:

- which view source is being queried
- whether that source is a named camera or the live `USER_PERSPECTIVE`
- where a requested object/scope projects into frame space
- how much of that target is currently on-screen

without collapsing view-space into truth-space or asking the guided loop to
infer framing state from image pixels alone.

## Current Runtime Baseline

The required building blocks already exist:

- `scene_get_viewport(...)` already distinguishes named-camera capture from
  `USER_PERSPECTIVE`
- `blender_addon/application/handlers/scene.py` already exposes
  `get_view_state(...)`, `restore_view_state(...)`, and `set_standard_view(...)`
- `server/adapters/mcp/vision/capture_runtime.py` already snapshots and
  restores visibility plus viewport state around deterministic capture presets

What is still missing is a typed read-only contract for view-space facts
themselves.

## Implementation Direction

- keep view selection and projection truth anchored in the existing Blender
  camera/viewport runtime, not in the router and not in a vision sidecar
- land the reusable projection seam before visibility verdicts so later
  reporting/adoption work consumes one shared contract
- keep heavy external geometry libraries out of the v1 baseline
- preserve the current `scene_get_viewport(...)` semantics instead of creating
  a second competing view model

## Repository Touchpoints

- `server/domain/tools/scene.py`
- `server/application/tool_handlers/scene_handler.py`
- `server/adapters/mcp/contracts/scene.py`
- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/vision/capture_runtime.py`
- `blender_addon/application/handlers/scene.py`
- `blender_addon/__init__.py`
- `blender_addon/infrastructure/rpc_server.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_view_state.py`
- `tests/unit/tools/scene/test_viewport_control.py`
- `tests/e2e/tools/scene/test_scene_get_viewport.py`
- `tests/e2e/tools/scene/test_scene_get_viewport_camera.py`

## Acceptance Criteria

- the repo has one typed view-space query/result seam for named-camera and
  `USER_PERSPECTIVE` paths
- that seam can report projected center, coarse 2D extent, and frame-coverage
  facts for a requested object/scope
- the implementation reuses the current camera/view-state stack instead of
  introducing a parallel view model
- the v1 baseline does not require heavy new geometry dependencies

## Docs To Update

- `_docs/LLM_GUIDE_V2.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_ADDON/README.md`

## Tests To Add/Update

- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_view_state.py`
- `tests/unit/tools/scene/test_viewport_control.py`
- `tests/e2e/tools/scene/test_scene_get_viewport.py`
- `tests/e2e/tools/scene/test_scene_get_viewport_camera.py`

## Changelog Impact

- include in the parent TASK-144 changelog entry when shipped

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-144-01-01](./TASK-144-01-01_View_Query_Selector_And_Projection_Contract.md) | Define the typed request/response seam for selecting one view source and returning compact projection/frame facts |
| 2 | [TASK-144-01-02](./TASK-144-01-02_Blender_View_Projection_Runtime_And_Frame_Coverage.md) | Implement the Blender-side projection/frame-coverage helper over the existing viewport/camera runtime |

## Status / Board Update

- closed on 2026-04-07 as part of the TASK-144 implementation wave
- the board is updated through the completed parent task
