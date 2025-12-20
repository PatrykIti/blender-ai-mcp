# MCP Server Documentation

Documentation for the MCP Server (Client Side).

## 📚 Topic Index

- **[Clean Architecture](./clean_architecture.md)**
  - Detailed description of layers and control flow (DI).
  - Dependency separation principles implemented in version 0.1.5.

## 🚀 Running (Docker)

The server can be run in a Docker container for environment isolation.

### 1. Build Image
```bash
docker build -t blender-ai-mcp .
```

### 2. Run
To allow the container server to connect to Blender on the host, configure the network properly.

**MacOS / Windows:**
```bash
docker run -i --rm -e BLENDER_RPC_HOST=host.docker.internal blender-ai-mcp
```

**Linux:**
```bash
docker run -i --rm --network host -e BLENDER_RPC_HOST=127.0.0.1 blender-ai-mcp
```

*(The `-i` flag is crucial for the interactive stdio communication used by MCP)*.

## 🛠 Available Tools

### 🧠 Mega Tools (LLM Context Optimization)

Unified tools that consolidate multiple related operations to reduce LLM context usage.

| Mega Tool | Actions | Description |
|-----------|---------|-------------|
| `scene_context` | `mode`, `selection` | Quick context queries (mode, selection state). |
| `scene_create` | `light`, `camera`, `empty` | Creates scene helper objects. |
| `scene_inspect` | `object`, `topology`, `modifiers`, `materials`, `constraints`, `modifier_data` | Detailed inspection queries for objects. |
| `mesh_select` | `all`, `none`, `linked`, `more`, `less`, `boundary` | Simple selection operations. |
| `mesh_select_targeted` | `by_index`, `loop`, `ring`, `by_location` | Targeted selection with parameters. |

**Total:** 18 tools → 5 mega tools (**-13 definitions** for LLM context)

### Scene Tools
Managing objects at the scene level.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `scene_list_objects` | *none* | Returns a list of all objects in the scene with their type and position. |
| `scene_delete_object` | `name` (str) | Deletes the specified object. Returns error if object does not exist. |
| `scene_clean_scene` | `keep_lights_and_cameras` (bool, default True) | Deletes objects from scene. If `True`, preserves cameras and lights. If `False`, cleans the project completely ("hard reset"). |
| `scene_duplicate_object` | `name` (str), `translation` ([x,y,z]) | Duplicates an object and optionally moves it. |
| `scene_set_active_object` | `name` (str) | Sets the active object (crucial for context-dependent operations). |
| `scene_set_mode` | `mode` (str) | Sets interaction mode (OBJECT, EDIT, SCULPT, etc.). |
| `scene_snapshot_state` | `include_mesh_stats` (bool), `include_materials` (bool) | Captures a structured JSON snapshot of scene state with SHA256 hash for change detection. |
| `scene_compare_snapshot` | `baseline_snapshot` (str), `target_snapshot` (str), `ignore_minor_transforms` (float) | Compares two snapshots and returns diff summary (added/removed/modified objects). |
| `scene_get_viewport` | `width` (int), `height` (int), `shading` (str), `camera_name` (str), `focus_target` (str), `output_mode` (str) | Returns a rendered image. `shading`: WIREFRAME/SOLID/MATERIAL. `camera_name`: specific cam or "USER_PERSPECTIVE". `focus_target`: object to frame. `output_mode`: IMAGE (default Image resource), BASE64 (raw string), FILE (host-visible path), MARKDOWN (inline preview + path). |
| `scene_get_custom_properties` | `object_name` (str) | Gets custom properties (metadata) from an object. Returns object_name, property_count, and properties dict. |
| `scene_set_custom_property` | `object_name` (str), `property_name` (str), `property_value` (str/int/float/bool), `delete` (bool) | Sets or deletes a custom property on an object. |
| `scene_get_hierarchy` | `object_name` (str, optional), `include_transforms` (bool) | Gets parent-child hierarchy for specific object or full scene tree. |
| `scene_get_bounding_box` | `object_name` (str), `world_space` (bool) | Gets bounding box corners, min/max, center, dimensions, and volume. |
| `scene_get_origin_info` | `object_name` (str) | Gets origin (pivot point) information relative to geometry and bounding box. |
| `scene_get_constraints` | `object_name` (str), `include_bones` (bool) | Returns object (and optional bone) constraints. |

