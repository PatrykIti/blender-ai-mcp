# TASK-038: Organic Modeling Tools (Medical/Biological)

**Priority:** 🔴 High
**Category:** Sculpt / Modeling
**Estimated Effort:** High
**Dependencies:** TASK-027 (Sculpting Tools)
**Status:** ✅ Done
**Completion Date:** 2025-11-30

---

## Overview

Organic modeling tools enable **creation of biological structures** - essential for medical visualization, anatomical models, creature design, and VFX.

**Use Cases:**
- Human organs (heart, liver, kidneys, brain)
- Blood vessels, arteries, veins
- Tumors, cysts, cellular structures
- Creature/monster design
- Biological VFX (tentacles, organic growth)

---

## Sub-Tasks

### TASK-038-1: Metaball Tools

**Status:** ✅ Done

Metaballs are **blobby primitives that merge together** - perfect for organic structures.

#### metaball_create

```python
@mcp.tool()
def metaball_create(
    ctx: Context,
    name: str = "Metaball",
    location: list[float] | None = None,
    element_type: Literal["BALL", "CAPSULE", "PLANE", "ELLIPSOID", "CUBE"] = "BALL",
    radius: float = 1.0,
    resolution: float = 0.2,  # Lower = higher quality
    threshold: float = 0.6   # Merge threshold
) -> str:
    """
    [OBJECT MODE][SCENE] Creates a metaball object.

    Metaballs automatically merge when close together, creating organic blob shapes.
    Perfect for: veins, tumors, fat deposits, cellular structures.

    Workflow: AFTER → metaball_add_element | metaball_to_mesh
    """
```

**Blender API:**
```python
bpy.ops.object.metaball_add(type=element_type, location=location or (0, 0, 0))
meta = bpy.context.active_object
meta.name = name
meta.data.resolution = resolution
meta.data.threshold = threshold
meta.data.elements[0].radius = radius
```

#### metaball_add_element

```python
@mcp.tool()
def metaball_add_element(
    ctx: Context,
    metaball_name: str,
    element_type: Literal["BALL", "CAPSULE", "PLANE", "ELLIPSOID", "CUBE"] = "BALL",
    location: list[float] = [0, 0, 0],  # Relative to metaball origin
    radius: float = 1.0,
    stiffness: float = 2.0  # How strongly it merges
) -> str:
    """
    [OBJECT MODE] Adds element to existing metaball.

    Multiple elements merge together based on proximity and stiffness.
    Use CAPSULE for tubular structures (blood vessels).
    """
```

**Blender API:**
```python
meta = bpy.data.objects[metaball_name]
bpy.context.view_layer.objects.active = meta
bpy.ops.object.mode_set(mode='EDIT')

elem = meta.data.elements.new(type=element_type)
elem.co = location
elem.radius = radius
elem.stiffness = stiffness

bpy.ops.object.mode_set(mode='OBJECT')
```

#### metaball_to_mesh

```python
@mcp.tool()
def metaball_to_mesh(
    ctx: Context,
    metaball_name: str,
    apply_resolution: bool = True
) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Converts metaball to mesh.

    Required for:
    - Mesh editing operations
    - Export to game engines
    - Further sculpting

    Workflow: AFTER → mesh_remesh_voxel (cleanup) | sculpt_* tools
    """
```

**Blender API:**
```python
meta = bpy.data.objects[metaball_name]
bpy.context.view_layer.objects.active = meta
meta.select_set(True)
bpy.ops.object.convert(target='MESH')
```

---

### TASK-038-2: Core Sculpt Brushes

**Status:** ✅ Done

Essential brushes for organic surface detail.

#### sculpt_brush_clay

```python
@mcp.tool()
def sculpt_brush_clay(
    ctx: Context,
    object_name: str | None = None,
    radius: float = 0.1,
    strength: float = 0.5,
    location: list[float] | None = None
) -> str:
    """
    [SCULPT MODE] Sets up Clay brush.

    Adds material like clay - builds up surface.
    Essential for: muscle mass, fat deposits, organ volume.
    """
```

#### sculpt_brush_inflate

```python
@mcp.tool()
def sculpt_brush_inflate(
    ctx: Context,
    object_name: str | None = None,
    radius: float = 0.1,
    strength: float = 0.5,
    location: list[float] | None = None
) -> str:
    """
    [SCULPT MODE] Sets up Inflate brush.

    Pushes geometry outward along normals - inflates like balloon.
    Essential for: swelling, tumors, blisters, organ volume.
    """
```

**Blender API:**
```python
bpy.ops.wm.tool_set_by_id(name="builtin_brush.Inflate")
```

#### sculpt_brush_blob

```python
@mcp.tool()
def sculpt_brush_blob(
    ctx: Context,
    object_name: str | None = None,
    radius: float = 0.1,
    strength: float = 0.5,
    location: list[float] | None = None
) -> str:
    """
    [SCULPT MODE] Sets up Blob brush.

    Creates rounded, organic bulges.
    Essential for: nodules, bumps, organic growths.
    """
```

