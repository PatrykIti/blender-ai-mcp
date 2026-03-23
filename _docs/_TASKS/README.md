# Kanban Tasks - Blender AI MCP

Task board for the project. Update statuses in markdown files.

## 📊 Statistics
- **To Do:** 11 tasks (~225 sub-tasks)
- **In Progress:** 1 tasks
- **Done:** 165

## 🧭 Terminology Guardrails

- MCP specification revisions are date-based (for example `2025-11-25`), not “MCP 3.x”.
- In this board, “3.x” refers to the **FastMCP** runtime line.
- If a task depends on protocol behavior, reference the MCP spec revision and/or SEP explicitly.

---

## 🚨 To Do

### FastMCP Platform & LLM UX
Execution note: this track currently spans TASK-083 through TASK-099 inclusive, including TASK-085 and TASK-090 through TASK-092. The table order is roadmap order, not a strict serial execution order; the delivery path is dependency-driven. TASK-094 remains an experimental track and is not part of the default critical path.

| ID | Title | Priority | Notes |
|----|-------|----------|-------|

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
| [TASK-110](./TASK-110_Legacy_Manual_Surface_Boundary.md) | **Legacy Manual Surface Boundary** | 🟡 Medium | 2026-03-23 |
| [TASK-109](./TASK-109_Scene_Camera_Parameter_UX_Clarification.md) | **Scene Camera Parameter UX Clarification** | 🟡 Medium | 2026-03-23 |
| [TASK-108](./TASK-108_Coverage_Expansion_For_Contracts_MCP_Areas_RPC_And_Surface_Runtime.md) | **Coverage Expansion for Contracts, MCP Areas, RPC Alignment, and Surface Runtime** | 🟡 Medium | 2026-03-23 |
| [TASK-107](./TASK-107_Workflow_Catalog_Get_Contract_Alignment.md) | **Workflow Catalog Get Contract Alignment** | 🟡 Medium | 2026-03-23 |
| [TASK-106](./TASK-106_Modeling_Transform_RPC_Result_Alignment.md) | **Modeling Transform RPC Result Alignment** | 🟡 Medium | 2026-03-23 |
| [TASK-105](./TASK-105_Legacy_Flat_List_Tools_Pagination_Compatibility.md) | **Legacy-Flat List Tools Pagination Compatibility** | 🟡 Medium | 2026-03-23 |
| [TASK-104](./TASK-104_Model_Facing_Workflow_Confirmation.md) | **Model-Facing Workflow Confirmation Boundary** | 🟡 Medium | 2026-03-23 |
| [TASK-094](./TASK-094_Code_Mode_Exploration.md) | **Code Mode Exploration for Large-Scale Orchestration** | 🟡 Medium | 2026-03-23 |
| [TASK-083](./TASK-083_FastMCP_3x_Platform_Migration.md) | **FastMCP 3.x Platform Migration** | 🔴 High | 2026-03-23 |
| [TASK-103](./TASK-103_Coverage_Expansion_For_Scene_Workflow_Catalog_Vector_Store_And_RPC.md) | **Coverage Expansion for Scene MCP Area, Workflow Catalog, Lance Store, and RPC Server** | 🟡 Medium | 2026-03-23 |
| [TASK-102](./TASK-102_Coverage_Expansion_For_Extraction_System_And_Scripts.md) | **Coverage Expansion for Extraction Handler, System MCP Area, and Tooling Scripts** | 🟡 Medium | 2026-03-23 |
| [TASK-101](./TASK-101_Coverage_Expansion_For_Tooling_And_MCP_Areas.md) | **Coverage Expansion for Tooling Scripts, Addon Bootstrap, and MCP Areas** | 🟡 Medium | 2026-03-23 |
| [TASK-100](./TASK-100_Router_Metadata_Schema_Alignment.md) | **Router Metadata Schema Alignment for Pre-commit Validation** | 🔴 High | 2026-03-22 |
| [TASK-092](./TASK-092_Server_Side_Sampling_Assistants.md) | **Server-Side Sampling Assistants** | 🟡 Medium | 2026-03-22 |
| [TASK-095](./TASK-095_LaBSE_Semantic_Layer_Boundaries.md) | **LaBSE Semantic Layer Boundaries** | 🔴 High | 2026-03-22 |
| [TASK-090](./TASK-090_Prompt_Layer_and_Tool_Compatible_Prompts.md) | **Prompt Layer and Tool-Compatible Prompt Delivery** | 🟡 Medium | 2026-03-22 |
| [TASK-093](./TASK-093_Observability_Timeouts_and_Pagination.md) | **Observability, Timeouts, and Pagination** | 🟡 Medium | 2026-03-22 |
| [TASK-099](./TASK-099_FastMCP_Docket_Runtime_Alignment_and_Shims_Removal.md) | **FastMCP-Docket Runtime Alignment and Shims Removal** | 🔴 High | 2026-03-22 |
| [TASK-098](./TASK-098_Background_Task_Adoption_for_Import_Export.md) | **Background Task Adoption for Import and Export Operations** | 🔴 High | 2026-03-22 |
| [TASK-088](./TASK-088_Background_Tasks_and_Progress.md) | **Background Tasks and Progress for Heavy Blender Work** | 🔴 High | 2026-03-22 |
| [TASK-086](./TASK-086_LLM_Optimized_API_Surfaces.md) | **LLM-Optimized API Surfaces** | 🔴 High | 2026-03-22 |
| [TASK-084](./TASK-084_Dynamic_Tool_Discovery.md) | **Dynamic Tool Discovery for Large Catalogs** | 🔴 High | 2026-03-22 |
| [TASK-091](./TASK-091_Versioned_Client_Surfaces.md) | **Versioned Client Surfaces for Safe API Evolution** | 🔴 High | 2026-03-22 |
| [TASK-089](./TASK-089_Typed_Contracts_and_Structured_Responses.md) | **Typed Contracts and Structured Responses** | 🔴 High | 2026-03-22 |
| [TASK-087](./TASK-087_Structured_User_Elicitation.md) | **Structured User Elicitation for Missing Parameters** | 🔴 High | 2026-03-22 |
| [TASK-085](./TASK-085_Session_Adaptive_Tool_Visibility.md) | **Session-Adaptive Tool Visibility** | 🔴 High | 2026-03-22 |
| [TASK-097](./TASK-097_Transparent_Correction_Audit_and_Postconditions.md) | **Transparent Correction Audit and Postconditions** | 🔴 High | 2026-03-22 |
| [TASK-096](./TASK-096_Confidence_Policy_for_Auto_Correction.md) | **Confidence Policy for Auto-Correction** | 🔴 High | 2026-03-22 |
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