> **Note:** Tools like `scene_get_mode`, `scene_list_selection`, `scene_inspect_*`, and `scene_create_*` have been consolidated into mega tools. Use `scene_context`, `scene_inspect`, and `scene_create` instead.

### Collection Tools
Organizational tools for managing Blender collections.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `collection_list` | `include_objects` (bool) | Lists all collections with hierarchy, object counts, and visibility flags. |
| `collection_list_objects` | `collection_name` (str), `recursive` (bool), `include_hidden` (bool) | Lists objects within a collection, optionally recursive through child collections. |
| `collection_manage` | `action` (create/delete/rename/move_object/link_object/unlink_object), `collection_name`, `new_name`, `parent_name`, `object_name` | Manages collections: create, delete, rename, and move/link/unlink objects between collections. |

### Material Tools
Material and shader management.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `material_list` | `include_unassigned` (bool) | Lists all materials with Principled BSDF parameters and object assignment counts. |
| `material_list_by_object` | `object_name` (str), `include_indices` (bool) | Lists material slots for a specific object. |
| `material_create` | `name`, `base_color`, `metallic`, `roughness`, `emission_color`, `emission_strength`, `alpha` | Creates new PBR material with Principled BSDF shader. |
| `material_assign` | `material_name`, `object_name`, `slot_index`, `assign_to_selection` | Assigns material to object or selected faces (Edit Mode). |
| `material_set_params` | `material_name`, `base_color`, `metallic`, `roughness`, `emission_color`, `emission_strength`, `alpha` | Modifies existing material parameters. |
| `material_set_texture` | `material_name`, `texture_path`, `input_name`, `color_space` | Binds image texture to material input (supports Normal maps). |
| `material_inspect_nodes` | `material_name` (str), `include_connections` (bool) | Inspects material shader node graph, returns nodes with types, inputs, outputs, and connections. |

### UV Tools
Texture coordinate mapping operations.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `uv_list_maps` | `object_name` (str), `include_island_counts` (bool) | Lists UV maps for a mesh object with active flags and loop counts. |
| `uv_unwrap` | `object_name` (str), `method` (str), `angle_limit` (float), `island_margin` (float), `scale_to_bounds` (bool) | Unwraps selected faces to UV space using projection methods (SMART_PROJECT, CUBE, CYLINDER, SPHERE, UNWRAP). |
| `uv_pack_islands` | `object_name` (str), `margin` (float), `rotate` (bool), `scale` (bool) | Packs UV islands for optimal texture space usage. |
| `uv_create_seam` | `object_name` (str), `action` (str) | Marks or clears UV seams on selected edges ('mark' or 'clear'). |

### Modeling Tools
Geometry creation and editing.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `modeling_create_primitive` | `primitive_type` (str), `size` (float), `location` ([x,y,z]), `rotation` ([x,y,z]) | Creates a simple 3D object (Cube, Sphere, Cylinder, Plane, Cone, Torus, Monkey). |
| `modeling_transform_object` | `name` (str), `location` (opt), `rotation` (opt), `scale` (opt) | Changes position, rotation, or scale of an existing object. |
| `modeling_add_modifier` | `name` (str), `modifier_type` (str), `properties` (dict) | Adds a modifier to an object (e.g., `SUBSURF`, `BEVEL`). |
| `modeling_apply_modifier` | `name` (str), `modifier_name` (str) | Applies a modifier, permanently changing the mesh geometry. |
| `modeling_convert_to_mesh` | `name` (str) | Converts a non-mesh object (e.g., Curve, Text, Surface) to a mesh. |
| `modeling_join_objects` | `object_names` (list[str]) | Joins multiple mesh objects into a single one. |
| `modeling_separate_object` | `name` (str), `type` (str) | Separates a mesh object into new objects (LOOSE, SELECTED, MATERIAL). |
| `modeling_set_origin` | `name` (str), `type` (str) | Sets the origin point of an object (e.g., ORIGIN_GEOMETRY_TO_CURSOR). |
| `modeling_list_modifiers` | `name` (str) | Lists all modifiers currently on the specified object. |
| `modeling_get_modifier_data` | `object_name` (str), `modifier_name` (str), `include_node_tree` (bool) | Returns full modifier properties (Geometry Nodes metadata optional). |
| `metaball_create` | `name`, `location`, `element_type`, `radius`, `resolution`, `threshold` | Creates a metaball object for organic blob shapes. |
| `metaball_add_element` | `metaball_name`, `element_type`, `location`, `radius`, `stiffness` | Adds element to existing metaball for merging. |
| `metaball_to_mesh` | `metaball_name`, `apply_resolution` | Converts metaball to mesh for editing. |
| `skin_create_skeleton` | `name`, `vertices`, `edges`, `location` | Creates skeleton mesh with Skin modifier for tubular structures. |
| `skin_set_radius` | `object_name`, `vertex_index`, `radius_x`, `radius_y` | Sets skin radius at vertices for varying thickness. |

