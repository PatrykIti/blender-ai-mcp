# 18. Basic Extrusions & Face Operations

**Date:** 2025-11-24  
**Version:** 0.2.1  
**Tasks:** TASK-011-2

## 🚀 Key Changes

### Mesh Editing Capabilities
The AI can now "grow" geometry, which is the fundamental action in 3D modeling.

### New Tools (Edit Mode)
- `mesh_extrude_region(move: List[float])`: Extrudes the currently selected vertices/edges/faces and optionally moves them immediately. This mimics the standard `E` key behavior in Blender.
- `mesh_fill_holes()`: Creates faces from selected geometry (equivalent to the `F` key).

### Technical Details
- **Implementation**: Uses `bpy.ops.mesh.extrude_region_move` for robust context handling.
- **Tests**: Added `tests/test_mesh_extrude.py` verifying extrusion arguments and hole filling logic with mocked `bmesh` and `bpy`.
