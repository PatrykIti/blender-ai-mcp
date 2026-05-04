# TASK-159-02-04: Scene Measure Assert And Guided Side Effects

**Parent:** [TASK-159-02](./TASK-159-02_Scene_MCP_Area_Modularization_And_Surface_Slices.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Extract measure/assert helper clusters from `scene.py` while preserving current
guided stale-state and spatial-check side effects.

## Repository Touchpoints

- `server/adapters/mcp/areas/scene.py`
- likely new helper module such as `server/adapters/mcp/areas/scene_measure_assert.py`
- `server/adapters/mcp/session_capabilities.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_macro_place_supported_pair_mcp.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/e2e/tools/scene/test_scene_measure_tools.py`
- `tests/e2e/tools/scene/test_scene_assert_tools.py`

## Current Code Anchors

- `scene_measure_distance(...)`
- `scene_measure_dimensions(...)`
- `scene_measure_gap(...)`
- `scene_measure_alignment(...)`
- `scene_measure_overlap(...)`
- `scene_assert_contact(...)`
- `scene_assert_dimensions(...)`
- `scene_assert_containment(...)`
- `scene_assert_symmetry(...)`
- `scene_assert_proportion(...)`

## Planned Code Shape

```python
from .scene_measure_assert import execute_scene_measure_gap, execute_scene_assert_contact
```

## Runtime / Security Contract Notes

- keep measurement/assertion as the deterministic truth layer
- preserve current guided stale-state, gate-refresh, and check-completion
  side effects attached to the wrappers
- keep server/addon RPC alignment unchanged for every extracted helper

## Tests To Add/Update

- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_macro_place_supported_pair_mcp.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/e2e/tools/scene/test_scene_measure_tools.py`
- `tests/e2e/tools/scene/test_scene_assert_tools.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_mcp_tools_batch.py tests/unit/tools/scene/test_macro_place_supported_pair_mcp.py tests/unit/tools/test_handler_rpc_alignment.py tests/e2e/tools/scene/test_scene_measure_tools.py tests/e2e/tools/scene/test_scene_assert_tools.py -q`

## Docs To Update

- inherit parent docs closeout unless measurement/assertion ownership wording
  changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- measure/assert helpers are no longer mixed inline with unrelated scene
  concerns
- deterministic truth-layer behavior remains stable
- guided side effects and RPC alignment stay covered by focused regression lanes

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