---

## 📚 Supplemental Document Index

The Kanban tables above track umbrella tasks and selected milestone entries. The index below covers additional task notes, bug-fix docs, and detailed core/tests/documentation slices that also live in this directory.

### Legacy And Reference Docs

| Document | Contains |
|---|---|
| [FASTMCP_3X_IMPLEMENTATION_MODEL](./FASTMCP_3X_IMPLEMENTATION_MODEL.md) | Shared implementation model for the FastMCP 3.x migration track |
| [TASK-013_Viewport_Output_Modes](./TASK-013_Viewport_Output_Modes.md) | Viewport output modes and Docker temp-file mapping |
| [TASK-014-15_Fix_Blender_Tool_Bugs](./TASK-014-15_Fix_Blender_Tool_Bugs.md) | Blender tool bug fixes for mode validation, boolean solver defaults, and edit-mode context |
| [TASK-055-FIX-2_Semantic_Matching_Improvements](./TASK-055-FIX-2_Semantic_Matching_Improvements.md) | Semantic matching improvements for `ModifierExtractor` |
| [TASK-055-FIX-3_ParameterStore_Context_Truncation](./TASK-055-FIX-3_ParameterStore_Context_Truncation.md) | ParameterStore context truncation bug fix |
| [TASK-055-FIX-4_Router_Workflow_Parameter_Passing](./TASK-055-FIX-4_Router_Workflow_Parameter_Passing.md) | Router workflow parameter passing bug fix |
| [TASK-055-FIX-5_Per_Step_Adaptation_Control](./TASK-055-FIX-5_Per_Step_Adaptation_Control.md) | Per-step adaptation control for workflow execution |
| [TASK-055-FIX-8_Computed_Parameters_Expression_Functions](./TASK-055-FIX-8_Computed_Parameters_Expression_Functions.md) | Reference for computed-parameter expression functions |
| [TASK-059_Expression_Evaluator_Logical_Operators](./TASK-059_Expression_Evaluator_Logical_Operators.md) | Logical and comparison operators for the expression evaluator |
| [TASK-061_Router_API_Alignment_and_Offline_Testing](./TASK-061_Router_API_Alignment_and_Offline_Testing.md) | Router / MCP API alignment, mega-tool rollout, and offline test stability |

### TASK-083 Detailed Docs

| Cluster | Files | Contains |
|---|---|---|
| `TASK-083-01` | [core](./TASK-083-01-01_Core_FastMCP_Dependency_Runtime_Audit.md), [tests](./TASK-083-01-02_Tests_FastMCP_Dependency_Runtime_Audit.md), [overview](./TASK-083-01_FastMCP_3x_Dependency_and_Runtime_Audit.md) | FastMCP 3.x dependency and runtime audit |
| `TASK-083-02` | [core](./TASK-083-02-01_Core_Provider_Component_Inventory.md), [tests](./TASK-083-02-02_Tests_Provider_Component_Inventory.md), [overview](./TASK-083-02_Provider_Based_Component_Inventory.md) | Provider-based component inventory |
| `TASK-083-03` | [surface profile settings and config](./TASK-083-03-01-01_Surface_Profile_Settings_and_Config.md), [server factory and bootstrap path](./TASK-083-03-01-02_Server_Factory_and_Bootstrap_Path.md), [core](./TASK-083-03-01_Core_Factory_Composition_Root.md), [tests](./TASK-083-03-02_Tests_Factory_Composition_Root.md), [overview](./TASK-083-03_Server_Factory_and_Composition_Root.md) | Server factory and composition root |
| `TASK-083-04` | [core](./TASK-083-04-01_Core_Transform_Pipeline_Baseline.md), [tests](./TASK-083-04-02_Tests_Transform_Pipeline_Baseline.md), [overview](./TASK-083-04_Transform_Pipeline_Baseline.md) | Transform pipeline baseline |
| `TASK-083-05` | [core](./TASK-083-05-01_Core_Context_Session_Execution_Bridge.md), [tests](./TASK-083-05-02_Tests_Context_Session_Execution_Bridge.md), [overview](./TASK-083-05_Context_Session_and_Execution_Bridge.md) | Context, session, and execution bridge |
| `TASK-083-06` | [core](./TASK-083-06-01_Core_Platform_Regression_Harness_Docs.md), [tests](./TASK-083-06-02_Tests_Platform_Regression_Harness_Docs.md), [overview](./TASK-083-06_Platform_Regression_Harness_and_Docs.md) | Platform regression harness and docs |

