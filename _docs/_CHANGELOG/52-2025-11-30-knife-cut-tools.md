# 52 - Knife & Cut Tools (TASK-032)

**Date:** 2025-11-30
**Version:** 1.25.0

## Summary

Implemented **TASK-032: Knife & Cut Tools** - Precision geometry cutting tools for hard-surface modeling, architectural details, and panel lines.

## Changes

### New Tools (4)

| Tool | Description |
|------|-------------|
| `mesh_knife_project` | Projects knife cut from view using selected geometry |
| `mesh_rip` | Rips (tears) geometry at selected vertices |
| `mesh_split` | Splits selection from mesh (disconnects without separating) |
| `mesh_edge_split` | Splits mesh at selected edges (creates seams) |

### Files Modified

**Server Side:**
- `server/domain/tools/mesh.py` - Added 4 abstract methods to IMeshTool
- `server/application/tool_handlers/mesh_handler.py` - Added 4 RPC methods
- `server/adapters/mcp/areas/mesh.py` - Added 4 MCP tool definitions

**Blender Addon:**
- `blender_addon/application/handlers/mesh.py` - Added 4 implementation methods
- `blender_addon/__init__.py` - Registered 4 RPC handlers

**Tests:**
- `tests/unit/tools/knife_cut/test_knife_cut_handler.py` - 9 unit tests
- `tests/e2e/tools/knife_cut/test_knife_cut_tools.py` - E2E test suite

## RPC Handlers Registered

| RPC Command | Handler Method |
|-------------|----------------|
| `mesh.knife_project` | `knife_project` |
| `mesh.rip` | `rip` |
| `mesh.split` | `split` |
| `mesh.edge_split` | `edge_split` |

## Use Cases

- **mesh_knife_project**: Logo cutouts, panel lines, window frames (requires orthographic view)
- **mesh_rip**: Creating openings, tears, separating connected geometry
- **mesh_split**: Creating movable parts that stay in same object
- **mesh_edge_split**: UV seam preparation, material boundaries, rigging preparation

## Testing

- 9 unit tests (all passing)
- E2E tests covering:
  - Knife project with cut_through options
  - Rip with and without fill
  - Split selected faces
  - Edge split on edge loops
  - Integration workflows