**Blender API:**
```python
bpy.ops.wm.tool_set_by_id(name="builtin_brush.Blob")
```

---

### TASK-038-3: Detail Sculpt Brushes

**Status:** ✅ Done

Brushes for fine detail and specialized shapes.

#### sculpt_brush_snake_hook

```python
@mcp.tool()
def sculpt_brush_snake_hook(
    ctx: Context,
    object_name: str | None = None,
    radius: float = 0.1,
    strength: float = 0.5,
    from_location: list[float] | None = None,
    to_location: list[float] | None = None
) -> str:
    """
    [SCULPT MODE] Sets up Snake Hook brush.

    Pulls geometry like taffy - creates long tendrils.
    Essential for: blood vessels, nerves, tentacles, organic protrusions.
    """
```

**Blender API:**
```python
bpy.ops.wm.tool_set_by_id(name="builtin_brush.Snake Hook")
```

#### sculpt_brush_draw

```python
@mcp.tool()
def sculpt_brush_draw(
    ctx: Context,
    object_name: str | None = None,
    radius: float = 0.1,
    strength: float = 0.5,
    location: list[float] | None = None
) -> str:
    """
    [SCULPT MODE] Sets up Draw brush.

    Basic sculpting - pushes/pulls surface.
    Essential for: general shaping, wrinkles, surface variation.
    """
```

#### sculpt_brush_pinch

```python
@mcp.tool()
def sculpt_brush_pinch(
    ctx: Context,
    object_name: str | None = None,
    radius: float = 0.1,
    strength: float = 0.5,
    location: list[float] | None = None
) -> str:
    """
    [SCULPT MODE] Sets up Pinch brush.

    Pulls geometry toward center - creates sharp creases.
    Essential for: wrinkles, folds, membrane attachments.
    """
```

---

### TASK-038-4: Dynamic Topology (Dyntopo)

**Status:** ✅ Done

Dynamically adds geometry while sculpting - essential for organic work.

#### sculpt_enable_dyntopo

```python
@mcp.tool()
def sculpt_enable_dyntopo(
    ctx: Context,
    object_name: str | None = None,
    detail_mode: Literal["RELATIVE", "CONSTANT", "BRUSH", "MANUAL"] = "RELATIVE",
    detail_size: float = 12.0,  # Pixels for RELATIVE, units for CONSTANT
    use_smooth_shading: bool = True
) -> str:
    """
    [SCULPT MODE] Enables Dynamic Topology.

    Dyntopo automatically adds/removes geometry as you sculpt.
    No need to worry about base mesh topology.

    Detail modes:
    - RELATIVE: Detail based on view distance (default)
    - CONSTANT: Fixed detail size in Blender units
    - BRUSH: Detail based on brush size
    - MANUAL: No automatic detail, use Flood Fill

    Essential for: sculpting from scratch, adding detail where needed.

    Warning: Destroys UV maps and vertex groups. Use for concept/base mesh.
    """
```

**Blender API:**
```python
obj = bpy.data.objects[object_name] if object_name else bpy.context.active_object
bpy.context.view_layer.objects.active = obj
bpy.ops.object.mode_set(mode='SCULPT')

bpy.context.sculpt_object.use_dynamic_topology_sculpting = True
bpy.context.scene.tool_settings.sculpt.detail_type_method = detail_mode
bpy.context.scene.tool_settings.sculpt.detail_size = detail_size
bpy.context.scene.tool_settings.sculpt.use_smooth_shading = use_smooth_shading
```

#### sculpt_disable_dyntopo

```python
@mcp.tool()
def sculpt_disable_dyntopo(
    ctx: Context,
    object_name: str | None = None
) -> str:
    """
    [SCULPT MODE] Disables Dynamic Topology.

    After disabling, consider mesh_remesh_voxel for clean topology.
    """
```

#### sculpt_dyntopo_flood_fill

```python
@mcp.tool()
def sculpt_dyntopo_flood_fill(
    ctx: Context,
    object_name: str | None = None
) -> str:
    """
    [SCULPT MODE] Applies detail level to entire mesh.

    Useful for: unifying detail level after sculpting.
    """
```

**Blender API:**
```python
bpy.ops.sculpt.detail_flood_fill()
```

---

### TASK-038-5: Proportional Editing

**Status:** ✅ Done

Soft selection with falloff - essential for organic mesh editing.

#### mesh_set_proportional_edit

```python
@mcp.tool()
def mesh_set_proportional_edit(
    ctx: Context,
    enabled: bool = True,
    falloff_type: Literal["SMOOTH", "SPHERE", "ROOT", "INVERSE_SQUARE", "SHARP", "LINEAR", "CONSTANT", "RANDOM"] = "SMOOTH",
    size: float = 1.0,
    use_connected: bool = False  # Only affect connected geometry
) -> str:
    """
    [EDIT MODE] Configures proportional editing.

    When enabled, transformations affect nearby vertices with falloff.
    Essential for: organic deformations, smooth surface adjustments.

    Falloff types:
    - SMOOTH: Gentle falloff (best for organic)
    - SPHERE: Spherical falloff
    - SHARP: Quick falloff
    - LINEAR: Linear falloff

    Workflow: Enable → mesh_transform_selected → movements affect neighbors
    """
```

