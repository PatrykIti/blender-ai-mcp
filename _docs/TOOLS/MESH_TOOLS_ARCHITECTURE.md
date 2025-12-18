# Mesh Tools Architecture (Edit Mode)

Mesh tools operate on the geometry (vertices, edges, faces) of the active mesh object.
**Context:** These tools automatically switch Blender to **Edit Mode** if necessary.

---

# 1. mesh_select_all ✅ Done
Selects or deselects all geometry elements.

Example:
```json
{
  "tool": "mesh_select_all",
  "args": {
    "deselect": true
  }
}
```

---

# 2. mesh_delete_selected ✅ Done
Deletes selected geometry elements.

Args:
- type: str ('VERT', 'EDGE', 'FACE')

Example:
```json
{
  "tool": "mesh_delete_selected",
  "args": {
    "type": "FACE"
  }
}
```

---

# 3. mesh_select_by_index ✅ Done
Selects specific geometry elements by their index using BMesh.
Supports different selection modes for precise control.

Args:
- indices: List[int]
- type: str ('VERT', 'EDGE', 'FACE')
- selection_mode: str ('SET', 'ADD', 'SUBTRACT') - Default is 'SET'

Example:
```json
{
  "tool": "mesh_select_by_index",
  "args": {
    "indices": [0, 1, 4, 5],
    "type": "VERT",
    "selection_mode": "SET"
  }
}
```

---

# 4. mesh_extrude_region ✅ Done
Extrudes the currently selected region (vertices, edges, or faces) and optionally moves it.
This is the primary tool for "growing" geometry.

Args:
- move: List[float] (optional [x, y, z] translation vector)

Example:
```json
{
  "tool": "mesh_extrude_region",
  "args": {
    "move": [0.0, 0.0, 2.0]
  }
}
```

---

# 5. mesh_fill_holes ✅ Done
Creates a face from selected edges or vertices (equivalent to pressing 'F').

Example:
```json
{
  "tool": "mesh_fill_holes",
  "args": {}
}
```

---

# 6. mesh_bevel ✅ Done
Bevels selected edges or vertices.

Args:
- offset: float (size of bevel)
- segments: int (roundness)
- affect: str ('EDGES' or 'VERTICES')

Example:
```json
{
  "tool": "mesh_bevel",
  "args": {
    "offset": 0.1,
    "segments": 2,
    "affect": "EDGES"
  }
}
```

---

# 7. mesh_loop_cut ✅ Done
Adds cuts to the mesh geometry. Currently uses subdivision logic on selected edges.

Args:
- number_cuts: int

Example:
```json
{
  "tool": "mesh_loop_cut",
  "args": {
    "number_cuts": 2
  }
}
```

---

# 8. mesh_inset ✅ Done
Insets selected faces (creates smaller faces inside).

Args:
- thickness: float
- depth: float (optional extrude/inset depth)

Example:
```json
{
  "tool": "mesh_inset",
  "args": {
    "thickness": 0.05,
    "depth": 0.0
  }
}
```

---

# 9. mesh_boolean ✅ Done
Performs a destructive boolean operation in Edit Mode.
Formula: Unselected - Selected (for DIFFERENCE).

Args:
- operation: str ('DIFFERENCE', 'UNION', 'INTERSECT')
- solver: str ('FAST', 'EXACT')

Example:
```json
{
  "tool": "mesh_boolean",
  "args": {
    "operation": "DIFFERENCE"
  }
}
```

---

# 10. mesh_merge_by_distance ✅ Done
Merges vertices that are close to each other (Remove Doubles).

Args:
- distance: float (threshold)

Example:
```json
{
  "tool": "mesh_merge_by_distance",
  "args": {
    "distance": 0.001
  }
}
```

---

# 11. mesh_subdivide ✅ Done
Subdivides selected geometry (Faces/Edges).

Args:
- number_cuts: int
- smoothness: float (0.0 - 1.0)

Example:
```json
{
  "tool": "mesh_subdivide",
  "args": {
    "number_cuts": 1,
    "smoothness": 0.0
  }
}
```

---

# 12. mesh_smooth ✅ Done
Smooths selected vertices using Laplacian smoothing.

