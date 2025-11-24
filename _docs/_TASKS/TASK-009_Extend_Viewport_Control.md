# TASK-009: Extend Viewport Control

## 🎯 Objective
Enhance the `scene_get_viewport` tool to provide the AI with control over the visual feedback it receives. The AI should be able to request specific shading modes (e.g., Wireframe to see topology) and choose which camera to look through.

## 📋 Requirements

### 1. Interface & Schema
*   Update `ISceneTool.get_viewport` signature.
*   Add optional parameters:
    *   `shading` (str): 'WIREFRAME', 'SOLID', 'MATERIAL', 'RENDERED'.
    *   `camera_name` (str): Name of the camera object to use.

### 2. Server Implementation
*   Update `SceneToolHandler` to pass these parameters via RPC.
*   Update `server.py` (MCP Adapter) to expose these parameters to the LLM.

### 3. Blender Addon Implementation
*   **Shading Control:**
    *   Locate the 3D View area.
    *   Temporarily override `space_data.shading.type`.
*   **Camera Control:**
    *   If `camera_name` is provided and exists: Temporarily set `scene.camera` to that object.
    *   If `camera_name` == "USER_PERSPECTIVE":
        *   Create a temporary camera.
        *   Position it to frame all objects (similar to "View All").
        *   Use this camera for render, ignoring the scene's active camera.
    *   If `camera_name` is None (default): Use the scene's active camera. If no active camera, fallback to "USER_PERSPECTIVE" logic.
*   **State Restoration:**
    *   Ensure that after the render, the scene's active camera and the viewport's shading mode are restored to their previous state. The tool must be side-effect free regarding the view.

## ✅ Checklist
- [ ] Update `server/domain/tools/scene.py` (Interface)
- [ ] Update `server/application/tool_handlers/scene_handler.py`
- [ ] Update `server/adapters/mcp/server.py`
- [ ] Update `blender_addon/application/handlers/scene.py`
- [ ] Verify state restoration (shading/camera)

## 📝 Tool Interface Example

### Request (JSON)
```json
{
  "tool": "scene_get_viewport",
  "args": {
    "width": 1024,
    "height": 768,
    "shading": "WIREFRAME",
    "camera_name": "Camera.001"
  }
}
```

### Response (Image)
The tool returns a FastMCP `Image` object, which the MCP protocol handles as binary data (base64 encoded internally if needed).
For the LLM, it appears as an image resource.

