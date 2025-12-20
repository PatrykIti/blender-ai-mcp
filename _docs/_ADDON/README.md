# Blender Addon Documentation

Documentation for the Blender Addon (Server Side).

## 📚 Topic Index

- **[RPC Architecture and Threading](./rpc_architecture.md)**
  - Explanation of the multi-threaded model.
  - `bpy.app.timers` mechanism.
  - JSON Protocol.

## 🛠 Structure (Clean Architecture)

The Addon is layered to separate Blender logic from networking mechanisms.

### 1. Entry Point (`__init__.py`)
The main entry point. Responsible for:
- Registration in Blender (`bl_info`).
- Instantiating Application Handlers.
- Registering Handlers in the RPC Server.
- Starting the server in a separate thread.

### 2. Application (`application/handlers/`)
Business Logic ("How to do it in Blender").
- `scene.py`: `SceneHandler` (List objects, delete).
- `modeling.py`: `ModelingHandler` (Create primitives, transforms, modifiers).
- Direct usage of `bpy`.

### 3. Infrastructure (`infrastructure/`)
Technical details.
- `rpc_server.py`: TCP Server implementation. It knows nothing about business logic, only accepts JSON requests and dispatches them to registered callbacks.

## 🛠 Available API Commands

### Scene (`application/handlers/scene.py`)

| RPC Command | Handler Method | Description |

|-------------|----------------|-------------|

| `list_objects` | `list_objects` | Lists objects in the scene. |

| `delete_object` | `delete_object` | Deletes an object. |

| `clean_scene` | `clean_scene` | Clears the scene. |

| `duplicate_object` | `duplicate_object` | Duplicates an object and optionally moves it. |

| `set_active_object` | `set_active_object` | Sets the active object. |

| `get_mode` | `get_mode` | Reports current Blender mode and selection context. |

| `list_selection` | `list_selection` | Lists selected objects and Edit Mode component counts. |

| `inspect_object` | `inspect_object` | Returns detailed metadata for a single object (transform, collections, modifiers, mesh stats). |
| `snapshot_state` | `snapshot_state` | Captures structured JSON snapshot with SHA256 hash. |
| `inspect_material_slots` | `inspect_material_slots` | Audits material slot assignments across scene. |
| `inspect_mesh_topology` | `inspect_mesh_topology` | Reports detailed topology stats (counts, N-gons, non-manifold). |
| `inspect_modifiers` | `inspect_modifiers` | Audits modifier stacks and properties. |
| `scene.get_constraints` | `get_constraints` | Returns object (and optional bone) constraints. |
| `get_viewport` | `get_viewport` | Returns a base64 encoded OpenGL render. Supports `shading`, `camera_name`, and `focus_target`. |
| `scene.get_custom_properties` | `get_custom_properties` | Gets custom properties (metadata) from an object. |
| `scene.set_custom_property` | `set_custom_property` | Sets or deletes a custom property on an object. |
| `scene.get_hierarchy` | `get_hierarchy` | Gets parent-child hierarchy for object or full scene. |
| `scene.get_bounding_box` | `get_bounding_box` | Gets bounding box corners in world/local space. |
| `scene.get_origin_info` | `get_origin_info` | Gets origin (pivot point) information for an object. |

### Collection (`application/handlers/collection.py`)

| RPC Command | Handler Method | Description |
|-------------|----------------|-------------|
| `collection.list` | `list_collections` | Lists all collections with hierarchy. |
| `collection.list_objects` | `list_objects` | Lists objects in a collection (recursive). |
| `collection.manage` | `manage_collection` | Manages collections (create, delete, rename, move/link/unlink objects). |

### Material (`application/handlers/material.py`)

| RPC Command | Handler Method | Description |
|-------------|----------------|-------------|
| `material.list` | `list_materials` | Lists all materials with BSDF parameters. |
| `material.list_by_object` | `list_by_object` | Lists material slots for specific object. |
| `material.create` | `create_material` | Creates new PBR material with Principled BSDF. |
| `material.assign` | `assign_material` | Assigns material to object or selected faces. |
| `material.set_params` | `set_material_params` | Modifies existing material parameters. |
| `material.set_texture` | `set_material_texture` | Binds image texture to material input. |
| `material.inspect_nodes` | `inspect_nodes` | Inspects material shader node graph with connections. |

