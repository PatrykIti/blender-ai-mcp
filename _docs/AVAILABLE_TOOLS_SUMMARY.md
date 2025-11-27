# Available Tools Summary

This document lists all currently implemented tools available for the AI, grouped by domain.
For detailed architectural decisions, see `MODELING_TOOLS_ARCHITECTURE.md` and `SCENE_TOOLS_ARCHITECTURE.md`.

---

## 🏗️ Scene Tools (`scene_`)
*Tools for managing the scene graph, selection, and visualization.*

| Tool Name | Arguments | Description | Status |
|-----------|-----------|-------------|--------|
| `scene_list_objects` | *none* | Returns a list of all objects in the scene with their type and position. | ✅ Done |
| `scene_delete_object` | `name` (str) | Deletes the specified object. | ✅ Done |
| `scene_clean_scene` | `keep_lights_and_cameras` (bool) | Clears the scene. Can perform a "hard reset" if set to False. | ✅ Done |
| `scene_duplicate_object` | `name` (str), `translation` ([x,y,z]) | Duplicates an object and optionally moves it. | ✅ Done |
| `scene_set_active_object` | `name` (str) | Sets the active object (crucial for modifiers). | ✅ Done |
| `scene_get_mode` | *none* | Reports current Blender mode, active object, and selected objects. | ✅ Done |
| `scene_list_selection` | *none* | Lists selected objects (Object Mode) plus vertex/edge/face counts in Edit Mode. | ✅ Done |
| `scene_inspect_object` | `name` (str) | Detailed report about a single object (transform, collections, modifiers, materials, mesh stats). | ✅ Done |
| `scene_get_viewport` | `width`, `height`, `shading`, `camera_name`, `focus_target`, `output_mode` | Returns a visual preview of the scene (OpenGL Render) with selectable output mode (IMAGE/BASE64/FILE/MARKDOWN). | ✅ Done |
| `scene_create_light` | `type`, `energy`, `color`, `location` | Creates a light source. | ✅ Done |
| `scene_create_camera` | `location`, `rotation`, `lens` | Creates a camera. | ✅ Done |
| `scene_create_empty` | `type`, `size`, `location` | Creates an Empty object. | ✅ Done |
| `scene_snapshot_state` | `include_mesh_stats`, `include_materials` | Captures a JSON snapshot of scene state with SHA256 hash. | ✅ Done |
| `scene_compare_snapshot` | `baseline_snapshot`, `target_snapshot`, `ignore_minor_transforms` | Compares two snapshots and returns diff summary. | ✅ Done |

---

## 📦 Collection Tools (`collection_`)
*Tools for managing Blender collections (organizational containers).*

| Tool Name | Arguments | Description | Status |
|-----------|-----------|-------------|--------|
| `collection_list` | `include_objects` (bool) | Lists all collections with hierarchy, object counts, and visibility flags. | ✅ Done |

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
| `mesh_select_all` | `deselect` (bool) | Selects/Deselects all geometry. | ✅ Done |
| `mesh_delete_selected` | `type` (VERT/EDGE/FACE) | Deletes selected elements. | ✅ Done |
| `mesh_select_by_index` | `indices`, `type`, `selection_mode` | Selects elements by index. | ✅ Done |
| `mesh_extrude_region` | `move` | Extrudes selected region. | ✅ Done |
| `mesh_fill_holes` | *none* | Fills holes (F key). | ✅ Done |
| `mesh_bevel` | `offset`, `segments` | Bevels selected edges. | ✅ Done |
| `mesh_loop_cut` | `number_cuts` | Adds topology (subdivide). | ✅ Done |
| `mesh_inset` | `thickness` | Insets faces. | ✅ Done |

---

## 🛠 Planned / In Progress

### Mesh Editing (`mesh_`) - Phase 2 Continued
- [ ] `mesh_boolean`
- [ ] `mesh_merge_by_distance`