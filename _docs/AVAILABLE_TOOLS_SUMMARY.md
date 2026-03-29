# Available Tools Summary

This is the runtime inventory for `blender-ai-mcp`: the broadest single view of what the server can currently do across grouped public tools, internal atomics, specialist families, and router/workflow entrypoints.

Planned tools are marked as 🚧.

Read this file as a **reference map**, not as the recommended first-contact surface for production LLM usage.
The product story is now:

- start from the guided/goal-first surface
- prefer grouped public tools and bounded macro/workflow tools
- keep hidden atomics as substrate and expert escape hatches
- use measurement/assertion as the truth layer when correctness matters

This file is an inventory/reference doc, not the canonical policy source for:

- what should be public vs hidden
- how tools are layered
- when `router_set_goal(...)` is expected

For the canonical product framing, use:

- [_docs/_MCP_SERVER/TOOL_LAYERING_POLICY.md](/Users/pciechanski/Documents/_moje_projekty/blender-ai-mcp/_docs/_MCP_SERVER/TOOL_LAYERING_POLICY.md)
- [_docs/_MCP_SERVER/README.md](/Users/pciechanski/Documents/_moje_projekty/blender-ai-mcp/_docs/_MCP_SERVER/README.md)
- [_docs/TOOLS/README.md](/Users/pciechanski/Documents/_moje_projekty/blender-ai-mcp/_docs/TOOLS/README.md)

Interpretation rule:

- this file may describe the full available inventory
- that does **not** mean the whole inventory should be public on production-oriented LLM surfaces
- public exposure is governed by the policy doc and surface matrix, not by inventory existence alone

---

## LLM-Guided Public Aliases

The `llm-guided` surface keeps the same internal capabilities but exposes a smaller, cleaner public contract line for high-value entry tools.

| Internal tool | `llm-guided` public name | Public arg changes |
|---|---|---|
| `scene_context` | `check_scene` | `action` -> `query` |
| `scene_inspect` | `inspect_scene` | `object_name` -> `target_object` |
| `scene_configure` | `configure_scene` | `settings` -> `config` |
| `workflow_catalog` | `browse_workflows` | `workflow_name` -> `name`, `query` -> `search_query` |

Current hidden/expert-only arguments on `llm-guided`:

- `inspect_scene`: hides `detailed`, `include_disabled`, `modifier_name`, `assistant_summary`, and similar backend-only inspection flags
- `mesh_inspect`: hides `selected_only`, `uv_layer`, `include_deltas`, `assistant_summary`
- `scene_snapshot_state`, `scene_compare_snapshot`, `scene_get_hierarchy`, `scene_get_bounding_box`, `scene_get_origin_info`: hide `assistant_summary`
- `browse_workflows`: hides ranking/import session internals such as `top_k`, `threshold`, `session_id`, and chunk controls

The router and dispatcher still use canonical internal tool names.

---

## Search-First Discovery Rollout

The guided production surface is intentionally search-first.

Default `llm-guided` entry surface:

- `router_set_goal`
- `router_get_status`
- `browse_workflows`
- `search_tools`
- `call_tool`

Task-capable heavy-operation rollout on task-enabled surfaces:

- `scene_get_viewport`
- `extraction_render_angles`
- `workflow_catalog(action="import_finalize")`
- `export_glb`
- `export_fbx`
- `export_obj`
- `import_obj`
- `import_fbx`
- `import_glb`
- `import_image_as_plane`

Prompt bridge tools on tool-only surfaces:

- `list_prompts`
- `get_prompt`

Native prompt products:

- `getting_started`
- `workflow_router_first`
- `manual_tools_no_router`
- `demo_low_poly_medieval_well`
- `demo_generic_modeling`
- `recommended_prompts`

Measured current baseline:

- `legacy-manual`: `163` visible tools, without router/workflow namespace exposure
- `legacy-flat`: `170` visible tools
- `llm-guided`: `8` visible tools

Why this matters:

- discovery respects guided visibility and does not leak hidden tools during bootstrap
- the initial tool payload stays intentionally small
- specialist families do not quietly become the default public path

Specialist families such as armature, sculpt, text, baking, and similar
maintainer-oriented areas are also intentionally excluded from the normal
`llm-guided` escape-hatch surface until a stronger macro layer exists.

This section is descriptive, not normative. Hidden atomic tools may still appear
in the inventory because they exist in the runtime/repo, even when they should
not be part of the normal public LLM-facing surface.

Interpretation rule for future tool waves:

- inventory existence does not imply public-default exposure
- macro/workflow tools are preferred for normal LLM-facing surfaces
- deterministic measure/assert tool families belong to the truth layer once available

---

## Structured Contract Surfaces

The current structured-contract baseline covers:

- `reference_images`
- `macro_cutout_recess`
- `macro_finish_form`
- `macro_relative_layout`
- `scene_context`
- `scene_inspect`
- `scene_create`
- `scene_configure`
- `mesh_select`
- `mesh_select_targeted`
- `scene_snapshot_state`
- `scene_compare_snapshot`
- `scene_get_custom_properties`
- `scene_get_hierarchy`
- `scene_get_bounding_box`
- `scene_get_origin_info`
- `scene_measure_distance`
- `scene_measure_dimensions`
- `scene_measure_gap`
- `scene_measure_alignment`
- `scene_measure_overlap`
- `scene_assert_contact`
- `scene_assert_dimensions`
- `scene_assert_containment`
- `scene_assert_symmetry`
- `scene_assert_proportion`
- `mesh_inspect`
- `router_set_goal`
- `router_get_status`
- `workflow_catalog`

These tools are intended to expose stable machine-readable payloads rather than prose-first JSON strings.
That matters because grouped tools, macro tools, router entrypoints, and truth-layer checks all compose better when results are typed and auditable.

For guided fallback paths, `router_set_goal` now also emits typed `guided_handoff` metadata so `no_match` continuation is an explicit product contract instead of a message-only hint.

## Server-Side Sampling Assistants

Current bounded assistant integration points:

- `scene_inspect`: optional `assistant_summary` on expert/internal paths
- `mesh_inspect`: optional `assistant_summary` on expert/internal paths
- `scene_snapshot_state`: optional `assistant_summary` on expert/internal paths
- `scene_compare_snapshot`: optional `assistant_summary` on expert/internal paths
- `scene_get_hierarchy`: optional `assistant_summary` on expert/internal paths
- `scene_get_bounding_box`: optional `assistant_summary` on expert/internal paths
- `scene_get_origin_info`: optional `assistant_summary` on expert/internal paths
- `router_set_goal`: bounded `repair_suggestion` on `no_match` / `error`
- `router_get_status`: bounded `repair_suggestion` when the latest router diagnostics indicate a recovery path
- `workflow_catalog`: bounded `repair_suggestion` on import recovery states

Assistant envelopes are structured and use explicit terminal statuses:

- `success`
- `unavailable`
- `masked_error`
- `rejected_by_policy`

---

## 🧠 Grouped Public Tools

> These grouped tools are part of the current public working layer.
> They should now be understood through the layered model from `TASK-113`:
> grouped public tools above a hidden/internal atomic layer.
> Internal action handlers still exist behind them and remain available to the
> router and internal execution paths.
>
> This is the current "middle layer" between the tiny guided bootstrap surface
> and the broader runtime inventory.

### Implemented

| Grouped Tool | Actions | Replaces | Status |
|-----------|---------|----------|--------|
| `scene_context` | `mode`, `selection` | `scene_get_mode`, `scene_list_selection` | ✅ Done |
| `scene_create` | `light`, `camera`, `empty` | `scene_create_light`, `scene_create_camera`, `scene_create_empty` | ✅ Done |
| `scene_inspect` | `object`, `topology`, `modifiers`, `materials`, `constraints`, `modifier_data`, `render`, `color_management`, `world` | `scene_inspect_object`, `scene_inspect_mesh_topology`, `scene_inspect_modifiers`, `scene_inspect_material_slots`, `scene_get_constraints`, `modeling_get_modifier_data`, read-side scene state inspection with world node-graph handoff fields | ✅ Done |
| `scene_configure` | `render`, `color_management`, `world` | bounded write-side scene appearance configuration under the grouped tool model | ✅ Done |
| `mesh_select` | `all`, `none`, `linked`, `more`, `less`, `boundary` | `mesh_select_all`, `mesh_select_linked`, `mesh_select_more`, `mesh_select_less`, `mesh_select_boundary` | ✅ Done |
| `mesh_select_targeted` | `by_index`, `loop`, `ring`, `by_location` | `mesh_select_by_index`, `mesh_select_loop`, `mesh_select_ring`, `mesh_select_by_location` | ✅ Done |
| `mesh_inspect` | `summary`, `vertices`, `edges`, `faces`, `uvs`, `normals`, `attributes`, `shape_keys`, `group_weights` | `mesh_get_*` introspection tools | ✅ Done |

### Planned

None.

**Current grouped public set:** 7 high-frequency grouped tools.

---

## 🏗️ Scene Tools (`scene_`)
*Tools for managing the scene graph, selection, and visualization.*

### Implemented

