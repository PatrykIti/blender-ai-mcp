# TASK-027: Sculpting Tools

**Status:** ✅ Done
**Priority:** 🟢 Low
**Category:** Sculpting Tools
**Completion Date:** 2025-11-29

---

## Overview

Implement sculpting tools for organic shape manipulation. These are lower priority as they require Sculpt Mode and are more advanced workflows.

---

# TASK-027-1: sculpt_auto

**Status:** ✅ Done
**Priority:** 🟢 Low

## Objective

Implement `sculpt_auto` as high-level sculpt macro for common organic shaping operations.

## Architecture Requirements

### 1. Domain Layer (`server/domain/tools/sculpt.py`)

Create new domain interface:

```python
from abc import ABC, abstractmethod
from typing import List, Optional

class ISculptTool(ABC):
    @abstractmethod
    def auto_sculpt(
        self,
        object_name: str = None,
        operation: str = "smooth",  # 'smooth', 'inflate', 'grab', 'flatten'
        strength: float = 0.5,
        iterations: int = 1,
        use_symmetry: bool = True,
        symmetry_axis: str = "X",
    ) -> str:
        pass
```

### 2. Application Layer (`server/application/tool_handlers/sculpt_handler.py`)

Create `SculptToolHandler`:

```python
from server.domain.tools.sculpt import ISculptTool
from server.domain.interfaces.rpc_client import IRpcClient

class SculptToolHandler(ISculptTool):
    def __init__(self, rpc_client: IRpcClient):
        self.rpc = rpc_client

    def auto_sculpt(self, object_name=None, operation="smooth", strength=0.5,
                    iterations=1, use_symmetry=True, symmetry_axis="X") -> str:
        return self.rpc.send_request("sculpt.auto", {
            "object_name": object_name,
            "operation": operation,
            "strength": strength,
            "iterations": iterations,
            "use_symmetry": use_symmetry,
            "symmetry_axis": symmetry_axis,
        })
```

### 3. Adapter Layer (`server/adapters/mcp/areas/sculpt.py`)

```python
from fastmcp import Context
from typing import Literal
from server.adapters.mcp.instance import mcp
from server.infrastructure.di import get_sculpt_handler

@mcp.tool()
def sculpt_auto(
    ctx: Context,
    object_name: str = None,
    operation: Literal["smooth", "inflate", "grab", "flatten"] = "smooth",
    strength: float = 0.5,
    iterations: int = 1,
    use_symmetry: bool = True,
    symmetry_axis: Literal["X", "Y", "Z"] = "X",
) -> str:
    """
    [SCULPT MODE][DESTRUCTIVE] High-level sculpt operation applied to entire mesh.

    Operations:
        - smooth: Smooths the entire surface (removes noise)
        - inflate: Expands mesh outward along normals
        - grab: Not applicable for auto (use brush tools)
        - flatten: Flattens surface irregularities

    Note: Object must be in Sculpt Mode. Use system_set_mode first.

    Workflow: BEFORE -> system_set_mode(mode='SCULPT') | AFTER -> mesh_remesh_voxel

    Args:
        object_name: Target object (default: active object)
        operation: Sculpt operation type
        strength: Operation strength 0-1
        iterations: Number of passes
        use_symmetry: Enable symmetry
        symmetry_axis: Symmetry axis
    """
    handler = get_sculpt_handler()
    return handler.auto_sculpt(
        object_name=object_name,
        operation=operation,
        strength=strength,
        iterations=iterations,
        use_symmetry=use_symmetry,
        symmetry_axis=symmetry_axis,
    )
```

### 4. Blender Addon (`blender_addon/application/handlers/sculpt.py`)

Create `SculptHandler`:

```python
import bpy

class SculptHandler:
    def auto_sculpt(self, object_name=None, operation="smooth", strength=0.5,
                    iterations=1, use_symmetry=True, symmetry_axis="X"):
        obj = bpy.data.objects.get(object_name) if object_name else bpy.context.active_object

        if not obj or obj.type != 'MESH':
            return f"Object '{object_name or 'active'}' is not a mesh"

        # Ensure Sculpt Mode
        bpy.context.view_layer.objects.active = obj
        if obj.mode != 'SCULPT':
            bpy.ops.object.mode_set(mode='SCULPT')

        # Set symmetry
        bpy.context.object.use_mesh_symmetry_x = (symmetry_axis == 'X' and use_symmetry)
        bpy.context.object.use_mesh_symmetry_y = (symmetry_axis == 'Y' and use_symmetry)
        bpy.context.object.use_mesh_symmetry_z = (symmetry_axis == 'Z' and use_symmetry)

        # Apply operation
        if operation == "smooth":
            for _ in range(iterations):
                bpy.ops.sculpt.mesh_filter(type='SMOOTH', strength=strength)
        elif operation == "inflate":
            for _ in range(iterations):
                bpy.ops.sculpt.mesh_filter(type='INFLATE', strength=strength)
        elif operation == "flatten":
            for _ in range(iterations):
                bpy.ops.sculpt.mesh_filter(type='FLATTEN', strength=strength)

        return f"Applied {operation} to '{obj.name}' ({iterations} iterations)"
```

### 5. Infrastructure & Registration