### TASK-084 Detailed Docs

| Cluster | Files | Contains |
|---|---|---|
| `TASK-084-01` | [capability manifest schema and tags](./TASK-084-01-01-01_Capability_Manifest_Schema_and_Tags.md), [inventory builder and enrichment](./TASK-084-01-01-02_Inventory_Builder_and_Enrichment.md), [core](./TASK-084-01-01_Core_Inventory_Normalization_Discovery_Taxonomy.md), [tests](./TASK-084-01-02_Tests_Inventory_Normalization_Discovery_Taxonomy.md), [overview](./TASK-084-01_Tool_Inventory_Normalization_and_Discovery_Taxonomy.md) | Public capability inventory and discovery taxonomy |
| `TASK-084-02` | [core](./TASK-084-02-01_Core_Search_Transform_Pinned_Entry.md), [tests](./TASK-084-02-02_Tests_Search_Transform_Pinned_Entry.md), [overview](./TASK-084-02_Search_Transform_and_Pinned_Entry_Surface.md) | Search transform and pinned entry surface |
| `TASK-084-03` | [core](./TASK-084-03-01_Core_Search_Document_Enrichment_Metadata.md), [tests](./TASK-084-03-02_Tests_Search_Document_Enrichment_Metadata.md), [overview](./TASK-084-03_Search_Document_Enrichment_from_Metadata_and_Docstrings.md) | Search document enrichment from metadata and docstrings |
| `TASK-084-04` | [core](./TASK-084-04-01_Core_Search_Execution_Router_Aware.md), [tests](./TASK-084-04-02_Tests_Search_Execution_Router_Aware.md), [overview](./TASK-084-04_Search_Execution_and_Router_Aware_Call_Path.md) | Search execution and router-aware call path |
| `TASK-084-05` | [core](./TASK-084-05-01_Core_Discovery_Tests_Benchmarks_Docs.md), [tests](./TASK-084-05-02_Tests_Discovery_Tests_Benchmarks_Docs.md), [overview](./TASK-084-05_Discovery_Tests_Benchmarks_and_Docs.md) | Discovery tests, benchmarks, and docs |

### TASK-085 Detailed Docs

| Cluster | Files | Contains |
|---|---|---|
| `TASK-085-01` | [core](./TASK-085-01-01_Core_Session_State_Capability.md), [tests](./TASK-085-01-02_Tests_Session_State_Capability.md), [overview](./TASK-085-01_Session_State_Model_and_Capability_Phases.md) | Session state model and capability phases |
| `TASK-085-02` | [visibility tags and manifest wiring](./TASK-085-02-01-01_Visibility_Tags_and_Manifest_Wiring.md), [visibility transform and policy engine](./TASK-085-02-01-02_Visibility_Transform_and_Policy_Engine.md), [core](./TASK-085-02-01_Core_Visibility_Engine_Tagged_Providers.md), [tests](./TASK-085-02-02_Tests_Visibility_Engine_Tagged_Providers.md), [overview](./TASK-085-02_Visibility_Policy_Engine_and_Tagged_Providers.md) | Visibility policy engine and tagged providers |
| `TASK-085-03` | [core](./TASK-085-03-01_Core_Router_Driven_Transitions.md), [tests](./TASK-085-03-02_Tests_Router_Driven_Transitions.md), [overview](./TASK-085-03_Router_Driven_Phase_Transitions.md) | Router-driven phase transitions |
| `TASK-085-04` | [core](./TASK-085-04-01_Core_Profiles_Guided_Presets.md), [tests](./TASK-085-04-02_Tests_Profiles_Guided_Presets.md), [overview](./TASK-085-04_Client_Profiles_and_Guided_Mode_Presets.md) | Client profiles and guided mode presets |
| `TASK-085-05` | [core](./TASK-085-05-01_Core_Visibility_Observability_Tests_Docs.md), [tests](./TASK-085-05-02_Tests_Visibility_Observability_Tests_Docs.md), [overview](./TASK-085-05_Visibility_Observability_Tests_and_Docs.md) | Visibility observability, tests, and docs |

### TASK-086 Detailed Docs

| Cluster | Files | Contains |
|---|---|---|
| `TASK-086-01` | [core](./TASK-086-01-01_Core_Public_Manifest_Naming_Conventions.md), [tests](./TASK-086-01-02_Tests_Public_Manifest_Naming_Conventions.md), [overview](./TASK-086-01_Public_Surface_Manifest_and_Naming_Conventions.md) | Public surface manifest and naming conventions |
| `TASK-086-02` | [core](./TASK-086-02-01_Core_Transform_Parameter_Aliasing.md), [tests](./TASK-086-02-02_Tests_Transform_Parameter_Aliasing.md), [overview](./TASK-086-02_Transform_Based_Tool_and_Parameter_Aliasing.md) | Transform-based tool and parameter aliasing |
| `TASK-086-03` | [core](./TASK-086-03-01_Core_LLM_Simplification_Hidden_Args.md), [tests](./TASK-086-03-02_Tests_LLM_Simplification_Hidden_Args.md), [overview](./TASK-086-03_LLM_First_Surface_Simplification_and_Hidden_Args.md) | LLM-first surface simplification and hidden args |
| `TASK-086-04` | [core](./TASK-086-04-01_Core_Compatibility_Adapters_Dispatcher_Alignment.md), [tests](./TASK-086-04-02_Tests_Compatibility_Adapters_Dispatcher_Alignment.md), [overview](./TASK-086-04_Compatibility_Adapters_and_Dispatcher_Alignment.md) | Compatibility adapters and dispatcher alignment |
| `TASK-086-05` | [core](./TASK-086-05-01_Core_QA_Examples_Documentation.md), [tests](./TASK-086-05-02_Tests_QA_Examples_Documentation.md), [overview](./TASK-086-05_Surface_QA_Examples_and_Documentation.md) | Surface QA, examples, and documentation |

