# Example E2E Test Results

**Date:** 2025-11-30
**Platform:** macOS (Darwin), Python 3.13.9, Blender 5.0
**Duration:** 12.25 seconds
**Result:** ✅ 142 PASSED

---

## Test Runner Output

```
python3 scripts/run_e2e_tests.py

[22:12:59] ✅ Using Blender: /Applications/Blender.app/Contents/MacOS/Blender
[22:12:59] 🚀 Building addon...
[22:12:59] ✅ Addon built: outputs/blender_ai_mcp.zip (50.1 KB)
[22:12:59] ℹ️ Checking if addon is installed...
[22:13:00] ✅ Addon installed: True
[22:13:00] 🚀 Uninstalling old addon...
[22:13:00] ✅ Addon uninstalled successfully
[22:13:00] ℹ️ Blender restart required after uninstall
[22:13:00] 🚀 Installing addon from outputs/blender_ai_mcp.zip...
[22:13:01] ✅ Addon installed and enabled successfully
[22:13:01] 🚀 Starting Blender with RPC server...
[22:13:01] ℹ️ NOTE: Blender window will open - this is required for RPC server
[22:13:01] ℹ️ Waiting for RPC server on 127.0.0.1:8765...
[22:13:02] ✅ RPC server is ready!
[22:13:02] 🚀 Running E2E tests...
```

---

## Pytest Output

```
============================= test session starts ==============================
platform darwin -- Python 3.13.9, pytest-9.0.1, pluggy-1.6.0
rootdir: /Users/pciechanski/Documents/private/blender-ai-mcp
configfile: pyproject.toml
plugins: anyio-4.11.0
collected 142 items
```

### Baking Tools (7 tests)
```
tests/e2e/tools/baking/test_baking_tools.py::test_bake_normal_self PASSED
tests/e2e/tools/baking/test_baking_tools.py::test_bake_normal_high_to_low PASSED
tests/e2e/tools/baking/test_baking_tools.py::test_bake_normal_no_uv_error PASSED
tests/e2e/tools/baking/test_baking_tools.py::test_bake_ao_default PASSED
tests/e2e/tools/baking/test_baking_tools.py::test_bake_combined_default PASSED
tests/e2e/tools/baking/test_baking_tools.py::test_bake_diffuse_default PASSED
tests/e2e/tools/baking/test_baking_tools.py::test_workflow_game_asset_baking PASSED
```

### Collection Tools (10 tests)
```
tests/e2e/tools/collection/test_collection_tools.py::test_collection_list PASSED
tests/e2e/tools/collection/test_collection_tools.py::test_collection_list_with_objects PASSED
tests/e2e/tools/collection/test_collection_tools.py::test_collection_list_objects PASSED
tests/e2e/tools/collection/test_collection_tools.py::test_collection_list_objects_invalid PASSED
tests/e2e/tools/collection/test_collection_tools.py::test_collection_manage_create PASSED
tests/e2e/tools/collection/test_collection_tools.py::test_collection_manage_create_with_parent PASSED
tests/e2e/tools/collection/test_collection_tools.py::test_collection_manage_rename PASSED
tests/e2e/tools/collection/test_collection_tools.py::test_collection_manage_delete PASSED
tests/e2e/tools/collection/test_collection_tools.py::test_collection_manage_invalid_action PASSED
tests/e2e/tools/collection/test_collection_tools.py::test_collection_manage_create_already_exists PASSED
```

