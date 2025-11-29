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

---

## 🎨 Material Tools (`material_`)
*Tools for managing materials and shaders.*

| Tool Name | Arguments | Description | Status |
|-----------|-----------|-------------|--------|
| `material_list` | `include_unassigned` (bool) | Lists all materials with shader parameters (Principled BSDF) and object assignment counts. | ✅ Done |
| `material_list_by_object` | `object_name` (str), `include_indices` (bool) | Lists material slots for a specific object. | ✅ Done |

---

## 🗺️ UV Tools (`uv_`)
*Tools for texture coordinate mapping operations.*

| Tool Name | Arguments | Description | Status |
|-----------|-----------|-------------|--------|
| `uv_list_maps` | `object_name` (str), `include_island_counts` (bool) | Lists UV maps for a mesh object with active flags and loop counts. | ✅ Done |

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

## 🛠 Planned / In Progress

### Mesh Editing (`mesh_`) - Phase 2 Continued