**Tag:** `[EDIT MODE][SELECTION-BASED][NON-DESTRUCTIVE]`

Args:
- iterations: int (1-100) - Number of smoothing passes
- factor: float (0.0-1.0) - Smoothing strength

Example:
```json
{
  "tool": "mesh_smooth",
  "args": {
    "iterations": 5,
    "factor": 0.5
  }
}
```

Use Case:
- Refining organic shapes
- Removing hard edges
- Smoothing after boolean operations

---

# 13. mesh_flatten ✅ Done
Flattens selected vertices to a plane perpendicular to specified axis.

**Tag:** `[EDIT MODE][SELECTION-BASED][DESTRUCTIVE]`

Args:
- axis: str ("X", "Y", or "Z") - Axis to flatten along

Example:
```json
{
  "tool": "mesh_flatten",
  "args": {
    "axis": "Z"
  }
}
```

Use Case:
- Creating perfectly flat surfaces (floors, walls)
- Aligning geometry to planes
- Preparing cutting planes for boolean operations

Behavior:
- X: All vertices get same X coordinate (creates YZ plane)
- Y: All vertices get same Y coordinate (creates XZ plane)
- Z: All vertices get same Z coordinate (creates XY plane)

---

# 14. mesh_list_groups ✅ Done
Lists vertex/face groups defined on the mesh object.

**Tag:** `[MESH][SAFE][READ-ONLY]`

Args:
- object_name: str
- group_type: str ('VERTEX' or 'FACE') - Default 'VERTEX'

Example:
```json
{
  "tool": "mesh_list_groups",
  "args": {
    "object_name": "Cube",
    "group_type": "VERTEX"
  }
}
```

---

# 15. mesh_select_loop ✅ Done

Selects an edge loop (continuous line of edges) based on target edge index.

**Tag:** `[EDIT MODE][SELECTION-BASED][SAFE]`

Args:
- edge_index: int (target edge to start loop selection)

Example:
```json
{
  "tool": "mesh_select_loop",
  "args": {
    "edge_index": 4
  }
}
```

Use Case:
- Selecting borders, seams, or topological rings
- Preparing edges for bevel or extrusion

---

# 16. mesh_select_ring ✅ Done

Selects an edge ring (parallel edges) based on target edge index.

**Tag:** `[EDIT MODE][SELECTION-BASED][SAFE]`

Args:
- edge_index: int (target edge to start ring selection)

Example:
```json
{
  "tool": "mesh_select_ring",
  "args": {
    "edge_index": 4
  }
}
```

Use Case:
- Selecting parallel edge bands
- Preparing for loop cuts or inset operations

---

# 17. mesh_select_linked ✅ Done

Selects all geometry connected to current selection (islands).

**Tag:** `[EDIT MODE][SELECTION-BASED][SAFE]`
**Priority:** 🔴 CRITICAL for mesh_boolean after join_objects

Args: None

Example:
```json
{
  "tool": "mesh_select_linked",
  "args": {}
}
```

Use Case:
- Selecting mesh islands after join_objects
- Preparing specific geometry for boolean operations

---

# 18. mesh_select_more ✅ Done

Grows the current selection by one step.

**Tag:** `[EDIT MODE][SELECTION-BASED][SAFE]`

Args: None

Example:
```json
{
  "tool": "mesh_select_more",
  "args": {}
}
```

---

# 19. mesh_select_less ✅ Done

Shrinks the current selection by one step.

**Tag:** `[EDIT MODE][SELECTION-BASED][SAFE]`

Args: None

Example:
```json
{
  "tool": "mesh_select_less",
  "args": {}
}
```

---

# 20. mesh_get_vertex_data ✅ Done

Returns vertex positions and selection states for programmatic analysis.

**Tag:** `[EDIT MODE][READ-ONLY][SAFE]`
**Priority:** 🔴 CRITICAL - Foundation for programmatic selection

Args:
- object_name: str
- selected_only: bool (default False)

Returns:
```json
{
  "vertex_count": 8,
  "selected_count": 4,
  "returned_count": 8,
  "vertices": [
    {"index": 0, "position": [1.0, 1.0, 1.0], "selected": true},
    {"index": 1, "position": [1.0, -1.0, 1.0], "selected": false}
  ]
}
```

