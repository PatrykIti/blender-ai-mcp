# TASK-012: Mesh Smooth & Flatten Tools

**Status:** ✅ Complete  
**Priority:** Medium  
**Phase:** Phase 2 - Mesh Editing  
**Dependencies:** TASK-011-1 (Edit Mode Foundation)  
**Completion Date:** 2025-11-25

---

## 📋 Overview

Implement `mesh_smooth` and `mesh_flatten` tools to enable AI-driven vertex smoothing and planar flattening operations. These are essential for refining organic shapes and creating precise planar surfaces without manual vertex manipulation.

**Key Goals:**
- Smooth selected vertices using Laplacian smoothing
- Flatten vertices to align with a specified plane (XYZ axes)
- Follow established Clean Architecture patterns (Domain -> Application -> Adapter)
- Provide clear, AI-friendly feedback and error handling

---

## 🏗️ Architecture Design

Following the patterns established in `MESH_TOOLS_ARCHITECTURE.md` and `TOOLS_ARCHITECTURE_DEEP_DIVE.md`:

### 1. Domain Layer (`server/domain/tools/`)

**File:** `server/domain/tools/mesh_smooth.py`

```python
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from typing import Literal

class MeshSmoothRequest(BaseModel):
    """Request model for mesh smoothing operation."""
    object_name: str = Field(..., description="Name of the mesh object")
    iterations: int = Field(1, ge=1, le=100, description="Number of smoothing iterations")
    factor: float = Field(0.5, ge=0.0, le=1.0, description="Smoothing strength (0=none, 1=max)")

class IMeshSmoothTool(ABC):
    """Interface for mesh smoothing operations."""
    
    @abstractmethod
    def smooth_vertices(self, request: MeshSmoothRequest) -> str:
        """
        Smooth selected vertices using Laplacian smoothing.
        
        Args:
            request: Smoothing parameters
            
        Returns:
            Success message with operation details
            
        Raises:
            ObjectNotFoundError: If object doesn't exist
            InvalidModeError: If not in Edit Mode
            NoSelectionError: If no vertices are selected
        """
        pass
```

**File:** `server/domain/tools/mesh_flatten.py`

```python
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from typing import Literal

class MeshFlattenRequest(BaseModel):
    """Request model for mesh flattening operation."""
    object_name: str = Field(..., description="Name of the mesh object")
    axis: Literal["X", "Y", "Z"] = Field(..., description="Axis to flatten along")

class IMeshFlattenTool(ABC):
    """Interface for mesh flattening operations."""
    
    @abstractmethod
    def flatten_vertices(self, request: MeshFlattenRequest) -> str:
        """
        Flatten selected vertices along specified axis.
        
        Args:
            request: Flattening parameters
            
        Returns:
            Success message with operation details
            
        Raises:
            ObjectNotFoundError: If object doesn't exist
            InvalidModeError: If not in Edit Mode
            NoSelectionError: If no vertices are selected
        """
        pass
```

---

### 2. Application Layer (`server/application/handlers/`)

**File:** `server/application/handlers/mesh_smooth_handler.py`

```python
from server.domain.tools.mesh_smooth import IMeshSmoothTool, MeshSmoothRequest
from server.infrastructure.rpc.rpc_client import RpcClient

class MeshSmoothHandler(IMeshSmoothTool):
    """Application handler for mesh smoothing operations."""
    
    def __init__(self, rpc_client: RpcClient):
        self._rpc = rpc_client
    
    def smooth_vertices(self, request: MeshSmoothRequest) -> str:
        """Execute mesh smoothing via RPC."""
        result = self._rpc.call(
            "mesh.smooth_vertices",
            object_name=request.object_name,
            iterations=request.iterations,
            factor=request.factor
        )
        return result
```

**File:** `server/application/handlers/mesh_flatten_handler.py`

```python
from server.domain.tools.mesh_flatten import IMeshFlattenTool, MeshFlattenRequest
from server.infrastructure.rpc.rpc_client import RpcClient

class MeshFlattenHandler(IMeshFlattenTool):
    """Application handler for mesh flattening operations."""
    
    def __init__(self, rpc_client: RpcClient):
        self._rpc = rpc_client
    
    def flatten_vertices(self, request: MeshFlattenRequest) -> str:
        """Execute mesh flattening via RPC."""
        result = self._rpc.call(
            "mesh.flatten_vertices",
            object_name=request.object_name,
            axis=request.axis
        )
        return result
```

---

### 3. Adapter Layer (`server/adapters/mcp/`)

**File:** `server/adapters/mcp/mesh_tools.py` (extend existing)

Add to existing mesh tools registration:

```python
@mcp.tool()
def mesh_smooth(
    object_name: str,
    iterations: int = 1,
    factor: float = 0.5
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][NON-DESTRUCTIVE] Smooths selected vertices.
    Uses Laplacian smoothing to refine organic shapes and remove hard edges.
    
    Args:
        object_name: Name of the mesh object to smooth
        iterations: Number of smoothing passes (1-100). More = smoother
        factor: Smoothing strength (0.0-1.0). 0=no effect, 1=maximum smoothing
    """
    handler = container.get(IMeshSmoothTool)
    request = MeshSmoothRequest(
        object_name=object_name,
        iterations=iterations,
        factor=factor
    )
    return handler.smooth_vertices(request)


@mcp.tool()
def mesh_flatten(
    object_name: str,
    axis: Literal["X", "Y", "Z"]
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Flattens selected vertices to plane.
    Aligns vertices perpendicular to chosen axis (X: YZ plane, Y: XZ plane, Z: XY plane).
    
    Args:
        object_name: Name of the mesh object
        axis: Axis to flatten along ("X", "Y", or "Z")
    """
    handler = container.get(IMeshFlattenTool)
    request = MeshFlattenRequest(
        object_name=object_name,
        axis=axis
    )
    return handler.flatten_vertices(request)
```

---

### 4. Blender Addon API (`blender_addon/api/`)

**File:** `blender_addon/api/mesh_smooth_api.py`

```python
"""Mesh smoothing API implementation."""
import bpy
from typing import Dict, Any

def smooth_vertices(
    object_name: str,
    iterations: int,
    factor: float
) -> Dict[str, Any]:
    """
    [EDIT MODE][SELECTION-BASED][NON-DESTRUCTIVE] Smooths selected vertices.
    Uses Laplacian smoothing algorithm.
    
    Args:
        object_name: Name of the mesh object
        iterations: Number of smoothing iterations
        factor: Smoothing strength (0.0-1.0)
    """
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "status": "error",
            "message": f"Object '{object_name}' not found"
        }
    
    if obj.type != 'MESH':
        return {
            "status": "error",
            "message": f"Object '{object_name}' is not a mesh (type: {obj.type})"
        }
    
    # Ensure Edit Mode
    if obj.mode != 'EDIT':
        return {
            "status": "error",
            "message": f"Object '{object_name}' must be in Edit Mode"
        }
    
    # Get selected vertex count
    import bmesh
    bm = bmesh.from_edit_mesh(obj.data)
    selected_verts = [v for v in bm.verts if v.select]
    
    if not selected_verts:
        return {
            "status": "error",
            "message": f"No vertices selected on '{object_name}'"
        }
    
    vert_count = len(selected_verts)
    
    # Execute smooth operation
    bpy.ops.mesh.vertices_smooth(
        factor=factor,
        repeat=iterations
    )
    
    return {
        "status": "success",
        "message": f"Smoothed {vert_count} vertices on '{object_name}' ({iterations} iterations, {factor:.2f} factor)"
    }
```

**File:** `blender_addon/api/mesh_flatten_api.py`

```python
"""Mesh flattening API implementation."""
import bpy
from typing import Dict, Any, Literal

def flatten_vertices(
    object_name: str,
    axis: Literal["X", "Y", "Z"]
) -> Dict[str, Any]:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Flattens selected vertices to plane.
    Aligns vertices perpendicular to chosen axis using scale-to-zero transform.
    
    Args:
        object_name: Name of the mesh object
        axis: Axis to flatten along ("X", "Y", or "Z")
    """
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "status": "error",
            "message": f"Object '{object_name}' not found"
        }
    
    if obj.type != 'MESH':
        return {
            "status": "error",
            "message": f"Object '{object_name}' is not a mesh (type: {obj.type})"
        }
    
    # Ensure Edit Mode
    if obj.mode != 'EDIT':
        return {
            "status": "error",
            "message": f"Object '{object_name}' must be in Edit Mode"
        }
    
    # Get selected vertex count
    import bmesh
    bm = bmesh.from_edit_mesh(obj.data)
    selected_verts = [v for v in bm.verts if v.select]
    
    if not selected_verts:
        return {
            "status": "error",
            "message": f"No vertices selected on '{object_name}'"
        }
    
    vert_count = len(selected_verts)
    
    # Map axis to constraint
    constraint_map = {
        "X": (True, False, False),
        "Y": (False, True, False),
        "Z": (False, False, True)
    }
    
    # Execute flatten operation using scale
    bpy.ops.transform.resize(
        value=(1, 1, 1),
        constraint_axis=constraint_map[axis],
        orient_type='GLOBAL'
    )
    
    # Apply scale to flatten
    constraint = constraint_map[axis]
    scale_value = [1.0, 1.0, 1.0]
    for i, constrained in enumerate(constraint):
        if constrained:
            scale_value[i] = 0.0
    
    bpy.ops.transform.resize(
        value=tuple(scale_value),
        constraint_axis=constraint,
        orient_type='GLOBAL'
    )
    
    return {
        "status": "success",
        "message": f"Flattened {vert_count} vertices on '{object_name}' along {axis} axis"
    }
```

---

### 5. RPC Server Registration (`blender_addon/rpc_server.py`)