### TASK-087 Detailed Docs

| Cluster | Files | Contains |
|---|---|---|
| `TASK-087-01` | [core](./TASK-087-01-01_Core_Elicitation_Domain_Response_Contracts.md), [tests](./TASK-087-01-02_Tests_Elicitation_Domain_Response_Contracts.md), [overview](./TASK-087-01_Elicitation_Domain_Model_and_Response_Contracts.md) | Clarification requirements model and MCP elicitation mapping |
| `TASK-087-02` | [core](./TASK-087-02-01_Core_Router_Parameter_Resolution_Integration.md), [tests](./TASK-087-02-02_Tests_Router_Parameter_Resolution_Integration.md), [overview](./TASK-087-02_Router_Parameter_Resolution_Integration.md) | Router parameter resolution integration |
| `TASK-087-03` | [core](./TASK-087-03-01_Core_Constrained_Choice_Multi_Select.md), [tests](./TASK-087-03-02_Tests_Constrained_Choice_Multi_Select.md), [overview](./TASK-087-03_Constrained_Choice_and_Multi_Select_Flows.md) | Constrained choice and multi-select flows |
| `TASK-087-04` | [core](./TASK-087-04-01_Core_Session_Persistence_Retry_Cancel.md), [tests](./TASK-087-04-02_Tests_Session_Persistence_Retry_Cancel.md), [overview](./TASK-087-04_Session_Persistence_Retry_and_Cancel_Semantics.md) | Session persistence, retry, and cancel semantics |
| `TASK-087-05` | [core](./TASK-087-05-01_Core_Fallback_Compatibility.md), [tests](./TASK-087-05-02_Tests_Fallback_Compatibility.md), [overview](./TASK-087-05_Tool_Only_Fallback_and_Compatibility_Mode.md) | Tool-only fallback and compatibility mode |
| `TASK-087-06` | [core](./TASK-087-06-01_Core_Elicitation_Tests_Docs.md), [tests](./TASK-087-06-02_Tests_Elicitation_Tests_Docs.md), [overview](./TASK-087-06_Elicitation_Tests_and_Docs.md) | Elicitation tests and docs |

### TASK-088 Detailed Docs

| Cluster | Files | Contains |
|---|---|---|
| `TASK-088-01` | [core](./TASK-088-01-01_Core_Heavy_Operation_Inventory_Candidacy.md), [tests](./TASK-088-01-02_Tests_Heavy_Operation_Inventory_Candidacy.md), [overview](./TASK-088-01_Heavy_Operation_Inventory_and_Task_Candidacy.md) | Heavy operation inventory and task candidacy |
| `TASK-088-02` | [core](./TASK-088-02-01_Core_Async_Bridge_Job_Registry.md), [tests](./TASK-088-02-02_Tests_Async_Bridge_Job_Registry.md), [overview](./TASK-088-02_Async_Task_Bridge_and_Job_Registry.md) | Async task bridge and job registry |
| `TASK-088-03` | [core](./TASK-088-03-01_Core_Progress_Cancellation_Result_Retrieval.md), [tests](./TASK-088-03-02_Tests_Progress_Cancellation_Result_Retrieval.md), [overview](./TASK-088-03_Progress_Cancellation_and_Result_Retrieval.md) | Progress, cancellation, and result retrieval |
| `TASK-088-04` | [addon job lifecycle primitives](./TASK-088-04-01-01_Addon_Job_Lifecycle_Primitives.md), [server RPC client and protocol](./TASK-088-04-01-02_Server_RPC_Client_and_Protocol.md), [core](./TASK-088-04-01_Core_RPC_Blender_Main_Thread.md), [tests](./TASK-088-04-02_Tests_RPC_Blender_Main_Thread.md), [overview](./TASK-088-04_RPC_and_Blender_Main_Thread_Adaptation.md) | RPC and Blender main-thread adaptation |
| `TASK-088-05` | [core](./TASK-088-05-01_Core_Background_Adoption_Imports_Renders.md), [tests](./TASK-088-05-02_Tests_Background_Adoption_Imports_Renders.md), [overview](./TASK-088-05_Background_Adoption_for_Imports_Renders_Extraction_and_Workflow_Import.md) | Background adoption for imports, renders, extraction, and workflow import |
| `TASK-088-06` | [core](./TASK-088-06-01_Core_Task_Mode_Operations_Docs.md), [tests](./TASK-088-06-02_Tests_Task_Mode_Operations_Docs.md), [overview](./TASK-088-06_Task_Mode_Tests_Operations_and_Docs.md) | Task mode tests, operations, and docs |

### TASK-089 Detailed Docs

