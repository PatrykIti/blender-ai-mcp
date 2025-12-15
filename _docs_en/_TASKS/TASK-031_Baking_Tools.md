# TASK-031: Baking Tools (Game Dev Critical)

**Priority:** 🔴 Critical
**Category:** Baking / Texturing
**Estimated Effort:** High
**Dependencies:** TASK-023 (Material Tools), TASK-024 (UV Tools)

---

## Overview

Baking is **absolutely critical for game development**. It allows transferring high-poly detail to low-poly meshes via texture maps. Without baking tools, creating game-ready assets is impossible.

**Use Cases:**
- Normal maps from high-poly sculpts
- Ambient Occlusion for shading
- Baking procedural materials to textures
- LOD (Level of Detail) workflows

---

## Sub-Tasks

### TASK-031-1: bake_normal_map

**Status:** ✅ Done

Bakes normal map from high-poly to low-poly or from geometry.

```python
@mcp.tool()
def bake_normal_map(
    ctx: Context,
    object_name: str,
    output_path: str,
    resolution: int = 1024,
    high_poly_source: str | None = None,  # If None, bakes from own geometry
    cage_extrusion: float = 0.1,
    margin: int = 16,
    normal_space: Literal["TANGENT", "OBJECT"] = "TANGENT"
) -> str:
    """
    [OBJECT MODE][REQUIRES UV] Bakes normal map.

    Modes:
    - Self-bake: Bakes normals from object's own geometry
    - High-to-low: Bakes from high_poly_source to target object

    Requirements:
    - Target object must have UV map
    - Material with image texture node (auto-created if missing)

    Workflow: BEFORE → uv_unwrap | AFTER → material_set_texture(input_name="Normal")
    """
```

**Blender API:**
```python
# Setup bake settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.bake_type = 'NORMAL'
bpy.context.scene.render.bake.normal_space = normal_space
bpy.context.scene.render.bake.margin = margin

# Create image
image = bpy.data.images.new(name, resolution, resolution)

# Setup material with image node
# ... (node setup code)

# Bake
if high_poly_source:
    bpy.context.scene.render.bake.use_selected_to_active = True
    bpy.context.scene.render.bake.cage_extrusion = cage_extrusion
    # Select high-poly, active = low-poly
    bpy.ops.object.bake(type='NORMAL')
else:
    bpy.ops.object.bake(type='NORMAL')

# Save image
image.filepath_raw = output_path
image.save()
```

---

### TASK-031-2: bake_ao

**Status:** ✅ Done

Bakes Ambient Occlusion map.

```python
@mcp.tool()
def bake_ao(
    ctx: Context,
    object_name: str,
    output_path: str,
    resolution: int = 1024,
    samples: int = 128,
    distance: float = 1.0,
    margin: int = 16
) -> str:
    """
    [OBJECT MODE][REQUIRES UV] Bakes ambient occlusion map.

    AO maps add depth and realism to materials without runtime cost.

    Workflow: BEFORE → uv_unwrap | AFTER → Use in game engine
    """
```

**Blender API:**
```python
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.bake_type = 'AO'
bpy.context.scene.cycles.samples = samples
bpy.context.scene.world.light_settings.distance = distance

bpy.ops.object.bake(type='AO')
```

---

### TASK-031-3: bake_combined

**Status:** ✅ Done

Bakes full material (diffuse + lighting) to texture.

```python
@mcp.tool()
def bake_combined(
    ctx: Context,
    object_name: str,
    output_path: str,
    resolution: int = 1024,
    samples: int = 128,
    margin: int = 16,
    use_pass_direct: bool = True,
    use_pass_indirect: bool = True,
    use_pass_color: bool = True
) -> str:
    """
    [OBJECT MODE][REQUIRES UV] Bakes combined render to texture.

    Useful for:
    - Lightmaps
    - Pre-baked lighting for mobile games
    - Texture atlases
    """
```

---

### TASK-031-4: bake_diffuse

**Status:** ✅ Done

Bakes diffuse/albedo color only.

```python
@mcp.tool()
def bake_diffuse(
    ctx: Context,
    object_name: str,
    output_path: str,
    resolution: int = 1024,
    margin: int = 16
) -> str:
    """
    [OBJECT MODE][REQUIRES UV] Bakes diffuse color to texture.

    Useful for baking procedural materials to static textures.
    """
```

---

## Implementation Notes

1. **Cycles Required**: Baking only works with Cycles renderer
2. **UV Required**: Object must have UV map - validate and error if missing
3. **Auto-setup**: Create temporary image texture node if material doesn't have one
4. **File formats**: Support PNG (default), EXR (for normals), JPEG
5. **Progress**: Baking can take time - consider async or timeout handling

---

## Architecture Considerations

Baking is complex and may require:
- Temporary scene modifications (renderer switch)
- Image creation and management
- Node tree manipulation
- Cleanup after baking

Consider creating a `BakingHandler` class in `blender_addon/application/handlers/baking.py`.

---

## Testing Requirements

- [x] Unit tests with mocked bpy.ops.object.bake (14 tests)
- [x] E2E test: Create sphere → UV unwrap → bake normal → verify image file
- [x] E2E test: High-to-low baking workflow
- [x] Test error handling for missing UVs
- [x] Test Cycles renderer auto-switch

## Implementation Summary

**Completed:** 2025-11-30

**Files Created/Modified:**
- `server/domain/tools/baking.py` - IBakingTool interface
- `server/application/tool_handlers/baking_handler.py` - RPC bridge implementation
- `server/adapters/mcp/areas/baking.py` - MCP tool definitions (4 tools)
- `server/infrastructure/di.py` - Added get_baking_handler provider
- `blender_addon/application/handlers/baking.py` - Blender API implementation
- `blender_addon/__init__.py` - RPC handler registration
- `tests/unit/tools/baking/test_baking_handler.py` - 14 unit tests
- `tests/e2e/tools/baking/test_baking_tools.py` - E2E tests

**Features:**
- Automatic Cycles renderer switching (required for baking)
- UV map validation with helpful error messages
- Auto-creation of bake material/node if missing
- Support for PNG, JPEG, EXR output formats
- High-to-low poly baking with cage extrusion
- TANGENT and OBJECT normal space support
