# Available Tools Summary

This document lists all currently implemented tools available for the AI, grouped by domain.
For detailed architectural decisions, see `MODELING_TOOLS_ARCHITECTURE.md` and `SCENE_TOOLS_ARCHITECTURE.md`.

---

## 🧠 LLM Context Optimization - Mega Tools

> **Unified tools that consolidate multiple related operations to reduce LLM context usage.**
> Original tools are kept as internal functions and routed via mega tools.

| Mega Tool | Actions | Replaces | Status |
|-----------|---------|----------|--------|
| `scene_context` | `mode`, `selection` | `scene_get_mode`, `scene_list_selection` | ✅ Done |
| `scene_create` | `light`, `camera`, `empty` | `scene_create_light`, `scene_create_camera`, `scene_create_empty` | ✅ Done |
| `scene_inspect` | `object`, `topology`, `modifiers`, `materials` | `scene_inspect_object`, `scene_inspect_mesh_topology`, `scene_inspect_modifiers`, `scene_inspect_material_slots` | ✅ Done |
| `mesh_select` | `all`, `none`, `linked`, `more`, `less`, `boundary` | `mesh_select_all`, `mesh_select_linked`, `mesh_select_more`, `mesh_select_less`, `mesh_select_boundary` | ✅ Done |
| `mesh_select_targeted` | `by_index`, `loop`, `ring`, `by_location` | `mesh_select_by_index`, `mesh_select_loop`, `mesh_select_ring`, `mesh_select_by_location` | ✅ Done |

**Total Savings:** 18 tools → 5 mega tools (**-13 definitions** for LLM context)

---

## 🏗️ Scene Tools (`scene_`)
*Tools for managing the scene graph, selection, and visualization.*

| Tool Name | Arguments | Description | Status |
|-----------|-----------|-------------|--------|
| `scene_context` | `action` (mode/selection) | **MEGA TOOL** - Quick context queries (mode, selection state). | ✅ Done |
| `scene_create` | `action` (light/camera/empty), params | **MEGA TOOL** - Creates scene helper objects (lights, cameras, empties). | ✅ Done |
| `scene_inspect` | `action` (object/topology/modifiers/materials), params | **MEGA TOOL** - Detailed inspection queries for objects and scene. | ✅ Done |
| `scene_list_objects` | *none* | Returns a list of all objects in the scene with their type and position. | ✅ Done |
| `scene_delete_object` | `name` (str) | Deletes the specified object. | ✅ Done |
| `scene_clean_scene` | `keep_lights_and_cameras` (bool) | Clears the scene. Can perform a "hard reset" if set to False. | ✅ Done |
| `scene_duplicate_object` | `name` (str), `translation` ([x,y,z]) | Duplicates an object and optionally moves it. | ✅ Done |
| `scene_set_active_object` | `name` (str) | Sets the active object (crucial for modifiers). | ✅ Done |
| `scene_get_viewport` | `width`, `height`, `shading`, `camera_name`, `focus_target`, `output_mode` | Returns a visual preview of the scene (OpenGL Render) with selectable output mode (IMAGE/BASE64/FILE/MARKDOWN). | ✅ Done |
| `scene_snapshot_state` | `include_mesh_stats`, `include_materials` | Captures a JSON snapshot of scene state with SHA256 hash. | ✅ Done |
| `scene_compare_snapshot` | `baseline_snapshot`, `target_snapshot`, `ignore_minor_transforms` | Compares two snapshots and returns diff summary. | ✅ Done |
| `scene_set_mode` | `mode` | Sets interaction mode (OBJECT, EDIT, SCULPT, etc.). | ✅ Done |