- Add `get_sculpt_handler()` to `server/infrastructure/di.py`
- Register RPC handler in `blender_addon/__init__.py`
- Add `sculpt` to `server/adapters/mcp/areas/__init__.py`

## Deliverables

- [x] New Sculpt domain
- [x] Application handler
- [x] MCP adapter
- [x] Blender addon handler
- [x] Unit tests
- [x] Documentation

---

# TASK-027-2: sculpt_brush_smooth

**Status:** ✅ Done
**Priority:** 🟢 Low

## Objective

Implement `sculpt_brush_smooth` for targeted smoothing with brush strokes.

## Architecture Requirements

### 1. Domain Layer

```python
@abstractmethod
def brush_smooth(
    self,
    object_name: str = None,
    location: List[float] = None,  # [x, y, z] world position
    radius: float = 0.1,
    strength: float = 0.5,
) -> str:
    pass
```

### 2. Adapter Layer

```python
@mcp.tool()
def sculpt_brush_smooth(
    ctx: Context,
    object_name: str = None,
    location: List[float] = None,
    radius: float = 0.1,
    strength: float = 0.5,
) -> str:
    """
    [SCULPT MODE][DESTRUCTIVE] Applies smooth brush at specified location.

    Workflow: BEFORE -> system_set_mode(mode='SCULPT'), mesh_get_vertex_data

    Args:
        object_name: Target object (default: active object)
        location: World position [x, y, z] for brush center
        radius: Brush radius in Blender units
        strength: Brush strength 0-1
    """
```

### 3. Blender Addon

```python
def brush_smooth(self, object_name=None, location=None, radius=0.1, strength=0.5):
    # Note: Programmatic brush strokes in Blender are complex
    # This is a simplified version using sculpt.brush_stroke

    obj = bpy.data.objects.get(object_name) if object_name else bpy.context.active_object

    if obj.mode != 'SCULPT':
        bpy.ops.object.mode_set(mode='SCULPT')

    # Set brush settings
    brush = bpy.context.tool_settings.sculpt.brush
    brush.size = int(radius * 100)  # Convert to pixels roughly
    brush.strength = strength

    # Select smooth brush
    bpy.ops.wm.tool_set_by_id(name="builtin_brush.Smooth")

    if location:
        # Convert world to view coordinates and apply stroke
        # This is complex and may need region/view context
        pass

    return f"Smooth brush ready at radius={radius}, strength={strength}"
```

## Note

Programmatic brush strokes are complex in Blender. Consider using mesh filters or vertex manipulation instead for AI workflows.

## Deliverables

- [x] Implementation + Tests
- [x] Documentation

---

# TASK-027-3: sculpt_brush_grab

**Status:** ✅ Done
**Priority:** 🟢 Low

## Objective

Implement `sculpt_brush_grab` for grabbing and moving geometry.

## Architecture Requirements

Similar to smooth brush, but with grab operation. This is challenging for programmatic use.

### Adapter Layer

```python
@mcp.tool()
def sculpt_brush_grab(
    ctx: Context,
    object_name: str = None,
    from_location: List[float] = None,
    to_location: List[float] = None,
    radius: float = 0.1,
    strength: float = 0.5,
) -> str:
    """
    [SCULPT MODE][DESTRUCTIVE] Grabs and moves geometry from one location to another.

    Args:
        object_name: Target object (default: active object)
        from_location: Start position [x, y, z]
        to_location: End position [x, y, z]
        radius: Brush radius
        strength: Brush strength 0-1
    """
```

## Deliverables

- [x] Implementation + Tests
- [x] Documentation

---

# TASK-027-4: sculpt_brush_crease

**Status:** ✅ Done
**Priority:** 🟢 Low

## Objective

Implement `sculpt_brush_crease` for creating sharp creases and lines.

## Architecture Requirements

### Adapter Layer

```python
@mcp.tool()
def sculpt_brush_crease(
    ctx: Context,
    object_name: str = None,
    location: List[float] = None,
    radius: float = 0.1,
    strength: float = 0.5,
    pinch: float = 0.5,
) -> str:
    """
    [SCULPT MODE][DESTRUCTIVE] Creates sharp crease at specified location.

    Args:
        object_name: Target object (default: active object)
        location: World position [x, y, z]
        radius: Brush radius
        strength: Brush strength 0-1
        pinch: Pinch amount for sharper creases
    """
```

## Deliverables

- [x] Implementation + Tests
- [x] Documentation

---

## Summary

| Tool | Priority | Description |
|------|----------|-------------|
| `sculpt_auto` | 🟢 Low | High-level sculpt macro (smooth, inflate, flatten) |
| `sculpt_brush_smooth` | 🟢 Low | Targeted smooth brush |
| `sculpt_brush_grab` | 🟢 Low | Grab and move geometry |
| `sculpt_brush_crease` | 🟢 Low | Create sharp creases |

## Notes

- Sculpting tools are complex for AI workflows
- Mesh filters (`sculpt.mesh_filter`) are more reliable than brush strokes
- Consider using mesh tools (smooth, shrink_fatten) for organic shaping instead
- Sculpting requires high polygon counts - use `mesh_remesh_voxel` first