### Export Tools (13 tests)
```
tests/e2e/tools/export/test_export_tools.py::TestExportGlb::test_export_glb_basic PASSED
tests/e2e/tools/export/test_export_tools.py::TestExportGlb::test_export_glb_with_options PASSED
tests/e2e/tools/export/test_export_tools.py::TestExportGlb::test_export_gltf PASSED
tests/e2e/tools/export/test_export_tools.py::TestExportFbx::test_export_fbx_basic PASSED
tests/e2e/tools/export/test_export_tools.py::TestExportFbx::test_export_fbx_with_options PASSED
tests/e2e/tools/export/test_export_tools.py::TestExportFbx::test_export_fbx_smooth_types PASSED
tests/e2e/tools/export/test_export_tools.py::TestExportObj::test_export_obj_basic PASSED
tests/e2e/tools/export/test_export_tools.py::TestExportObj::test_export_obj_with_materials PASSED
tests/e2e/tools/export/test_export_tools.py::TestExportObj::test_export_obj_with_options PASSED
tests/e2e/tools/export/test_export_tools.py::TestExportObj::test_export_obj_triangulated PASSED
tests/e2e/tools/export/test_export_tools.py::TestExportEdgeCases::test_export_creates_nested_directories PASSED
tests/e2e/tools/export/test_export_tools.py::TestExportEdgeCases::test_export_adds_extension_if_missing PASSED
tests/e2e/tools/export/test_export_tools.py::TestExportEdgeCases::test_export_all_formats PASSED
```

### Import Tools (9 tests)
```
tests/e2e/tools/import_tool/test_import_tools.py::TestImportOBJ::test_import_obj_roundtrip PASSED
tests/e2e/tools/import_tool/test_import_tools.py::TestImportOBJ::test_import_obj_with_scale PASSED
tests/e2e/tools/import_tool/test_import_tools.py::TestImportFBX::test_import_fbx_roundtrip PASSED
tests/e2e/tools/import_tool/test_import_tools.py::TestImportGLB::test_import_glb_roundtrip PASSED
tests/e2e/tools/import_tool/test_import_tools.py::TestImportGLB::test_import_gltf_separate PASSED
tests/e2e/tools/import_tool/test_import_tools.py::TestImportImageAsPlane::test_import_image_as_plane PASSED
tests/e2e/tools/import_tool/test_import_tools.py::TestImportErrorHandling::test_import_nonexistent_file PASSED
tests/e2e/tools/import_tool/test_import_tools.py::TestImportErrorHandling::test_import_invalid_format PASSED
tests/e2e/tools/import_tool/test_import_tools.py::TestImportIntegration::test_import_modify_export PASSED
```

### Knife & Cut Tools (9 tests)
```
tests/e2e/tools/knife_cut/test_knife_cut_tools.py::test_knife_project_basic PASSED
tests/e2e/tools/knife_cut/test_knife_cut_tools.py::test_rip_vertex PASSED
tests/e2e/tools/knife_cut/test_knife_cut_tools.py::test_rip_with_fill PASSED
tests/e2e/tools/knife_cut/test_knife_cut_tools.py::test_split_selected_faces PASSED
tests/e2e/tools/knife_cut/test_knife_cut_tools.py::test_split_no_selection_error PASSED
tests/e2e/tools/knife_cut/test_knife_cut_tools.py::test_edge_split_selected_loop PASSED
tests/e2e/tools/knife_cut/test_knife_cut_tools.py::test_edge_split_no_selection_error PASSED
tests/e2e/tools/knife_cut/test_knife_cut_tools.py::test_workflow_split_and_transform PASSED
tests/e2e/tools/knife_cut/test_knife_cut_tools.py::test_workflow_edge_split_for_uv_seam PASSED
```

