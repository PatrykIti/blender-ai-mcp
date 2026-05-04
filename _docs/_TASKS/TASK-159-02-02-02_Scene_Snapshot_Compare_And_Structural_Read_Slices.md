# TASK-159-02-02-02: Scene Snapshot, Compare, And Structural Read Slices

**Parent:** [TASK-159-02-02](./TASK-159-02-02_Scene_Context_Inspect_Snapshot_And_Structural_Read_Slices.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Separate snapshot/compare and structural-read helpers from the rest of the
read-heavy branch so hierarchy, bbox, and origin reads land in one focused
structural-read leaf.

## Repository Touchpoints

- `server/adapters/mcp/areas/scene.py`
- likely helper module such as `server/adapters/mcp/areas/scene_state_reads.py`
- `server/adapters/mcp/contracts/scene.py`
- `tests/unit/tools/scene/test_scene_state_assistants.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/e2e/tools/scene/test_snapshot_tools.py`

## Current Code Anchors

- `scene_snapshot_state(...)`
- `scene_compare_snapshot(...)`
- `scene_get_hierarchy(...)`
- `scene_get_bounding_box(...)`
- `scene_get_origin_info(...)`

## Planned Code Shape

```python
from .scene_state_reads import (
    execute_scene_snapshot_state,
    execute_scene_compare_snapshot,
    execute_scene_structural_read,
)
```

## Runtime / Security Contract Notes

- preserve snapshot payloads, structural-read contracts, and assistant-summary
  behavior
- keep current read-only posture for hierarchy/bbox/origin flows

## Tests To Add/Update

- `tests/unit/tools/scene/test_scene_state_assistants.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/e2e/tools/scene/test_snapshot_tools.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_state_assistants.py tests/unit/tools/scene/test_scene_contracts.py tests/unit/tools/test_handler_rpc_alignment.py tests/unit/adapters/mcp/test_structured_contract_delivery.py tests/e2e/tools/scene/test_snapshot_tools.py -q`

## Docs To Update

- inherit parent docs closeout unless structural-read ownership wording changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- snapshot/compare plus structural-read helpers have a focused home outside the
  monolith
- current snapshot, hierarchy, bbox, and origin contracts remain unchanged

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
