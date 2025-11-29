# TASK-030: Mesh Cleanup & Optimization

**Priority:** 🔴 High
**Category:** Mesh Tools
**Estimated Effort:** Medium
**Dependencies:** TASK-011 (Edit Mode Foundation)

---

## Overview

Cleanup tools are **essential for game dev** - they optimize geometry, remove unnecessary vertices/edges, and fix common mesh issues. Without these, meshes have excessive polycount and rendering issues.

**Use Cases:**
- Low-poly game assets (removing edge loops)
- Retopology cleanup
- Import cleanup (after OBJ/FBX import)
- Boolean operation cleanup

---

## Sub-Tasks

### TASK-030-1: mesh_dissolve

**Status:** 🚧 To Do

Dissolves selected geometry while preserving shape.

```python
@mcp.tool()
def mesh_dissolve(
    ctx: Context,
    dissolve_type: Literal["verts", "edges", "faces", "limited"] = "limited",
    angle_limit: float = 5.0,  # degrees, for limited dissolve
    use_face_split: bool = False,
    use_boundary_tear: bool = False,
    object_name: str | None = None
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Dissolves geometry.

    Types:
    - verts: Dissolve selected vertices
    - edges: Dissolve selected edges
    - faces: Dissolve selected faces
    - limited: Auto-dissolve edges below angle threshold (cleanup)

    Workflow: BEFORE → mesh_select(action="all") | Limited dissolve is great for cleanup
    """
```

**Blender API:**
```python
if dissolve_type == "verts":
    bpy.ops.mesh.dissolve_verts()
elif dissolve_type == "edges":
    bpy.ops.mesh.dissolve_edges()
elif dissolve_type == "faces":
    bpy.ops.mesh.dissolve_faces()
elif dissolve_type == "limited":
    bpy.ops.mesh.dissolve_limited(angle_limit=math.radians(angle_limit))
```

---

### TASK-030-2: mesh_tris_to_quads

**Status:** 🚧 To Do

Converts triangles to quads where possible.

```python
@mcp.tool()
def mesh_tris_to_quads(
    ctx: Context,
    face_threshold: float = 40.0,  # degrees
    shape_threshold: float = 40.0,  # degrees
    object_name: str | None = None
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Converts triangles to quads.

    Useful for:
    - Cleaning up triangulated imports (OBJ, FBX)
    - Post-boolean cleanup
    - Preparing mesh for subdivision

    Workflow: BEFORE → mesh_select(action="all")
    """
```

**Blender API:**
```python
bpy.ops.mesh.tris_convert_to_quads(
    face_threshold=math.radians(face_threshold),
    shape_threshold=math.radians(shape_threshold)
)
```

---

### TASK-030-3: mesh_normals_make_consistent

**Status:** 🚧 To Do

Recalculates normals to face consistently outward.

```python
@mcp.tool()
def mesh_normals_make_consistent(
    ctx: Context,
    inside: bool = False,  # True = flip to inside
    object_name: str | None = None
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Recalculates normals.

    Fixes:
    - Inverted faces (black patches in render)
    - Inconsistent shading
    - Boolean operation artifacts

    Workflow: BEFORE → mesh_select(action="all")
    """
```

**Blender API:**
```python
bpy.ops.mesh.normals_make_consistent(inside=inside)
```

---

### TASK-030-4: mesh_decimate (Optional)

**Status:** 🚧 To Do

Reduces polycount while preserving shape.

```python
@mcp.tool()
def mesh_decimate(
    ctx: Context,
    ratio: float = 0.5,  # 0.0-1.0, target ratio
    use_symmetry: bool = False,
    symmetry_axis: Literal["X", "Y", "Z"] = "X",
    object_name: str | None = None
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Decimates selected geometry.

    For whole-object decimation, use modeling_add_modifier(type="DECIMATE").
    This tool works on selection only.
    """
```

**Blender API:**
```python
bpy.ops.mesh.decimate(ratio=ratio)
```

---

## Implementation Notes

1. `mesh_dissolve` with `limited` type is the most commonly used cleanup tool
2. Return statistics: "Dissolved X vertices, Y edges" or "Converted X triangles to Y quads"
3. `mesh_normals_make_consistent` should warn if mesh is not manifold

---

## Testing Requirements

- [ ] Unit tests for each tool
- [ ] E2E test: Import triangulated mesh → tris_to_quads → verify quad count
- [ ] E2E test: Boolean operation → dissolve limited → verify cleanup
- [ ] E2E test: Inverted normals → make consistent → verify render
