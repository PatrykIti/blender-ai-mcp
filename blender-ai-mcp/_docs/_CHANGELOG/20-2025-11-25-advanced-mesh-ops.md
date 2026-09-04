# Changelog: Advanced Mesh Operations

## Added
- **Mesh Tools (Edit Mode):**
    - `mesh.boolean`: Perform boolean operations (INTERSECT, UNION, DIFFERENCE) in Edit Mode.
    - `mesh.merge_by_distance`: Clean up geometry by merging vertices within a distance threshold.
    - `mesh.subdivide`: Subdivide selected geometry with optional smoothness.

## Updated
- **Addon:** Registered new handlers in `blender_addon/__init__.py`.
- **Server:** Added new methods to `MeshToolHandler` and `IMeshTool`.
- **Tests:** Added `tests/test_mesh_advanced.py` covering new operations.
