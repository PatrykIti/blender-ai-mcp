# TASK-034: Text & Annotations

**Priority:** 🟡 Medium
**Category:** Modeling Tools
**Estimated Effort:** Low-Medium
**Dependencies:** TASK-004 (Modeling Tools)

---

## Overview

Text tools enable **3D typography and annotations** - essential for architectural visualization, signage, logo creation, and dimension labels.

**Use Cases:**
- 3D logos and signage
- Architectural dimension annotations
- Product labels
- Game UI elements (3D text)

---

## Sub-Tasks

### TASK-034-1: text_create

**Status:** 🚧 To Do

Creates a 3D text object.

```python
@mcp.tool()
def text_create(
    ctx: Context,
    text: str = "Text",
    name: str = "Text",
    location: list[float] | None = None,
    font: str | None = None,  # Path to .ttf/.otf or None for default
    size: float = 1.0,
    extrude: float = 0.0,  # Depth
    bevel_depth: float = 0.0,
    bevel_resolution: int = 0,
    align_x: Literal["LEFT", "CENTER", "RIGHT", "JUSTIFY", "FLUSH"] = "LEFT",
    align_y: Literal["TOP", "TOP_BASELINE", "MIDDLE", "BOTTOM_BASELINE", "BOTTOM"] = "BOTTOM_BASELINE"
) -> str:
    """
    [OBJECT MODE][SCENE] Creates a 3D text object.

    Text objects are curves and can be extruded, beveled, and converted to mesh.

    Workflow: AFTER → text_to_mesh (for game export) | modeling_add_modifier
    """
```

**Blender API:**
```python
bpy.ops.object.text_add(location=location or (0, 0, 0))
text_obj = bpy.context.active_object
text_obj.name = name

# Set text content
text_obj.data.body = text

# Font
if font:
    text_obj.data.font = bpy.data.fonts.load(font)

# Geometry
text_obj.data.size = size
text_obj.data.extrude = extrude
text_obj.data.bevel_depth = bevel_depth
text_obj.data.bevel_resolution = bevel_resolution

# Alignment
text_obj.data.align_x = align_x
text_obj.data.align_y = align_y
```

---

### TASK-034-2: text_edit

**Status:** 🚧 To Do

Modifies existing text object content and properties.

```python
@mcp.tool()
def text_edit(
    ctx: Context,
    object_name: str,
    text: str | None = None,
    size: float | None = None,
    extrude: float | None = None,
    bevel_depth: float | None = None
) -> str:
    """
    [OBJECT MODE] Edits text object properties.

    Only provided parameters are modified, others remain unchanged.
    """
```

**Blender API:**
```python
text_obj = bpy.data.objects[object_name]
if text_obj.type != 'FONT':
    raise ValueError(f"Object '{object_name}' is not a text object")

if text is not None:
    text_obj.data.body = text
if size is not None:
    text_obj.data.size = size
# ... etc
```

---

### TASK-034-3: text_to_mesh

**Status:** 🚧 To Do

Converts text object to mesh geometry.

```python
@mcp.tool()
def text_to_mesh(
    ctx: Context,
    object_name: str,
    keep_original: bool = False
) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Converts text to mesh.

    Required for:
    - Game engine export (text objects don't export)
    - Mesh editing operations
    - Boolean operations

    Workflow: BEFORE → text_create | AFTER → mesh_* tools, export_*
    """
```

**Blender API:**
```python
text_obj = bpy.data.objects[object_name]
bpy.context.view_layer.objects.active = text_obj
text_obj.select_set(True)

if keep_original:
    bpy.ops.object.duplicate()

bpy.ops.object.convert(target='MESH')
```

**Note:** We already have `modeling_convert_to_mesh` in TASK-008_1 which handles curves/text. Consider if this is redundant or if we need text-specific handling.

---

## Implementation Notes

1. Text objects are type `'FONT'` in Blender
2. Font loading: validate file exists before loading
3. `text_to_mesh` may produce high-poly meshes - consider adding decimate option
4. Consider `modeling_convert_to_mesh` integration - may already handle text

---

## Testing Requirements

- [ ] Unit tests for each tool
- [ ] E2E test: Create text → extrude → convert to mesh → export GLB
- [ ] Test custom font loading
- [ ] Test alignment options
- [ ] Verify modeling_convert_to_mesh handles text (if so, text_to_mesh may be redundant)
