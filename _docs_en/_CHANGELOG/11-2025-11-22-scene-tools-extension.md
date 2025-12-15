# 11. Scene Tools Extension (Duplicate, Set Active, Viewport)

**Date:** 2025-11-22  
**Version:** 0.1.10  
**Tasks:** TASK-007

## 🚀 Key Changes

### Domain Layer (`server/domain/tools/scene.py`)
- Updated `ISceneTool` interface with new methods:
  - `duplicate_object(name: str, translation: Optional[List[float]] = None) -> Dict[str, Any]`
  - `set_active_object(name: str) -> str`
  - `get_viewport(width: int = 1024, height: int = 768) -> str` (Returns Base64 encoded image)

### Blender Addon (Server Side)
- **`blender_addon/application/handlers/scene.py`**:
  - Implemented `duplicate_object`: Selects object, duplicates it using `bpy.ops.object.duplicate()`, and optionally translates it.
  - Implemented `set_active_object`: Sets the active object in `bpy.context.view_layer.objects.active`.
  - Implemented `get_viewport`: Render scene using OpenGL (`bpy.ops.render.opengl`) with a temporary camera if needed, returning a Base64 encoded image.

### Application Layer (`server/application/tool_handlers/scene_handler.py`)
- Implemented new methods in `SceneToolHandler` to delegate calls to the RPC client.

### Adapters Layer (`server/adapters/mcp/server.py`)
- Registered new MCP tools:
  - `duplicate_object`
  - `set_active_object`
  - `get_viewport` (Returns `fastmcp.Image` resource).

### Testing
- Added `tests/test_scene_tools_extended.py`: Unit tests verifying the logic of new tools using `unittest.mock` and `PropertyMock`.

AI can now duplicate objects, control selection, and "see" the scene via viewport renders.
