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

# Rules
1. **Prefix `mesh_`**: All tools must start with this prefix.
2. **Edit Mode**: These tools MUST operate in Edit Mode. The handler handles the switch.
3. **BMesh**: Advanced operations should use `bmesh` for consistent indexing.