### UV (`application/handlers/uv.py`)

| RPC Command | Handler Method | Description |
|-------------|----------------|-------------|
| `uv.list_maps` | `list_maps` | Lists UV maps for mesh object. |
| `uv.unwrap` | `unwrap` | Unwraps selected faces using projection methods. |
| `uv.pack_islands` | `pack_islands` | Packs UV islands for optimal texture space. |
| `uv.create_seam` | `create_seam` | Marks or clears UV seams on selected edges. |

### Modeling (`application/handlers/modeling.py`)



| RPC Command | Handler Method | Description |



|-------------|----------------|-------------|



| `create_primitive` | `create_primitive` | Creates a primitive (Cube, Sphere, etc.). |



| `transform_object` | `transform_object` | Moves, rotates, or scales an object. |



| `add_modifier` | `add_modifier` | Adds a modifier to an object. |



| `apply_modifier` | `apply_modifier` | Applies (finalizes) a modifier on an object. |



| `convert_to_mesh` | `convert_to_mesh` | Converts a non-mesh object to a mesh. |



| `join_objects` | `join_objects` | Joins multiple mesh objects into one. |



| `separate_object` | `separate_object` | Separates a mesh object into new objects. |



| `set_origin` | `set_origin` | Sets the origin point of an object. |

| `get_modifiers` | `get_modifiers` | Returns a list of modifiers on the object. |
| `modeling.get_modifier_data` | `get_modifier_data` | Returns full modifier properties (Geometry Nodes metadata optional). |
| `modeling.metaball_create` | `metaball_create` | Creates metaball object. |
| `modeling.metaball_add_element` | `metaball_add_element` | Adds element to metaball. |
| `modeling.metaball_to_mesh` | `metaball_to_mesh` | Converts metaball to mesh. |
| `modeling.skin_create_skeleton` | `skin_create_skeleton` | Creates skeleton for skin modifier. |
| `modeling.skin_set_radius` | `skin_set_radius` | Sets skin radius at vertices. |


### Mesh (`application/handlers/mesh.py`)

| RPC Command | Handler Method | Description |

|-------------|----------------|-------------|

| `select_all` | `select_all` | Selects or deselects all geometry elements. |

| `delete_selected` | `delete_selected` | Deletes selected elements (VERT, EDGE, FACE). |

| `select_by_index` | `select_by_index` | Selects elements by index using BMesh (supports SET/ADD/SUBTRACT). |

| `extrude_region` | `extrude_region` | Extrudes selected region (optionally moves). |

| `fill_holes` | `fill_holes` | Fills holes by creating faces. |

| `bevel` | `bevel` | Bevels selected edges/vertices. |

| `loop_cut` | `loop_cut` | Adds loop cuts (subdivides). |

| `inset` | `inset` | Insets selected faces. |

| `boolean` | `boolean` | Boolean operation (Edit Mode). |

| `merge_by_distance` | `merge_by_distance` | Merges vertices (Remove Doubles). |