### Mesh Tools (Edit Mode)
Low-level geometry manipulation.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `mesh_delete_selected` | `type` (str) | Deletes selected elements ('VERT', 'EDGE', 'FACE'). |
| `mesh_extrude_region` | `move` (list[float]) | Extrudes selected region and optionally translates it. |
| `mesh_fill_holes` | *none* | Creates faces from selection (F key). |
| `mesh_bevel` | `offset`, `segments` | Bevels selected geometry. |
| `mesh_loop_cut` | `number_cuts` | Adds cuts (subdivides) to selection. |
| `mesh_inset` | `thickness`, `depth` | Insets selected faces. |
| `mesh_boolean` | `operation`, `solver='EXACT'` | Boolean op (Unselected - Selected). Note: FAST solver removed in Blender 5.0+. |
| `mesh_merge_by_distance` | `distance` | Remove doubles / merge vertices. |
| `mesh_subdivide` | `number_cuts`, `smoothness` | Subdivides selected geometry. |
| `mesh_smooth` | `iterations`, `factor` | Smooths selected vertices using Laplacian smoothing. |
| `mesh_flatten` | `axis` | Flattens selected vertices to plane (X/Y/Z). |
| `mesh_list_groups` | `object_name`, `group_type` | Lists vertex groups or face maps/attributes. |
| `mesh_get_vertex_data` | `object_name`, `selected_only` | Returns vertex positions and selection states. |
| `mesh_get_edge_data` | `object_name`, `selected_only` | Returns edge connectivity and flags. |
| `mesh_get_face_data` | `object_name`, `selected_only` | Returns face connectivity, normals, and material index. |
| `mesh_get_uv_data` | `object_name`, `uv_layer`, `selected_only` | Returns UV coordinates per face loop. |
| `mesh_get_loop_normals` | `object_name`, `selected_only` | Returns per-loop normals (split/custom). |
| `mesh_get_vertex_group_weights` | `object_name`, `group_name`, `selected_only` | Returns vertex group weights. |
| `mesh_get_attributes` | `object_name`, `attribute_name`, `selected_only` | Returns mesh attributes (vertex colors/layers). |
| `mesh_get_shape_keys` | `object_name`, `include_deltas` | Returns shape key data (optional deltas). |
| `mesh_randomize` | `amount`, `uniform`, `normal`, `seed` | Randomizes vertex positions for organic surfaces. |
| `mesh_shrink_fatten` | `value` | Moves vertices along their normals (inflate/deflate). |
| `mesh_create_vertex_group` | `object_name`, `name` | Creates a new vertex group on mesh object. |
| `mesh_assign_to_group` | `object_name`, `group_name`, `weight` | Assigns selected vertices to vertex group. |
| `mesh_remove_from_group` | `object_name`, `group_name` | Removes selected vertices from vertex group. |
| `mesh_bisect` | `plane_co`, `plane_no`, `clear_inner`, `clear_outer`, `fill` | Cuts mesh along a plane. |
| `mesh_edge_slide` | `value` | Slides selected edges along mesh topology. |
| `mesh_vert_slide` | `value` | Slides selected vertices along connected edges. |
| `mesh_triangulate` | *none* | Converts selected faces to triangles. |
| `mesh_remesh_voxel` | `voxel_size`, `adaptivity` | Remeshes object using Voxel algorithm (Object Mode). |
| `mesh_transform_selected` | `translate`, `rotate`, `scale`, `pivot` | Transforms selected geometry (move/rotate/scale). **CRITICAL** |
| `mesh_bridge_edge_loops` | `number_cuts`, `interpolation`, `smoothness`, `twist` | Bridges two edge loops with faces. |
| `mesh_duplicate_selected` | `translate` | Duplicates selected geometry within the same mesh. |
| `mesh_spin` | `steps`, `angle`, `axis`, `center`, `dupli` | Spins/lathes selected geometry around an axis. |
| `mesh_screw` | `steps`, `turns`, `axis`, `center`, `offset` | Creates spiral/screw geometry from selected profile. |
| `mesh_add_vertex` | `position` | Adds a single vertex at the specified position. |
| `mesh_add_edge_face` | *none* | Creates edge or face from selected vertices (F key). |
| `mesh_edge_crease` | `crease_value` | Sets crease weight on selected edges (0.0-1.0) for Subdivision Surface control. |
| `mesh_bevel_weight` | `weight` | Sets bevel weight on selected edges (0.0-1.0) for selective beveling. |
| `mesh_mark_sharp` | `action` | Marks ('mark') or clears ('clear') sharp edges for Auto Smooth. |
| `mesh_dissolve` | `dissolve_type`, `angle_limit`, `use_face_split`, `use_boundary_tear` | Dissolves geometry (limited/verts/edges/faces) while preserving shape. |
| `mesh_tris_to_quads` | `face_threshold`, `shape_threshold` | Converts triangles to quads based on angle thresholds. |
| `mesh_normals_make_consistent` | `inside` | Recalculates normals to face consistently outward (or inward if inside=True). |
| `mesh_decimate` | `ratio`, `use_symmetry`, `symmetry_axis` | Reduces polycount while preserving shape (Edit Mode). |
| `mesh_knife_project` | `cut_through` | Projects cut from selected geometry (requires view angle). |
| `mesh_rip` | `use_fill` | Rips (tears) geometry at selected vertices. |
| `mesh_split` | *none* | Splits selection from mesh (disconnects without separating). |
| `mesh_edge_split` | *none* | Splits mesh at selected edges (creates seams). |
| `mesh_set_proportional_edit` | `enabled`, `falloff_type`, `size`, `use_connected` | Configures proportional editing mode for organic deformations. |
| `mesh_symmetrize` | `direction`, `threshold` | Makes mesh symmetric by mirroring one side to the other. |
| `mesh_grid_fill` | `span`, `offset`, `use_interp_simple` | Fills boundary with a grid of quads (superior to triangle fill). |
| `mesh_poke_faces` | `offset`, `use_relative_offset`, `center_mode` | Pokes faces (adds vertex at center, creates triangle fan). |
| `mesh_beautify_fill` | `angle_limit` | Rearranges triangles to more uniform triangulation. |
| `mesh_mirror` | `axis`, `use_mirror_merge`, `merge_threshold` | Mirrors selected geometry within the same object. |