**Deprecated (now internal, use mega tools):**
- ~~`scene_get_mode`~~ → Use `scene_context(action="mode")`
- ~~`scene_list_selection`~~ → Use `scene_context(action="selection")`
- ~~`scene_create_light`~~ → Use `scene_create(action="light", ...)`
- ~~`scene_create_camera`~~ → Use `scene_create(action="camera", ...)`
- ~~`scene_create_empty`~~ → Use `scene_create(action="empty", ...)`
- ~~`scene_inspect_object`~~ → Use `scene_inspect(action="object", ...)`
- ~~`scene_inspect_mesh_topology`~~ → Use `scene_inspect(action="topology", ...)`
- ~~`scene_inspect_modifiers`~~ → Use `scene_inspect(action="modifiers", ...)`
- ~~`scene_inspect_material_slots`~~ → Use `scene_inspect(action="materials", ...)`

---

## 📦 Collection Tools (`collection_`)
*Tools for managing Blender collections (organizational containers).*

| Tool Name | Arguments | Description | Status |
|-----------|-----------|-------------|--------|
| `collection_list` | `include_objects` (bool) | Lists all collections with hierarchy, object counts, and visibility flags. | ✅ Done |
| `collection_list_objects` | `collection_name` (str), `recursive` (bool), `include_hidden` (bool) | Lists objects within specified collection, optionally recursive. | ✅ Done |
| `collection_manage` | `action` (create/delete/rename/move_object/link_object/unlink_object), `collection_name`, `new_name`, `parent_name`, `object_name` | Manages collections: create, delete, rename, and move/link/unlink objects between collections. | ✅ Done |

---

## 🎨 Material Tools (`material_`)
*Tools for managing materials and shaders.*

| Tool Name | Arguments | Description | Status |
|-----------|-----------|-------------|--------|
| `material_list` | `include_unassigned` (bool) | Lists all materials with shader parameters (Principled BSDF) and object assignment counts. | ✅ Done |
| `material_list_by_object` | `object_name` (str), `include_indices` (bool) | Lists material slots for a specific object. | ✅ Done |
| `material_create` | `name`, `base_color`, `metallic`, `roughness`, `emission_color`, `emission_strength`, `alpha` | Creates new PBR material with Principled BSDF shader. | ✅ Done |
| `material_assign` | `material_name`, `object_name`, `slot_index`, `assign_to_selection` | Assigns material to object or selected faces (Edit Mode). | ✅ Done |
| `material_set_params` | `material_name`, `base_color`, `metallic`, `roughness`, etc. | Modifies existing material parameters. | ✅ Done |
| `material_set_texture` | `material_name`, `texture_path`, `input_name`, `color_space` | Binds image texture to material input (supports Normal maps). | ✅ Done |

---

## 🗺️ UV Tools (`uv_`)
*Tools for texture coordinate mapping operations.*

| Tool Name | Arguments | Description | Status |
|-----------|-----------|-------------|--------|
| `uv_list_maps` | `object_name` (str), `include_island_counts` (bool) | Lists UV maps for a mesh object with active flags and loop counts. | ✅ Done |
| `uv_unwrap` | `object_name`, `method`, `angle_limit`, `island_margin`, `scale_to_bounds` | Unwraps selected faces to UV space using projection methods (SMART_PROJECT, CUBE, CYLINDER, SPHERE, UNWRAP). | ✅ Done |
| `uv_pack_islands` | `object_name`, `margin`, `rotate`, `scale` | Packs UV islands for optimal texture space usage. | ✅ Done |
| `uv_create_seam` | `object_name`, `action` | Marks or clears UV seams on selected edges ('mark' or 'clear'). | ✅ Done |

---

## 🧊 Modeling Tools (`modeling_`)
*Object-level geometry operations (non-destructive or container management).*

