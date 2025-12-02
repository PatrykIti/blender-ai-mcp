# Lattice Tools Architecture

This document describes the architecture and implementation details for Lattice deformation tools in blender-ai-mcp.

## Overview

Lattice tools enable **non-destructive shape manipulation** using a cage of control points. Essential for architectural structures (tapering towers), organic modeling, and animation deformations.

**Key Use Cases:**
- Eiffel Tower tapering (narrowing towards top)
- Character body adjustments
- Product design (curved surfaces)
- Animation deformations

---

## Tool Categories

### Core Operations

| Tool | Operation | Reliability |
|------|-----------|-------------|
| `lattice_create` | Creates lattice object, auto-fits to target | High |
| `lattice_bind` | Binds object to lattice via modifier | High |
| `lattice_edit_point` | Moves lattice control points | High |

---

## Tool Specifications

### lattice_create

**[OBJECT MODE][SCENE]**

Creates a lattice object for non-destructive deformation. If `target_object` is provided, automatically sizes and positions the lattice to encompass the target's bounding box with a 5% margin.

```
Workflow: AFTER  lattice_bind(target_object, lattice_name)
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | "Lattice" | Name for the lattice object |
| `target_object` | Optional[str] | None | Object to fit lattice to |
| `location` | Optional[List[float]] | None | Manual position [x, y, z] |
| `points_u` | int | 2 | Resolution along U axis (2-64) |
| `points_v` | int | 2 | Resolution along V axis (2-64) |
| `points_w` | int | 2 | Resolution along W axis (2-64) |
| `interpolation` | Literal | "KEY_LINEAR" | Interpolation type |

**Interpolation Types:**
- `KEY_LINEAR` - Linear interpolation (sharp transitions)
- `KEY_CARDINAL` - Cardinal spline (smooth)
- `KEY_CATMULL_ROM` - Catmull-Rom spline (smooth, passes through points)
- `KEY_BSPLINE` - B-Spline (smoothest, doesn't pass through points)

**Examples:**
```python
# Create simple lattice
lattice_create(name="MyLattice")

# Create fitted lattice for tower tapering
lattice_create(name="TowerLattice", target_object="Tower", points_u=2, points_v=2, points_w=4)
```

---

### lattice_bind

**[OBJECT MODE][NON-DESTRUCTIVE]**

Binds an object to a lattice using Blender's Lattice modifier. Deforming the lattice will deform the bound object.

```
Workflow: BEFORE  lattice_create | AFTER  Edit lattice points to deform object
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `object_name` | str | *required* | Name of object to bind |
| `lattice_name` | str | *required* | Name of lattice to bind to |
| `vertex_group` | Optional[str] | None | Vertex group to limit effect |

**Examples:**
```python
# Basic binding
lattice_bind(object_name="Tower", lattice_name="TowerLattice")

# Binding with vertex group (only affects specific vertices)
lattice_bind(object_name="Character", lattice_name="BendLattice", vertex_group="Torso")
```

---

### lattice_edit_point

**[OBJECT MODE]**

Moves lattice control points to deform bound objects. Supports moving single or multiple points with relative (offset) or absolute positioning.

**Point Index Calculation:**
```
index = u + (v * points_u) + (w * points_u * points_v)
```

For a 2x2x4 lattice (16 points):
- Bottom layer: indices 0-3
- Second layer: indices 4-7
- Third layer: indices 8-11
- Top layer: indices 12-15

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lattice_name` | str | *required* | Name of lattice to edit |
| `point_index` | int or List[int] | *required* | Point index(es) to move |
| `offset` | List[float] | *required* | [x, y, z] offset or position |
| `relative` | bool | True | If True, offset; if False, absolute |

**Examples:**
```python
# Move single point relatively
lattice_edit_point(lattice_name="Lattice", point_index=5, offset=[0.1, 0.2, 0.0])

# Move top layer inward for tapering (2x2x4 lattice)
lattice_edit_point(lattice_name="TowerLattice", point_index=[12, 13, 14, 15], offset=[-0.3, -0.3, 0])

# Set absolute position
lattice_edit_point(lattice_name="Lattice", point_index=7, offset=[1.0, 1.0, 2.0], relative=False)
```

---

## Architecture

### Layer Structure

```

 1. DOMAIN LAYER
    server/domain/tools/lattice.py
    - ILatticeTool interface
    - lattice_create, lattice_bind, lattice_edit_point

 2. APPLICATION LAYER
    server/application/tool_handlers/lattice_handler.py
    - LatticeToolHandler implements ILatticeTool
    - Sends RPC requests to Blender

 3. ADAPTER LAYER
    server/adapters/mcp/areas/lattice.py
    - @mcp.tool() decorated functions
    - lattice_create, lattice_bind, lattice_edit_point

 4. BLENDER ADDON
    blender_addon/application/handlers/lattice.py
    - LatticeHandler class
    - bpy.data.lattices, bpy.data.objects, modifier API

