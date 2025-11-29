# TASK-024: UV Tools

**Status:** To Do
**Priority:** 🟡 Medium
**Category:** UV Tools

---

## Overview

Implement UV mapping tools for texture coordinate management.

---

# TASK-024-1: uv_unwrap

**Status:** To Do
**Priority:** 🟡 Medium

## Objective

Implement `uv_unwrap` for automatic UV unwrapping with multiple projection methods.

## Architecture Requirements

### 1. Domain Layer (`server/domain/tools/uv.py`)

Extend `IUVTool` interface:

```python
@abstractmethod
def unwrap(
    self,
    object_name: str = None,
    method: str = "SMART_PROJECT",  # 'SMART_PROJECT', 'CUBE', 'CYLINDER', 'SPHERE', 'UNWRAP'
    angle_limit: float = 66.0,  # for SMART_PROJECT
    island_margin: float = 0.02,
    scale_to_bounds: bool = True,
) -> str:
    pass
```

### 2. Application Layer

Implement RPC bridge in `UVToolHandler`.

### 3. Adapter Layer (`server/adapters/mcp/areas/uv.py`)

```python
@mcp.tool()
def uv_unwrap(
    ctx: Context,
    object_name: str = None,
    method: Literal["SMART_PROJECT", "CUBE", "CYLINDER", "SPHERE", "UNWRAP"] = "SMART_PROJECT",
    angle_limit: float = 66.0,
    island_margin: float = 0.02,
    scale_to_bounds: bool = True,
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Unwraps selected faces to UV space.

    Methods:
        - SMART_PROJECT: Automatic projection based on face angles (best for complex meshes)
        - CUBE: Cube projection (best for boxy objects)
        - CYLINDER: Cylindrical projection
        - SPHERE: Spherical projection
        - UNWRAP: Standard unwrap (requires seams for best results)

    Workflow: BEFORE -> mesh_select (select faces) | AFTER -> uv_pack_islands

    Args:
        object_name: Target object (default: active object)
        method: Unwrap method
        angle_limit: Angle threshold for SMART_PROJECT (degrees)
        island_margin: Space between UV islands
        scale_to_bounds: Scale UVs to fill 0-1 space
    """
```

### 4. Blender Addon (`blender_addon/application/handlers/uv.py`)

Extend `UVHandler`:

```python
def unwrap(self, object_name=None, method="SMART_PROJECT", angle_limit=66.0, island_margin=0.02, scale_to_bounds=True):
    obj = bpy.data.objects.get(object_name) if object_name else bpy.context.active_object

    if obj.type != 'MESH':
        return f"Object '{obj.name}' is not a mesh"

    # Ensure Edit Mode
    if obj.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')

    if method == "SMART_PROJECT":
        bpy.ops.uv.smart_project(
            angle_limit=math.radians(angle_limit),
            island_margin=island_margin,
            scale_to_bounds=scale_to_bounds
        )
    elif method == "CUBE":
        bpy.ops.uv.cube_project(
            scale_to_bounds=scale_to_bounds
        )
    elif method == "CYLINDER":
        bpy.ops.uv.cylinder_project(
            scale_to_bounds=scale_to_bounds
        )
    elif method == "SPHERE":
        bpy.ops.uv.sphere_project(
            scale_to_bounds=scale_to_bounds
        )
    elif method == "UNWRAP":
        bpy.ops.uv.unwrap(
            method='ANGLE_BASED',
            margin=island_margin
        )

    return f"Unwrapped '{obj.name}' using {method}"
```

### 5. Registration

Register RPC handler in `blender_addon/__init__.py`.

## Deliverables

- [ ] Domain interface extension
- [ ] Application handler implementation
- [ ] MCP adapter with docstrings
- [ ] Blender addon handler
- [ ] Unit tests
- [ ] Documentation updates

---

# TASK-024-2: uv_pack_islands

**Status:** To Do
**Priority:** 🟡 Medium

## Objective

Implement `uv_pack_islands` to optimize UV island layout for texture space efficiency.

## Architecture Requirements

### 1. Domain Layer

```python
@abstractmethod
def pack_islands(
    self,
    object_name: str = None,
    margin: float = 0.02,
    rotate: bool = True,
    scale: bool = True,
) -> str:
    pass
```

### 2. Adapter Layer

```python
@mcp.tool()
def uv_pack_islands(
    ctx: Context,
    object_name: str = None,
    margin: float = 0.02,
    rotate: bool = True,
    scale: bool = True,
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Packs UV islands for optimal texture space usage.

    Workflow: BEFORE -> uv_unwrap

    Args:
        object_name: Target object (default: active object)
        margin: Space between packed islands
        rotate: Allow rotation for better packing
        scale: Allow scaling islands to fill space
    """
```

### 3. Blender Addon

```python
def pack_islands(self, object_name=None, margin=0.02, rotate=True, scale=True):
    obj = bpy.data.objects.get(object_name) if object_name else bpy.context.active_object

    if obj.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')

    # Select all UVs
    bpy.ops.uv.select_all(action='SELECT')

    # Pack
    bpy.ops.uv.pack_islands(
        margin=margin,
        rotate=rotate,
        scale=scale
    )

    return f"Packed UV islands for '{obj.name}'"
```

## Deliverables

- [ ] Implementation + Tests
- [ ] Documentation

---

# TASK-024-3: uv_create_seam (Optional)

**Status:** To Do
**Priority:** 🟢 Low

## Objective

Implement `uv_create_seam` to mark/clear UV seams on edges.

## Architecture Requirements

### 1. Domain Layer

```python
@abstractmethod
def create_seam(
    self,
    object_name: str = None,
    action: str = "mark",  # 'mark', 'clear'
) -> str:
    pass
```

### 2. Adapter Layer

```python
@mcp.tool()
def uv_create_seam(
    ctx: Context,
    object_name: str = None,
    action: Literal["mark", "clear"] = "mark",
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][NON-DESTRUCTIVE] Marks or clears UV seams on selected edges.

    Seams guide the UNWRAP method to split UV islands at specific edges.

    Workflow: BEFORE -> mesh_select_targeted (select edges) | AFTER -> uv_unwrap

    Args:
        object_name: Target object (default: active object)
        action: 'mark' to add seams, 'clear' to remove
    """
```

### 3. Blender Addon

```python
def create_seam(self, object_name=None, action="mark"):
    obj = bpy.data.objects.get(object_name) if object_name else bpy.context.active_object

    if obj.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')

    if action == "mark":
        bpy.ops.mesh.mark_seam(clear=False)
        return f"Marked seams on selected edges"
    else:
        bpy.ops.mesh.mark_seam(clear=True)
        return f"Cleared seams from selected edges"
```

## Deliverables

- [ ] Implementation + Tests
- [ ] Documentation

---

## Summary

| Tool | Priority | Description |
|------|----------|-------------|
| `uv_unwrap` | 🟡 Medium | Automatic UV unwrapping with projection methods |
| `uv_pack_islands` | 🟡 Medium | Optimize UV island layout |
| `uv_create_seam` | 🟢 Low | Mark/clear UV seams on edges |