| Tool Name | Arguments | Description | Status |
|-----------|-----------|-------------|--------|
| `scene_context` | `action` (mode/selection) | Grouped context queries (mode, selection state). | ✅ Done |
| `scene_create` | `action` (light/camera/empty), params | Grouped creation tool for lights, cameras, and empties. | ✅ Done |
| `scene_inspect` | `action` (object/topology/modifiers/materials/constraints/modifier_data/render/color_management/world), params | Grouped inspection tool for objects plus scene-level render/color/world state, including node-graph handoff fields for node-based worlds. | ✅ Done |
| `scene_configure` | `action` (render/color_management/world), `settings` | Grouped write-side tool for render, color-management, and bounded world/background configuration. Full node-graph rebuild stays outside this surface. | ✅ Done |
| `scene_list_objects` | *none* | Returns a list of all objects in the scene with their type and position. | ✅ Done |
| `scene_delete_object` | `name` (str) | Deletes the specified object. | ✅ Done |
| `scene_clean_scene` | `keep_lights_and_cameras` (bool) | Clears the scene. Can perform a "hard reset" if set to False. | ✅ Done |
| `scene_duplicate_object` | `name` (str), `translation` ([x,y,z]) | Duplicates an object and optionally moves it. | ✅ Done |
| `scene_set_active_object` | `name` (str) | Sets the active object (crucial for modifiers). | ✅ Done |
| `scene_camera_orbit` | `angle_horizontal`, `angle_vertical`, `target_object` (optional), `target_point` (optional) | Orbits the viewport around a target object or point. | ✅ Done |
| `scene_camera_focus` | `object_name`, `zoom_factor` | Focuses the viewport on one object. Use `object_name`, not `target`, `target_object`, or `focus_target`. | ✅ Done |
| `scene_get_viewport` | `width`, `height`, `shading`, `camera_name`, `focus_target`, `output_mode` | Returns a visual preview of the scene with selectable output mode (IMAGE/BASE64/FILE/MARKDOWN). `USER_PERSPECTIVE` follows the live 3D viewport; named-camera capture follows render visibility. | ✅ Done |
| `reference_images` | `action`, `source_path`, `reference_id`, `label`, `notes`, `target_object`, `target_view` | Goal-scoped reference image lifecycle surface. `attach` can now also stage pending references before the goal exists; the next `router_set_goal(...)` adopts them automatically. | ✅ Done |
| `scene_snapshot_state` | `include_mesh_stats`, `include_materials` | Captures a JSON snapshot of scene state with SHA256 hash. | ✅ Done |
| `scene_compare_snapshot` | `baseline_snapshot`, `target_snapshot`, `ignore_minor_transforms` | Compares two snapshots and returns diff summary. | ✅ Done |
| `scene_set_mode` | `mode` | Sets interaction mode (OBJECT, EDIT, SCULPT, etc.). | ✅ Done |
| `scene_get_custom_properties` | `object_name` | Gets custom properties (metadata) from an object. | ✅ Done |
| `scene_set_custom_property` | `object_name`, `property_name`, `property_value`, `delete` | Sets or deletes a custom property on an object. | ✅ Done |
| `scene_get_hierarchy` | `object_name` (optional), `include_transforms` | Gets parent-child hierarchy for object or full scene tree. | ✅ Done |
| `scene_get_bounding_box` | `object_name`, `world_space` | Gets bounding box corners, min/max, center, dimensions, volume. | ✅ Done |
| `scene_get_origin_info` | `object_name` | Gets origin (pivot point) information relative to geometry. | ✅ Done |
| `scene_measure_distance` | `from_object`, `to_object`, `reference` | Measures origin or bbox-center distance between two objects. | ✅ Done |
| `scene_measure_dimensions` | `object_name`, `world_space` | Measures object dimensions and volume from its bounding box. | ✅ Done |
| `scene_measure_gap` | `from_object`, `to_object`, `tolerance` | Measures bbox gap/contact state between two objects. | ✅ Done |
| `scene_measure_alignment` | `from_object`, `to_object`, `axes`, `reference`, `tolerance` | Measures bbox alignment across chosen axes. | ✅ Done |
| `scene_measure_overlap` | `from_object`, `to_object`, `tolerance` | Measures bbox overlap/touching state and intersection volume. | ✅ Done |
| `scene_assert_contact` | `from_object`, `to_object`, `max_gap`, `allow_overlap` | Asserts pass/fail contact relation from measured gap and overlap state. | ✅ Done |
| `scene_assert_dimensions` | `object_name`, `expected_dimensions`, `tolerance`, `world_space` | Asserts pass/fail dimensions against an expected vector. | ✅ Done |
| `scene_assert_containment` | `inner_object`, `outer_object`, `min_clearance`, `tolerance` | Asserts pass/fail containment plus measured clearance/protrusion details. | ✅ Done |
| `scene_assert_symmetry` | `left_object`, `right_object`, `axis`, `mirror_coordinate`, `tolerance` | Asserts mirrored symmetry between two objects across a chosen axis. | ✅ Done |
| `scene_assert_proportion` | `object_name`, `axis_a`, `expected_ratio`, `axis_b`, `reference_object`, `reference_axis`, `tolerance`, `world_space` | Asserts pass/fail ratio/proportion against the expected value. | ✅ Done |