### Material Tools (14 tests)
```
tests/e2e/tools/material/test_material_tools.py::test_material_list PASSED
tests/e2e/tools/material/test_material_tools.py::test_material_list_exclude_unassigned PASSED
tests/e2e/tools/material/test_material_tools.py::test_material_list_by_object PASSED
tests/e2e/tools/material/test_material_tools.py::test_material_list_by_object_invalid PASSED
tests/e2e/tools/material/test_material_tools.py::test_material_create_basic PASSED
tests/e2e/tools/material/test_material_tools.py::test_material_create_with_params PASSED
tests/e2e/tools/material/test_material_tools.py::test_material_create_with_emission PASSED
tests/e2e/tools/material/test_material_tools.py::test_material_create_transparent PASSED
tests/e2e/tools/material/test_material_tools.py::test_material_assign_to_object PASSED
tests/e2e/tools/material/test_material_tools.py::test_material_assign_invalid_material PASSED
tests/e2e/tools/material/test_material_tools.py::test_material_set_params PASSED
tests/e2e/tools/material/test_material_tools.py::test_material_set_params_invalid_material PASSED
tests/e2e/tools/material/test_material_tools.py::test_material_set_texture_invalid_material PASSED
tests/e2e/tools/material/test_material_tools.py::test_material_set_texture_invalid_path PASSED
```

### Mesh Cleanup Tools (17 tests)
```
tests/e2e/tools/mesh/test_mesh_cleanup.py::test_dissolve_limited_default PASSED
tests/e2e/tools/mesh/test_mesh_cleanup.py::test_dissolve_limited_custom_angle PASSED
tests/e2e/tools/mesh/test_mesh_cleanup.py::test_dissolve_verts PASSED
tests/e2e/tools/mesh/test_mesh_cleanup.py::test_dissolve_invalid_type_raises PASSED
tests/e2e/tools/mesh/test_mesh_cleanup.py::test_tris_to_quads_default PASSED
tests/e2e/tools/mesh/test_mesh_cleanup.py::test_tris_to_quads_custom_thresholds PASSED
tests/e2e/tools/mesh/test_mesh_cleanup.py::test_tris_to_quads_already_quads PASSED
tests/e2e/tools/mesh/test_mesh_cleanup.py::test_normals_make_consistent_outward PASSED
tests/e2e/tools/mesh/test_mesh_cleanup.py::test_normals_make_consistent_inward PASSED
tests/e2e/tools/mesh/test_mesh_cleanup.py::test_normals_on_complex_mesh PASSED
tests/e2e/tools/mesh/test_mesh_cleanup.py::test_decimate_default PASSED
tests/e2e/tools/mesh/test_mesh_cleanup.py::test_decimate_custom_ratio PASSED
tests/e2e/tools/mesh/test_mesh_cleanup.py::test_decimate_with_symmetry PASSED
tests/e2e/tools/mesh/test_mesh_cleanup.py::test_decimate_invalid_axis_raises PASSED
tests/e2e/tools/mesh/test_mesh_cleanup.py::test_workflow_cleanup_imported_mesh PASSED
tests/e2e/tools/mesh/test_mesh_cleanup.py::test_workflow_optimize_high_poly PASSED
tests/e2e/tools/mesh/test_mesh_cleanup.py::test_workflow_retopology_preparation PASSED
```

### Mesh Edge Weights Tools (16 tests)
```
tests/e2e/tools/mesh/test_mesh_edge_weights.py::test_edge_crease_full_sharp PASSED
tests/e2e/tools/mesh/test_mesh_edge_weights.py::test_edge_crease_partial PASSED
tests/e2e/tools/mesh/test_mesh_edge_weights.py::test_edge_crease_remove PASSED
tests/e2e/tools/mesh/test_mesh_edge_weights.py::test_edge_crease_no_selection_raises PASSED
tests/e2e/tools/mesh/test_mesh_edge_weights.py::test_bevel_weight_full PASSED
tests/e2e/tools/mesh/test_mesh_edge_weights.py::test_bevel_weight_partial PASSED
tests/e2e/tools/mesh/test_mesh_edge_weights.py::test_bevel_weight_remove PASSED
tests/e2e/tools/mesh/test_mesh_edge_weights.py::test_bevel_weight_no_selection_raises PASSED
tests/e2e/tools/mesh/test_mesh_edge_weights.py::test_mark_sharp PASSED
tests/e2e/tools/mesh/test_mesh_edge_weights.py::test_clear_sharp PASSED
tests/e2e/tools/mesh/test_mesh_edge_weights.py::test_mark_sharp_no_selection_raises PASSED
tests/e2e/tools/mesh/test_mesh_edge_weights.py::test_mark_sharp_invalid_action_raises PASSED
tests/e2e/tools/mesh/test_mesh_edge_weights.py::test_workflow_crease_with_subsurf PASSED
tests/e2e/tools/mesh/test_mesh_edge_weights.py::test_workflow_bevel_weight_with_bevel_modifier PASSED
tests/e2e/tools/mesh/test_mesh_edge_weights.py::test_workflow_mark_sharp_with_auto_smooth PASSED
```