| `subdivide` | `subdivide` | Subdivides selected geometry. |
| `smooth_vertices` | `smooth_vertices` | Smooths selected vertices using Laplacian smoothing. |
| `flatten_vertices` | `flatten_vertices` | Flattens selected vertices to plane along specified axis. |
| `list_groups` | `list_groups` | Lists vertex/face groups defined on the mesh. |
| `mesh.get_vertex_data` | `get_vertex_data` | Returns vertex positions and selection states. |
| `mesh.get_edge_data` | `get_edge_data` | Returns edge connectivity and flags. |
| `mesh.get_face_data` | `get_face_data` | Returns face connectivity, normals, and materials. |
| `mesh.get_uv_data` | `get_uv_data` | Returns UV coordinates per face loop. |
| `mesh.get_loop_normals` | `get_loop_normals` | Returns per-loop normals (split/custom). |
| `mesh.get_vertex_group_weights` | `get_vertex_group_weights` | Returns vertex group weights. |
| `mesh.get_attributes` | `get_attributes` | Returns mesh attributes (vertex colors/layers). |
| `mesh.get_shape_keys` | `get_shape_keys` | Returns shape key data (optional deltas). |
| `randomize` | `randomize` | Randomizes vertex positions for organic surfaces. |
| `shrink_fatten` | `shrink_fatten` | Moves vertices along their normals (inflate/deflate). |
| `create_vertex_group` | `create_vertex_group` | Creates a new vertex group on mesh object. |
| `assign_to_group` | `assign_to_group` | Assigns selected vertices to vertex group with weight. |
| `remove_from_group` | `remove_from_group` | Removes selected vertices from vertex group. |
| `bisect` | `bisect` | Cuts mesh along a plane. |
| `edge_slide` | `edge_slide` | Slides selected edges along mesh topology. |
| `vert_slide` | `vert_slide` | Slides selected vertices along connected edges. |
| `triangulate` | `triangulate` | Converts selected faces to triangles. |
| `remesh_voxel` | `remesh_voxel` | Performs voxel remesh on object (Object Mode). |
| `transform_selected` | `transform_selected` | Transforms selected geometry (move/rotate/scale). |
| `bridge_edge_loops` | `bridge_edge_loops` | Bridges two edge loops with faces. |
| `duplicate_selected` | `duplicate_selected` | Duplicates selected geometry. |
| `spin` | `spin` | Spins/lathes selected geometry around axis. |
| `screw` | `screw` | Creates spiral/screw geometry. |
| `add_vertex` | `add_vertex` | Adds single vertex at position. |
| `add_edge_face` | `add_edge_face` | Creates edge or face from selected vertices. |
| `edge_crease` | `edge_crease` | Sets crease weight on selected edges. |
| `bevel_weight` | `bevel_weight` | Sets bevel weight on selected edges. |
| `mark_sharp` | `mark_sharp` | Marks or clears sharp edges. |
| `mesh.dissolve` | `dissolve` | Dissolves geometry (limited/verts/edges/faces). |
| `mesh.tris_to_quads` | `tris_to_quads` | Converts triangles to quads. |
| `mesh.normals_make_consistent` | `normals_make_consistent` | Recalculates normals to face consistently. |
| `mesh.decimate` | `decimate` | Reduces polycount while preserving shape. |
| `mesh.knife_project` | `knife_project` | Projects cut from selected geometry (view-dependent). |
| `mesh.rip` | `rip` | Rips (tears) geometry at selected vertices. |
| `mesh.split` | `split` | Splits selection from mesh (disconnects without separating). |
| `mesh.edge_split` | `edge_split` | Splits mesh at selected edges (creates seams). |
| `mesh.set_proportional_edit` | `set_proportional_edit` | Configures proportional editing mode. |
| `mesh.symmetrize` | `symmetrize` | Makes mesh symmetric by mirroring one side to the other. |
| `mesh.grid_fill` | `grid_fill` | Fills boundary with a grid of quads. |
| `mesh.poke_faces` | `poke_faces` | Pokes selected faces (adds vertex at center). |
| `mesh.beautify_fill` | `beautify_fill` | Rearranges triangles to more uniform triangulation. |
| `mesh.mirror` | `mirror` | Mirrors selected geometry within the same object. |


### Curve (`application/handlers/curve.py`)

| RPC Command | Handler Method | Description |
|-------------|----------------|-------------|
| `curve.create_curve` | `create_curve` | Creates curve primitive (Bezier, NURBS, Path, Circle). |
| `curve.curve_to_mesh` | `curve_to_mesh` | Converts curve to mesh. |


### Text (`application/handlers/text.py`)

| RPC Command | Handler Method | Description |
|-------------|----------------|-------------|
| `text.create` | `create` | Creates 3D text object with optional extrusion and bevel. |
| `text.edit` | `edit` | Edits text object content and properties. |
| `text.to_mesh` | `to_mesh` | Converts text to mesh for game export. |


### Sculpt (`application/handlers/sculpt.py`)