> **Note:** Selection tools (`mesh_select_all`, `mesh_select_by_index`, `mesh_select_loop`, etc.) have been consolidated into mega tools. Use `mesh_select` and `mesh_select_targeted` instead.

### Curve Tools
Curve creation and conversion.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `curve_create` | `curve_type`, `location` | Creates curve primitive (BEZIER, NURBS, PATH, CIRCLE). |
| `curve_to_mesh` | `object_name` | Converts curve object to mesh geometry. |
| `curve_get_data` | `object_name` | Returns curve splines, points, and settings. |

### Text Tools
3D typography and text annotations.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `text_create` | `text`, `name`, `location`, `font`, `size`, `extrude`, `bevel_depth`, `bevel_resolution`, `align_x`, `align_y` | Creates 3D text object with optional extrusion and bevel. |
| `text_edit` | `object_name`, `text`, `size`, `extrude`, `bevel_depth`, `bevel_resolution`, `align_x`, `align_y` | Edits existing text object content and properties. |
| `text_to_mesh` | `object_name`, `keep_original` | Converts text to mesh for game export and editing. |

### Sculpt Tools
Sculpt Mode operations for organic shape manipulation.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `sculpt_auto` | `operation` (smooth/inflate/flatten/sharpen), `strength`, `iterations`, `use_symmetry`, `symmetry_axis` | High-level sculpt operation using mesh filters. Applies to entire mesh. Recommended for AI workflows. |
| `sculpt_brush_smooth` | `location`, `radius`, `strength` | Sets up smooth brush at specified location. |
| `sculpt_brush_grab` | `from_location`, `to_location`, `radius`, `strength` | Sets up grab brush for moving geometry. |
| `sculpt_brush_crease` | `location`, `radius`, `strength`, `pinch` | Sets up crease brush for creating sharp lines. |
| `sculpt_brush_clay` | `radius`, `strength` | Sets up clay brush for adding material (muscle mass, fat deposits). |
| `sculpt_brush_inflate` | `radius`, `strength` | Sets up inflate brush for pushing geometry outward (tumors, swelling). |
| `sculpt_brush_blob` | `radius`, `strength` | Sets up blob brush for creating rounded organic bulges. |
| `sculpt_brush_snake_hook` | `radius`, `strength` | Sets up snake hook brush for pulling tendrils (blood vessels, nerves). |
| `sculpt_brush_draw` | `radius`, `strength` | Sets up draw brush for basic sculpting. |
| `sculpt_brush_pinch` | `radius`, `strength` | Sets up pinch brush for creating sharp creases (wrinkles, folds). |
| `sculpt_enable_dyntopo` | `detail_mode`, `detail_size`, `use_smooth_shading` | Enables Dynamic Topology for automatic geometry addition. |
| `sculpt_disable_dyntopo` | *none* | Disables Dynamic Topology. |
| `sculpt_dyntopo_flood_fill` | *none* | Applies current detail level to entire mesh. |

