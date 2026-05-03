# TASK-159-03-02: Addon Scene Measure Assert And RPC Parity

**Parent:** [TASK-159-03](./TASK-159-03_Addon_Scene_Handler_Modularization_And_Blender_Ownership_Boundaries.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Separate addon measure/assert helpers from `SceneHandler` while preserving
server-addon RPC parity and deterministic truth semantics.

## Repository Touchpoints

- `blender_addon/application/handlers/scene.py`
- likely new helper module such as `blender_addon/application/handlers/scene_measure_assert_mixin.py`
- `server/application/tool_handlers/scene_handler.py`
- `tests/unit/tools/scene/test_scene_measure_tools.py`
- `tests/unit/tools/scene/test_scene_assert_tools.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/e2e/tools/scene/test_scene_measure_tools.py`
- `tests/e2e/tools/scene/test_scene_assert_tools.py`

## Current Code Anchors

- `SceneHandler.measure_distance(...)`
- `SceneHandler.measure_gap(...)`
- `SceneHandler.measure_overlap(...)`
- `SceneHandler.assert_contact(...)`
- `SceneHandler.assert_dimensions(...)`
- `SceneHandler.assert_containment(...)`
- `SceneHandler.assert_symmetry(...)`
- `SceneHandler.assert_proportion(...)`

## Planned Code Shape

```python
class SceneHandler(SceneMeasureAssertMixin, ...):
    pass
```

## Runtime / Security Contract Notes

- keep measurement/assertion deterministic and Blender-backed
- preserve existing RPC method names, result envelopes, and rounding semantics
- keep server-side handler expectations aligned with addon result shapes

## Tests To Add/Update

- `tests/unit/tools/scene/test_scene_measure_tools.py`
- `tests/unit/tools/scene/test_scene_assert_tools.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/e2e/tools/scene/test_scene_measure_tools.py`
- `tests/e2e/tools/scene/test_scene_assert_tools.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_measure_tools.py tests/unit/tools/scene/test_scene_assert_tools.py tests/unit/tools/test_handler_rpc_alignment.py tests/e2e/tools/scene/test_scene_measure_tools.py tests/e2e/tools/scene/test_scene_assert_tools.py -q`

## Docs To Update

- inherit parent docs closeout unless addon measure/assert ownership wording
  changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- measure/assert helpers no longer share one edit zone with unrelated scene code
- RPC parity remains stable across unit and Blender-backed tests
- truth-layer payloads and error strings stay unchanged

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
