# Kanban Tasks - Blender AI MCP

Task board for the project. Update statuses in markdown files.

## 📊 Statistics
- **To Do:** 23 tasks (~180 sub-tasks)
- **In Progress:** 1 task
- **Done:** 139

---

## 🚨 To Do

### FastMCP Platform & LLM UX
| ID | Title | Priority | Notes |
|----|-------|----------|-------|
| [TASK-083](./TASK-083_FastMCP_3x_Platform_Migration.md) | **FastMCP 3.x Platform Migration** | 🔴 High | Providers + transforms as the new server base |
| [TASK-084](./TASK-084_Dynamic_Tool_Discovery.md) | **Dynamic Tool Discovery for Large Catalogs** | 🔴 High | Tool Search as the primary discovery model |
| [TASK-085](./TASK-085_Session_Adaptive_Tool_Visibility.md) | **Session-Adaptive Tool Visibility** | 🔴 High | Per-session visibility and phase-based capability exposure |
| [TASK-086](./TASK-086_LLM_Optimized_API_Surfaces.md) | **LLM-Optimized API Surfaces** | 🔴 High | Rename/reshape public MCP surfaces without rewriting business logic |
| [TASK-087](./TASK-087_Structured_User_Elicitation.md) | **Structured User Elicitation for Missing Parameters** | 🔴 High | First-class clarification flow for router/workflow inputs |
| [TASK-088](./TASK-088_Background_Tasks_and_Progress.md) | **Background Tasks and Progress for Heavy Blender Work** | 🔴 High | Non-blocking jobs for imports, renders, analysis, reconstruction |
| [TASK-089](./TASK-089_Typed_Contracts_and_Structured_Responses.md) | **Typed Contracts and Structured Responses** | 🔴 High | Structured state exchange for critical tools |
| [TASK-090](./TASK-090_Prompt_Layer_and_Tool_Compatible_Prompts.md) | **Prompt Layer and Tool-Compatible Prompt Delivery** | 🟡 Medium | Prompts as first-class server product, including tool-only clients |
| [TASK-091](./TASK-091_Versioned_Client_Surfaces.md) | **Versioned Client Surfaces for Safe API Evolution** | 🔴 High | Legacy and LLM-first surfaces can coexist |
| [TASK-092](./TASK-092_Server_Side_Sampling_Assistants.md) | **Server-Side Sampling Assistants** | 🟡 Medium | Bounded internal reasoning helpers for analysis and recovery |
| [TASK-093](./TASK-093_Observability_Timeouts_and_Pagination.md) | **Observability, Timeouts, and Pagination** | 🟡 Medium | Better tracing, safer execution, cleaner component listings |
| [TASK-094](./TASK-094_Code_Mode_Exploration.md) | **Code Mode Exploration for Large-Scale Orchestration** | 🟡 Medium | Experimental track for code-driven orchestration |

### Router & Workflow Extraction
| ID | Title | Priority | Notes |
|----|-------|----------|-------|
| [TASK-058](./TASK-058_Loop_System_String_Interpolation.md) | **Loop System & String Interpolation** | 🔴 High | Loop parameter + $FORMAT() for simplified YAML workflows |
| [TASK-055-FIX-7](./TASK-055-FIX-7_Dynamic_Plank_System_Simple_Table.md) | **Dynamic Plank System + Parameter Renaming** | 🟡 Medium | simple_table.yaml: rename parameters + adaptive plank count + fractional planks |
| [TASK-054](./TASK-054_Ensemble_Matcher_Enhancements.md) | **Ensemble Matcher Enhancements** | 🟡 Medium | 8 sub-tasks: telemetry/metrics + async parallel execution (TASK-054-1 obsolete - replaced by TASK-055-FIX Bug 3) |
| [TASK-042](./TASK-042_Automatic_Workflow_Extraction_System.md) | **Automatic Workflow Extraction System** | 🔴 High | 6 phases: import → analyze → decompose → map → generate YAML → LLM Vision |

### Mesh Introspection
| ID | Title | Priority | Notes |
|----|-------|----------|-------|

### Scene & Rig Introspection
| ID | Title | Priority | Notes |
|----|-------|----------|-------|

