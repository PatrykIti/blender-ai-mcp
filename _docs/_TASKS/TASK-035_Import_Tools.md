# TASK-035: Import Tools

**Priority:** 🟠 High
**Category:** Import / System
**Estimated Effort:** Medium
**Dependencies:** None

---

## Overview

Import tools enable **bringing external assets into Blender** - essential for reference images, asset library integration, and working with client files.

**Use Cases:**
- Importing architectural plans as reference
- Loading client OBJ/FBX files for modification
- Reference images for modeling
- Asset library integration

---

## Sub-Tasks

### TASK-035-1: import_obj

**Status:** ✅ Done

Imports OBJ file.

```python
@mcp.tool()
def import_obj(
    ctx: Context,
    filepath: str,
    use_split_objects: bool = True,
    use_split_groups: bool = False,
    use_groups_as_vgroups: bool = False,
    use_image_search: bool = True,
    global_scale: float = 1.0,
    axis_forward: Literal["-X", "X", "-Y", "Y", "-Z", "Z"] = "-Z",
    axis_up: Literal["-X", "X", "-Y", "Y", "-Z", "Z"] = "Y"
) -> str:
    """
    [OBJECT MODE][SCENE] Imports OBJ file.

    OBJ is the most universal 3D format - supports geometry, UVs, normals, and materials.

    Workflow: AFTER → mesh_tris_to_quads (if triangulated) | mesh_normals_make_consistent
    """
```

**Blender API (Blender 4.0+):**
```python
bpy.ops.wm.obj_import(
    filepath=filepath,
    use_split_objects=use_split_objects,
    use_split_groups=use_split_groups,
    global_scale=global_scale,
    forward_axis=axis_forward,
    up_axis=axis_up
)
```

---

### TASK-035-2: import_fbx

**Status:** ✅ Done

Imports FBX file.

```python
@mcp.tool()
def import_fbx(
    ctx: Context,
    filepath: str,
    use_custom_normals: bool = True,
    use_image_search: bool = True,
    use_alpha_decals: bool = False,
    ignore_leaf_bones: bool = False,
    automatic_bone_orientation: bool = False,
    global_scale: float = 1.0,
    apply_transform: bool = False,
    axis_forward: Literal["-X", "X", "-Y", "Y", "-Z", "Z"] = "-Z",
    axis_up: Literal["-X", "X", "-Y", "Y", "-Z", "Z"] = "Y"
) -> str:
    """
    [OBJECT MODE][SCENE] Imports FBX file.

    FBX supports geometry, materials, animations, armatures, and more.
    Industry standard for game engines (Unity, Unreal).

    Workflow: AFTER → Check imported objects with scene_list_objects
    """
```

**Blender API:**
```python
bpy.ops.import_scene.fbx(
    filepath=filepath,
    use_custom_normals=use_custom_normals,
    use_image_search=use_image_search,
    ignore_leaf_bones=ignore_leaf_bones,
    automatic_bone_orientation=automatic_bone_orientation,
    global_scale=global_scale,
    axis_forward=axis_forward,
    axis_up=axis_up
)
```

---

### TASK-035-3: import_image_as_plane

**Status:** ✅ Done

Imports image as a textured plane (reference image).

```python
@mcp.tool()
def import_image_as_plane(
    ctx: Context,
    filepath: str,
    name: str | None = None,
    location: list[float] | None = None,
    size: float = 1.0,
    align_to: Literal["WORLD", "VIEW", "CAM"] = "WORLD",
    align_axis: Literal["X+", "Y+", "Z+", "X-", "Y-", "Z-"] = "Z+",
    shader: Literal["PRINCIPLED", "SHADELESS", "EMISSION"] = "PRINCIPLED",
    use_transparency: bool = True
) -> str:
    """
    [OBJECT MODE][SCENE] Imports image as textured plane.

    Perfect for:
    - Reference images (blueprints, concept art)
    - Background plates
    - Decals and signage
    - Quick texturing

    Workflow: Use as reference for modeling
    """
```

**Blender API:**
```python
# Requires "Import Images as Planes" addon (built-in, may need enabling)
bpy.ops.import_image.to_plane(
    files=[{"name": filepath}],
    directory=os.path.dirname(filepath),
    align_axis=align_axis,
    shader=shader,
    use_transparency=use_transparency
)
```

**Note:** This addon must be enabled. Tool should auto-enable if not already.

---

### TASK-035-4: import_glb

**Status:** ✅ Done

Imports GLB/GLTF file.

```python
@mcp.tool()
def import_glb(
    ctx: Context,
    filepath: str,
    import_pack_images: bool = True,
    merge_vertices: bool = False,
    import_shading: Literal["NORMALS", "FLAT", "SMOOTH"] = "NORMALS"
) -> str:
    """
    [OBJECT MODE][SCENE] Imports GLB/GLTF file.

    GLTF is the modern web/game format - supports PBR materials, animations, and more.
    """
```

**Blender API:**
```python
bpy.ops.import_scene.gltf(
    filepath=filepath,
    import_pack_images=import_pack_images,
    merge_vertices=merge_vertices,
    import_shading=import_shading
)
```

---

## Implementation Notes

1. **File validation**: Check file exists before import
2. **Path handling**: Support both absolute and relative paths
3. **Addon enabling**: `import_image_as_plane` requires addon - auto-enable
4. **Return value**: Return list of imported object names
5. **Error handling**: Handle file not found, invalid format, etc.

---

## Symmetry with Export Tools

We already have:
- `export_glb` → add `import_glb`
- `export_fbx` → add `import_fbx`
- `export_obj` → add `import_obj`

---

## Testing Requirements

- [x] Unit tests with mocked bpy.ops (13 tests)
- [x] E2E test: Export cube to OBJ → import → verify geometry
- [x] E2E test: Import reference image → verify plane created
- [x] Test file not found error handling
- [x] Test addon auto-enable for import_image_as_plane

## Implementation Summary

**Completed:** 2025-11-30

**Files Created:**
- `server/domain/tools/import_tool.py` - IImportTool interface (4 methods)
- `server/application/tool_handlers/import_handler.py` - RPC bridge
- `server/adapters/mcp/areas/import_tool.py` - 4 MCP tools
- `blender_addon/application/handlers/import_handler.py` - Blender implementations

**Files Modified:**
- `server/infrastructure/di.py` - Added get_import_handler provider
- `server/adapters/mcp/areas/__init__.py` - Registered import_tool module
- `blender_addon/__init__.py` - Registered 4 RPC handlers

**Test Files:**
- `tests/unit/tools/import_tool/test_import_handler.py` - 13 unit tests
- `tests/e2e/tools/import_tool/test_import_tools.py` - E2E roundtrip tests

**Notes:**
- All tools validate file existence before import
- `import_image_as_plane` auto-enables the required addon if not already enabled
- Returns list of imported object names for verification