| Cluster | Files | Contains |
|---|---|---|
| `TASK-089-01` | [core](./TASK-089-01-01_Core_Contract_Catalog_Response_Guidelines.md), [tests](./TASK-089-01-02_Tests_Contract_Catalog_Response_Guidelines.md), [overview](./TASK-089-01_Contract_Catalog_and_Response_Guidelines.md) | Contract catalog and response guidelines |
| `TASK-089-02` | [scene contract definitions](./TASK-089-02-01-01_Scene_Contract_Definitions.md), [handler and adapter integration](./TASK-089-02-01-02_Handler_and_Adapter_Integration.md), [core](./TASK-089-02-01_Core_Structured_Scene_Context_Inspection.md), [tests](./TASK-089-02-02_Tests_Structured_Scene_Context_Inspection.md), [overview](./TASK-089-02_Structured_Scene_Context_and_Inspection_Contracts.md) | Structured scene context and inspection contracts |
| `TASK-089-03` | [mesh contract envelopes and schemas](./TASK-089-03-01-01_Mesh_Contract_Envelopes_and_Schemas.md), [handler and paging integration](./TASK-089-03-01-02_Handler_and_Paging_Integration.md), [core](./TASK-089-03-01_Core_Structured_Mesh_Introspection_Contracts.md), [tests](./TASK-089-03-02_Tests_Structured_Mesh_Introspection_Contracts.md), [overview](./TASK-089-03_Structured_Mesh_Introspection_Contracts.md) | Structured mesh introspection contracts |
| `TASK-089-04` | [router contracts and execution report](./TASK-089-04-01-01_Router_Contracts_and_Execution_Report.md), [workflow catalog contracts](./TASK-089-04-01-02_Workflow_Catalog_Contracts.md), [core](./TASK-089-04-01_Core_Router_Workflow_Execution_Report.md), [tests](./TASK-089-04-02_Tests_Router_Workflow_Execution_Report.md), [overview](./TASK-089-04_Router_Workflow_and_Execution_Report_Contracts.md) | Router, workflow, and execution report contracts |
| `TASK-089-05` | [core](./TASK-089-05-01_Core_Adapter_Dual_Format_Delivery.md), [tests](./TASK-089-05-02_Tests_Adapter_Dual_Format_Delivery.md), [overview](./TASK-089-05_Adapter_Dual_Format_Delivery_Strategy.md) | Native structured-first delivery and compatibility strategy |
| `TASK-089-06` | [core](./TASK-089-06-01_Core_Contract_Tests_Schemas_Documentation.md), [tests](./TASK-089-06-02_Tests_Contract_Tests_Schemas_Documentation.md), [overview](./TASK-089-06_Contract_Tests_Schemas_and_Documentation.md) | Contract tests, schemas, and documentation |

### TASK-090 Detailed Docs

| Cluster | Files | Contains |
|---|---|---|
| `TASK-090-01` | [core](./TASK-090-01-01_Core_Prompt_Asset_Inventory_Taxonomy.md), [tests](./TASK-090-01-02_Tests_Prompt_Asset_Inventory_Taxonomy.md), [overview](./TASK-090-01_Prompt_Asset_Inventory_and_Taxonomy.md) | Prompt asset inventory and taxonomy |
| `TASK-090-02` | [core](./TASK-090-02-01_Core_FastMCP_Prompt_Provider_Rendering.md), [tests](./TASK-090-02-02_Tests_FastMCP_Prompt_Provider_Rendering.md), [overview](./TASK-090-02_FastMCP_Prompt_Provider_and_Rendering.md) | FastMCP prompt provider and rendering |
| `TASK-090-03` | [core](./TASK-090-03-01_Core_Prompts_Bridge.md), [tests](./TASK-090-03-02_Tests_Prompts_Bridge.md), [overview](./TASK-090-03_Prompts_As_Tools_Bridge.md) | Prompts as tools bridge |
| `TASK-090-04` | [core](./TASK-090-04-01_Core_Session_Aware_Prompt_Selection.md), [tests](./TASK-090-04-02_Tests_Session_Aware_Prompt_Selection.md), [overview](./TASK-090-04_Session_Aware_Prompt_Selection.md) | Session-aware prompt selection |
| `TASK-090-05` | [core](./TASK-090-05-01_Core_Prompt_QA_Examples_Documentation.md), [tests](./TASK-090-05-02_Tests_Prompt_QA_Examples_Documentation.md), [overview](./TASK-090-05_Prompt_QA_Examples_and_Documentation.md) | Prompt QA, examples, and documentation |

### TASK-091 Detailed Docs

| Cluster | Files | Contains |
|---|---|---|
| `TASK-091-01` | [core](./TASK-091-01-01_Core_Versioning_Matrix.md), [tests](./TASK-091-01-02_Tests_Versioning_Matrix.md), [overview](./TASK-091-01_Versioning_Policy_and_Surface_Matrix.md) | Versioning policy and surface matrix |
| `TASK-091-02` | [core](./TASK-091-02-01_Core_Shared_Providers_Component_Versions.md), [tests](./TASK-091-02-02_Tests_Shared_Providers_Component_Versions.md), [overview](./TASK-091-02_Shared_Providers_with_Component_Versions.md) | Shared providers with component versions |
| `TASK-091-03` | [core](./TASK-091-03-01_Core_Version_Filtered_Composition.md), [tests](./TASK-091-03-02_Tests_Version_Filtered_Composition.md), [overview](./TASK-091-03_Version_Filtered_Server_Composition.md) | Version-filtered server composition |
| `TASK-091-04` | [core](./TASK-091-04-01_Core_Selection_Bootstrap_Configuration.md), [tests](./TASK-091-04-02_Tests_Selection_Bootstrap_Configuration.md), [overview](./TASK-091-04_Client_Selection_and_Bootstrap_Configuration.md) | Client selection and bootstrap configuration |
| `TASK-091-05` | [core](./TASK-091-05-01_Core_Versioned_Tests_Documentation.md), [tests](./TASK-091-05-02_Tests_Versioned_Tests_Documentation.md), [overview](./TASK-091-05_Versioned_Surface_Tests_and_Documentation.md) | Versioned surface tests and documentation |

