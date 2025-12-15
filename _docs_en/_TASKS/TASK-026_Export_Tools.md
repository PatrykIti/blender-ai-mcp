# TASK-026: Export Tools

**Status:** ✅ Done
**Priority:** 🟡 Medium
**Category:** Export Tools

---

## Overview

Implement file export tools for common 3D formats (GLB/GLTF, FBX, OBJ).

---

# TASK-026-1: export_glb

**Status:** ✅ Done
**Priority:** 🟠 High

## Objective

Implement `export_glb` for exporting to GLB/GLTF format (web-friendly, game engines).

## Architecture Requirements

### 1. Domain Layer (`server/domain/tools/export.py`)

Create new domain interface:

```python
from abc import ABC, abstractmethod
from typing import List, Optional

class IExportTool(ABC):
    @abstractmethod
    def export_glb(
        self,
        filepath: str,
        export_selected: bool = False,
        export_animations: bool = True,
        export_materials: bool = True,
        apply_modifiers: bool = True,
    ) -> str:
        pass
```

### 2. Application Layer (`server/application/tool_handlers/export_handler.py`)

Create `ExportToolHandler`:

```python
from server.domain.tools.export import IExportTool
from server.domain.interfaces.rpc_client import IRpcClient

class ExportToolHandler(IExportTool):
    def __init__(self, rpc_client: IRpcClient):
        self.rpc = rpc_client

    def export_glb(self, filepath, export_selected=False, export_animations=True,
                   export_materials=True, apply_modifiers=True) -> str:
        return self.rpc.send_request("export.glb", {
            "filepath": filepath,
            "export_selected": export_selected,
            "export_animations": export_animations,
            "export_materials": export_materials,
            "apply_modifiers": apply_modifiers,
        })
```

### 3. Adapter Layer (`server/adapters/mcp/areas/export.py`)

```python
from fastmcp import Context
from typing import Literal
from server.adapters.mcp.instance import mcp
from server.infrastructure.di import get_export_handler

@mcp.tool()
def export_glb(
    ctx: Context,
    filepath: str,
    export_selected: bool = False,
    export_animations: bool = True,
    export_materials: bool = True,
    apply_modifiers: bool = True,
) -> str:
    """
    [OBJECT MODE][SCENE][SAFE] Exports scene or selected objects to GLB/GLTF format.

    GLB is the binary variant of GLTF - ideal for web, game engines (Unity, Unreal, Godot).
    Supports PBR materials, animations, and skeletal rigs.

    Args:
        filepath: Output file path (must end with .glb or .gltf)
        export_selected: Export only selected objects (default: entire scene)
        export_animations: Include animations
        export_materials: Include materials and textures
        apply_modifiers: Apply modifiers before export
    """
    handler = get_export_handler()
    return handler.export_glb(
        filepath=filepath,
        export_selected=export_selected,
        export_animations=export_animations,
        export_materials=export_materials,
        apply_modifiers=apply_modifiers,
    )
```

### 4. Blender Addon (`blender_addon/application/handlers/export.py`)

Create `ExportHandler`:

```python
import bpy
import os

class ExportHandler:
    def export_glb(self, filepath, export_selected=False, export_animations=True,
                   export_materials=True, apply_modifiers=True):
        # Ensure correct extension
        if not filepath.endswith(('.glb', '.gltf')):
            filepath += '.glb'

        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        bpy.ops.export_scene.gltf(
            filepath=filepath,
            export_format='GLB' if filepath.endswith('.glb') else 'GLTF_SEPARATE',
            use_selection=export_selected,
            export_animations=export_animations,
            export_materials='EXPORT' if export_materials else 'NONE',
            export_apply=apply_modifiers,
        )

        return f"Exported to '{filepath}'"
```

### 5. Infrastructure & Registration

- Add `get_export_handler()` to `server/infrastructure/di.py`
- Register RPC handler in `blender_addon/__init__.py`
- Add `export` to `server/adapters/mcp/areas/__init__.py`

## Deliverables

- [x] New Export domain
- [x] Application handler
- [x] MCP adapter
- [x] Blender addon handler
- [x] Unit tests
- [x] Documentation

---

# TASK-026-2: export_fbx

**Status:** ✅ Done
**Priority:** 🟡 Medium

## Objective

Implement `export_fbx` for exporting to FBX format (industry standard for game engines).

