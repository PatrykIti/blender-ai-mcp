# TASK-067: Update Root README MCP Client Configs (Collapsible + Codex CLI)

**Status**: ✅ Done  
**Priority**: 🟡 Medium  
**Category**: Docs / DX  
**Completed**: 2025-12-17

## Objective

Improve `README.md` so:
- MCP client configuration snippets are easy to find and don’t dominate the page
- Router onboarding is clearer (workflow-first flow + `status: "error"` visibility)
- The Router section doesn’t conflict with global test counts

## Changes

### 1) Make MCP client config snippets collapsible

**File:** `README.md`

Wrap each “MCP client config” block in `<details>` so the page is scannable:
- Cline / Claude Code (`cline_mcp_settings.json`) — macOS/Windows
- Cline / Claude Code (`cline_mcp_settings.json`) — Linux
- GitHub Copilot CLI config

### 2) Add Codex CLI configuration section
```toml
[mcp_servers.blender-ai-mcp]
command = "docker"
# Optional
args = [
    "run",
    "-i",
    "-v",
    "/tmp:/tmp",
    "-e",
    "BLENDER_AI_TMP_INTERNAL_DIR=/tmp",
    "-e",
    "BLENDER_AI_TMP_EXTERNAL_DIR=/tmp",
    "-e",
    "ROUTER_ENABLED=true",
    "-e",
    "LOG_LEVEL=DEBUG",
    "-e",
    "BLENDER_RPC_HOST=host.docker.internal",
    "blender-ai-mcp:latest"
]
# Optional: propagate additional env vars to the MCP server.
# A default whitelist of env vars will be propagated to the MCP server.
# https://github.com/openai/codex/blob/main/codex-rs/rmcp-client/src/utils.rs#L82
env = {}
enabled_tools = [
       "scene_list_objects",
        "scene_delete_object",
        "scene_clean_scene",
        "scene_duplicate_object",
        "scene_set_active_object",
        "scene_get_viewport",
        "scene_set_mode",
        "scene_context",
        "scene_create",
        "scene_inspect",
        "scene_snapshot_state",
        "scene_compare_snapshot",
        "scene_rename_object",
        "scene_hide_object",
        "scene_show_all_objects",
        "scene_isolate_object",
        "scene_camera_orbit",
        "scene_camera_focus",
        "scene_get_custom_properties",
        "scene_set_custom_property",
        "scene_get_hierarchy",
        "scene_get_bounding_box",
        "scene_get_origin_info",
        "collection_list",
        "collection_list_objects",
        "collection_manage",
        "material_list",
        "material_list_by_object",
        "material_create",
        "material_assign",
        "material_set_params",
        "material_set_texture",
        "material_inspect_nodes",
        "uv_list_maps",
        "uv_unwrap",
        "uv_pack_islands",
        "uv_create_seam",
        "modeling_create_primitive",
        "modeling_transform_object",
        "modeling_add_modifier",
        "modeling_apply_modifier",
        "modeling_convert_to_mesh",
        "modeling_join_objects",
        "modeling_separate_object",
        "modeling_set_origin",
        "modeling_list_modifiers",
        "mesh_select",
        "mesh_select_targeted",
        "mesh_delete_selected",
        "mesh_extrude_region",
        "mesh_fill_holes",
        "mesh_bevel",
        "mesh_loop_cut",
        "mesh_inset",
        "mesh_boolean",
        "mesh_merge_by_distance",
        "mesh_subdivide",
        "mesh_smooth",
        "mesh_flatten",
        "mesh_list_groups",
        "mesh_get_vertex_data",
        "mesh_randomize",
        "mesh_shrink_fatten",
        "mesh_create_vertex_group",
        "mesh_assign_to_group",
        "mesh_remove_from_group",
        "mesh_bisect",
        "mesh_edge_slide",
        "mesh_vert_slide",
        "mesh_triangulate",
        "mesh_remesh_voxel",
        "mesh_transform_selected",
        "mesh_bridge_edge_loops",
        "mesh_duplicate_selected",
        "mesh_spin",
        "mesh_screw",
        "mesh_add_vertex",
        "mesh_add_edge_face",
        "mesh_edge_crease",
        "mesh_bevel_weight",
        "mesh_mark_sharp",
        "mesh_dissolve",
        "mesh_tris_to_quads",
        "mesh_normals_make_consistent",
        "mesh_decimate",
        "mesh_knife_project",
        "mesh_rip",
        "mesh_split",
        "mesh_edge_split",
        "mesh_symmetrize",
        "mesh_grid_fill",
        "mesh_poke_faces",
        "mesh_beautify_fill",
        "mesh_mirror",
        "curve_create",
        "curve_to_mesh",
        "text_create",
        "text_edit",
        "text_to_mesh",
        "export_glb",
        "export_fbx",
        "export_obj",
        "sculpt_auto",
        "sculpt_brush_smooth",
        "sculpt_brush_grab",
        "sculpt_brush_crease",
        "sculpt_brush_clay",
        "sculpt_brush_inflate",
        "sculpt_brush_blob",
        "sculpt_brush_snake_hook",
        "sculpt_brush_draw",
        "sculpt_brush_pinch",
        "sculpt_enable_dyntopo",
        "sculpt_disable_dyntopo",
        "sculpt_dyntopo_flood_fill",
        "metaball_create",
        "metaball_add_element",
        "metaball_to_mesh",
        "skin_create_skeleton",
        "skin_set_radius",
        "lattice_create",
        "lattice_bind",
        "lattice_edit_point",
        "mesh_set_proportional_edit",
        "system_set_mode",
        "system_undo",
        "system_redo",
        "system_save_file",
        "system_new_file",
        "system_snapshot",
        "bake_normal_map",
        "bake_ao",
        "bake_combined",
        "bake_diffuse",
        "import_obj",
        "import_fbx",
        "import_glb",
        "import_image_as_plane",
        "extraction_deep_topology",
        "extraction_component_separate",
        "extraction_detect_symmetry",
        "extraction_edge_loop_analysis",
        "extraction_face_group_analysis",
        "extraction_render_angles",
        "armature_create",
        "armature_add_bone",
        "armature_bind",
        "armature_pose_bone",
        "armature_weight_paint_assign",
        "workflow_catalog",
        "router_set_goal",
        "router_get_status",
        "router_clear_goal"
      ]
```

### 3) Clarify workflow-first Router usage in root README

**File:** `README.md`

Add a short “Workflow-First Quick Start” showing:
- Optional workflow discovery via `workflow_catalog(action="search", ...)`
- Mandatory `router_set_goal(goal=...)`
- Response handling for `ready` / `needs_input` / `no_match` / `error`

### 4) Resolve confusing test-count messaging

**File:** `README.md`

The Router section previously used hard-coded test counts that drifted from the global testing section.
Update it to reference the **🧪 Testing** section for up-to-date numbers instead of repeating stale counts.
Also remove hard-coded counts from the testing section and add `--collect-only` commands to show current totals.

## Acceptance Criteria

- [x] `README.md` configuration snippets are collapsed by default.
- [x] Codex CLI configuration is documented with a working TOML example.
- [x] No behavioral changes to the server — documentation only.