### TASK-092 Detailed Docs

| Cluster | Files | Contains |
|---|---|---|
| `TASK-092-01` | [core](./TASK-092-01-01_Core_Sampling_Assistant_Governance_Safety.md), [tests](./TASK-092-01-02_Tests_Sampling_Assistant_Governance_Safety.md), [overview](./TASK-092-01_Sampling_Assistant_Governance_and_Safety_Boundaries.md) | Sampling assistant governance and safety boundaries |
| `TASK-092-02` | [core](./TASK-092-02-01_Core_Assistant_Runner_Typed_Result.md), [tests](./TASK-092-02-02_Tests_Assistant_Runner_Typed_Result.md), [overview](./TASK-092-02_Assistant_Runner_with_Typed_Result_Wrappers.md) | Assistant runner with typed result wrappers |
| `TASK-092-03` | [core](./TASK-092-03-01_Core_Inspection_Summarizer_Repair_Suggester.md), [tests](./TASK-092-03-02_Tests_Inspection_Summarizer_Repair_Suggester.md), [overview](./TASK-092-03_Inspection_Summarizer_and_Repair_Suggester_Assistants.md) | Inspection summarizer and repair suggester assistants |
| `TASK-092-04` | [core](./TASK-092-04-01_Core_Router_Integration_Masking_Budget.md), [tests](./TASK-092-04-02_Tests_Router_Integration_Masking_Budget.md), [overview](./TASK-092-04_Router_Integration_Masking_and_Budget_Control.md) | Router integration, masking, and budget control |
| `TASK-092-05` | [core](./TASK-092-05-01_Core_Sampling_Assistant_Tests_Documentation.md), [tests](./TASK-092-05-02_Tests_Sampling_Assistant_Tests_Documentation.md), [overview](./TASK-092-05_Sampling_Assistant_Tests_and_Documentation.md) | Sampling assistant tests and documentation |

### TASK-093 Detailed Docs

| Cluster | Files | Contains |
|---|---|---|
| `TASK-093-01` | [core](./TASK-093-01-01_Core_Telemetry_OpenTelemetry_Bootstrap.md), [tests](./TASK-093-01-02_Tests_Telemetry_OpenTelemetry_Bootstrap.md), [overview](./TASK-093-01_Telemetry_Model_and_OpenTelemetry_Bootstrap.md) | Telemetry model and OpenTelemetry bootstrap |
| `TASK-093-02` | [platform timeout policy and config](./TASK-093-02-01-01_Platform_Timeout_Policy_and_Config.md), [RPC and addon timeout coordination](./TASK-093-02-01-02_RPC_and_Addon_Timeout_Coordination.md), [core](./TASK-093-02-01_Core_Timeout.md), [tests](./TASK-093-02-02_Tests_Timeout.md), [overview](./TASK-093-02_Tool_and_Task_Timeout_Policy.md) | Tool and task timeout policy |
| `TASK-093-03` | [core](./TASK-093-03-01_Core_Pagination_Rollout_Component_Data.md), [tests](./TASK-093-03-02_Tests_Pagination_Rollout_Component_Data.md), [overview](./TASK-093-03_Pagination_Rollout_for_Component_and_Data_Listings.md) | Pagination rollout for component and data listings |
| `TASK-093-04` | [core](./TASK-093-04-01_Core_Operational_Status_Diagnostics.md), [tests](./TASK-093-04-02_Tests_Operational_Status_Diagnostics.md), [overview](./TASK-093-04_Operational_Status_and_Diagnostics_Surface.md) | Operational status and diagnostics surface |
| `TASK-093-05` | [core](./TASK-093-05-01_Core_Operations_Tests_Documentation.md), [tests](./TASK-093-05-02_Tests_Operations_Tests_Documentation.md), [overview](./TASK-093-05_Operations_Tests_and_Documentation.md) | Operations tests and documentation |

### TASK-094 Detailed Docs

| Cluster | Files | Contains |
|---|---|---|
| `TASK-094-01` | [core](./TASK-094-01-01_Core_Code_Experiment_Design_Guardrails.md), [tests](./TASK-094-01-02_Tests_Code_Experiment_Design_Guardrails.md), [overview](./TASK-094-01_Code_Mode_Experiment_Design_and_Guardrails.md) | Code mode experiment design and guardrails |
| `TASK-094-02` | [core](./TASK-094-02-01_Core_Read_Code_Pilot.md), [tests](./TASK-094-02-02_Tests_Read_Code_Pilot.md), [overview](./TASK-094-02_Read_Only_Code_Mode_Pilot_Surface.md) | Read-only code mode pilot surface |
| `TASK-094-03` | [core](./TASK-094-03-01_Core_Evaluation_Harness_Benchmark_Scenarios.md), [tests](./TASK-094-03-02_Tests_Evaluation_Harness_Benchmark_Scenarios.md), [overview](./TASK-094-03_Evaluation_Harness_and_Benchmark_Scenarios.md) | Evaluation harness and benchmark scenarios |
| `TASK-094-04` | [core](./TASK-094-04-01_Core_Decision_Memo_Documentation.md), [tests](./TASK-094-04-02_Tests_Decision_Memo_Documentation.md), [overview](./TASK-094-04_Decision_Memo_and_Documentation.md) | Decision memo and documentation |