## Architecture Requirements

### 1. Domain Layer

```python
@abstractmethod
def export_fbx(
    self,
    filepath: str,
    export_selected: bool = False,
    export_animations: bool = True,
    apply_modifiers: bool = True,
    mesh_smooth_type: str = "FACE",  # 'OFF', 'FACE', 'EDGE'
    use_armature_deform_only: bool = False,
) -> str:
    pass
```

### 2. Adapter Layer

```python
@mcp.tool()
def export_fbx(
    ctx: Context,
    filepath: str,
    export_selected: bool = False,
    export_animations: bool = True,
    apply_modifiers: bool = True,
    mesh_smooth_type: Literal["OFF", "FACE", "EDGE"] = "FACE",
) -> str:
    """
    [OBJECT MODE][SCENE][SAFE] Exports scene or selected objects to FBX format.

    FBX is the industry standard for game engines and DCC interchange.
    Supports animations, armatures, blend shapes, and materials.

    Args:
        filepath: Output file path (must end with .fbx)
        export_selected: Export only selected objects
        export_animations: Include animations and armature
        apply_modifiers: Apply modifiers before export
        mesh_smooth_type: Smoothing export method
    """
```

### 3. Blender Addon

```python
def export_fbx(self, filepath, export_selected=False, export_animations=True,
               apply_modifiers=True, mesh_smooth_type="FACE"):
    if not filepath.endswith('.fbx'):
        filepath += '.fbx'

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    bpy.ops.export_scene.fbx(
        filepath=filepath,
        use_selection=export_selected,
        bake_anim=export_animations,
        use_mesh_modifiers=apply_modifiers,
        mesh_smooth_type=mesh_smooth_type,
        add_leaf_bones=False,
        primary_bone_axis='Y',
        secondary_bone_axis='X',
    )

    return f"Exported to '{filepath}'"
```

## Deliverables

- [x] Implementation + Tests
- [x] Documentation

---

# TASK-026-3: export_obj

**Status:** ✅ Done
**Priority:** 🟢 Low

## Objective

Implement `export_obj` for exporting to OBJ format (simple, universal mesh format).

## Architecture Requirements

### 1. Domain Layer

```python
@abstractmethod
def export_obj(
    self,
    filepath: str,
    export_selected: bool = False,
    apply_modifiers: bool = True,
    export_materials: bool = True,
    export_uvs: bool = True,
    export_normals: bool = True,
    triangulate: bool = False,
) -> str:
    pass
```

### 2. Adapter Layer

```python
@mcp.tool()
def export_obj(
    ctx: Context,
    filepath: str,
    export_selected: bool = False,
    apply_modifiers: bool = True,
    export_materials: bool = True,
    export_uvs: bool = True,
    export_normals: bool = True,
    triangulate: bool = False,
) -> str:
    """
    [OBJECT MODE][SCENE][SAFE] Exports scene or selected objects to OBJ format.

    OBJ is a simple, universal mesh format supported by virtually all 3D software.
    Creates .obj (geometry) and .mtl (materials) files.

    Args:
        filepath: Output file path (must end with .obj)
        export_selected: Export only selected objects
        apply_modifiers: Apply modifiers before export
        export_materials: Export .mtl material file
        export_uvs: Include UV coordinates
        export_normals: Include vertex normals
        triangulate: Convert quads/ngons to triangles
    """
```

### 3. Blender Addon

```python
def export_obj(self, filepath, export_selected=False, apply_modifiers=True,
               export_materials=True, export_uvs=True, export_normals=True,
               triangulate=False):
    if not filepath.endswith('.obj'):
        filepath += '.obj'

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    bpy.ops.wm.obj_export(
        filepath=filepath,
        export_selected_objects=export_selected,
        apply_modifiers=apply_modifiers,
        export_materials=export_materials,
        export_uv=export_uvs,
        export_normals=export_normals,
        export_triangulated_mesh=triangulate,
    )

    return f"Exported to '{filepath}'"
```

## Deliverables

- [x] Implementation + Tests
- [x] Documentation

---

## Summary

| Tool | Priority | Description |
|------|----------|-------------|
| `export_glb` | 🟠 High | Export to GLB/GLTF (web, game engines) |
| `export_fbx` | 🟡 Medium | Export to FBX (industry standard) |
| `export_obj` | 🟢 Low | Export to OBJ (universal mesh format) |
