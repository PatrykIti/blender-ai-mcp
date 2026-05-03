# TASK-159-02-02-01: Scene Context And Selection Read Slices

**Parent:** [TASK-159-02-02](./TASK-159-02-02_Scene_Context_Inspect_Snapshot_And_Structural_Read_Slices.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Separate `scene_context(...)` and its mode/selection helpers from the rest of
the read-heavy branch so context reads land in one focused adapter-state leaf.

## Repository Touchpoints

- `server/adapters/mcp/areas/scene.py`
- likely helper module such as `server/adapters/mcp/areas/scene_state_reads.py`
- `tests/unit/tools/scene/test_scene_context_mega.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`

## Current Code Anchors

- `scene_context(...)`
- `_scene_get_mode(...)`
- `_scene_list_selection(...)`

## Planned Code Shape

```python
from .scene_state_reads import execute_scene_context
```

## Runtime / Security Contract Notes

- preserve read-only semantics and the current mode/selection payload contract
- keep current request validation and structured delivery behavior unchanged

## Tests To Add/Update

- `tests/unit/tools/scene/test_scene_context_mega.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_context_mega.py tests/unit/tools/scene/test_scene_mcp_tools_batch.py tests/unit/adapters/mcp/test_structured_contract_delivery.py -q`

## Docs To Update

- inherit parent docs closeout unless context-read ownership wording changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- `scene_context(...)` plus mode/selection reads have a focused home outside
  the monolith
- current mode/selection payloads and read-only behavior remain unchanged

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