### TASK-095 Detailed Docs

| Cluster | Files | Contains |
|---|---|---|
| `TASK-095-01` | [core](./TASK-095-01-01_Core_Semantic_Responsibility_Code_Audit.md), [tests](./TASK-095-01-02_Tests_Semantic_Responsibility_Code_Audit.md), [overview](./TASK-095-01_Semantic_Responsibility_Policy_and_Code_Audit.md) | Semantic responsibility policy and code audit |
| `TASK-095-02` | [core](./TASK-095-02-01_Core_Discovery_Handoff_LaBSE_FastMCP.md), [tests](./TASK-095-02-02_Tests_Discovery_Handoff_LaBSE_FastMCP.md), [overview](./TASK-095-02_Discovery_Handoff_From_LaBSE_to_FastMCP_Search.md) | Discovery handoff from LaBSE to FastMCP Search |
| `TASK-095-03` | [core](./TASK-095-03-01_Core_Truth_Verification_Handoff_Inspection.md), [tests](./TASK-095-03-02_Tests_Truth_Verification_Handoff_Inspection.md), [overview](./TASK-095-03_Truth_and_Verification_Handoff_to_Inspection_Contracts.md) | Truth and verification handoff to inspection contracts |
| `TASK-095-04` | [core](./TASK-095-04-01_Core_Parameter_Memory_Workflow_Matching.md), [tests](./TASK-095-04-02_Tests_Parameter_Memory_Workflow_Matching.md), [overview](./TASK-095-04_Parameter_Memory_and_Workflow_Matching_Hardening.md) | Parameter memory and workflow matching hardening |
| `TASK-095-05` | [core](./TASK-095-05-01_Core_Boundary_Tests_Telemetry_Documentation.md), [tests](./TASK-095-05-02_Tests_Boundary_Tests_Telemetry_Documentation.md), [overview](./TASK-095-05_Boundary_Tests_Telemetry_and_Documentation.md) | Boundary tests, telemetry, and documentation |

### TASK-096 Detailed Docs

| Cluster | Files | Contains |
|---|---|---|
| `TASK-096-01` | [core](./TASK-096-01-01_Core_Correction_Taxonomy_Risk_Matrix.md), [tests](./TASK-096-01-02_Tests_Correction_Taxonomy_Risk_Matrix.md), [overview](./TASK-096-01_Correction_Taxonomy_and_Risk_Matrix.md) | Correction taxonomy and risk matrix |
| `TASK-096-02` | [core](./TASK-096-02-01_Core_Confidence_Scoring_Normalization_Engines.md), [tests](./TASK-096-02-02_Tests_Confidence_Scoring_Normalization_Engines.md), [overview](./TASK-096-02_Confidence_Scoring_Normalization_Across_Engines.md) | Confidence scoring normalization across engines |
| `TASK-096-03` | [core](./TASK-096-03-01_Core_Auto_Fix_Ask_Block.md), [tests](./TASK-096-03-02_Tests_Auto_Fix_Ask_Block.md), [overview](./TASK-096-03_Auto_Fix_Ask_Block_Policy_Engine.md) | Auto-fix, ask, block policy engine |
| `TASK-096-04` | [core](./TASK-096-04-01_Core_Medium_Confidence_Elicitation_Escalation.md), [tests](./TASK-096-04-02_Tests_Medium_Confidence_Elicitation_Escalation.md), [overview](./TASK-096-04_Medium_Confidence_Elicitation_and_Escalation.md) | Medium-confidence elicitation and escalation |
| `TASK-096-05` | [core](./TASK-096-05-01_Core_Session_Memory_Operator_Transparency.md), [tests](./TASK-096-05-02_Tests_Session_Memory_Operator_Transparency.md), [overview](./TASK-096-05_Session_Memory_and_Operator_Transparency.md) | Session memory and operator transparency |
| `TASK-096-06` | [core](./TASK-096-06-01_Core_Policy_Telemetry_Documentation.md), [tests](./TASK-096-06-02_Tests_Policy_Telemetry_Documentation.md), [overview](./TASK-096-06_Policy_Tests_Telemetry_and_Documentation.md) | Policy tests, telemetry, and documentation |

### TASK-097 Detailed Docs

