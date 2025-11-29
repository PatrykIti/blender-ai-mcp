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
| `scene_inspect` | `object`, `topology`, `modifiers`, `materials` | Detailed inspection queries for objects. |
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

> **Note:** Tools like `scene_get_mode`, `scene_list_selection`, `scene_inspect_*`, and `scene_create_*` have been consolidated into mega tools. Use `scene_context`, `scene_inspect`, and `scene_create` instead.

### Collection Tools
Organizational tools for managing Blender collections.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `collection_list` | `include_objects` (bool) | Lists all collections with hierarchy, object counts, and visibility flags. |
| `collection_list_objects` | `collection_name` (str), `recursive` (bool), `include_hidden` (bool) | Lists objects within a collection, optionally recursive through child collections. |

### Material Tools
Material and shader management.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `material_list` | `include_unassigned` (bool) | Lists all materials with Principled BSDF parameters and object assignment counts. |
| `material_list_by_object` | `object_name` (str), `include_indices` (bool) | Lists material slots for a specific object. |

### UV Tools
Texture coordinate mapping operations.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `uv_list_maps` | `object_name` (str), `include_island_counts` (bool) | Lists UV maps for a mesh object with active flags and loop counts. |

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
| `mesh_boolean` | `operation`, `solver='EXACT'` | Boolean op (Unselected - Selected). Note: FAST solver removed in Blender 4.0+. |
| `mesh_merge_by_distance` | `distance` | Remove doubles / merge vertices. |
| `mesh_subdivide` | `number_cuts`, `smoothness` | Subdivides selected geometry. |
| `mesh_smooth` | `iterations`, `factor` | Smooths selected vertices using Laplacian smoothing. |
| `mesh_flatten` | `axis` | Flattens selected vertices to plane (X/Y/Z). |
| `mesh_list_groups` | `object_name`, `group_type` | Lists vertex groups or face maps/attributes. |
| `mesh_get_vertex_data` | `object_name`, `selected_only` | Returns vertex positions and selection states. |
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

> **Note:** Selection tools (`mesh_select_all`, `mesh_select_by_index`, `mesh_select_loop`, etc.) have been consolidated into mega tools. Use `mesh_select` and `mesh_select_targeted` instead.

### Curve Tools
Curve creation and conversion.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `curve_create` | `curve_type`, `location` | Creates curve primitive (BEZIER, NURBS, PATH, CIRCLE). |
| `curve_to_mesh` | `object_name` | Converts curve object to mesh geometry. |

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