Example:
```json
{
  "tool": "mesh_get_vertex_data",
  "args": {
    "object_name": "Cube",
    "selected_only": false
  }
}
```

Use Case:
- Analyzing vertex positions for selection decisions
- Foundation for mesh_select_by_location validation

---

# 21. mesh_select_by_location ✅ Done

Selects geometry within coordinate range on specified axis.

**Tag:** `[EDIT MODE][SELECTION-BASED][SAFE]`

Args:
- axis: str ('X', 'Y', 'Z')
- min_coord: float
- max_coord: float
- mode: str ('VERT', 'EDGE', 'FACE') - default 'VERT'

Example:
```json
{
  "tool": "mesh_select_by_location",
  "args": {
    "axis": "Z",
    "min_coord": 0.5,
    "max_coord": 2.0,
    "mode": "VERT"
  }
}
```

Use Case:
- "Select all vertices above Z=0.5"
- Spatial operations without knowing exact indices

---

# 22. mesh_select_boundary ✅ Done

Selects boundary edges (1 adjacent face) or boundary vertices.

**Tag:** `[EDIT MODE][SELECTION-BASED][SAFE]`
**Priority:** 🔴 CRITICAL for mesh_fill_holes workflow

Args:
- mode: str ('EDGE', 'VERT') - default 'EDGE'

Example:
```json
{
  "tool": "mesh_select_boundary",
  "args": {
    "mode": "EDGE"
  }
}
```

Use Case:
- Targeting specific holes for mesh_fill_holes
- Identifying open edges for quality checks
- Selecting boundary loops for extrusion

---

# 23. mesh_randomize ✅ Done

Randomizes vertex positions for organic surface variations.

**Tag:** `[EDIT MODE][SELECTION-BASED][DESTRUCTIVE]`

Args:
- amount: float (maximum displacement, default 0.1)
- uniform: float (uniform random factor 0-1, default 0.0)
- normal: float (normal-based factor 0-1, default 0.0)
- seed: int (random seed, 0 = random)

Example:
```json
{
  "tool": "mesh_randomize",
  "args": {
    "amount": 0.05,
    "uniform": 0.5,
    "normal": 0.0,
    "seed": 42
  }
}
```

Use Case:
- Creating organic terrain variations
- Adding imperfections to mechanical surfaces
- Generating natural-looking irregularities

---

# 24. mesh_shrink_fatten ✅ Done

Moves vertices along their normals (inflate/deflate effect).

**Tag:** `[EDIT MODE][SELECTION-BASED][DESTRUCTIVE]`

Args:
- value: float (distance along normals, + outward, - inward)

Example:
```json
{
  "tool": "mesh_shrink_fatten",
  "args": {
    "value": 0.1
  }
}
```

Use Case:
- Inflating geometry for organic shapes
- Creating shell/thickness effects
- Sculpting surface details

---

# 25. mesh_create_vertex_group ✅ Done

Creates a new vertex group on mesh object.

**Tag:** `[MESH][SAFE]`

Args:
- object_name: str (target mesh object)
- name: str (name for new group)

Example:
```json
{
  "tool": "mesh_create_vertex_group",
  "args": {
    "object_name": "Cube",
    "name": "TopVertices"
  }
}
```

Use Case:
- Organizing vertices for armature weights
- Preparing selection sets for modifiers
- Grouping vertices for later operations

---

# 26. mesh_assign_to_group ✅ Done

Assigns selected vertices to vertex group with weight.

**Tag:** `[EDIT MODE][SELECTION-BASED][SAFE]`

Args:
- object_name: str (target mesh object)
- group_name: str (vertex group name)
- weight: float (weight value 0.0-1.0, default 1.0)

Example:
```json
{
  "tool": "mesh_assign_to_group",
  "args": {
    "object_name": "Cube",
    "group_name": "TopVertices",
    "weight": 1.0
  }
}
```

Use Case:
- Assigning bone weights for rigging
- Setting up modifier influence areas
- Creating soft selection masks

---

# 27. mesh_remove_from_group ✅ Done

Removes selected vertices from vertex group.

