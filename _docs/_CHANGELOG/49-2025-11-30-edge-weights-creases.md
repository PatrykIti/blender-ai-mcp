# 49 - 2025-11-30 - Edge Weights & Creases (TASK-029)

## Summary

Implemented Edge Weights & Creases tools for subdivision control. These tools are **critical for game dev** and hard-surface modeling, enabling control over how subdivision surface and bevel modifiers affect geometry.

## New MCP Tools

### mesh_edge_crease
Sets crease weight on selected edges for Subdivision Surface modifier control.
- `crease_value`: float (0.0 to 1.0)
- 0.0 = fully smoothed, 1.0 = fully sharp

### mesh_bevel_weight
Sets bevel weight on selected edges for selective beveling with Bevel modifier.
- `weight`: float (0.0 to 1.0)
- Use with Bevel modifier's "Weight" limit method

### mesh_mark_sharp
Marks or clears sharp edges for Smooth by Angle (5.0+) and Edge Split modifier.
- `action`: "mark" | "clear"
- Affects normal calculations and shading

## Use Cases

- **Hard-surface modeling**: weapons, vehicles, devices
- **Architectural details**: window frames, door edges
- **Character modeling**: eye sockets, fingernails

## Technical Details

### Implementation (4-Layer Architecture)
1. **Domain Layer**: Added abstract methods to `IMeshTool` interface
2. **Application Layer**: RPC bridge methods in `MeshToolHandler`
3. **Adapter Layer**: MCP tool definitions with semantic tags
4. **Blender Addon**: BMesh-based implementations for edge data manipulation

### Semantic Tags
- `mesh_edge_crease`: `[EDIT MODE][SELECTION-BASED][NON-DESTRUCTIVE]`
- `mesh_bevel_weight`: `[EDIT MODE][SELECTION-BASED][NON-DESTRUCTIVE]`
- `mesh_mark_sharp`: `[EDIT MODE][SELECTION-BASED][NON-DESTRUCTIVE]`

## Testing

### Unit Tests (15 tests, all passing)
- `tests/unit/tools/mesh/test_mesh_edge_weights.py`
- Tests for value clamping, selection validation, action handling

### E2E Tests (created, require manual Blender run)
- `tests/e2e/tools/mesh/test_mesh_edge_weights.py`
- Workflow tests: Crease + Subsurf, Bevel Weight + Bevel modifier, Mark Sharp

## Files Changed

### Server
- `server/domain/tools/mesh.py` - Added abstract methods
- `server/application/tool_handlers/mesh_handler.py` - Added RPC handlers
- `server/adapters/mcp/areas/mesh.py` - Added MCP tool definitions

### Blender Addon
- `blender_addon/application/handlers/mesh.py` - Added BMesh implementations
- `blender_addon/__init__.py` - Registered RPC handlers

### Tests
- `tests/unit/tools/mesh/test_mesh_edge_weights.py` (new)
- `tests/e2e/tools/mesh/test_mesh_edge_weights.py` (new)

## Related Tasks

- **TASK-029-1**: mesh_edge_crease ✅
- **TASK-029-2**: mesh_bevel_weight ✅
- **TASK-029-3**: mesh_mark_sharp ✅

## Version

1.22.0
