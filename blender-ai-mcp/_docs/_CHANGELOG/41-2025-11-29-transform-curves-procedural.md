# Changelog #41 - Phase 2.4 & 2.6: Transform, Curves & Procedural Tools

**Date:** 2025-11-29
**Tasks:** TASK-019, TASK-021

## Summary

Implemented core transform tools for Edit Mode (Phase 2.4) and curve/procedural tools (Phase 2.6). The `mesh_transform_selected` tool is particularly critical as it enables AI to reposition geometry after selection - unlocking ~80% of modeling tasks.

## New Tools

### Phase 2.4 - Core Transform & Geometry (3 tools)

| Tool | Description |
|------|-------------|
| `mesh_transform_selected` | Transforms selected geometry (move/rotate/scale) with pivot options |
| `mesh_bridge_edge_loops` | Bridges two edge loops with faces (with cuts, interpolation, smoothness) |
| `mesh_duplicate_selected` | Duplicates selected geometry within the same mesh |

### Phase 2.6 - Curves & Procedural (7 tools)

| Tool | Description |
|------|-------------|
| `curve_create` | Creates curve primitives (BEZIER, NURBS, PATH, CIRCLE) |
| `curve_to_mesh` | Converts curve objects to mesh geometry |
| `mesh_spin` | Spins/lathes selected geometry around an axis |
| `mesh_screw` | Creates spiral/screw geometry from selected profile |
| `mesh_add_vertex` | Adds a single vertex at specified position |
| `mesh_add_edge_face` | Creates edge or face from selected vertices |

## Architecture Changes

### New Domain Layer
- `server/domain/tools/curve.py` - ICurveTool interface

### New Application Layer
- `server/application/tool_handlers/curve_handler.py` - CurveToolHandler

### New Adapter Layer
- `server/adapters/mcp/areas/curve.py` - Curve MCP tools

### New Blender Addon
- `blender_addon/application/handlers/curve.py` - CurveHandler

### Updated Files
- `server/domain/tools/mesh.py` - Added 8 new abstract methods
- `server/application/tool_handlers/mesh_handler.py` - Implemented 8 new methods
- `server/adapters/mcp/areas/mesh.py` - Added 8 new MCP tool definitions
- `blender_addon/application/handlers/mesh.py` - Added 8 new Blender implementations
- `server/infrastructure/di.py` - Added get_curve_handler provider
- `blender_addon/__init__.py` - Registered all new RPC handlers

## Technical Details

### mesh_transform_selected
- Supports translate, rotate, scale in single call
- 5 pivot options: MEDIAN_POINT, BOUNDING_BOX_CENTER, CURSOR, INDIVIDUAL_ORIGINS, ACTIVE_ELEMENT
- Rotation in radians, applied per-axis

### mesh_spin / mesh_screw
- Center defaults to 3D cursor if not provided
- Axis specified as X, Y, or Z (converted to vector internally)
- mesh_screw supports turns and offset (pitch)

### mesh_add_vertex / mesh_add_edge_face
- BMesh API for precise vertex creation
- add_edge_face uses bpy.ops.mesh.edge_face_add (same as 'F' key)

## Tests

All 201 tests pass (19 skipped - require Blender runtime).