**Tag:** `[EDIT MODE][SELECTION-BASED][SAFE]`

Args:
- object_name: str (target mesh object)
- group_name: str (vertex group name)

Example:
```json
{
  "tool": "mesh_remove_from_group",
  "args": {
    "object_name": "Cube",
    "group_name": "TopVertices"
  }
}
```

Use Case:
- Refining vertex group assignments
- Correcting weight painting mistakes
- Adjusting modifier influence

---

# 28. mesh_bisect ✅ Done

Cuts mesh along a plane defined by point and normal.

**Tag:** `[EDIT MODE][SELECTION-BASED][DESTRUCTIVE]`

Args:
- plane_co: [x, y, z] (point on the cutting plane)
- plane_no: [x, y, z] (normal direction of the plane)
- clear_inner: bool (remove geometry on negative side, default false)
- clear_outer: bool (remove geometry on positive side, default false)
- fill: bool (fill the cut with a face, default false)

Example:
```json
{
  "tool": "mesh_bisect",
  "args": {
    "plane_co": [0, 0, 0],
    "plane_no": [0, 0, 1],
    "clear_outer": true,
    "fill": true
  }
}
```

Use Case:
- Cutting meshes in half
- Creating cross-sections
- Removing parts of geometry above/below a plane

---

# 29. mesh_edge_slide ✅ Done

Slides selected edges along mesh topology.

**Tag:** `[EDIT MODE][SELECTION-BASED][DESTRUCTIVE]`

Args:
- value: float (-1.0 to 1.0, slide amount)

Example:
```json
{
  "tool": "mesh_edge_slide",
  "args": {
    "value": 0.5
  }
}
```

Use Case:
- Repositioning edge loops without changing topology
- Fine-tuning mesh flow
- Adjusting topology for better deformation

---

# 30. mesh_vert_slide ✅ Done

Slides selected vertices along connected edges.

**Tag:** `[EDIT MODE][SELECTION-BASED][DESTRUCTIVE]`

Args:
- value: float (-1.0 to 1.0, slide amount)

Example:
```json
{
  "tool": "mesh_vert_slide",
  "args": {
    "value": -0.3
  }
}
```

Use Case:
- Repositioning vertices along edge paths
- Precise vertex placement
- Maintaining edge flow while adjusting position

---

# 31. mesh_triangulate ✅ Done

Converts selected faces to triangles.

**Tag:** `[EDIT MODE][SELECTION-BASED][DESTRUCTIVE]`

Args: None (operates on selection)

Example:
```json
{
  "tool": "mesh_triangulate",
  "args": {}
}
```

Use Case:
- Preparing mesh for game engine export
- Ensuring consistent topology
- Boolean cleanup

---

# 32. mesh_remesh_voxel ✅ Done

Performs voxel remesh on the object.

**Tag:** `[OBJECT MODE][DESTRUCTIVE]`

Args:
- voxel_size: float (size of voxels, default 0.1)
- adaptivity: float (polygon reduction in flat areas, 0-1, default 0)

Example:
```json
{
  "tool": "mesh_remesh_voxel",
  "args": {
    "voxel_size": 0.05,
    "adaptivity": 0.5
  }
}
```

Use Case:
- Creating uniform topology after boolean operations
- Preparing mesh for sculpting
- Cleaning up complex geometry
- NOTE: Destroys UVs, vertex groups, and existing topology!

---

# 33. mesh_transform_selected ✅ Done

Transforms selected geometry (move/rotate/scale).

**Tag:** `[EDIT MODE][SELECTION-BASED][DESTRUCTIVE]`
**Priority:** 🔴 CRITICAL - Unlocks ~80% of modeling tasks

Args:
- translate: [x, y, z] or string "[x, y, z]" (optional) - Translation vector
- rotate: [x, y, z] or string "[x, y, z]" (optional) - Rotation in radians per axis
- scale: [x, y, z] or string "[x, y, z]" (optional) - Scale factors
- pivot: str ('MEDIAN_POINT', 'BOUNDING_BOX_CENTER', 'CURSOR', 'INDIVIDUAL_ORIGINS', 'ACTIVE_ELEMENT')