### Scene Tools (7 tests)
```
tests/e2e/tools/scene/test_scene_inspect_material_slots.py::test_inspect_material_slots_basic PASSED
tests/e2e/tools/scene/test_scene_inspect_material_slots.py::test_inspect_material_slots_exclude_empty PASSED
tests/e2e/tools/scene/test_scene_inspect_material_slots.py::test_inspect_material_slots_with_filter PASSED
tests/e2e/tools/scene/test_scene_inspect_material_slots.py::test_inspect_material_slots_warnings PASSED
tests/e2e/tools/scene/test_snapshot_tools.py::test_snapshot_state PASSED
tests/e2e/tools/scene/test_snapshot_tools.py::test_snapshot_state_with_options PASSED
tests/e2e/tools/scene/test_snapshot_tools.py::test_snapshot_hash_consistency PASSED
```

### Sculpt Tools (13 tests)
```
tests/e2e/tools/sculpt/test_sculpt_tools.py::TestSculptAutoE2E::test_sculpt_auto_smooth_basic PASSED
tests/e2e/tools/sculpt/test_sculpt_tools.py::TestSculptAutoE2E::test_sculpt_auto_inflate PASSED
tests/e2e/tools/sculpt/test_sculpt_tools.py::TestSculptAutoE2E::test_sculpt_auto_flatten PASSED
tests/e2e/tools/sculpt/test_sculpt_tools.py::TestSculptAutoE2E::test_sculpt_auto_sharpen PASSED
tests/e2e/tools/sculpt/test_sculpt_tools.py::TestSculptAutoE2E::test_sculpt_auto_with_symmetry PASSED
tests/e2e/tools/sculpt/test_sculpt_tools.py::TestSculptAutoE2E::test_sculpt_auto_multiple_iterations PASSED
tests/e2e/tools/sculpt/test_sculpt_tools.py::TestSculptBrushSmoothE2E::test_brush_smooth_setup PASSED
tests/e2e/tools/sculpt/test_sculpt_tools.py::TestSculptBrushSmoothE2E::test_brush_smooth_with_location PASSED
tests/e2e/tools/sculpt/test_sculpt_tools.py::TestSculptBrushGrabE2E::test_brush_grab_setup PASSED
tests/e2e/tools/sculpt/test_sculpt_tools.py::TestSculptBrushGrabE2E::test_brush_grab_with_locations PASSED
tests/e2e/tools/sculpt/test_sculpt_tools.py::TestSculptBrushCreaseE2E::test_brush_crease_setup PASSED
tests/e2e/tools/sculpt/test_sculpt_tools.py::TestSculptBrushCreaseE2E::test_brush_crease_with_location PASSED
tests/e2e/tools/sculpt/test_sculpt_tools.py::TestSculptErrorHandlingE2E::test_sculpt_auto_invalid_object PASSED
```