> **Note:** For reliable AI workflows, use `sculpt_auto` with mesh filters. Brush tools set up the brush but don't execute strokes programmatically.

### Export Tools
File export operations.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `export_glb` | `filepath`, `export_selected`, `export_animations`, `export_materials`, `apply_modifiers` | Exports to GLB/GLTF format (web, game engines). |
| `export_fbx` | `filepath`, `export_selected`, `export_animations`, `apply_modifiers`, `mesh_smooth_type` | Exports to FBX format (industry standard). |
| `export_obj` | `filepath`, `export_selected`, `apply_modifiers`, `export_materials`, `export_uvs`, `export_normals`, `triangulate` | Exports to OBJ format (universal mesh). |

### Import Tools
File import operations.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `import_obj` | `filepath`, `use_split_objects`, `use_split_groups`, `global_scale`, `forward_axis`, `up_axis` | Imports OBJ file (geometry, UVs, normals). |
| `import_fbx` | `filepath`, `use_custom_normals`, `use_image_search`, `ignore_leaf_bones`, `automatic_bone_orientation`, `global_scale` | Imports FBX file (geometry, materials, animations). |
| `import_glb` | `filepath`, `import_pack_images`, `merge_vertices`, `import_shading` | Imports GLB/GLTF file (PBR materials, animations). |
| `import_image_as_plane` | `filepath`, `name`, `location`, `size`, `align_axis`, `shader`, `use_transparency` | Imports image as textured plane (reference images). |

### Lattice Tools
Non-destructive shape deformation using control point cages.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `lattice_create` | `name`, `target_object`, `location`, `points_u`, `points_v`, `points_w`, `interpolation` | Creates lattice object, auto-fits to target object bounds. |
| `lattice_bind` | `object_name`, `lattice_name`, `vertex_group` | Binds object to lattice via Lattice modifier. |
| `lattice_edit_point` | `lattice_name`, `point_index`, `offset`, `relative` | Moves lattice control points to deform bound objects. |
| `lattice_get_points` | `object_name` | Returns lattice point positions and resolution. |

### Armature Tools
Skeletal rigging and pose utilities.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `armature_create` | `name`, `location`, `bone_name`, `bone_length` | Creates armature with initial bone. |
| `armature_add_bone` | `armature_name`, `bone_name`, `head`, `tail`, `parent_bone`, `use_connect` | Adds bone to existing armature with optional parenting. |
| `armature_bind` | `mesh_name`, `armature_name`, `bind_type` | Binds mesh to armature (AUTO/ENVELOPE/EMPTY). |
| `armature_pose_bone` | `armature_name`, `bone_name`, `rotation`, `location`, `scale` | Poses bone in Pose Mode. |
| `armature_weight_paint_assign` | `object_name`, `vertex_group`, `weight`, `mode` | Assigns weights to selected vertices. |
| `armature_get_data` | `object_name`, `include_pose` | Returns armature bones and hierarchy (optional pose data). |