Example:
```json
{
  "tool": "mesh_transform_selected",
  "args": {
    "translate": [0, 0, 2],
    "rotate": [0, 0, 1.5708],
    "scale": [1, 1, 1],
    "pivot": "MEDIAN_POINT"
  }
}
```

Use Case:
- Repositioning geometry after selection
- Rotating faces/edges/vertices
- Scaling selected elements
- Combined transformations in single call

---

# 34. mesh_bridge_edge_loops ✅ Done

Bridges two edge loops with faces.

**Tag:** `[EDIT MODE][SELECTION-BASED][DESTRUCTIVE]`

Args:
- number_cuts: int (default 0) - Number of intermediate cuts
- interpolation: str ('LINEAR', 'PATH', 'SURFACE') - Bridge interpolation type
- smoothness: float (0.0-1.0) - Smoothness factor
- twist: int (default 0) - Twist offset

Example:
```json
{
  "tool": "mesh_bridge_edge_loops",
  "args": {
    "number_cuts": 4,
    "interpolation": "SURFACE",
    "smoothness": 1.0
  }
}
```

Use Case:
- Connecting two separate edge loops
- Creating connecting geometry between holes
- Building tube-like structures

---

# 35. mesh_duplicate_selected ✅ Done

Duplicates selected geometry within the same mesh.

**Tag:** `[EDIT MODE][SELECTION-BASED][DESTRUCTIVE]`

Args:
- translate: [x, y, z] (optional) - Offset for duplicated geometry

Example:
```json
{
  "tool": "mesh_duplicate_selected",
  "args": {
    "translate": [2, 0, 0]
  }
}
```

Use Case:
- Creating copies of geometry within mesh
- Building repetitive structures
- Duplicating and offsetting for patterns

---

# 36. mesh_spin ✅ Done

Spins/lathes selected geometry around an axis.

**Tag:** `[EDIT MODE][SELECTION-BASED][DESTRUCTIVE]`

Args:
- steps: int (default 12) - Number of steps/segments
- angle: float (default 6.283185 = 360°) - Total angle in radians
- axis: str ('X', 'Y', 'Z') - Axis to spin around
- center: [x, y, z] (optional) - Center point (default: 3D cursor)
- dupli: bool (default False) - Duplicate instead of extrude

Example:
```json
{
  "tool": "mesh_spin",
  "args": {
    "steps": 32,
    "angle": 6.283185,
    "axis": "Z",
    "center": [0, 0, 0]
  }
}
```

Use Case:
- Creating vases, bowls, glasses (lathe)
- Circular patterns
- Rotational geometry

---

# 37. mesh_screw ✅ Done

Creates spiral/screw/helical geometry.

**Tag:** `[EDIT MODE][SELECTION-BASED][DESTRUCTIVE]`

Args:
- steps: int (default 12) - Steps per turn
- turns: int (default 1) - Number of complete rotations
- axis: str ('X', 'Y', 'Z') - Axis to screw around
- center: [x, y, z] (optional) - Center point (default: 3D cursor)
- offset: float (default 0.0) - Distance per turn (pitch)

Example:
```json
{
  "tool": "mesh_screw",
  "args": {
    "steps": 32,
    "turns": 3,
    "axis": "Z",
    "offset": 0.5
  }
}
```

Use Case:
- Creating springs
- Threads/screws
- Spiral staircases
- Helical patterns

---

# 38. mesh_add_vertex ✅ Done

Adds a single vertex at the specified position.

**Tag:** `[EDIT MODE][DESTRUCTIVE]`

Args:
- position: [x, y, z] - Coordinates for new vertex

Example:
```json
{
  "tool": "mesh_add_vertex",
  "args": {
    "position": [1, 2, 3]
  }
}
```

Use Case:
- Building geometry from scratch
- Adding connection points
- Creating guide vertices

---

# 39. mesh_add_edge_face ✅ Done

Creates an edge or face from selected vertices.

**Tag:** `[EDIT MODE][SELECTION-BASED][DESTRUCTIVE]`

Args: None (operates on selection)

Behavior:
- 2 vertices selected → creates edge
- 3+ vertices selected → creates face

Example:
```json
{
  "tool": "mesh_add_edge_face",
  "args": {}
}
```