```

### RPC Commands

| RPC Command | Handler Method |
|-------------|----------------|
| `lattice.create` | `LatticeHandler.lattice_create()` |
| `lattice.bind` | `LatticeHandler.lattice_bind()` |
| `lattice.edit_point` | `LatticeHandler.lattice_edit_point()` |

---

## Implementation Notes

### Auto-Fit to Target Object

When `target_object` is provided to `lattice_create`:

1. Get target object's bounding box (8 corners)
2. Transform corners to world space using `matrix_world`
3. Calculate min/max coordinates
4. Add 5% margin to dimensions
5. Position lattice at center of bounding box
6. Scale lattice to encompass target

```python
# Pseudo-code for auto-fit
target = bpy.data.objects[target_object]
corners = [matrix_world @ Vector(corner) for corner in target.bound_box]
min_coords = [min(c[i] for c in corners) for i in range(3)]
max_coords = [max(c[i] for c in corners) for i in range(3)]
center = [(min_coords[i] + max_coords[i]) / 2 for i in range(3)]
size = [(max_coords[i] - min_coords[i]) * 1.05 for i in range(3)]  # 5% margin
```

### Point Indexing

Lattice points are indexed in U  V  W order (fastest to slowest varying):

```
For 2x2x2 lattice:
Index 0: (U=0, V=0, W=0) - bottom front left
Index 1: (U=1, V=0, W=0) - bottom front right
Index 2: (U=0, V=1, W=0) - bottom back left
Index 3: (U=1, V=1, W=0) - bottom back right
Index 4: (U=0, V=0, W=1) - top front left
Index 5: (U=1, V=0, W=1) - top front right
Index 6: (U=0, V=1, W=1) - top back left
Index 7: (U=1, V=1, W=1) - top back right
```

### Modifier Behavior

- The Lattice modifier is **non-destructive** - original geometry is preserved
- Multiple objects can be bound to the same lattice
- Vertex groups can limit the effect to specific vertices
- The modifier can be applied to make changes permanent

---

## Example Workflows

### Eiffel Tower Tapering

```python
# 1. Create tower base
modeling_create_primitive(primitive_type="CUBE", name="Tower")
modeling_transform_object(name="Tower", scale=[0.5, 0.5, 3.0])

# 2. Create lattice fitted to tower
lattice_create(name="TowerLattice", target_object="Tower", points_u=2, points_v=2, points_w=4)

# 3. Bind tower to lattice
lattice_bind(object_name="Tower", lattice_name="TowerLattice")

# 4. Taper by moving top points inward
# For 2x2x4 = 16 points, top layer is indices 12-15
lattice_edit_point(lattice_name="TowerLattice", point_index=[12, 13, 14, 15], offset=[-0.3, -0.3, 0])
```

### Organic Character Adjustment

```python
# 1. Bind character to lattice for torso adjustments
lattice_create(name="TorsoLattice", target_object="Character", points_u=3, points_v=3, points_w=4)
lattice_bind(object_name="Character", lattice_name="TorsoLattice", vertex_group="Torso")

# 2. Adjust middle section
lattice_edit_point(lattice_name="TorsoLattice", point_index=[18, 19, 20], offset=[0.1, 0.0, 0.0])
```

---

## Testing

### Unit Tests

Location: `tests/unit/tools/lattice/test_lattice_handler.py`

Tests cover (19 tests):
- Default lattice creation
- Custom resolution and interpolation
- Auto-fit to target object
- Target object not found error
- Invalid interpolation type error
- Invalid point counts error
- Binding with and without vertex group
- Object/lattice not found errors
- Type validation (must be lattice)
- Vertex group not found error
- Single point relative movement
- Multiple point movement
- Absolute positioning
- Lattice not found error
- Non-lattice object error
- Point index out of range error
- Negative point index error

### E2E Tests

Location: `tests/e2e/tools/lattice/test_lattice_tools.py`

Requires running Blender with addon enabled. Tests complete workflow from creation to deformation.

---

## Alternatives

When lattice tools are too complex for simple deformations, consider:

| Task | Alternative Tool |
|------|------------------|
| Simple bending | `modeling_add_modifier(type="SIMPLE_DEFORM")` |
| Tapering | `modeling_add_modifier(type="SIMPLE_DEFORM", properties={"deform_method": "TAPER"})` |
| Twisting | `modeling_add_modifier(type="SIMPLE_DEFORM", properties={"deform_method": "TWIST"})` |
| Local deformation | `mesh_transform_selected` in Edit Mode |

Lattice deformation is best when:
- You need control over specific regions
- The deformation is complex (multiple points)
- You want to preserve the option to adjust later
- Multiple objects should deform together