| Tool Name | Arguments | Description | Status |
|-----------|-----------|-------------|--------|
| `modeling_create_primitive` | `primitive_type`, `size/radius`, `location`, `rotation` | Creates basic shapes (Cube, Sphere, Cylinder, Plane, Cone, Monkey). | ✅ Done |
| `modeling_transform_object` | `name`, `location`, `rotation`, `scale` | Moves, rotates, or scales an object. | ✅ Done |
| `modeling_add_modifier` | `name`, `modifier_type`, `properties` | Adds a modifier (e.g., Bevel, Subsurf) to an object. | ✅ Done |
| `modeling_apply_modifier` | `name`, `modifier_name` | Applies (finalizes) a modifier permanently to the mesh. | ✅ Done |
| `modeling_list_modifiers` | `name` | Lists all modifiers on an object. | ✅ Done |
| `modeling_convert_to_mesh` | `name` | Converts Curve/Text/Surface objects to Mesh. | ✅ Done |
| `modeling_join_objects` | `object_names` (list) | Joins multiple objects into one mesh. | ✅ Done |
| `modeling_separate_object` | `name`, `type` (LOOSE/SELECTED/MATERIAL) | Separates a mesh into multiple objects. | ✅ Done |
| `modeling_set_origin` | `name`, `type` (GEOMETRY/CURSOR/CENTER_OF_MASS) | Sets the object's origin point. | ✅ Done |

---

## 🕸️ Mesh Tools (`mesh_`) - Edit Mode
*Low-level geometry manipulation (vertices, edges, faces).*

| Tool Name | Arguments | Description | Status |
|-----------|-----------|-------------|--------|
| `mesh_select` | `action` (all/none/linked/more/less/boundary) | **MEGA TOOL** - Simple selection operations. | ✅ Done |
| `mesh_select_targeted` | `action` (by_index/loop/ring/by_location), params | **MEGA TOOL** - Targeted selection operations with parameters. | ✅ Done |
| `mesh_delete_selected` | `type` (VERT/EDGE/FACE) | Deletes selected elements. | ✅ Done |
| `mesh_extrude_region` | `move` | Extrudes selected region. | ✅ Done |
| `mesh_fill_holes` | *none* | Fills holes (F key). | ✅ Done |
| `mesh_bevel` | `offset`, `segments` | Bevels selected edges. | ✅ Done |
| `mesh_loop_cut` | `number_cuts` | Adds topology (subdivide). | ✅ Done |
| `mesh_inset` | `thickness` | Insets faces. | ✅ Done |
| `mesh_boolean` | `operation`, `solver` | Boolean operation (Unselected - Selected). | ✅ Done |
| `mesh_merge_by_distance` | `distance` | Merges vertices within threshold distance. | ✅ Done |
| `mesh_subdivide` | `number_cuts`, `smoothness` | Subdivides selected geometry. | ✅ Done |
| `mesh_smooth` | `iterations`, `factor` | Smooths selected vertices. | ✅ Done |
| `mesh_flatten` | `axis` | Flattens selected vertices to plane. | ✅ Done |
| `mesh_list_groups` | `object_name`, `group_type` | Lists vertex groups or face maps/attributes. | ✅ Done |
| `mesh_get_vertex_data` | `object_name`, `selected_only` | Returns vertex positions/selection states. 🔴 CRITICAL | ✅ Done |
| `mesh_randomize` | `amount`, `uniform`, `normal`, `seed` | Randomizes vertex positions for organic surfaces. | ✅ Done |
| `mesh_shrink_fatten` | `value` | Moves vertices along their normals (inflate/deflate). | ✅ Done |
| `mesh_create_vertex_group` | `object_name`, `name` | Creates a new vertex group on mesh object. | ✅ Done |
| `mesh_assign_to_group` | `object_name`, `group_name`, `weight` | Assigns selected vertices to vertex group. | ✅ Done |
| `mesh_remove_from_group` | `object_name`, `group_name` | Removes selected vertices from vertex group. | ✅ Done |
| `mesh_bisect` | `plane_co`, `plane_no`, `clear_inner`, `clear_outer`, `fill` | Cuts mesh along a plane. | ✅ Done |
| `mesh_edge_slide` | `value` | Slides selected edges along mesh topology. | ✅ Done |
| `mesh_vert_slide` | `value` | Slides selected vertices along connected edges. | ✅ Done |
| `mesh_triangulate` | *none* | Converts selected faces to triangles. | ✅ Done |
| `mesh_remesh_voxel` | `voxel_size`, `adaptivity` | Remeshes object using Voxel algorithm (Object Mode). | ✅ Done |
| `mesh_transform_selected` | `translate`, `rotate`, `scale`, `pivot` | Transforms selected geometry (move/rotate/scale). 🔴 CRITICAL | ✅ Done |
| `mesh_bridge_edge_loops` | `number_cuts`, `interpolation`, `smoothness`, `twist` | Bridges two edge loops with faces. | ✅ Done |
| `mesh_duplicate_selected` | `translate` | Duplicates selected geometry within the same mesh. | ✅ Done |
| `mesh_spin` | `steps`, `angle`, `axis`, `center`, `dupli` | Spins/lathes selected geometry around an axis. | ✅ Done |
| `mesh_screw` | `steps`, `turns`, `axis`, `center`, `offset` | Creates spiral/screw geometry from selected profile. | ✅ Done |
| `mesh_add_vertex` | `position` | Adds a single vertex at the specified position. | ✅ Done |
| `mesh_add_edge_face` | *none* | Creates edge or face from selected vertices. | ✅ Done |
| `mesh_edge_crease` | `crease_value` | Sets crease weight on selected edges (0.0-1.0) for Subdivision Surface control. | ✅ Done |
| `mesh_bevel_weight` | `weight` | Sets bevel weight on selected edges (0.0-1.0) for selective beveling. | ✅ Done |
| `mesh_mark_sharp` | `action` (mark/clear) | Marks or clears sharp edges for Auto Smooth and Edge Split. | ✅ Done |
| `mesh_dissolve` | `dissolve_type` (limited/verts/edges/faces), `angle_limit`, `use_face_split`, `use_boundary_tear` | Dissolves geometry while preserving shape (cleanup). | ✅ Done |
| `mesh_tris_to_quads` | `face_threshold`, `shape_threshold` | Converts triangles to quads based on angle thresholds. | ✅ Done |
| `mesh_normals_make_consistent` | `inside` | Recalculates normals to face consistently outward (or inward). | ✅ Done |
| `mesh_decimate` | `ratio`, `use_symmetry`, `symmetry_axis` | Reduces polycount while preserving shape. | ✅ Done |
| `mesh_knife_project` | `cut_through` | Projects cut from selected geometry (requires view angle). | ✅ Done |
| `mesh_rip` | `use_fill` | Rips (tears) geometry at selected vertices. | ✅ Done |
| `mesh_split` | *none* | Splits selection from mesh (disconnects without separating). | ✅ Done |
| `mesh_edge_split` | *none* | Splits mesh at selected edges (creates seams). | ✅ Done |