**Blender API:**
```python
bpy.context.scene.tool_settings.use_proportional_edit = enabled
bpy.context.scene.tool_settings.proportional_edit_falloff = falloff_type
bpy.context.scene.tool_settings.proportional_size = size
bpy.context.scene.tool_settings.use_proportional_connected = use_connected
```

---

### TASK-038-6: Skin Modifier Workflow

**Status:** ✅ Done

Creates mesh surface from skeleton - perfect for tubular structures.

#### skin_create_skeleton

```python
@mcp.tool()
def skin_create_skeleton(
    ctx: Context,
    name: str = "VesselSkeleton",
    vertices: list[list[float]] = [[0, 0, 0], [0, 0, 1]],
    edges: list[list[int]] | None = None,  # Auto-connect if None
    location: list[float] | None = None
) -> str:
    """
    [OBJECT MODE][SCENE] Creates skeleton mesh for Skin modifier.

    Define vertices as path points, edges connect them.
    Skin modifier will create tubular mesh around this skeleton.

    Use case: blood vessels, nerves, tree branches, tentacles.

    Workflow: AFTER → modeling_add_modifier(type="SKIN") | skin_set_radius
    """
```

**Blender API:**
```python
import bmesh

mesh = bpy.data.meshes.new(name)
obj = bpy.data.objects.new(name, mesh)
bpy.context.collection.objects.link(obj)

bm = bmesh.new()
verts = [bm.verts.new(v) for v in vertices]
bm.verts.ensure_lookup_table()

if edges is None:
    # Auto-connect sequentially
    for i in range(len(verts) - 1):
        bm.edges.new([verts[i], verts[i + 1]])
else:
    for e in edges:
        bm.edges.new([verts[e[0]], verts[e[1]]])

bm.to_mesh(mesh)
bm.free()

# Add skin modifier
modifier = obj.modifiers.new(name="Skin", type='SKIN')
```

#### skin_set_radius

```python
@mcp.tool()
def skin_set_radius(
    ctx: Context,
    object_name: str,
    vertex_index: int | list[int] | None = None,  # None = all selected
    radius_x: float = 0.25,
    radius_y: float = 0.25
) -> str:
    """
    [EDIT MODE] Sets skin radius at vertices.

    Each vertex can have different X/Y radius for elliptical cross-sections.

    Use case: Varying vessel thickness (aorta thicker than capillaries).
    """
```

**Blender API:**
```python
obj = bpy.data.objects[object_name]
bpy.context.view_layer.objects.active = obj
bpy.ops.object.mode_set(mode='EDIT')

# Access skin data
bpy.ops.object.mode_set(mode='OBJECT')
for v in obj.data.skin_vertices[0].data:
    if vertex_index is None or v.index in vertex_index:
        v.radius = [radius_x, radius_y]
```

---

## Example Workflows

### Heart Model
```python
# 1. Start with metaball for main chambers
metaball_create(name="Heart", element_type="ELLIPSOID", radius=1.0)
metaball_add_element("Heart", element_type="BALL", location=[0.5, 0, 0.3], radius=0.8)
metaball_add_element("Heart", element_type="BALL", location=[-0.5, 0, 0.3], radius=0.8)
metaball_to_mesh("Heart")

# 2. Enable dyntopo for detail sculpting
sculpt_enable_dyntopo(detail_mode="RELATIVE", detail_size=8)

# 3. Shape with brushes
sculpt_brush_clay()      # Add volume
sculpt_brush_pinch()     # Create seams between chambers
sculpt_brush_smooth()    # Smooth surfaces
```

### Blood Vessels
```python
# 1. Create vessel skeleton
skin_create_skeleton(
    name="Artery",
    vertices=[[0,0,0], [0,0,1], [0.3,0,1.5], [-0.3,0,1.5], [0,0,2]],
    edges=[[0,1], [1,2], [1,3], [2,4], [3,4]]  # Branching
)

# 2. Add skin modifier (already added by skin_create_skeleton)
# 3. Adjust radii
skin_set_radius("Artery", vertex_index=0, radius_x=0.15)  # Thick at base
skin_set_radius("Artery", vertex_index=[2,3], radius_x=0.08)  # Thinner branches

# 4. Convert to mesh
modeling_apply_modifier("Artery", "Skin")

# 5. Smooth
mesh_smooth(iterations=2)
```

---

## Testing Requirements

- [ ] Unit tests for each tool
- [ ] E2E test: Create metaball organ → convert → sculpt → export
- [ ] E2E test: Blood vessel workflow with skin modifier
- [ ] E2E test: Dyntopo sculpting from sphere to organic shape
- [ ] Test proportional editing with mesh_transform_selected
