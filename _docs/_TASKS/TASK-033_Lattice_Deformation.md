# TASK-033: Lattice Deformation

**Priority:** 🟠 High
**Category:** Modeling Tools
**Estimated Effort:** Medium
**Dependencies:** TASK-004 (Modeling Tools)

---

## Overview

Lattice deformation enables **non-destructive shape manipulation** using a cage of control points. Essential for architectural structures (tapering towers), organic modeling, and animation.

**Use Cases:**
- Eiffel Tower tapering (narrowing towards top)
- Character body adjustments
- Product design (curved surfaces)
- Animation deformations

---

## Sub-Tasks

### TASK-033-1: lattice_create

**Status:** ✅ Done

Creates a lattice object sized to fit target object.

```python
@mcp.tool()
def lattice_create(
    ctx: Context,
    name: str = "Lattice",
    target_object: str | None = None,  # If provided, fit to object bounds
    location: list[float] | None = None,
    points_u: int = 2,
    points_v: int = 2,
    points_w: int = 2,
    interpolation: Literal["KEY_LINEAR", "KEY_CARDINAL", "KEY_CATMULL_ROM", "KEY_BSPLINE"] = "KEY_LINEAR"
) -> str:
    """
    [OBJECT MODE][SCENE] Creates a lattice object.

    If target_object is provided, lattice is automatically sized and positioned
    to encompass the target object's bounding box.

    Workflow: AFTER → lattice_bind(target_object, lattice_name)
    """
```

**Blender API:**
```python
bpy.ops.object.add(type='LATTICE', location=location)
lattice = bpy.context.active_object
lattice.name = name
lattice.data.points_u = points_u
lattice.data.points_v = points_v
lattice.data.points_w = points_w
lattice.data.interpolation_type_u = interpolation
lattice.data.interpolation_type_v = interpolation
lattice.data.interpolation_type_w = interpolation

# If target_object, fit to bounds
if target_object:
    target = bpy.data.objects[target_object]
    # Calculate bounding box and scale/position lattice
```

---

### TASK-033-2: lattice_bind

**Status:** ✅ Done

Binds object to lattice using Lattice modifier.

```python
@mcp.tool()
def lattice_bind(
    ctx: Context,
    object_name: str,
    lattice_name: str,
    vertex_group: str | None = None  # Optional: only affect specific vertices
) -> str:
    """
    [OBJECT MODE][NON-DESTRUCTIVE] Binds object to lattice deformer.

    Adds a Lattice modifier to the target object pointing to the lattice.
    Deforming the lattice will deform the object.

    Workflow: BEFORE → lattice_create | AFTER → Edit lattice points to deform object
    """
```

**Blender API:**
```python
obj = bpy.data.objects[object_name]
modifier = obj.modifiers.new(name="Lattice", type='LATTICE')
modifier.object = bpy.data.objects[lattice_name]
if vertex_group:
    modifier.vertex_group = vertex_group
```

---

### TASK-033-3: lattice_edit_point

**Status:** ✅ Done

Moves lattice control points programmatically.

```python
@mcp.tool()
def lattice_edit_point(
    ctx: Context,
    lattice_name: str,
    point_index: int | list[int],
    offset: list[float],  # [x, y, z] offset from original position
    relative: bool = True  # If False, set absolute position
) -> str:
    """
    [OBJECT MODE] Moves lattice control points.

    Use case: Programmatically taper a tower by moving top lattice points inward.

    Example - Taper tower:
    1. Create 2x2x4 lattice around tower
    2. Move top 4 points (indices 12-15) inward by offset=[-0.3, -0.3, 0]
    """
```

**Blender API:**
```python
lattice = bpy.data.objects[lattice_name]
points = lattice.data.points

if isinstance(point_index, int):
    point_index = [point_index]

for idx in point_index:
    if relative:
        points[idx].co_deform += Vector(offset)
    else:
        points[idx].co_deform = Vector(offset)
```

---

## Example: Eiffel Tower Tapering

```python
# 1. Create tower base (stack of cubes or procedural)
modeling_create_primitive(primitive_type="CUBE", name="Tower")
modeling_transform_object(name="Tower", scale=[0.5, 0.5, 3.0])

# 2. Create lattice fitted to tower
lattice_create(name="TowerLattice", target_object="Tower", points_u=2, points_v=2, points_w=4)

# 3. Bind tower to lattice
lattice_bind(object_name="Tower", lattice_name="TowerLattice")

# 4. Taper by moving top points inward
# Top layer points (assuming 2x2x4 = 16 points, top 4 are indices 12-15)
lattice_edit_point(lattice_name="TowerLattice", point_index=[12, 13, 14, 15], offset=[-0.3, -0.3, 0])
```

---

## Implementation Notes

1. `lattice_create` with `target_object` should calculate bounding box and add small margin
2. Lattice point indices go: U → V → W (fastest to slowest varying)
3. Consider helper function to get point indices by layer (bottom, middle, top)
4. `lattice_edit_point` should work in Object Mode on the lattice data

---

## Testing Requirements

- [x] Unit tests for each tool (19 tests in tests/unit/tools/lattice/)
- [x] E2E test: Create cube → create fitted lattice → bind → edit points → verify deformation
- [x] E2E test: Taper workflow (tower example)
- [x] Test vertex group binding

---

## Router Integration

For each tool, create metadata JSON file in `server/router/infrastructure/tools_metadata/lattice/`:

### Example: lattice_create.json

```json
{
  "tool_name": "lattice_create",
  "category": "lattice",
  "mode_required": "OBJECT",
  "selection_required": false,
  "keywords": ["lattice", "deform", "cage", "control points", "taper"],
  "sample_prompts": [
    "create a lattice for this object",
    "add lattice deformer",
    "setup lattice cage around the tower"
  ],
  "parameters": {
    "name": {"type": "string", "default": "Lattice"},
    "target_object": {"type": "string", "description": "Object to fit lattice to"},
    "points_u": {"type": "int", "default": 2, "range": [2, 64]},
    "points_v": {"type": "int", "default": 2, "range": [2, 64]},
    "points_w": {"type": "int", "default": 2, "range": [2, 64]}
  },
  "related_tools": ["lattice_bind", "lattice_edit_point"],
  "patterns": ["tower_like:tapering"],
  "description": "Creates a lattice object for non-destructive deformation."
}
```

---

## Documentation Updates Required

After implementing these tools, update:

| File | What to Update |
|------|----------------|
| `_docs/_TASKS/TASK-033_Lattice_Deformation.md` | Mark sub-tasks as ✅ Done |
| `_docs/_TASKS/README.md` | Move task to Done section |
| `_docs/_CHANGELOG/{NN}-{date}-lattice-tools.md` | Create changelog entry |
| `_docs/_MCP_SERVER/README.md` | Add tools to MCP tools table |
| `_docs/_ADDON/README.md` | Add RPC commands to handler table |
| `_docs/AVAILABLE_TOOLS_SUMMARY.md` | Add tools with arguments |
| `_docs/MODELING_TOOLS_ARCHITECTURE.md` | Add Lattice section |
| `README.md` | Update roadmap checkboxes, add to autoApprove lists |