**Deprecated (now internal, use mega tools):**
- ~~`mesh_select_all`~~ → Use `mesh_select(action="all")` or `mesh_select(action="none")`
- ~~`mesh_select_linked`~~ → Use `mesh_select(action="linked")`
- ~~`mesh_select_more`~~ → Use `mesh_select(action="more")`
- ~~`mesh_select_less`~~ → Use `mesh_select(action="less")`
- ~~`mesh_select_boundary`~~ → Use `mesh_select(action="boundary")`
- ~~`mesh_select_by_index`~~ → Use `mesh_select_targeted(action="by_index", ...)`
- ~~`mesh_select_loop`~~ → Use `mesh_select_targeted(action="loop", ...)`
- ~~`mesh_select_ring`~~ → Use `mesh_select_targeted(action="ring", ...)`
- ~~`mesh_select_by_location`~~ → Use `mesh_select_targeted(action="by_location", ...)`

---

## 〰️ Curve Tools (`curve_`)
*Tools for creating and managing curve objects.*

| Tool Name | Arguments | Description | Status |
|-----------|-----------|-------------|--------|
| `curve_create` | `curve_type` (BEZIER/NURBS/PATH/CIRCLE), `location` | Creates a curve primitive object. | ✅ Done |
| `curve_to_mesh` | `object_name` | Converts a curve object to mesh geometry. | ✅ Done |

---

## 📤 Export Tools (`export_`)
*Tools for exporting scene or objects to various 3D file formats.*

