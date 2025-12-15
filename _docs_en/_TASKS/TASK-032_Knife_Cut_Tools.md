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

**Status:** ✅ Done

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

**Status:** ✅ Done

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

**Status:** ✅ Done

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

**Status:** ✅ Done

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

- [x] Unit tests for each tool (9 tests)
- [x] E2E test: Create cube → select top face → split → verify disconnection
- [x] E2E test: Edge split → verify vertex duplication
- [x] Test knife_project limitations/requirements

## Implementation Summary

**Completed:** 2025-11-30

**Files Modified:**
- `server/domain/tools/mesh.py` - Added 4 abstract methods
- `server/application/tool_handlers/mesh_handler.py` - Added 4 RPC methods
- `server/adapters/mcp/areas/mesh.py` - Added 4 MCP tools
- `blender_addon/application/handlers/mesh.py` - Added 4 Blender implementations
- `blender_addon/__init__.py` - Registered 4 RPC handlers

**Test Files:**
- `tests/unit/tools/knife_cut/test_knife_cut_handler.py` - 9 unit tests
- `tests/e2e/tools/knife_cut/test_knife_cut_tools.py` - E2E tests

**Notes:**
- mesh_knife_project is view-dependent and requires orthographic views for best results
- mesh_rip uses rip_move operator with zero translation for programmatic use
- All tools include proper error handling for missing selections
