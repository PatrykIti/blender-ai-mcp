# TASK-029: Edge Weights & Creases (Subdivision Control)

**Priority:** 🔴 High
**Category:** Mesh Tools
**Estimated Effort:** Medium
**Dependencies:** TASK-011 (Edit Mode Foundation)
**Status:** ✅ Done
**Completion Date:** 2025-11-30

---

## Overview

Edge weights and creases are **critical for game dev** - they control how subdivision surface and bevel modifiers affect geometry. Without these tools, creating smooth models with sharp edges is impossible.

**Use Cases:**
- Hard-surface modeling (weapons, vehicles, devices)
- Architectural details (window frames, door edges)
- Character modeling (eye sockets, fingernails)

---

## Sub-Tasks

### TASK-029-1: mesh_edge_crease

**Status:** ✅ Done

Controls subdivision surface sharpness on selected edges.

```python
@mcp.tool()
def mesh_edge_crease(
    ctx: Context,
    crease_value: float = 1.0,  # 0.0 = smooth, 1.0 = fully sharp
    object_name: str | None = None
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][NON-DESTRUCTIVE] Sets crease weight on selected edges.

    Crease controls how Subdivision Surface modifier affects edges:
    - 0.0 = fully smoothed
    - 1.0 = fully sharp (no subdivision effect)

    Workflow: BEFORE → mesh_select_targeted(action="loop") | AFTER → modeling_add_modifier(type="SUBSURF")
    """
```

**Blender API:**
```python
bpy.ops.transform.edge_crease(value=crease_value)
# OR via bmesh:
for edge in bm.edges:
    if edge.select:
        edge.crease = crease_value
```

---

### TASK-029-2: mesh_bevel_weight

**Status:** ✅ Done

Controls which edges are affected by Bevel modifier.

```python
@mcp.tool()
def mesh_bevel_weight(
    ctx: Context,
    weight: float = 1.0,  # 0.0 = no bevel, 1.0 = full bevel
    object_name: str | None = None
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][NON-DESTRUCTIVE] Sets bevel weight on selected edges.

    When Bevel modifier uses "Weight" limit method, only edges with weight > 0 are beveled.

    Workflow: BEFORE → mesh_select_targeted(action="loop") | AFTER → modeling_add_modifier(type="BEVEL", limit_method="WEIGHT")
    """
```

**Blender API:**
```python
bpy.ops.transform.edge_bevelweight(value=weight)
# OR via bmesh:
bevel_layer = bm.edges.layers.bevel_weight.verify()
for edge in bm.edges:
    if edge.select:
        edge[bevel_layer] = weight
```

---

### TASK-029-3: mesh_mark_sharp

**Status:** ✅ Done

Marks edges as sharp for flat shading / auto-smooth.

```python
@mcp.tool()
def mesh_mark_sharp(
    ctx: Context,
    action: Literal["mark", "clear"] = "mark",
    object_name: str | None = None
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][NON-DESTRUCTIVE] Marks/clears sharp edges.

    Sharp edges affect:
    - Auto Smooth (splits normals at sharp edges)
    - Edge Split modifier
    - Normal display

    Workflow: BEFORE → mesh_select_targeted(action="loop")
    """
```

**Blender API:**
```python
if action == "mark":
    bpy.ops.mesh.mark_sharp()
else:
    bpy.ops.mesh.mark_sharp(clear=True)
```

---

## Implementation Notes

1. All three tools require **Edit Mode** with edges selected
2. Values are clamped to 0.0-1.0 range
3. Return descriptive messages with edge count affected
4. Consider adding `mesh_select` action for "sharp" edges selection

---

## Testing Requirements

- [x] Unit tests for each tool (15 tests passing)
- [x] E2E test: Create cube → select edges → set crease → add Subsurf → verify sharp corners
- [x] E2E test: Bevel weight + Bevel modifier workflow
- [x] E2E test: Mark sharp + Auto Smooth workflow
