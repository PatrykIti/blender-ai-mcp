# 112 - 2025-12-15: Router preserves Edit Mode selection (auto_select_all fix)

**Status**: ✅ Completed  
**Type**: Bug Fix / Safety / UX  
**Task**: [TASK-063](../_TASKS/TASK-063_Router_Auto_Selection_Preservation.md)

---

## Summary

Fixed a Router issue where selection-based mesh tools could unexpectedly run on the whole mesh due to stale/incorrect selection detection, causing `mesh_select(action="all")` to be injected ahead of operations like `mesh_extrude_region` and `mesh_bevel`.

---

## Changes

- Scene context:
  - Normalize Blender edit mode strings (`EDIT_MESH` → `EDIT`) for consistent mode handling.
  - Map topology keys from addon output (`vertex_count`/`edge_count`/`face_count`/`triangle_count`) into Router `TopologyInfo`.
  - Refresh edit-mode selection counts even when returning cached context (selection treated as “hot” data).
- Docs:
  - Clarified Router `auto_selection` behavior (only selects-all when edit selection is empty).
- Tests:
  - Added regression coverage for cached edit-mode selection refresh.

---

## Files Modified (high level)

- Router runtime:
  - `server/router/application/analyzers/scene_context_analyzer.py`
  - `server/router/domain/entities/scene_context.py`
- Tests:
  - `tests/unit/router/application/test_scene_context_analyzer.py`
- Docs:
  - `_docs/_ROUTER/README.md`
  - `_docs/TOOLS/MEGA_TOOLS_ARCHITECTURE.md`

---

## Validation

```bash
poetry run pytest tests/unit/router/application/test_scene_context_analyzer.py -q
```