**Historical atomic paths now primarily internal or grouped-surface backed:**
- ~~`scene_get_mode`~~ → Use `scene_context(action="mode")`
- ~~`scene_list_selection`~~ → Use `scene_context(action="selection")`
- ~~`scene_create_light`~~ → Use `scene_create(action="light", ...)`
- ~~`scene_create_camera`~~ → Use `scene_create(action="camera", ...)`
- ~~`scene_create_empty`~~ → Use `scene_create(action="empty", ...)`
- ~~`scene_inspect_object`~~ → Use `scene_inspect(action="object", ...)`
- ~~`scene_inspect_mesh_topology`~~ → Use `scene_inspect(action="topology", ...)`
- ~~`scene_inspect_modifiers`~~ → Use `scene_inspect(action="modifiers", ...)`
- ~~`scene_inspect_material_slots`~~ → Use `scene_inspect(action="materials", ...)`
- ~~`scene_get_constraints`~~ → Use `scene_inspect(action="constraints", ...)`

---

## 📦 Collection Tools (`collection_`)
*Tools for managing Blender collections (organizational containers).*

### Implemented

| Tool Name | Arguments | Description | Status |
|-----------|-----------|-------------|--------|
| `collection_list` | `include_objects` (bool) | Lists all collections with hierarchy, object counts, and visibility flags. | ✅ Done |
| `collection_list_objects` | `collection_name` (str), `recursive` (bool), `include_hidden` (bool) | Lists objects within specified collection, optionally recursive. | ✅ Done |
| `collection_manage` | `action` (create/delete/rename/move_object/link_object/unlink_object), `collection_name`, `new_name`, `parent_name`, `object_name` | Manages collections: create, delete, rename, and move/link/unlink objects between collections. | ✅ Done |

---

## 🎨 Material Tools (`material_`)
*Tools for managing materials and shaders.*

### Implemented

| Tool Name | Arguments | Description | Status |
|-----------|-----------|-------------|--------|
| `material_list` | `include_unassigned` (bool) | Lists all materials with shader parameters (Principled BSDF) and object assignment counts. | ✅ Done |
| `material_list_by_object` | `object_name` (str), `include_indices` (bool) | Lists material slots for a specific object. | ✅ Done |
| `material_create` | `name`, `base_color`, `metallic`, `roughness`, `emission_color`, `emission_strength`, `alpha` | Creates new PBR material (colors accept list or string `"[...]"`). | ✅ Done |
| `material_assign` | `material_name`, `object_name`, `slot_index`, `assign_to_selection` | Assigns material to object or selected faces (Edit Mode). | ✅ Done |
| `material_set_params` | `material_name`, `base_color`, `metallic`, `roughness`, etc. | Modifies existing material parameters. | ✅ Done |
| `material_set_texture` | `material_name`, `texture_path`, `input_name`, `color_space` | Binds image texture to material input (supports Normal maps). | ✅ Done |
| `material_inspect_nodes` | `material_name`, `include_connections` | Inspects material shader node graph, returns nodes with types, inputs, and connections. | ✅ Done |

---

## 🗺️ UV Tools (`uv_`)
*Tools for texture coordinate mapping operations.*

### Implemented

| Tool Name | Arguments | Description | Status |
|-----------|-----------|-------------|--------|
| `uv_list_maps` | `object_name` (str), `include_island_counts` (bool) | Lists UV maps for a mesh object with active flags and loop counts. | ✅ Done |
| `uv_unwrap` | `object_name`, `method`, `angle_limit`, `island_margin`, `scale_to_bounds` | Unwraps selected faces to UV space using projection methods (SMART_PROJECT, CUBE, CYLINDER, SPHERE, UNWRAP). | ✅ Done |
| `uv_pack_islands` | `object_name`, `margin`, `rotate`, `scale` | Packs UV islands for optimal texture space usage. | ✅ Done |
| `uv_create_seam` | `object_name`, `action` | Marks or clears UV seams on selected edges ('mark' or 'clear'). | ✅ Done |

---

## 🧊 Modeling Tools (`modeling_`)
*Object-level geometry operations (non-destructive or container management).*

### Implemented