### Reconstruction (Mesh, Material, Scene)
| ID | Title | Priority | Notes |
|----|-------|----------|-------|
| [TASK-076](./TASK-076_Mesh_Build_Mega_Tool.md) | **Mesh Build Mega Tool (Core Topology)** | 🔴 High | Write-side reconstruction for vertices/edges/faces |
| [TASK-077](./TASK-077_Mesh_Build_Surface_Data.md) | **Mesh Build Surface Data (UVs, Materials, Attributes)** | 🔴 High | UVs + material indices + attributes |
| [TASK-078](./TASK-078_Mesh_Build_Deformation_Data.md) | **Mesh Build Deformation Data (Normals, Weights, Shape Keys)** | 🔴 High | Custom normals + weights + shape keys |
| [TASK-079](./TASK-079_Node_Graph_Build_Tools.md) | **Node Graph Build Tools (Material + Geometry Nodes)** | 🔴 High | Rebuild shader/GN graphs |
| [TASK-080](./TASK-080_Image_Asset_Tools.md) | **Image Asset Tools (List, Load, Export, Pack)** | 🟡 Medium | Texture asset pipeline |
| [TASK-081](./TASK-081_Scene_Render_World_Settings.md) | **Scene Render + World Settings (Inspect & Apply)** | 🟡 Medium | Render + world settings |
| [TASK-082](./TASK-082_Animation_and_Drivers_Tools.md) | **Animation and Driver Tools (Inspect + Build)** | 🟡 Medium | Actions, FCurves, drivers, NLA |

---

## 🚧 In Progress

| ID | Title | Priority | Notes |
|----|-------|----------|-------|
| [TASK-055-FIX-7](./TASK-055-FIX-7_Dynamic_Plank_System_Simple_Table.md) | **Dynamic Plank System + Parameter Renaming for simple_table.yaml** | 🟡 Medium | Phase 1: Parameter renaming + Phase 2: 15 conditional planks |

---

## ✅ Done