Add to existing `BlenderRpcServer._register_handlers()`:

```python
# Mesh Smoothing & Flattening
from .api.mesh_smooth_api import smooth_vertices
from .api.mesh_flatten_api import flatten_vertices

self.register("mesh.smooth_vertices", smooth_vertices)
self.register("mesh.flatten_vertices", flatten_vertices)
```

---

## ✅ Acceptance Criteria

1. **Functional Requirements:**
   - [ ] `mesh_smooth` smooths selected vertices with configurable iterations and factor
   - [ ] `mesh_flatten` aligns vertices to XYZ planes correctly
   - [ ] Both tools validate Edit Mode and vertex selection
   - [ ] Clear error messages for invalid states

2. **Architectural Compliance:**
   - [ ] Domain interfaces define contracts (no implementation)
   - [ ] Application handlers delegate to RPC client
   - [ ] Adapter layer has AI-friendly docstrings
   - [ ] Blender API layer contains all `bpy` logic

3. **Testing:**
   - [ ] Manual test: Smooth a UV Sphere (iterations=5, factor=0.8)
   - [ ] Manual test: Flatten Cube top face along Z axis
   - [ ] Error handling: Test without selection, wrong mode, non-existent object

4. **Documentation:**
   - [ ] Update `_docs/_CHANGELOG/` with new tools
   - [ ] Update `_docs/_ADDON/mesh_tools.md` with API details
   - [ ] Update `_docs/_MCP_SERVER/mesh_tools.md` with MCP tool specs
   - [ ] Mark task as ✅ Complete in `_docs/_TASKS/README.md`
   - [ ] Update README.md Phase 2 checklist

---

## 🧪 Testing Strategy

### Manual Test Cases

**Test 1: Basic Smoothing**
```
1. Create UV Sphere
2. Enter Edit Mode (mesh_mode_switch)
3. Select all vertices (mesh_select_all)
4. Execute: mesh_smooth("Sphere", iterations=5, factor=0.5)
5. Expected: Sphere becomes more uniform/organic
```

**Test 2: Aggressive Smoothing**
```
1. Create Cube with Subdivision modifier
2. Enter Edit Mode
3. Select top face vertices
4. Execute: mesh_smooth("Cube", iterations=20, factor=1.0)
5. Expected: Top face becomes dome-like
```

**Test 3: Flatten to XY Plane**
```
1. Create Cube
2. Enter Edit Mode
3. Select top 4 vertices
4. Move vertices randomly in Z
5. Execute: mesh_flatten("Cube", axis="Z")
6. Expected: All selected verts align to same Z coordinate
```

**Test 4: Error Handling - No Selection**
```
1. Create Cube, enter Edit Mode
2. Deselect all (mesh_select_all with mode="DESELECT")
3. Execute: mesh_smooth("Cube")
4. Expected: Error "No vertices selected on 'Cube'"
```

---

## 📝 Implementation Checklist

- [x] Create Domain interfaces (`mesh_smooth.py`, `mesh_flatten.py`)
- [x] Create Application handlers (smooth/flatten handlers)
- [x] Create Blender API implementations (smooth/flatten API)
- [x] Register RPC endpoints in `rpc_server.py`
- [x] Register MCP tools in `mesh_tools.py` (Adapter)
- [x] Update DI container bindings in `server/main.py`
- [x] Run manual tests
- [x] Update documentation (_CHANGELOG, _ADDON, _MCP_SERVER)
- [x] Update README.md roadmap
- [x] Update TASK-012 status to ✅ Complete
- [ ] Commit with GPG signature

---

## 🔗 Related Files

**Server:**
- `server/domain/tools/mesh_smooth.py` (new)
- `server/domain/tools/mesh_flatten.py` (new)
- `server/application/handlers/mesh_smooth_handler.py` (new)
- `server/application/handlers/mesh_flatten_handler.py` (new)
- `server/adapters/mcp/mesh_tools.py` (extend)

**Blender Addon:**
- `blender_addon/api/mesh_smooth_api.py` (new)
- `blender_addon/api/mesh_flatten_api.py` (new)
- `blender_addon/rpc_server.py` (extend)

**Documentation:**
- `_docs/_CHANGELOG/` (create new entry)
- `_docs/_ADDON/mesh_tools.md` (update)
- `_docs/_MCP_SERVER/mesh_tools.md` (update)
- `README.md` (update Phase 2 checklist)

---

## 📚 References

- **Blender API:**
  - `bpy.ops.mesh.vertices_smooth()` - Laplacian smoothing
  - `bpy.ops.transform.resize()` - Used for flattening via scale to 0
  
- **Architecture Patterns:**
  - `_docs/TOOLS_ARCHITECTURE_DEEP_DIVE.md` - Clean Architecture layers
  - `_docs/MESH_TOOLS_ARCHITECTURE.md` - Mesh tool patterns
  - `GEMINI.md` - Core principles and layering rules