### System Tools (12 tests)
```
tests/e2e/tools/system/test_system_tools.py::TestSystemSetMode::test_set_mode_object PASSED
tests/e2e/tools/system/test_system_tools.py::TestSystemSetMode::test_set_mode_edit PASSED
tests/e2e/tools/system/test_system_tools.py::TestSystemSetMode::test_set_mode_invalid PASSED
tests/e2e/tools/system/test_system_tools.py::TestSystemUndoRedo::test_undo_single PASSED
tests/e2e/tools/system/test_system_tools.py::TestSystemUndoRedo::test_redo_single PASSED
tests/e2e/tools/system/test_system_tools.py::TestSystemUndoRedo::test_undo_multiple PASSED
tests/e2e/tools/system/test_system_tools.py::TestSystemFileOperations::test_save_file_to_temp PASSED
tests/e2e/tools/system/test_system_tools.py::TestSystemFileOperations::test_new_file PASSED
tests/e2e/tools/system/test_system_tools.py::TestSystemSnapshot::test_snapshot_save_and_list PASSED
tests/e2e/tools/system/test_system_tools.py::TestSystemSnapshot::test_snapshot_restore PASSED
tests/e2e/tools/system/test_system_tools.py::TestSystemSnapshot::test_snapshot_not_found PASSED
tests/e2e/tools/system/test_system_tools.py::TestSystemSnapshot::test_snapshot_auto_name PASSED
```

### UV Tools (12 tests)
```
tests/e2e/tools/uv/test_uv_tools.py::test_uv_list_maps_basic PASSED
tests/e2e/tools/uv/test_uv_tools.py::test_uv_list_maps_with_island_counts PASSED
tests/e2e/tools/uv/test_uv_tools.py::test_uv_list_maps_invalid_object PASSED
tests/e2e/tools/uv/test_uv_tools.py::test_uv_list_maps_non_mesh_object PASSED
tests/e2e/tools/uv/test_uv_tools.py::test_uv_unwrap_smart_project PASSED
tests/e2e/tools/uv/test_uv_tools.py::test_uv_unwrap_cube_project PASSED
tests/e2e/tools/uv/test_uv_tools.py::test_uv_unwrap_cylinder_project PASSED
tests/e2e/tools/uv/test_uv_tools.py::test_uv_unwrap_sphere_project PASSED
tests/e2e/tools/uv/test_uv_tools.py::test_uv_unwrap_standard PASSED
tests/e2e/tools/uv/test_uv_tools.py::test_uv_unwrap_invalid_object PASSED
tests/e2e/tools/uv/test_uv_tools.py::test_uv_pack_islands_basic PASSED
tests/e2e/tools/uv/test_uv_tools.py::test_uv_pack_islands_custom_params PASSED
tests/e2e/tools/uv/test_uv_tools.py::test_uv_pack_islands_invalid_object PASSED
tests/e2e/tools/uv/test_uv_tools.py::test_uv_create_seam_mark PASSED
tests/e2e/tools/uv/test_uv_tools.py::test_uv_create_seam_clear PASSED
tests/e2e/tools/uv/test_uv_tools.py::test_uv_create_seam_invalid_object PASSED
```

---

## Summary

```
============================= 142 passed in 12.25s =============================

[22:13:16] ✅ E2E tests passed!
[22:13:16] ✅ Test log saved: tests/e2e/e2e_test_PASSED_20251130_221316.log
[22:13:16] 🚀 Terminating Blender process...
[22:13:16] ✅ Blender terminated gracefully
```

---

## Test Coverage Summary

| Tool Area | Tests | Status |
|-----------|-------|--------|
| Baking | 7 | ✅ PASSED |
| Collection | 10 | ✅ PASSED |
| Export | 13 | ✅ PASSED |
| Import | 9 | ✅ PASSED |
| Knife/Cut | 9 | ✅ PASSED |
| Material | 14 | ✅ PASSED |
| Mesh Cleanup | 17 | ✅ PASSED |
| Mesh Edge Weights | 16 | ✅ PASSED |
| Scene | 7 | ✅ PASSED |
| Sculpt | 13 | ✅ PASSED |
| System | 12 | ✅ PASSED |
| UV | 15 | ✅ PASSED |
| **Total** | **142** | ✅ **ALL PASSED** |