| Tool Name | Arguments | Description | Status |
|-----------|-----------|-------------|--------|
| `macro_cutout_recess` | `target_object`, `width`, `height`, `depth`, `face`, `offset`, `mode`, `bevel_width`, `bevel_segments`, `cleanup`, `cutter_name` | Bounded macro for cutter creation, placement, optional bevel, boolean application, and helper cleanup on one target object. | ✅ Done |
| `macro_finish_form` | `target_object`, `preset`, `bevel_width`, `bevel_segments`, `subsurf_levels`, `thickness`, `solidify_offset` | Bounded macro for applying one finishing preset stack such as `rounded_housing`, `panel_finish`, `shell_thicken`, or `smooth_subdivision` without rebuilding the modifier chain manually. | ✅ Done |
| `macro_relative_layout` | `moving_object`, `reference_object`, `x_mode`, `y_mode`, `z_mode`, `contact_axis`, `contact_side`, `gap`, `offset` | Bounded macro for relative object placement using bbox alignment modes, optional outside-face contact/gap placement, and one deterministic transform. | ✅ Done |
| `modeling_create_primitive` | `primitive_type`, `size/radius`, `location`, `rotation` | Creates basic shapes (Cube, Sphere, Cylinder, Plane, Cone, Monkey). | ✅ Done |
| `modeling_transform_object` | `name`, `location`, `rotation`, `scale` | Moves, rotates, or scales an object. | ✅ Done |
| `modeling_add_modifier` | `name`, `modifier_type`, `properties` | Adds a non-destructive object modifier (BOOLEAN: set `properties.object` / `object_name` to the cutter object's name). Successful addon responses carry structured modifier metadata. | ✅ Done |
| `modeling_apply_modifier` | `name`, `modifier_name` | Applies (finalizes) a modifier permanently to the mesh. | ✅ Done |
| `modeling_list_modifiers` | `name` | Lists all modifiers on an object. | ✅ Done |
| `modeling_convert_to_mesh` | `name` | Converts Curve/Text/Surface objects to Mesh. | ✅ Done |
| `modeling_join_objects` | `object_names` (list) | Joins multiple objects into one mesh. | ✅ Done |
| `modeling_separate_object` | `name`, `type` (LOOSE/SELECTED/MATERIAL) | Separates a mesh into multiple objects. | ✅ Done |
| `modeling_set_origin` | `name`, `type` (GEOMETRY/CURSOR/CENTER_OF_MASS) | Sets the object's origin point. | ✅ Done |
| `metaball_create` | `name`, `location`, `element_type`, `radius`, `resolution`, `threshold` | Creates metaball object for organic blob shapes. | ✅ Done |
| `metaball_add_element` | `metaball_name`, `element_type`, `location`, `radius`, `stiffness` | Adds element to existing metaball for merging. | ✅ Done |
| `metaball_to_mesh` | `metaball_name`, `apply_resolution` | Converts metaball to mesh for editing. | ✅ Done |
| `skin_create_skeleton` | `name`, `vertices`, `edges`, `location` | Creates skeleton mesh with Skin modifier for tubular structures. | ✅ Done |
| `skin_set_radius` | `object_name`, `vertex_index`, `radius_x`, `radius_y` | Sets skin radius at vertices for varying thickness. | ✅ Done |

**Historical internal read-side path now routed through grouped inspection:**
- ~~`modeling_get_modifier_data`~~ → Use `scene_inspect(action="modifier_data", ...)`

---

## 🔲 Lattice Tools (`lattice_`)
*Non-destructive deformation using lattice cages for architectural and organic modeling.*

### Implemented

| Tool Name | Arguments | Description | Status |
|-----------|-----------|-------------|--------|
| `lattice_create` | `name`, `target_object`, `location`, `points_u`, `points_v`, `points_w`, `interpolation` | Creates lattice object. If target_object provided, auto-fits to bounding box. | ✅ Done |
| `lattice_bind` | `object_name`, `lattice_name`, `vertex_group` | Binds object to lattice using Lattice modifier. Non-destructive deformation. | ✅ Done |
| `lattice_edit_point` | `lattice_name`, `point_index`, `offset`, `relative` | Moves lattice control points to deform bound objects. | ✅ Done |
| `lattice_get_points` | `object_name` | Returns lattice point positions and resolution. | ✅ Done |

**Use Cases:**
- Tapering towers (Eiffel Tower workflow)
- Bending/twisting shapes
- Organic character deformations
- Product design (curved surfaces)

---

## 🕸️ Mesh Tools (`mesh_`) - Edit Mode
*Low-level geometry manipulation (vertices, edges, faces).*

### Implemented

| Tool Name | Arguments | Description | Status |
|-----------|-----------|-------------|--------|
| `mesh_select` | `action` (all/none/linked/more/less/boundary) | Grouped selection operations. | ✅ Done |
| `mesh_select_targeted` | `action` (by_index/loop/ring/by_location), params | Grouped targeted selection operations. | ✅ Done |
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
| `mesh_transform_selected` | `translate`, `rotate`, `scale`, `pivot` | Transforms selected geometry (move/rotate/scale). Vectors accept list or string `"[...]"`. 🔴 CRITICAL | ✅ Done |
| `mesh_bridge_edge_loops` | `number_cuts`, `interpolation`, `smoothness`, `twist` | Bridges two edge loops with faces. | ✅ Done |
| `mesh_duplicate_selected` | `translate` | Duplicates selected geometry within the same mesh. | ✅ Done |
| `mesh_spin` | `steps`, `angle`, `axis`, `center`, `dupli` | Spins/lathes selected geometry around an axis. | ✅ Done |
| `mesh_screw` | `steps`, `turns`, `axis`, `center`, `offset` | Creates spiral/screw geometry from selected profile. | ✅ Done |
| `mesh_add_vertex` | `position` | Adds a single vertex at the specified position. | ✅ Done |
| `mesh_add_edge_face` | *none* | Creates edge or face from selected vertices. | ✅ Done |
| `mesh_edge_crease` | `crease_value` | Sets crease weight on selected edges (0.0-1.0) for Subdivision Surface control. | ✅ Done |
| `mesh_bevel_weight` | `weight` | Sets bevel weight on selected edges (0.0-1.0) for selective beveling. | ✅ Done |
| `mesh_mark_sharp` | `action` (mark/clear) | Marks or clears sharp edges for Smooth by Angle (5.0+) and Edge Split. | ✅ Done |
| `mesh_dissolve` | `dissolve_type` (limited/verts/edges/faces), `angle_limit`, `use_face_split`, `use_boundary_tear` | Dissolves geometry while preserving shape (cleanup). | ✅ Done |
| `mesh_tris_to_quads` | `face_threshold`, `shape_threshold` | Converts triangles to quads based on angle thresholds. | ✅ Done |
| `mesh_normals_make_consistent` | `inside` | Recalculates normals to face consistently outward (or inward). | ✅ Done |
| `mesh_decimate` | `ratio`, `use_symmetry`, `symmetry_axis` | Reduces polycount while preserving shape. | ✅ Done |
| `mesh_knife_project` | `cut_through` | Projects cut from selected geometry (requires view angle). | ✅ Done |
| `mesh_rip` | `use_fill` | Rips (tears) geometry at selected vertices. | ✅ Done |
| `mesh_split` | *none* | Splits selection from mesh (disconnects without separating). | ✅ Done |
| `mesh_edge_split` | *none* | Splits mesh at selected edges (creates seams). | ✅ Done |
| `mesh_set_proportional_edit` | `enabled`, `falloff_type`, `size`, `use_connected` | Configures proportional editing mode for organic deformations. | ✅ Done |
| `mesh_symmetrize` | `direction`, `threshold` | Makes mesh symmetric by mirroring one side to the other. | ✅ Done |
| `mesh_grid_fill` | `span`, `offset`, `use_interp_simple` | Fills boundary with a grid of quads (superior to triangle fill). | ✅ Done |
| `mesh_poke_faces` | `offset`, `use_relative_offset`, `center_mode` | Pokes faces (adds vertex at center, creates triangle fan). | ✅ Done |
| `mesh_beautify_fill` | `angle_limit` | Rearranges triangles to more uniform triangulation. | ✅ Done |
| `mesh_mirror` | `axis`, `use_mirror_merge`, `merge_threshold` | Mirrors selected geometry within the same object. | ✅ Done |

**Historical mesh-inspection atomics now primarily internal or grouped-surface backed:**
- ~~`mesh_get_vertex_data`~~ → Use `mesh_inspect(action="vertices", ...)`
- ~~`mesh_get_edge_data`~~ → Use `mesh_inspect(action="edges", ...)`
- ~~`mesh_get_face_data`~~ → Use `mesh_inspect(action="faces", ...)`
- ~~`mesh_get_uv_data`~~ → Use `mesh_inspect(action="uvs", ...)`
- ~~`mesh_get_loop_normals`~~ → Use `mesh_inspect(action="normals", ...)`
- ~~`mesh_get_vertex_group_weights`~~ → Use `mesh_inspect(action="group_weights", ...)`
- ~~`mesh_get_attributes`~~ → Use `mesh_inspect(action="attributes", ...)`
- ~~`mesh_get_shape_keys`~~ → Use `mesh_inspect(action="shape_keys", ...)`

**Historical mesh-selection atomics now primarily internal or grouped-surface backed:**
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

### Implemented

| Tool Name | Arguments | Description | Status |
|-----------|-----------|-------------|--------|
| `curve_create` | `curve_type` (BEZIER/NURBS/PATH/CIRCLE), `location` | Creates a curve primitive object. | ✅ Done |
| `curve_to_mesh` | `object_name` | Converts a curve object to mesh geometry. | ✅ Done |
| `curve_get_data` | `object_name` | Returns curve splines, points, and settings. | ✅ Done |

---

## 🔤 Text Tools (`text_`)
*Tools for 3D typography and text annotations.*

### Implemented

| Tool Name | Arguments | Description | Status |
|-----------|-----------|-------------|--------|
| `text_create` | `text`, `name`, `location`, `font`, `size`, `extrude`, `bevel_depth`, `bevel_resolution`, `align_x`, `align_y` | Creates a 3D text object with optional extrusion and bevel. | ✅ Done |
| `text_edit` | `object_name`, `text`, `size`, `extrude`, `bevel_depth`, `bevel_resolution`, `align_x`, `align_y` | Edits existing text object content and properties. | ✅ Done |
| `text_to_mesh` | `object_name`, `keep_original` | Converts text object to mesh for game export and editing. | ✅ Done |

**Use Cases:**
- 3D logos and signage
- Architectural dimension annotations
- Product labels and branding
- Game UI elements (3D text)

---

## 📤 Export Tools (`export_`)
*Tools for exporting scene or objects to various 3D file formats.*

### Implemented

| Tool Name | Arguments | Description | Status |
|-----------|-----------|-------------|--------|
| `export_glb` | `filepath`, `export_selected`, `export_animations`, `export_materials`, `apply_modifiers` | Exports to GLB/GLTF format (web, game engines). | ✅ Done |
| `export_fbx` | `filepath`, `export_selected`, `export_animations`, `apply_modifiers`, `mesh_smooth_type` | Exports to FBX format (industry standard). | ✅ Done |
| `export_obj` | `filepath`, `export_selected`, `apply_modifiers`, `export_materials`, `export_uvs`, `export_normals`, `triangulate` | Exports to OBJ format (universal mesh). | ✅ Done |

---

## 🎨 Sculpt Tools (`sculpt_`)
*Tools for Sculpt Mode operations (organic shape manipulation).*

### Implemented

| Tool Name | Arguments | Description | Status |
|-----------|-----------|-------------|--------|
| `sculpt_auto` | `operation` (smooth/inflate/flatten/sharpen), `strength`, `iterations`, `use_symmetry`, `symmetry_axis` | High-level sculpt operation using mesh filters. Applies to entire mesh. | ✅ Done |
| `sculpt_deform_region` | `center`, `radius`, `delta`, `strength`, `falloff`, `use_symmetry`, `symmetry_axis` | Deterministically deforms a local mesh region. Programmatic replacement for brush-style grab behavior. | ✅ Done |
| `sculpt_crease_region` | `center`, `radius`, `depth`, `pinch`, `falloff`, `use_symmetry`, `symmetry_axis` | Deterministically creates a local crease/groove region. Programmatic replacement for brush-style crease behavior. | ✅ Done |
| `sculpt_smooth_region` | `center`, `radius`, `strength`, `iterations`, `falloff`, `use_symmetry`, `symmetry_axis` | Deterministically smooths a local mesh region using edge-adjacency averaging. | ✅ Done |
| `sculpt_inflate_region` | `center`, `radius`, `amount`, `falloff`, `use_symmetry`, `symmetry_axis` | Deterministically inflates or deflates a local mesh region. | ✅ Done |
| `sculpt_pinch_region` | `center`, `radius`, `amount`, `falloff`, `use_symmetry`, `symmetry_axis` | Deterministically pinches a local mesh region toward the influence center. | ✅ Done |
| `sculpt_enable_dyntopo` | `object_name`, `detail_mode`, `detail_size`, `use_smooth_shading` | Enables Dynamic Topology with RELATIVE/CONSTANT/BRUSH/MANUAL modes. | ✅ Done |
| `sculpt_disable_dyntopo` | `object_name` | Disables Dynamic Topology. | ✅ Done |
| `sculpt_dyntopo_flood_fill` | `object_name` | Applies current detail level to entire mesh. | ✅ Done |

---

## ⚙️ System Tools (`system_`)
*System-level operations for mode switching, undo/redo, and file management.*

### Implemented

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

### Implemented

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

## 📥 Import Tools (`import_`)
*Tools for importing external 3D files and reference images.*

### Implemented

| Tool Name | Arguments | Description | Status |
|-----------|-----------|-------------|--------|
| `import_obj` | `filepath`, `use_split_objects`, `use_split_groups`, `global_scale`, `forward_axis`, `up_axis` | Imports OBJ file (geometry, UVs, normals). | ✅ Done |
| `import_fbx` | `filepath`, `use_custom_normals`, `use_image_search`, `ignore_leaf_bones`, `automatic_bone_orientation`, `global_scale` | Imports FBX file (geometry, materials, animations). | ✅ Done |
| `import_glb` | `filepath`, `import_pack_images`, `merge_vertices`, `import_shading` | Imports GLB/GLTF file (PBR materials, animations). | ✅ Done |
| `import_image_as_plane` | `filepath`, `name`, `location`, `size`, `align_axis`, `shader`, `use_transparency` | Imports image as textured plane (reference images, blueprints). | ✅ Done |

---

## 🔍 Extraction Tools (`extraction_`)
*Specialized analysis tools for the Automatic Workflow Extraction System (TASK-042).*

### Implemented

| Tool Name | Arguments | Description | Status |
|-----------|-----------|-------------|--------|
| `extraction_deep_topology` | `object_name` (str) | Deep topology analysis: vertex/edge/face counts, feature detection (bevels, insets, extrusions), base primitive estimation. | ✅ Done |
| `extraction_component_separate` | `object_name` (str), `min_vertex_count` (int) | Separates mesh into loose parts (components) for individual analysis. | ✅ Done |
| `extraction_detect_symmetry` | `object_name` (str), `tolerance` (float) | Detects symmetry planes (X/Y/Z) using KDTree matching with confidence scores. | ✅ Done |
| `extraction_edge_loop_analysis` | `object_name` (str) | Analyzes edge loops: parallel groups, chamfer detection, support loop candidates. | ✅ Done |
| `extraction_face_group_analysis` | `object_name` (str), `angle_threshold` (float) | Analyzes face groups by normal, height levels, inset/extrusion detection. | ✅ Done |
| `extraction_render_angles` | `object_name` (str), `angles` (list), `resolution` (int), `output_dir` (str) | Renders object from multiple angles (front, back, left, right, top, iso) for LLM Vision analysis. | ✅ Done |

**Use Cases:**
- Analyzing imported 3D models for workflow extraction
- Detecting mesh features (bevels, insets, extrusions)
- Component separation and symmetry detection
- Multi-angle rendering for LLM-based semantic analysis

---

## 🦴 Armature Tools (`armature_`)
*Skeletal animation and rigging tools for character/mechanical animation.*

### Implemented

| Tool Name | Arguments | Description | Status |
|-----------|-----------|-------------|--------|
| `armature_create` | `name`, `location`, `bone_name`, `bone_length` | Creates armature with initial bone for rigging. | ✅ Done |
| `armature_add_bone` | `armature_name`, `bone_name`, `head`, `tail`, `parent_bone`, `use_connect` | Adds new bone to existing armature with optional parenting. | ✅ Done |
| `armature_bind` | `mesh_name`, `armature_name`, `bind_type` (AUTO/ENVELOPE/EMPTY) | Binds mesh to armature with automatic weight calculation. | ✅ Done |
| `armature_pose_bone` | `armature_name`, `bone_name`, `rotation`, `location`, `scale` | Poses armature bone (rotation/location/scale in Pose Mode). | ✅ Done |
| `armature_weight_paint_assign` | `object_name`, `vertex_group`, `weight`, `mode` (REPLACE/ADD/SUBTRACT) | Assigns weights to selected vertices for manual rigging. | ✅ Done |
| `armature_get_data` | `object_name`, `include_pose` | Returns armature bones and hierarchy (optional pose data). | ✅ Done |

**Use Cases:**
- Character rigging for games/film
- Mechanical rigs (robot arms, machines)
- Procedural animation setups
- Weight painting for precise deformation control

---

## 🤖 Workflow Catalog & Router Tools (`workflow_catalog`, `router_*`)
*Tools for browsing/importing workflows and controlling the Router Supervisor.*

This family is the goal-first orchestration entry layer.
On guided surfaces, `router_set_goal` is the default production starting point and `workflow_catalog`/`browse_workflows` is the main discovery bridge into bounded workflow behavior.

### Implemented

| Tool Name | Arguments | Description | Status |
|-----------|-----------|-------------|--------|
| `workflow_catalog` | `action` (list/get/search/import/import_init/import_append/import_finalize/import_abort), `workflow_name`, `query`, `top_k`, `threshold`, `filepath`, `overwrite`, `content`, `content_type`, `source_name`, `session_id`, `chunk_data`, `chunk_index`, `total_chunks` | Lists/searches/inspects workflow definitions and imports YAML/JSON via file path, inline content, or chunked sessions. Returns `needs_input` when a name conflict requires overwrite confirmation. | ✅ Done |
| `reference_images` | `action` (attach/list/remove/clear), `source_path`, `reference_id`, `label`, `notes`, `target_object`, `target_view` | Goal-scoped reference image intake and lifecycle surface. Copies local image paths into session temp storage, lists active references, removes one by id, or clears the whole current-goal reference set. | ✅ Done |
| `router_set_goal` | `goal` (str), `resolved_params` (dict, optional) | Sets the active build goal for the router session. Returns status (ready/needs_input/no_match/disabled/error), matched workflow info, resolved params with sources, unresolved inputs for follow-up calls, and explicit `guided_handoff` metadata when the intended continuation is guided manual build/utility instead of workflow execution. | ✅ Done |
| `router_get_status` | *none* | Returns current router session state, visibility diagnostics, pending clarification info, and router/component stats. | ✅ Done |
| `router_clear_goal` | *none* | Clears the current modeling goal. | ✅ Done |

**Use Cases:**
- Preview/search similar workflows and inspect their steps
- Setting modeling goals for intelligent workflow expansion
- Goal-first session bootstrap and follow-up parameter resolution through one entry tool

---

## 🛠 Planned / In Progress

None.