Use Case:
- Connecting vertices with edges
- Filling gaps with faces
- Manual geometry construction
- Equivalent to pressing 'F' key in Blender

---

# 40. mesh_edge_crease ✅ Done

Sets crease weight on selected edges for Subdivision Surface modifier control.

**Tag:** `[EDIT MODE][SELECTION-BASED][NON-DESTRUCTIVE]`

Args:
- crease_value: float (0.0 to 1.0)
  - 0.0 = fully smoothed (no crease effect)
  - 1.0 = fully sharp (edge remains sharp after subdivision)

Example:
```json
{
  "tool": "mesh_edge_crease",
  "args": {
    "crease_value": 1.0
  }
}
```

Use Case:
- Hard-surface modeling (weapons, vehicles, devices)
- Maintaining sharp edges while having smooth surfaces elsewhere
- Architectural details (window frames, door edges)

Workflow: BEFORE → mesh_select_targeted(action="loop") | AFTER → modeling_add_modifier(type="SUBSURF")

---

# 41. mesh_bevel_weight ✅ Done

Sets bevel weight on selected edges for selective beveling with Bevel modifier.

**Tag:** `[EDIT MODE][SELECTION-BASED][NON-DESTRUCTIVE]`

Args:
- weight: float (0.0 to 1.0)
  - 0.0 = no bevel effect
  - 1.0 = full bevel effect

Example:
```json
{
  "tool": "mesh_bevel_weight",
  "args": {
    "weight": 1.0
  }
}
```

Use Case:
- Product design (selective edge beveling)
- Hard-surface modeling with controlled bevel application
- Architectural details

Workflow: BEFORE → mesh_select_targeted(action="loop") | AFTER → modeling_add_modifier(type="BEVEL", limit_method="WEIGHT")

---

# 42. mesh_mark_sharp ✅ Done

Marks or clears sharp edges for Auto Smooth and Edge Split modifier.

**Tag:** `[EDIT MODE][SELECTION-BASED][NON-DESTRUCTIVE]`

Args:
- action: str ("mark" or "clear")

Example:
```json
{
  "tool": "mesh_mark_sharp",
  "args": {
    "action": "mark"
  }
}
```

Use Case:
- Visual edge definition
- Smooth shading control
- Normal maps preparation
- Edge Split modifier workflow

Sharp edges affect:
- Auto Smooth: Splits normals at sharp edges for flat shading
- Edge Split modifier: Creates hard edges without geometry duplication
- Normal display and shading calculations

---

# 43. mesh_dissolve ✅ Done (TASK-030-1)

Dissolves selected geometry while preserving shape. Essential for mesh cleanup.

**Tag:** `[EDIT MODE][SELECTION-BASED][DESTRUCTIVE]`

Args:
- dissolve_type: str ("limited", "verts", "edges", "faces") - default: "limited"
- angle_limit: float (degrees, for limited dissolve) - default: 5.0
- use_face_split: bool - default: false
- use_boundary_tear: bool - default: false

Example:
```json
{
  "tool": "mesh_dissolve",
  "args": {
    "dissolve_type": "limited",
    "angle_limit": 5.0
  }
}
```

Dissolve Types:
- **limited**: Auto-dissolves edges below angle threshold (most common cleanup)
- **verts**: Dissolves selected vertices, merging connected edges/faces
- **edges**: Dissolves selected edges, merging adjacent faces
- **faces**: Dissolves selected faces, removing them while preserving boundaries

Use Case:
- Boolean operation cleanup
- Removing unnecessary edge loops
- Import cleanup (OBJ/FBX)
- Reducing mesh complexity

Workflow: BEFORE → mesh_select(action="all") | Limited dissolve is ideal for cleanup

---

# 44. mesh_tris_to_quads ✅ Done (TASK-030-2)

Converts triangles to quads where possible based on angle thresholds.

**Tag:** `[EDIT MODE][SELECTION-BASED][DESTRUCTIVE]`

Args:
- face_threshold: float (degrees, max angle between face normals) - default: 40.0
- shape_threshold: float (degrees, max shape deviation) - default: 40.0

Example:
```json
{
  "tool": "mesh_tris_to_quads",
  "args": {
    "face_threshold": 40.0,
    "shape_threshold": 40.0
  }
}
```

