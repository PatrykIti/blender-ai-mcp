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

# Rules
1. **Prefix `mesh_`**: All tools must start with this prefix.
2. **Edit Mode**: Most tools operate in Edit Mode. Introspection tools (like `list_groups`) may work in Object Mode.
3. **BMesh**: Advanced operations should use `bmesh` for consistent indexing.
