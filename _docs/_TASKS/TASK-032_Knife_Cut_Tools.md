# TASK-032: Knife & Cut Tools

**Priority:** 🟠 High
**Category:** Mesh Tools
**Estimated Effort:** Medium
**Dependencies:** TASK-011 (Edit Mode Foundation)

---

## Overview

Knife and cut tools enable **precise geometry cutting** - essential for hard-surface modeling, architectural details, and panel lines.

**Use Cases:**
- Hard-surface panel cuts (sci-fi, vehicles)
- Window/door cutouts in architecture
- Logo/pattern projection
- Splitting geometry for material assignment

---

## Sub-Tasks

### TASK-032-1: mesh_knife_project

**Status:** 🚧 To Do

Projects knife cut from view using selected edges/faces as cutter.

```python
@mcp.tool()
def mesh_knife_project(
    ctx: Context,
    cut_through: bool = True,
    object_name: str | None = None
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Projects cut from selected geometry.

    How it works:
    1. Select cutting geometry (edges/faces in another object or same object)
    2. Knife project cuts the mesh where the selection projects from view

    Use case: Cut logo shape into surface, panel lines, window frames.

    Note: Requires specific view angle - best used with orthographic views.

    Workflow: BEFORE → Position view orthographically, select cutter geometry
    """
```

**Blender API:**
```python
bpy.ops.mesh.knife_project(cut_through=cut_through)
```

---

### TASK-032-2: mesh_rip

**Status:** 🚧 To Do

Rips (tears) geometry at selected vertices/edges.

```python
@mcp.tool()
def mesh_rip(
    ctx: Context,
    use_fill: bool = False,
    object_name: str | None = None
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Rips geometry at selection.

    Creates a hole/tear in the mesh at selected vertices or edges.
    Useful for creating openings, tears, or separating connected geometry.

    Workflow: BEFORE → mesh_select_targeted(action="by_index", element_type="VERT")
    """
```

**Blender API:**
```python
bpy.ops.mesh.rip('INVOKE_DEFAULT', use_fill=use_fill)
# Note: rip requires cursor position, may need workaround
```

---

### TASK-032-3: mesh_split

**Status:** 🚧 To Do

Splits selected geometry from the rest of the mesh.

```python
@mcp.tool()
def mesh_split(
    ctx: Context,
    object_name: str | None = None
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Splits selection from mesh.

    Unlike 'separate', split keeps geometry in the same object but disconnects it.
    Useful for creating movable parts that stay in the same object.

    Workflow: BEFORE → mesh_select (select faces to split)
    """
```

**Blender API:**
```python
bpy.ops.mesh.split()
```

---

### TASK-032-4: mesh_edge_split

**Status:** 🚧 To Do

Splits edges to create sharp boundaries.

```python
@mcp.tool()
def mesh_edge_split(
    ctx: Context,
    object_name: str | None = None
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Splits mesh at selected edges.

    Creates a seam/split along selected edges - geometry becomes disconnected
    but stays in place. Useful for:
    - UV seam preparation
    - Material boundaries
    - Rigging preparation

    Workflow: BEFORE → mesh_select_targeted(action="loop")
    """
```

**Blender API:**
```python
bpy.ops.mesh.edge_split()
```

---

## Implementation Notes

1. **mesh_rip** is tricky - it normally requires mouse position. May need bmesh approach
2. **mesh_knife_project** works best with orthographic view - document this limitation
3. Return statistics: "Split X faces" or "Ripped Y vertices"

---

## Alternative: Bisect Enhancement

Consider that `mesh_bisect` (TASK-018-1) already exists. These tools complement it for different use cases:
- `mesh_bisect`: Cut with mathematical plane
- `mesh_knife_project`: Cut with projected shape
- `mesh_split`: Disconnect without cutting
- `mesh_rip`: Create holes/tears

---

## Testing Requirements

- [ ] Unit tests for each tool
- [ ] E2E test: Create cube → select top face → split → verify disconnection
- [ ] E2E test: Edge split → verify vertex duplication
- [ ] Test knife_project limitations/requirements