Use Case:
- Cleaning triangulated imports (OBJ, FBX, STL)
- Post-boolean cleanup
- Preparing mesh for subdivision surface

Higher thresholds = more aggressive conversion (may create distorted quads)
Lower thresholds = conservative conversion (better quality but fewer conversions)

Workflow: BEFORE → mesh_select(action="all") | AFTER → mesh_dissolve (optional cleanup)

---

# 45. mesh_normals_make_consistent ✅ Done (TASK-030-3)

Recalculates normals to face consistently outward (or inward).

**Tag:** `[EDIT MODE][SELECTION-BASED][NON-DESTRUCTIVE]`

Args:
- inside: bool (true = normals point inward) - default: false

Example:
```json
{
  "tool": "mesh_normals_make_consistent",
  "args": {
    "inside": false
  }
}
```

Use Case:
- Fixing inverted faces (black patches in render)
- Inconsistent shading correction
- Boolean operation artifacts
- Import cleanup

Symptoms of flipped normals:
- Black faces in rendered view
- Incorrect lighting/shadows
- Backface culling issues in game engines
- Problems with boolean operations

Workflow: BEFORE → mesh_select(action="all") | Essential after import or boolean ops

---

# 46. mesh_decimate ✅ Done (TASK-030-4)

Reduces polycount while preserving shape (Edit Mode operation).

**Tag:** `[EDIT MODE][SELECTION-BASED][DESTRUCTIVE]`

Args:
- ratio: float (target ratio, 0.0-1.0) - default: 0.5
- use_symmetry: bool - default: false
- symmetry_axis: str ("X", "Y", "Z") - default: "X"

Example:
```json
{
  "tool": "mesh_decimate",
  "args": {
    "ratio": 0.5,
    "use_symmetry": false
  }
}
```

Use Case:
- LOD (Level of Detail) generation
- Game-ready asset optimization
- Retopology preparation
- Reducing sculpt detail

For whole-object decimation, consider `modeling_add_modifier(type="DECIMATE")` which offers more control (collapse/unsubdiv/planar modes).

ratio values:
- 1.0 = keep all faces (no change)
- 0.5 = keep 50% of faces
- 0.25 = keep 25% of faces (aggressive reduction)

Workflow: BEFORE → mesh_select(action="all") | Use symmetry for symmetric meshes

---

# 47. mesh_set_proportional_edit ✅ Done (TASK-038)

Configures proportional editing mode for organic deformations.

**Tag:** `[EDIT MODE][CONFIGURATION][SAFE]`

Args:
- enabled: bool (enable/disable proportional editing) - default true
- falloff_type: str ("SMOOTH", "SPHERE", "ROOT", "INVERSE_SQUARE", "SHARP", "LINEAR", "CONSTANT", "RANDOM") - default "SMOOTH"
- size: float (influence radius) - default 1.0
- use_connected: bool (only affect connected geometry) - default false

Example:
```json
{
  "tool": "mesh_set_proportional_edit",
  "args": {
    "enabled": true,
    "falloff_type": "SMOOTH",
    "size": 2.0,
    "use_connected": false
  }
}
```

Falloff Types:
- **SMOOTH** - Gradual falloff (default, most natural)
- **SPHERE** - Spherical falloff (sharp boundary)
- **ROOT** - Square root falloff (medium transition)
- **INVERSE_SQUARE** - Strong center influence
- **SHARP** - Sharp falloff (concentrated effect)
- **LINEAR** - Linear falloff (even transition)
- **CONSTANT** - All affected vertices move equally
- **RANDOM** - Random influence (organic variation)

Use Case:
- Organic surface deformation
- Natural-looking vertex adjustments
- Soft modifications to mesh areas
- Mountain/terrain modeling

Workflow: Set proportional edit → mesh_transform_selected (transforms use proportional influence)

---

# Rules
1. **Prefix `mesh_`**: All tools must start with this prefix.
2. **Edit Mode**: Most tools operate in Edit Mode. Introspection tools (like `list_groups`) may work in Object Mode.
3. **BMesh**: Advanced operations should use `bmesh` for consistent indexing.