### System Tools
System-level operations for mode switching, undo/redo, and file management.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `system_set_mode` | `mode`, `object_name` | Switches Blender mode (OBJECT/EDIT/SCULPT/POSE/...) with optional object selection. |
| `system_undo` | `steps` | Undoes last operation(s), max 10 steps per call. |
| `system_redo` | `steps` | Redoes previously undone operation(s), max 10 steps per call. |
| `system_save_file` | `filepath`, `compress` | Saves current .blend file. Auto-generates temp path if unsaved. |
| `system_new_file` | `load_ui` | Creates new file (resets scene to startup). |
| `system_snapshot` | `action`, `name` | Manages quick save/restore checkpoints (save/restore/list/delete). |

### Baking Tools
Texture baking operations using Cycles renderer. Critical for game development workflows.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `bake_normal_map` | `object_name`, `output_path`, `resolution`, `high_poly_source`, `cage_extrusion`, `margin`, `normal_space` | Bakes normal map from geometry or high-poly to low-poly. Supports TANGENT/OBJECT space. |
| `bake_ao` | `object_name`, `output_path`, `resolution`, `samples`, `distance`, `margin` | Bakes ambient occlusion map with configurable samples. |
| `bake_combined` | `object_name`, `output_path`, `resolution`, `samples`, `margin`, `use_pass_direct`, `use_pass_indirect`, `use_pass_color` | Bakes full render (material + lighting) to texture. |
| `bake_diffuse` | `object_name`, `output_path`, `resolution`, `margin` | Bakes diffuse/albedo color only (no lighting). |

### Extraction Tools
Analysis tools for the Automatic Workflow Extraction System (TASK-042). Enables deep topology analysis, component detection, symmetry detection, and multi-angle rendering for LLM Vision integration.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `extraction_deep_topology` | `object_name`, `include_feature_detection` | Deep topology analysis with base primitive detection (CUBE/PLANE/CYLINDER/SPHERE/CUSTOM) and feature detection (bevels, insets, extrusions). |
| `extraction_component_separate` | `object_name`, `analyze_components` | Separates mesh into loose parts for individual analysis. Returns component bounding boxes and centroids. |
| `extraction_detect_symmetry` | `object_name`, `tolerance`, `axes` | Detects X/Y/Z symmetry planes using KDTree with confidence scores (0.0-1.0). |
| `extraction_edge_loop_analysis` | `object_name`, `include_parallel_detection` | Analyzes edge loops, boundary/manifold/non-manifold edges, parallel loop groups, and chamfer edge detection. |
| `extraction_face_group_analysis` | `object_name`, `normal_tolerance`, `height_tolerance` | Analyzes face groups by normal direction, height levels, and inset/extrusion pattern detection. |
| `extraction_render_angles` | `object_name`, `output_dir`, `resolution`, `angles` | Multi-angle renders (front, back, left, right, top, iso) for LLM Vision semantic analysis. |

### Workflow Catalog Tools
Read-only tools for browsing and inspecting workflow definitions (no execution).

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `workflow_catalog` | `action` (list/get/search), `workflow_name`, `query`, `top_k`, `threshold` | Lists workflows, searches similar workflows, and returns workflow definitions (including steps) without executing them. |

### Router Tools
Tools for managing the Router Supervisor and executing matched workflows.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `router_set_goal` | `goal` (str), `resolved_params` (dict, optional) | Sets modeling goal with automatic parameter resolution. Returns JSON with status (ready/needs_input/no_match/disabled/error), resolved params with sources, and unresolved params. Call again with resolved_params to provide answers. Mappings stored automatically for future semantic reuse. |
| `router_get_status` | *none* | Gets current Router Supervisor status (goal, pending workflow, stats). |
| `router_clear_goal` | *none* | Clears the current modeling goal. |

## 🛠 Key Components

### Entry Point (`server/main.py`)
Minimalist entry point.

### Dependency Injection (`server/infrastructure/di.py`)
Set of "Providers" (factory functions). Injects configuration from `server/infrastructure/config.py`.

### Configuration (`server/infrastructure/config.py`)
Environment variable handling (e.g., Blender IP address).

### Application Handlers (`server/application/tool_handlers/`)
Concrete tool logic implementations.
- `scene_handler.py`: Scene operations.
- `modeling_handler.py`: Modeling operations.

### Interfaces (`server/domain/`)
Abstract definitions of system contracts.
- `interfaces/rpc.py`: Contract for RPC client.
- `tools/scene.py`: Contract for scene tools.
- `tools/modeling.py`: Contract for modeling tools.
