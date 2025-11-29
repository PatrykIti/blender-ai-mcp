# UV Tools Architecture

UV tools handle texture coordinate mapping operations, providing comprehensive UV mapping, unwrapping, and seam management for mesh objects.

---

## 1. uv_list_maps ✅ Done

Lists UV maps for a specified mesh object, including active flags and optional island statistics.

Args:
- object_name: str - Name of the mesh object to query
- include_island_counts: bool (default False) - Include UV loop counts (island counts not yet implemented)

Returns:
- object_name: str - Name of the queried object
- uv_map_count: int - Number of UV maps
- uv_maps: list - Detailed UV map data

Each UV map entry contains:
- name: str - UV map name
- is_active: bool - Whether this is the active UV map
- is_active_render: bool - Whether this is active for rendering
- uv_loop_count: int (optional) - Number of UV coordinates
- island_count: int (optional) - Number of UV islands (not yet implemented)

Example:
```json
{
  "tool": "uv_list_maps",
  "args": {
    "object_name": "Cube",
    "include_island_counts": true
  }
}
```

Response:
```json
{
  "object_name": "Cube",
  "uv_map_count": 1,
  "uv_maps": [
    {
      "name": "UVMap",
      "is_active": true,
      "is_active_render": true,
      "uv_loop_count": 24
    }
  ]
}
```

---

## Rules

1. **Prefix `uv_`**: All UV tools must start with this prefix.
2. **Mesh-only**: UV operations only apply to MESH objects.
3. **Object Mode**: UV map queries work in Object Mode for performance.
4. **Island Counting**: Full UV island analysis requires bmesh and is marked as future enhancement.

---

## Architecture Layers

### Domain Layer
- **`server/domain/tools/uv.py`**
  - Defines `IUVTool` interface
  - Declares abstract methods for UV operations

### Application Layer
- **`server/application/tool_handlers/uv_handler.py`**
  - Implements `IUVTool` interface
  - Delegates to RPC client for Blender communication

### Blender Addon Handler
- **`blender_addon/application/handlers/uv.py`**
  - Accesses `obj.data.uv_layers` for UV map data
  - Reads active flags: `uv_layer.active`, `uv_layer.active_render`
  - Counts UV coordinates via `len(uv_layer.data)`
  - Validates mesh type before processing

### MCP Adapter
- **`server/adapters/mcp/server.py`**
  - Exposes `@mcp.tool() uv_list_maps()`
  - Tagged: `[UV][SAFE][READ-ONLY]`
  - Formats output with active flags and counts

### Dependency Injection
- **`server/infrastructure/di.py`**
  - Provides `get_uv_handler()` factory function
  - Injects RPC client dependency

### Registration
- **`blender_addon/__init__.py`**
  - Instantiates `UVHandler()`
  - Registers RPC endpoint: `uv.list_maps`

---

## 2. uv_unwrap ✅ Done

Unwraps selected faces to UV space using specified projection method.

**Tags:** `[EDIT MODE][SELECTION-BASED][DESTRUCTIVE]`

**Args:**
- `object_name`: str (optional) - Target object (default: active object)
- `method`: str - Projection method: SMART_PROJECT, CUBE, CYLINDER, SPHERE, UNWRAP
- `angle_limit`: float - Angle threshold for SMART_PROJECT (degrees, 0-89)
- `island_margin`: float - Space between UV islands (0.0-1.0)
- `scale_to_bounds`: bool - Scale UVs to fill 0-1 space

**Methods:**
- **SMART_PROJECT**: Automatic projection based on face angles (best for complex meshes)
- **CUBE**: Cube projection (best for boxy objects)
- **CYLINDER**: Cylindrical projection
- **SPHERE**: Spherical projection
- **UNWRAP**: Standard unwrap (requires seams for best results)

**Workflow:** BEFORE → mesh_select (select faces) | AFTER → uv_pack_islands

Example:
```json
{
  "tool": "uv_unwrap",
  "args": {
    "object_name": "Cube",
    "method": "SMART_PROJECT",
    "angle_limit": 66.0,
    "island_margin": 0.02,
    "scale_to_bounds": true
  }
}
```

---

## 3. uv_pack_islands ✅ Done

Packs UV islands for optimal texture space usage.

**Tags:** `[EDIT MODE][SELECTION-BASED][DESTRUCTIVE]`

**Args:**
- `object_name`: str (optional) - Target object (default: active object)
- `margin`: float - Space between packed islands (0.0-1.0)
- `rotate`: bool - Allow rotation for better packing
- `scale`: bool - Allow scaling islands to fill space

**Workflow:** BEFORE → uv_unwrap

Example:
```json
{
  "tool": "uv_pack_islands",
  "args": {
    "object_name": "Cube",
    "margin": 0.02,
    "rotate": true,
    "scale": true
  }
}
```

---

## 4. uv_create_seam ✅ Done

Marks or clears UV seams on selected edges.

**Tags:** `[EDIT MODE][SELECTION-BASED][NON-DESTRUCTIVE]`

**Args:**
- `object_name`: str (optional) - Target object (default: active object)
- `action`: str - 'mark' to add seams, 'clear' to remove seams

**Workflow:** BEFORE → mesh_select_targeted (select edges) | AFTER → uv_unwrap (with UNWRAP method)

Example:
```json
{
  "tool": "uv_create_seam",
  "args": {
    "object_name": "Cube",
    "action": "mark"
  }
}
```

---

## Future Enhancements

- **UV Island Counting**: Implement proper island detection using bmesh.ops
- **UV Overlap Detection**: Identify overlapping UV coordinates
- **UV Density Analysis**: Calculate texel density per face
- **UV Distortion Metrics**: Measure stretching and compression
- **Active Map Setting**: Tool to change active UV map

---

## Related Tools

- `scene_inspect_object` - Includes basic UV map count
- `material_list_by_object` - Shows material slots (textures use UV maps)
- `mesh_select` - Select geometry before UV operations
- `mesh_select_targeted` - Select specific edges for seam marking

---

**Status:** ✅ Complete (Phase 8)
**Version:** 1.17.0
