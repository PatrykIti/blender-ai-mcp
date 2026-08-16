# 123 - 2025-12-21: Introspection API fixes (Blender 5.0+)

**Status**: ✅ Completed  
**Type**: Bugfix / API Alignment  
**Task**: TASK-070..074 follow-up

---

## Summary

Fixed Blender 5.0+ introspection regressions: loop normals no longer call removed APIs, curve handle data uses 5.0 fields, and armature inspection is now exposed via MCP.

---

## Changes

- `mesh_inspect` normals no longer call `mesh.calc_normals()` (removed in 5.0+); relies on `mesh.corner_normals`.
- `curve_get_data` uses Bezier handle left/right types and derives a handle type (no deprecated `handle_type`).
- Exposed `armature_get_data` MCP tool and ensured area registration.

---

## Files Modified (high level)

- Blender Addon:
  - `blender_addon/application/handlers/mesh.py`
  - `blender_addon/application/handlers/curve.py`
- MCP Server:
  - `server/adapters/mcp/areas/armature.py`
  - `server/adapters/mcp/areas/__init__.py`

---

## Validation

- `pytest tests/unit/tools/curve/test_get_data.py tests/unit/tools/mesh/test_get_loop_normals.py tests/unit/tools/sculpt/test_sculpt_tools.py -q`
- `pytest tests/e2e/tools/mesh/test_mesh_edge_weights.py::test_workflow_mark_sharp_with_auto_smooth tests/e2e/tools/sculpt/test_sculpt_tools.py::TestSculptAutoE2E::test_sculpt_auto_smooth_basic -q`