| RPC Command | Handler Method | Description |
|-------------|----------------|-------------|
| `sculpt.auto` | `auto_sculpt` | High-level sculpt operation using mesh filters (smooth, inflate, flatten, sharpen). |
| `sculpt.brush_smooth` | `brush_smooth` | Sets up smooth brush at specified location. |
| `sculpt.brush_grab` | `brush_grab` | Sets up grab brush for moving geometry. |
| `sculpt.brush_crease` | `brush_crease` | Sets up crease brush for creating sharp lines. |
| `sculpt.brush_clay` | `brush_clay` | Sets up clay brush for adding material. |
| `sculpt.brush_inflate` | `brush_inflate` | Sets up inflate brush for pushing outward. |
| `sculpt.brush_blob` | `brush_blob` | Sets up blob brush for organic bulges. |
| `sculpt.brush_snake_hook` | `brush_snake_hook` | Sets up snake hook brush for tendrils. |
| `sculpt.brush_draw` | `brush_draw` | Sets up draw brush for basic sculpting. |
| `sculpt.brush_pinch` | `brush_pinch` | Sets up pinch brush for creases. |
| `sculpt.enable_dyntopo` | `enable_dyntopo` | Enables Dynamic Topology. |
| `sculpt.disable_dyntopo` | `disable_dyntopo` | Disables Dynamic Topology. |
| `sculpt.dyntopo_flood_fill` | `dyntopo_flood_fill` | Applies detail to entire mesh. |


### Export (`application/handlers/export.py`)

| RPC Command | Handler Method | Description |
|-------------|----------------|-------------|
| `export.glb` | `export_glb` | Exports to GLB/GLTF format (web, game engines). |
| `export.fbx` | `export_fbx` | Exports to FBX format (industry standard). |
| `export.obj` | `export_obj` | Exports to OBJ format (universal mesh). |


### System (`application/handlers/system.py`)

| RPC Command | Handler Method | Description |
|-------------|----------------|-------------|
| `system.set_mode` | `set_mode` | Switches Blender mode (OBJECT/EDIT/SCULPT/POSE/...) with optional object selection. |
| `system.undo` | `undo` | Undoes last operation(s), max 10 steps per call. |
| `system.redo` | `redo` | Redoes previously undone operation(s), max 10 steps per call. |
| `system.save_file` | `save_file` | Saves current .blend file (with optional filepath). |
| `system.new_file` | `new_file` | Creates new file (resets scene to startup). |
| `system.snapshot` | `snapshot` | Manages quick save/restore checkpoints (save/restore/list/delete). |


### Baking (`application/handlers/baking.py`)

| RPC Command | Handler Method | Description |
|-------------|----------------|-------------|
| `baking.normal_map` | `bake_normal_map` | Bakes normal map from geometry or high-poly to low-poly. |
| `baking.ao` | `bake_ao` | Bakes ambient occlusion map. |
| `baking.combined` | `bake_combined` | Bakes full render (material + lighting) to texture. |
| `baking.diffuse` | `bake_diffuse` | Bakes diffuse/albedo color only (no lighting). |


### Import (`application/handlers/import_handler.py`)

| RPC Command | Handler Method | Description |
|-------------|----------------|-------------|
| `import.obj` | `import_obj` | Imports OBJ file (geometry, UVs, normals). |
| `import.fbx` | `import_fbx` | Imports FBX file (geometry, materials, animations). |
| `import.glb` | `import_glb` | Imports GLB/GLTF file (PBR materials, animations). |
| `import.image_as_plane` | `import_image_as_plane` | Imports image as textured plane (reference images). |


### Lattice (`application/handlers/lattice.py`)

| RPC Command | Handler Method | Description |
|-------------|----------------|-------------|
| `lattice.create` | `lattice_create` | Creates lattice object, auto-fits to target bounds. |
| `lattice.bind` | `lattice_bind` | Binds object to lattice via Lattice modifier. |
| `lattice.edit_point` | `lattice_edit_point` | Moves lattice control points for deformation. |


### Extraction (`application/handlers/extraction.py`)

Analysis tools for the Automatic Workflow Extraction System (TASK-042).

| RPC Command | Handler Method | Description |
|-------------|----------------|-------------|
| `extraction.deep_topology` | `deep_topology` | Deep topology analysis with base primitive and feature detection. |
| `extraction.component_separate` | `component_separate` | Separates mesh into loose parts for individual analysis. |
| `extraction.detect_symmetry` | `detect_symmetry` | Detects X/Y/Z symmetry planes using KDTree with confidence scores. |
| `extraction.edge_loop_analysis` | `edge_loop_analysis` | Analyzes edge loops, boundary/manifold/non-manifold edges. |
| `extraction.face_group_analysis` | `face_group_analysis` | Analyzes face groups by normal direction and height levels. |
| `extraction.render_angles` | `render_angles` | Multi-angle renders for LLM Vision semantic analysis. |
