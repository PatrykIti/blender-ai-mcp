# 2. Scene Tools Implementation (MVP)

**Date:** 2025-11-22  
**Version:** 0.1.1  
**Tasks:** TASK-003

## 🚀 Key Changes

### MCP Server (Client Side)
- Initialized main server file: `server/main.py`.
- Configured `FastMCP` instance.
- Implemented first tools available for AI:
  - `list_objects()`: Returns a list of scene objects (name, type, location).
  - `delete_object(name)`: Deletes an object by name.
  - `clean_scene()`: Clears the scene of geometric objects (Mesh, Curve, etc.), keeping cameras and lights.

### Blender Addon (Server Side)
- Added module `blender_addon/api/scene.py` with logic implementation at the `bpy` level.
- Registered new RPC handlers in `blender_addon/__init__.py`.
- Added safeguards against deleting non-existent objects (raises `ValueError` -> returns JSON error).

### Testing
- Added `tests/test_scene_tools.py`: Unit tests with full mocking of `bpy.data` and `bpy.context`. Verifies logic without running Blender.