| ID | Title | Priority | Completion Date |
|----|-------|----------|-----------------|
| [TASK-075](./TASK-075_Workflow_Catalog_Import.md) | **Workflow Catalog Import (YAML/JSON, inline/chunked)** | 🟡 Medium | 2025-12-20 |
| [TASK-074](./TASK-074_Mesh_Inspect_Mega_Tool.md) | **Mesh Inspect Mega Tool** | 🟡 Medium | 2025-12-19 |
| [TASK-073](./TASK-073_Rig_Curve_Lattice_Introspection.md) | **Rig/Curve/Lattice Introspection** | 🔴 High | 2025-12-19 |
| [TASK-072](./TASK-072_Modifier_Constraint_Introspection.md) | **Modifier & Constraint Introspection** | 🔴 High | 2025-12-19 |
| [TASK-071](./TASK-071_Mesh_Introspection_Advanced.md) | **Mesh Introspection Advanced** | 🔴 High | 2025-12-19 |
| [TASK-070](./TASK-070_Mesh_Topology_Introspection_Extensions.md) | **Mesh Topology Introspection Extensions** | 🔴 High | 2025-12-19 |
| [TASK-069](./TASK-069_Repo_Community_Standards_and_Release_Docs.md) | **Repo Professionalization: SECURITY/SUPPORT/CoC + Support Matrix + Release/Dev Docs** | 🟡 Medium | 2025-12-18 |
| [TASK-068](./TASK-068_License_BUSL_Compliance.md) | **License: BUSL 1.1 Compliance + Apache Change License File** | 🔴 High | 2025-12-17 |
| [TASK-067](./TASK-067_Update_Root_README_MCP_Client_Configs.md) | **Update Root README MCP Client Configs (Collapsible + Codex CLI)** | 🟡 Medium | 2025-12-17 |
| [TASK-066](./TASK-066_Remove_Legacy_Goal_Matching_Fallback.md) | **Remove Legacy Goal Matching Fallback (Ensemble-Only)** | 🔴 High | 2025-12-17 |
| [TASK-065](./TASK-065_Workflow_Catalog_Tool.md) | **Workflow Catalog Tool (replace vector_db_manage)** | 🟡 Medium | 2025-12-17 |
| [TASK-064](./TASK-064_Flexible_List_Parameter_Parsing.md) | **Flexible vector/color params** | 🟡 Medium | 2025-12-15 |
| [TASK-063](./TASK-063_Router_Auto_Selection_Preservation.md) | **Router: preserve edit selection** | 🔴 High | 2025-12-15 |
| [TASK-062](./TASK-062_Modeling_Add_Modifier_Boolean_Object_Reference.md) | **`modeling_add_modifier` BOOLEAN: object by name** | 🔴 High | 2025-12-15 |
| [TASK-060](./TASK-060_Unified_Expression_Evaluator.md) | **Unified Expression Evaluator** | 🔴 High | 2025-12-12 |
| [TASK-057](./TASK-057_Remove_Old_Pattern_Expansion_Path.md) | **Remove Old Pattern-Based Expansion Path** | 🟡 Medium | 2025-12-11 |
| [TASK-056](./TASK-056_Workflow_System_Enhancements.md) | **Workflow System Enhancements** | 🔴 High | 2025-12-11 |
| [TASK-053](./TASK-053_Ensemble_Matcher_System.md) | **Ensemble Matcher System** | 🔴 High | 2025-12-11 |
| [TASK-055-FIX](./TASK-055-FIX_Unified_Parameter_Resolution.md) | **Unified Parameter Resolution** | 🔴 High | 2025-12-11 |
| [TASK-055-FIX-6](./TASK-055-FIX-6_Flexible_YAML_Parameter_Loading.md) | **Flexible YAML Parameter Loading with Semantic Extensions** | 🔴 Critical | 2025-12-10 |
| [TASK-055](./TASK-055_Interactive_Parameter_Resolution.md) | **Interactive Parameter Resolution** | 🔴 High | 2025-12-08 |
| [TASK-052](./TASK-052_Intelligent_Parametric_Adaptation.md) | **Parametric Workflow Variables** | 🔴 High | 2025-12-07 |
| [TASK-051](./TASK-051_Confidence_Based_Workflow_Adaptation.md) | **Confidence-Based Workflow Adaptation** | 🔴 High | 2025-12-07 |
| [TASK-050](./TASK-050_Multi_Embedding_Workflow_System.md) | **Multi-Embedding Workflow System** | 🔴 High | 2025-12-07 |
| [TASK-049](./TASK-049_Fix_ToolDispatcher_Mappings.md) | **Fix ToolDispatcher Mappings** | 🔴 High | 2025-12-07 |
| [TASK-048](./TASK-048_Proper_DI_For_Classifiers_Shared_LaBSE_model.md) | **Proper DI for Classifiers + Shared LaBSE Model** | 🔴 High | 2025-12-07 |
| [TASK-047](./TASK-047_Migration_Router_Semantic_Search_To_LanceDB.md) | **LanceDB Vector Store Migration** | 🔴 High | 2025-12-06 |
| [TASK-046](./TASK-046_Router_Semantic_Generalization.md) | **Router Semantic Generalization (LaBSE)** | 🔴 High | 2025-12-06 |
| [TASK-041](./TASK-041_Router_YAML_Workflow_Integration.md) | **Router YAML Workflow Integration** | 🔴 High | 2025-12-03 |
| [TASK-037](./TASK-037_Armature_Rigging.md) | **Armature & Rigging** | 🟢 Low | 2025-12-05 |
| [TASK-036](./TASK-036_Symmetry_Advanced_Fill.md) | **Symmetry & Advanced Fill** | 🟡 Medium | 2025-12-05 |
| [TASK-045](./TASK-045_Object_Inspection_Tools.md) | **Object Inspection Tools** | 🟡 Medium | 2025-12-04 |
| [TASK-034](./TASK-034_Text_Annotations.md) | **Text & Annotations** | 🟡 Medium | 2025-12-04 |
| [TASK-044](./TASK-044_Extraction_Analysis_Tools.md) | **Extraction Analysis Tools** | 🔴 High | 2025-12-04 |
| [TASK-043](./TASK-043_Scene_Utility_Tools.md) | **Scene Utility Tools** | 🔴 High | 2025-12-03 |
| [TASK-033](./TASK-033_Lattice_Deformation.md) | **Lattice Deformation** | 🟠 High | 2025-12-03 |
| [TASK-039](./TASK-039_Router_Supervisor_Implementation.md) | **Router Supervisor Implementation** | 🔴 High | 2025-12-02 |
| [TASK-040](./TASK-040_Router_E2E_Test_Coverage_Extension.md) | **Router E2E Test Coverage Extension** | 🟡 Medium | 2025-12-02 |
| [TASK-028](./TASK-028_E2E_Testing_Infrastructure.md) | **E2E Testing Infrastructure** | 🔴 High | 2025-11-30 |
| [TASK-038](./TASK-038_Organic_Modeling_Tools.md) | **Organic Modeling Tools** | 🔴 High | 2025-11-30 |
| [TASK-035-4](./TASK-035_Import_Tools.md#task-035-4-import_glb) | **import_glb** | 🟠 High | 2025-11-30 |
| [TASK-035-3](./TASK-035_Import_Tools.md#task-035-3-import_image_as_plane) | **import_image_as_plane** | 🟠 High | 2025-11-30 |
| [TASK-035-2](./TASK-035_Import_Tools.md#task-035-2-import_fbx) | **import_fbx** | 🟠 High | 2025-11-30 |
| [TASK-035-1](./TASK-035_Import_Tools.md#task-035-1-import_obj) | **import_obj** | 🟠 High | 2025-11-30 |
| [TASK-032-4](./TASK-032_Knife_Cut_Tools.md#task-032-4-mesh_edge_split) | **mesh_edge_split** | 🟠 High | 2025-11-30 |
| [TASK-032-3](./TASK-032_Knife_Cut_Tools.md#task-032-3-mesh_split) | **mesh_split** | 🟠 High | 2025-11-30 |
| [TASK-032-2](./TASK-032_Knife_Cut_Tools.md#task-032-2-mesh_rip) | **mesh_rip** | 🟠 High | 2025-11-30 |
| [TASK-032-1](./TASK-032_Knife_Cut_Tools.md#task-032-1-mesh_knife_project) | **mesh_knife_project** | 🟠 High | 2025-11-30 |
| [TASK-031-4](./TASK-031_Baking_Tools.md#task-031-4-bake_diffuse) | **bake_diffuse** | 🔴 Critical | 2025-11-30 |
| [TASK-031-3](./TASK-031_Baking_Tools.md#task-031-3-bake_combined) | **bake_combined** | 🔴 Critical | 2025-11-30 |
| [TASK-031-2](./TASK-031_Baking_Tools.md#task-031-2-bake_ao) | **bake_ao** | 🔴 Critical | 2025-11-30 |
| [TASK-031-1](./TASK-031_Baking_Tools.md#task-031-1-bake_normal_map) | **bake_normal_map** | 🔴 Critical | 2025-11-30 |
| [TASK-030-4](./TASK-030_Mesh_Cleanup_Optimization.md#task-030-4-mesh_decimate) | **mesh_decimate** | 🔴 High | 2025-11-30 |
| [TASK-030-3](./TASK-030_Mesh_Cleanup_Optimization.md#task-030-3-mesh_normals_make_consistent) | **mesh_normals_make_consistent** | 🔴 High | 2025-11-30 |
| [TASK-030-2](./TASK-030_Mesh_Cleanup_Optimization.md#task-030-2-mesh_tris_to_quads) | **mesh_tris_to_quads** | 🔴 High | 2025-11-30 |
| [TASK-030-1](./TASK-030_Mesh_Cleanup_Optimization.md#task-030-1-mesh_dissolve) | **mesh_dissolve** | 🔴 High | 2025-11-30 |
| [TASK-029-3](./TASK-029_Edge_Weights_Creases.md#task-029-3-mesh_mark_sharp) | **mesh_mark_sharp** | 🔴 High | 2025-11-30 |
| [TASK-029-2](./TASK-029_Edge_Weights_Creases.md#task-029-2-mesh_bevel_weight) | **mesh_bevel_weight** | 🔴 High | 2025-11-30 |
| [TASK-029-1](./TASK-029_Edge_Weights_Creases.md#task-029-1-mesh_edge_crease) | **mesh_edge_crease** | 🔴 High | 2025-11-30 |
| [TASK-025-4](./TASK-025_System_Tools.md#task-025-4-system_snapshot) | **system_snapshot** | 🟢 Low | 2025-11-29 |
| [TASK-025-3](./TASK-025_System_Tools.md#task-025-3-system_save_file--system_new_file) | **system_save_file / system_new_file** | 🟡 Medium | 2025-11-29 |
| [TASK-025-2](./TASK-025_System_Tools.md#task-025-2-system_undo--system_redo) | **system_undo / system_redo** | 🟡 Medium | 2025-11-29 |
| [TASK-025-1](./TASK-025_System_Tools.md#task-025-1-system_set_mode) | **system_set_mode** | 🟡 Medium | 2025-11-29 |
| [TASK-026-3](./TASK-026_Export_Tools.md#task-026-3-export_obj) | **export_obj** | 🟢 Low | 2025-11-29 |
| [TASK-026-2](./TASK-026_Export_Tools.md#task-026-2-export_fbx) | **export_fbx** | 🟡 Medium | 2025-11-29 |
| [TASK-026-1](./TASK-026_Export_Tools.md#task-026-1-export_glb) | **export_glb** | 🟠 High | 2025-11-29 |
| [TASK-027-4](./TASK-027_Sculpting_Tools.md#task-027-4-sculpt_brush_crease) | **sculpt_brush_crease** | 🟢 Low | 2025-11-29 |
| [TASK-027-3](./TASK-027_Sculpting_Tools.md#task-027-3-sculpt_brush_grab) | **sculpt_brush_grab** | 🟢 Low | 2025-11-29 |
| [TASK-027-2](./TASK-027_Sculpting_Tools.md#task-027-2-sculpt_brush_smooth) | **sculpt_brush_smooth** | 🟢 Low | 2025-11-29 |
| [TASK-027-1](./TASK-027_Sculpting_Tools.md#task-027-1-sculpt_auto) | **sculpt_auto** | 🟢 Low | 2025-11-29 |
| [TASK-022-1](./TASK-022_Collection_Tools.md#task-022-1-collection_manage) | **collection_manage** (create, delete, rename, move) | 🟡 Medium | 2025-11-29 |
| [TASK-024-3](./TASK-024_UV_Tools.md#task-024-3-uv_create_seam-optional) | **uv_create_seam** | 🟢 Low | 2025-11-29 |
| [TASK-024-2](./TASK-024_UV_Tools.md#task-024-2-uv_pack_islands) | **uv_pack_islands** | 🟡 Medium | 2025-11-29 |
| [TASK-024-1](./TASK-024_UV_Tools.md#task-024-1-uv_unwrap) | **uv_unwrap** | 🟡 Medium | 2025-11-29 |
| [TASK-023-4](./TASK-023_Material_Tools.md#task-023-4-material_set_texture) | **material_set_texture** | 🟡 Medium | 2025-11-29 |
| [TASK-023-3](./TASK-023_Material_Tools.md#task-023-3-material_set_params) | **material_set_params** | 🟡 Medium | 2025-11-29 |
| [TASK-023-2](./TASK-023_Material_Tools.md#task-023-2-material_assign) | **material_assign** | 🟠 High | 2025-11-29 |
| [TASK-023-1](./TASK-023_Material_Tools.md#task-023-1-material_create) | **material_create** | 🟠 High | 2025-11-29 |
| [TASK-021-5](./TASK-021_Phase_2_6_Curves_Procedural.md#task-021-5-mesh-add-geometry-tools) | **Mesh Add Geometry Tools** (vertex, edge, face) | 🟢 Low | 2025-11-29 |
| [TASK-021-4](./TASK-021_Phase_2_6_Curves_Procedural.md#task-021-4-mesh-screw-tool) | **Mesh Screw Tool** | 🟡 Medium | 2025-11-29 |
| [TASK-021-3](./TASK-021_Phase_2_6_Curves_Procedural.md#task-021-3-mesh-spin-tool) | **Mesh Spin Tool** | 🟡 Medium | 2025-11-29 |
| [TASK-021-2](./TASK-021_Phase_2_6_Curves_Procedural.md#task-021-2-curve-to-mesh-tool) | **Curve To Mesh Tool** | 🟡 Medium | 2025-11-29 |
| [TASK-021-1](./TASK-021_Phase_2_6_Curves_Procedural.md#task-021-1-curve-create-tool) | **Curve Create Tool** | 🟡 Medium | 2025-11-29 |
| [TASK-019-3](./TASK-019_Phase_2_4_Core_Transform.md#task-019-3-mesh-duplicate-selected-tool) | **Mesh Duplicate Selected Tool** | 🟡 Medium | 2025-11-29 |
| [TASK-019-2](./TASK-019_Phase_2_4_Core_Transform.md#task-019-2-mesh-bridge-edge-loops-tool) | **Mesh Bridge Edge Loops Tool** | 🟡 Medium | 2025-11-29 |
| [TASK-019-1](./TASK-019_Phase_2_4_Core_Transform.md#task-019-1-mesh-transform-selected-tool) | **Mesh Transform Selected Tool** 🔥 CRITICAL | 🔴 Critical | 2025-11-29 |
| [TASK-018-4](./TASK-018_Phase_2_5_Precision.md#task-018-4-mesh-remesh-voxel-tool) | **Mesh Remesh Voxel Tool** | 🟡 Medium | 2025-11-29 |
| [TASK-018-3](./TASK-018_Phase_2_5_Precision.md#task-018-3-mesh-triangulate-tool) | **Mesh Triangulate Tool** | 🟢 Low | 2025-11-29 |
| [TASK-018-2](./TASK-018_Phase_2_5_Precision.md#task-018-2-mesh-edgevertex-slide-tools) | **Mesh Edge/Vertex Slide Tools** | 🟡 Medium | 2025-11-29 |
| [TASK-018-1](./TASK-018_Phase_2_5_Precision.md#task-018-1-mesh-bisect-tool) | **Mesh Bisect Tool** | 🟡 Medium | 2025-11-29 |
| [TASK-017-2](./TASK-016_017_Organic_and_Groups.md#task-017-2-mesh-assignremove-vertex-group-tools) | **Mesh Assign/Remove Vertex Group Tools** | 🟡 Medium | 2025-11-29 |
| [TASK-017-1](./TASK-016_017_Organic_and_Groups.md#task-017-1-mesh-create-vertex-group-tool) | **Mesh Create Vertex Group Tool** | 🟡 Medium | 2025-11-29 |
| [TASK-016-2](./TASK-016_017_Organic_and_Groups.md#task-016-2-mesh-shrinkfatten-tool) | **Mesh Shrink/Fatten Tool** | 🟡 Medium | 2025-11-29 |
| [TASK-016-1](./TASK-016_017_Organic_and_Groups.md#task-016-1-mesh-randomize-tool) | **Mesh Randomize Tool** | 🟡 Medium | 2025-11-29 |
| [TASK-020-5](./TASK-020-5_Scene_Inspect_Mega_Tool.md) | **Scene Inspect Mega Tool** (object, topology, modifiers, materials) | 🔴 High | 2025-11-29 |
| [TASK-020-4](./TASK-020-4_Mesh_Select_Targeted_Mega_Tool.md) | **Mesh Select Targeted Mega Tool** (by_index, loop, ring, by_location) | 🔴 High | 2025-11-29 |
| [TASK-020-3](./TASK-020-3_Scene_Create_Mega_Tool.md) | **Scene Create Mega Tool** (light, camera, empty) | 🟡 Medium | 2025-11-29 |
| [TASK-020-2](./TASK-020-2_Mesh_Select_Mega_Tool.md) | **Mesh Select Mega Tool** (all, none, linked, more, less, boundary) | 🔴 High | 2025-11-29 |
| [TASK-020-1](./TASK-020-1_Scene_Context_Mega_Tool.md) | **Scene Context Mega Tool** (mode, selection) | 🔴 High | 2025-11-29 |
| [TASK-015-1-WH](./TASK-015-1_Workflow_Hints.md) | **Workflow Hints for All MCP Tools** | 🟡 Medium | 2025-11-28 |
| [TASK-015-7](./TASK-015_Phase_2_1_Advanced_Selection.md#task-015-7-mesh-select-boundary-tool) | **Mesh Select Boundary Tool** | 🔴 Critical | 2025-11-28 |
| [TASK-015-6](./TASK-015_Phase_2_1_Advanced_Selection.md#task-015-6-mesh-select-by-location-tool) | **Mesh Select By Location Tool** | 🟡 Medium | 2025-11-28 |
| [TASK-015-5](./TASK-015_Phase_2_1_Advanced_Selection.md#task-015-5-mesh-get-vertex-data-tool) | **Mesh Get Vertex Data Tool** | 🔴 Critical | 2025-11-28 |
| [TASK-015-4](./TASK-015_Phase_2_1_Advanced_Selection.md#task-015-4-mesh-select-moreless-tools) | **Mesh Select More/Less Tools** | 🟡 Medium | 2025-11-28 |
| [TASK-015-3](./TASK-015_Phase_2_1_Advanced_Selection.md#task-015-3-mesh-select-linked-tool) | **Mesh Select Linked Tool** | 🔴 Critical | 2025-11-28 |
| [TASK-015-2](./TASK-015_Phase_2_1_Advanced_Selection.md#task-015-2-mesh-select-ring-tool) | **Mesh Select Ring Tool** | 🟡 Medium | 2025-11-28 |
| [TASK-015-1](./TASK-015_Phase_2_1_Advanced_Selection.md#task-015-1-mesh-select-loop-tool) | **Mesh Select Loop Tool** | 🟡 Medium | 2025-11-28 |
| [TASK-014-14](./TASK-014-14_Scene_Inspect_Modifiers.md) | **Scene Inspect Modifiers Tool** | 🟡 Medium | 2025-11-27 |
| [TASK-014-13](./TASK-014-13_Scene_Inspect_Mesh_Topology.md) | **Scene Inspect Mesh Topology Tool** | 🔴 High | 2025-11-27 |
| [TASK-014-12](./TASK-014-12_Mesh_List_Groups.md) | **Mesh List Groups Tool** | 🟡 Medium | 2025-11-27 |
| [TASK-014-11](./TASK-014-11_UV_List_Maps.md) | **UV List Maps Tool** | 🟡 Medium | 2025-11-27 |
| [TASK-014-10](./TASK-014-10_Scene_Inspect_Material_Slots.md) | **Scene Inspect Material Slots Tool** | 🟡 Medium | 2025-11-27 |
| [TASK-014-9](./TASK-014-9_Material_List_By_Object.md) | **Material List By Object Tool** | 🟢 Low | 2025-11-27 |
| [TASK-014-8](./TASK-014-8_Material_List.md) | **Material List Tool** | 🟢 Low | 2025-11-27 |
| [TASK-014-7](./TASK-014-7_Collection_List_Objects.md) | **Collection List Objects Tool** | 🟢 Low | 2025-11-27 |
| [TASK-014-6](./TASK-014-6_Collection_List.md) | **Collection List Tool** | 🟢 Low | 2025-11-27 |
| [TASK-014-5](./TASK-014-5_Scene_Compare_Snapshot.md) | **Scene Compare Snapshot Tool** | 🟡 Medium | 2025-11-27 |
| [TASK-014-4](./TASK-014-4_Scene_Snapshot_State.md) | **Scene Snapshot State Tool** | 🟡 Medium | 2025-11-27 |
| [TASK-014-3](./TASK-014-3_Scene_Inspect_Object.md) | **Scene Inspect Object Tool** | 🔴 High | 2025-11-27 |
| [TASK-014-2](./TASK-014-2_Scene_List_Selection.md) | **Scene List Selection Tool** | 🟡 Medium | 2025-11-27 |
| [TASK-014-1](./TASK-014-1_Scene_Get_Mode.md) | **Scene Get Mode Tool** | 🟢 Low | 2025-11-27 |
| [TASK-012](./TASK-012_Mesh_Smooth_Flatten.md) | **Mesh Smooth & Flatten Tools** | 🟡 Medium | 2025-11-25 |
| [TASK-011-7](./TASK-011-7_Scene_Tool_Docstring_Standardization.md) | **Scene Tool Docstring Standardization** | 🟢 Low | 2025-11-25 |
| [TASK-011-6](./TASK-011-6_Modeling_Tool_Docstring_Standardization.md) | **Modeling Tool Docstring Standardization** | 🟢 Low | 2025-11-25 |
| [TASK-011-5](./TASK-011-5_Mesh_Tool_Docstring_Standardization.md) | **Mesh Tool Docstring Standardization** | 🟢 Low | 2025-11-25 |
| [TASK-011-4](./TASK-011-4_Advanced_Mesh_Ops.md) | **Advanced Mesh Ops (Boolean, Merge, Subdivide)** | 🟡 Medium | 2025-11-25 |
| [TASK-011-3](./TASK-011-3_Edge_Operations.md) | **Edge Operations (Bevel, Loop Cut, Inset)** | 🟡 Medium | 2025-11-24 |
| [TASK-011-2](./TASK-011-2_Basic_Extrusions.md) | **Basic Extrusions & Face Operations** | 🔴 High | 2025-11-24 |
| [TASK-011-X](./TASK-011-X_Mode_Switching.md) | **Scene Mode Switching Tool** | 🔴 High | 2025-11-24 |
| [TASK-011-1](./TASK-011-1_Edit_Mode_Foundation.md) | **Edit Mode Foundation (Selection & Deletion)** | 🔴 High | 2025-11-24 |
| [TASK-010](./TASK-010_Scene_Construction_Tools.md) | **Scene Construction Tools (Lights, Cameras, Empties)** | 🟡 Medium | 2025-11-24 |
| [TASK-009](./TASK-009_Extend_Viewport_Control.md) | **Extend Viewport Control (Shading & Camera)** | 🟡 Medium | 2025-11-24 |
| [TASK-001](./TASK-001_Project_Setup.md) | **Project Initialization and Structure** | 🔴 High | 2025-11-22 |
| [TASK-002](./TASK-002_Communication_Core.md) | **Communication Bridge Implementation (RPC)** | 🔴 High | 2025-11-22 |
| [TASK-003](./TASK-003_MCP_Scene_Tools.md) | **MVP MCP Server and Scene Tools** | 🟡 Medium | 2025-11-22 |
| [TASK-003_1](./TASK-003_1_Refactor_Architecture.md) | **Server Architecture Refactor (Clean Architecture)** | 🔴 High | 2025-11-22 |
| [TASK-003_2](./TASK-003_2_Refactor_Main_DI.md) | **Main and DI Refactor (Separation of Concerns)** | 🔴 High | 2025-11-22 |
| [TASK-003_3](./TASK-003_3_Refactor_FastMCP_Dependency_Injection.md) | **FastMCP DI Implementation (Depends)** | 🔴 High | 2025-11-22 |
| [TASK-003_4](./TASK-003_4_Refactor_Addon_Architecture.md) | **Addon Architecture Refactor (Clean Architecture)** | 🔴 High | 2025-11-22 |
| [TASK-004](./TASK-004_Modeling_Tools.md) | **Modeling Tools (Mesh Ops)** | 🟡 Medium | 2025-11-22 |
| [TASK-005](./TASK-005_Dockerize_Server.md) | **MCP Server Containerization (Docker)** | 🟡 Medium | 2025-11-22 |
| [TASK-006](./TASK-006_Project_Standardization_and_CICD.md) | **Project Standardization and CI/CD Setup** | 🔴 High | 2025-11-22 |
| [TASK-007](./TASK-007_Scene_Tools_Extension.md) | **Scene Tools Extension (Duplicate, Set Active, Viewport)** | 🔴 High | 2025-11-22 |
| [TASK-008](./TASK-008_Implement_Apply_Modifier.md) | **Implement Modeling Tool - Apply Modifier** | 🟡 Medium | 2025-11-22 |
| [TASK-008_1](./TASK-008_1_Modeling_Tools_Completion.md) | **Modeling Tools Completion (Object Mode)** | 🔴 High | 2025-11-22 |
| [TASK-008_2](./TASK-008_2_Standardize_Tool_Naming.md) | **Standardize Tool Naming (Prefixing)** | 🟡 Medium | 2025-11-22 |

---

## ℹ️ Priority Legend
- 🔴 **High**: Blockers or key functionality.
- 🟡 **Medium**: Important, but non-blocking.
- 🟢 **Low**: Nice to have / Improvements.