| Tool Name | Arguments | Description | Status |
|-----------|-----------|-------------|--------|
| `export_glb` | `filepath`, `export_selected`, `export_animations`, `export_materials`, `apply_modifiers` | Exports to GLB/GLTF format (web, game engines). | ✅ Done |
| `export_fbx` | `filepath`, `export_selected`, `export_animations`, `apply_modifiers`, `mesh_smooth_type` | Exports to FBX format (industry standard). | ✅ Done |
| `export_obj` | `filepath`, `export_selected`, `apply_modifiers`, `export_materials`, `export_uvs`, `export_normals`, `triangulate` | Exports to OBJ format (universal mesh). | ✅ Done |

---

## 🎨 Sculpt Tools (`sculpt_`)
*Tools for Sculpt Mode operations (organic shape manipulation).*

| Tool Name | Arguments | Description | Status |
|-----------|-----------|-------------|--------|
| `sculpt_auto` | `operation` (smooth/inflate/flatten/sharpen), `strength`, `iterations`, `use_symmetry`, `symmetry_axis` | High-level sculpt operation using mesh filters. Applies to entire mesh. | ✅ Done |
| `sculpt_brush_smooth` | `location`, `radius`, `strength` | Sets up smooth brush at specified location. | ✅ Done |
| `sculpt_brush_grab` | `from_location`, `to_location`, `radius`, `strength` | Sets up grab brush for moving geometry. | ✅ Done |
| `sculpt_brush_crease` | `location`, `radius`, `strength`, `pinch` | Sets up crease brush for creating sharp lines. | ✅ Done |

---

## ⚙️ System Tools (`system_`)
*System-level operations for mode switching, undo/redo, and file management.*

| Tool Name | Arguments | Description | Status |
|-----------|-----------|-------------|--------|
| `system_set_mode` | `mode` (str), `object_name` (str, optional) | Switches Blender mode (OBJECT/EDIT/SCULPT/POSE/...) with optional object selection. | ✅ Done |
| `system_undo` | `steps` (int, default 1) | Undoes last operation(s), max 10 steps per call. | ✅ Done |
| `system_redo` | `steps` (int, default 1) | Redoes previously undone operation(s), max 10 steps per call. | ✅ Done |
| `system_save_file` | `filepath` (str, optional), `compress` (bool) | Saves current .blend file. Auto-generates temp path if unsaved. | ✅ Done |
| `system_new_file` | `load_ui` (bool) | Creates new file (resets scene to startup). | ✅ Done |
| `system_snapshot` | `action` (save/restore/list/delete), `name` (str, optional) | Manages quick save/restore checkpoints in temp directory. | ✅ Done |

---

## 🔥 Baking Tools (`bake_`)
*Texture baking operations using Cycles renderer. Critical for game development workflows.*

| Tool Name | Arguments | Description | Status |
|-----------|-----------|-------------|--------|
| `bake_normal_map` | `object_name`, `output_path`, `resolution`, `high_poly_source`, `cage_extrusion`, `margin`, `normal_space` | Bakes normal map from geometry or high-poly to low-poly. Supports TANGENT/OBJECT space. | ✅ Done |
| `bake_ao` | `object_name`, `output_path`, `resolution`, `samples`, `distance`, `margin` | Bakes ambient occlusion map with configurable ray distance and samples. | ✅ Done |
| `bake_combined` | `object_name`, `output_path`, `resolution`, `samples`, `margin`, `use_pass_direct`, `use_pass_indirect`, `use_pass_color` | Bakes full render (material + lighting) to texture with configurable passes. | ✅ Done |
| `bake_diffuse` | `object_name`, `output_path`, `resolution`, `margin` | Bakes diffuse/albedo color only (no lighting). | ✅ Done |

**Requirements:**
- Object must have UV map (use `uv_unwrap` first)
- Cycles renderer (auto-switched)
- For high-to-low baking: both high-poly and low-poly objects

---

## 🛠 Planned / In Progress

*(All tasks completed!)*
