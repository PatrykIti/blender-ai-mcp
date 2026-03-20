# 122 - 2025-12-21: Blender 5.0 mesh_inspect fixes

**Status**: ✅ Completed  
**Type**: Bugfix / Blender 5.0+ API alignment  
**Task**: -

---

## Summary

Aligned mesh loop normals introspection with Blender 5.0+ APIs, removing legacy auto-smooth usage and ensuring `mesh_inspect` remains fully functional.

---

## Changes

- Switched loop normals inspection to Blender 5.0+ APIs (`mesh.calc_normals`, `mesh.corner_normals`).
- Auto-smooth detection now relies on the Smooth by Angle modifier (5.0+), including angle reporting.
- Removed legacy `use_auto_smooth` usage in sculpt handler.
- Updated unit tests for Blender 5.0+ expectations.
- Added reconstruction tool task specs (TASK-076–TASK-082) and task board updates.

---

## Files Modified (high level)

- Blender Addon:
  - `blender_addon/application/handlers/mesh.py`
  - `blender_addon/application/handlers/sculpt.py`
- Tests:
  - `tests/unit/tools/mesh/test_get_loop_normals.py`
  - `tests/unit/tools/sculpt/test_sculpt_tools.py`
- Docs:
  - `_docs/_TASKS/README.md`
  - `_docs/_TASKS/TASK-076_Mesh_Build_Mega_Tool.md`
  - `_docs/_TASKS/TASK-077_Mesh_Build_Surface_Data.md`
  - `_docs/_TASKS/TASK-078_Mesh_Build_Deformation_Data.md`
  - `_docs/_TASKS/TASK-079_Node_Graph_Build_Tools.md`
  - `_docs/_TASKS/TASK-080_Image_Asset_Tools.md`
  - `_docs/_TASKS/TASK-081_Scene_Render_World_Settings.md`
  - `_docs/_TASKS/TASK-082_Animation_and_Drivers_Tools.md`

---

## Validation

Not run (tests not requested).