| Cluster | Files | Contains |
|---|---|---|
| `TASK-097-01` | [core](./TASK-097-01-01_Core_Correction_Event_Audit_Schema.md), [tests](./TASK-097-01-02_Tests_Correction_Event_Audit_Schema.md), [overview](./TASK-097-01_Correction_Event_Model_and_Audit_Schema.md) | Correction event model and audit schema |
| `TASK-097-02` | [core](./TASK-097-02-01_Core_Router_Execution_Report_Pipeline.md), [tests](./TASK-097-02-02_Tests_Router_Execution_Report_Pipeline.md), [overview](./TASK-097-02_Router_Execution_Report_Pipeline.md) | Router execution report pipeline |
| `TASK-097-03` | [core](./TASK-097-03-01_Core_Postcondition_Registry_High_Risk.md), [tests](./TASK-097-03-02_Tests_Postcondition_Registry_High_Risk.md), [overview](./TASK-097-03_Postcondition_Registry_for_High_Risk_Fixes.md) | Postcondition registry for high-risk fixes |
| `TASK-097-04` | [postcondition mapping and verification trigger](./TASK-097-04-01-01_Postcondition_Mapping_and_Verification_Trigger.md), [inspection call bridge and result evaluation](./TASK-097-04-01-02_Inspection_Call_Bridge_and_Result_Evaluation.md), [core](./TASK-097-04-01_Core_Inspection_Verification_Integration.md), [tests](./TASK-097-04-02_Tests_Inspection_Verification_Integration.md), [overview](./TASK-097-04_Inspection_Based_Verification_Integration.md) | Inspection-based verification integration |
| `TASK-097-05` | [core](./TASK-097-05-01_Core_Audit_Exposure_MCP_Responses.md), [tests](./TASK-097-05-02_Tests_Audit_Exposure_MCP_Responses.md), [overview](./TASK-097-05_Audit_Exposure_in_MCP_Responses_and_Logs.md) | Audit exposure in MCP responses and logs |
| `TASK-097-06` | [core](./TASK-097-06-01_Core_Correction_Audit_Tests_Documentation.md), [tests](./TASK-097-06-02_Tests_Correction_Audit_Tests_Documentation.md), [overview](./TASK-097-06_Correction_Audit_Tests_and_Documentation.md) | Correction audit tests and documentation |

### TASK-098 Detailed Docs

| Cluster | Files | Contains |
|---|---|---|
| `TASK-098-01` | [addon export job adoption](./TASK-098-01-01-01_Addon_Export_Job_Adoption.md), [async export MCP entrypoints](./TASK-098-01-01-02_Async_Export_MCP_Entrypoints.md), [core](./TASK-098-01-01_Core_Export_Task_Mode_Adoption.md), [tests](./TASK-098-01-02_Tests_Export_Task_Mode_Adoption.md), [overview](./TASK-098-01_Export_Task_Mode_Adoption.md) | Export task-mode adoption |
| `TASK-098-02` | [addon import job adoption](./TASK-098-02-01-01_Addon_Import_Job_Adoption.md), [async import MCP entrypoints](./TASK-098-02-01-02_Async_Import_MCP_Entrypoints.md), [core](./TASK-098-02-01_Core_Import_Task_Mode_Adoption.md), [tests](./TASK-098-02-02_Tests_Import_Task_Mode_Adoption.md), [overview](./TASK-098-02_Import_Task_Mode_Adoption.md) | Import task-mode adoption |
| `TASK-098-03` | [core](./TASK-098-03-01_Core_Import_Image_As_Plane_Candidacy_Adoption.md), [tests](./TASK-098-03-02_Tests_Import_Image_As_Plane_Compatibility_Polish.md), [overview](./TASK-098-03_Import_Image_As_Plane_and_Compatibility_Polish.md) | `import_image_as_plane` candidacy and compatibility polish |
| `TASK-098-04` | [core](./TASK-098-04-01_Core_Operations_Rollback_Documentation.md), [tests](./TASK-098-04-02_Tests_Operations_Rollback_Documentation.md), [overview](./TASK-098-04_Operations_Rollback_and_Documentation.md) | Operations, rollback, and documentation |

### TASK-099 Detailed Docs

| Cluster | Files | Contains |
|---|---|---|
| `TASK-099-01` | [core](./TASK-099-01-01_Core_Runtime_Version_Audit.md), [tests](./TASK-099-01-02_Tests_Runtime_Reproduction_Harness.md), [overview](./TASK-099-01_Compatibility_Matrix_and_Reproduction_Harness.md) | Compatibility matrix and reproduction harness |
| `TASK-099-02` | [runtime version guards and error surfaces](./TASK-099-02-01-01_Runtime_Version_Guards_and_Error_Surfaces.md), [shims containment and instrumentation](./TASK-099-02-01-02_Shims_Containment_and_Instrumentation.md), [core](./TASK-099-02-01_Core_Runtime_Guards_and_Containment.md), [tests](./TASK-099-02-02_Tests_Runtime_Guards_and_Containment.md), [overview](./TASK-099-02_Runtime_Guards_and_Shim_Containment.md) | Runtime guards and shim containment |
| `TASK-099-03` | [FastMCP Docket version selection](./TASK-099-03-01-01_FastMCP_Docket_Version_Selection.md), [real task runtime validation](./TASK-099-03-01-02_Real_Task_Runtime_Validation.md), [core](./TASK-099-03-01_Core_Upstream_Version_Alignment.md), [tests](./TASK-099-03-02_Tests_Upstream_Version_Alignment.md), [overview](./TASK-099-03_Upstream_Version_Alignment_and_Validation.md) | Upstream version alignment and validation |
| `TASK-099-04` | [core](./TASK-099-04-01_Core_Shims_Removal.md), [tests](./TASK-099-04-02_Tests_Shims_Removal_and_Release_Documentation.md), [overview](./TASK-099-04_Shims_Removal_and_Release_Documentation.md) | Shim removal and release documentation |
