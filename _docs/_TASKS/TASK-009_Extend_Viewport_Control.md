# TASK-009: Extend Viewport Control

## 🎯 Objective
Enhance the `scene_get_viewport` tool to provide the AI with control over the visual feedback it receives. The AI should be able to:
1.  Request specific shading modes (e.g., Wireframe to see topology).
2.  Choose which camera to look through.
3.  **Focus on specific objects** or the whole scene when generating a dynamic view.

## 📋 Requirements

### 1. Interface & Schema
*   Update `ISceneTool.get_viewport` signature.
*   Add optional parameters:
    *   `shading` (str): 'WIREFRAME', 'SOLID', 'MATERIAL', 'RENDERED'.
    *   `camera_name` (str): Name of the camera object to use.
    *   `focus_target` (str): Name of the object to frame (focus on). Only applicable when `camera_name` is not a specific existing camera (i.e., when using "USER_PERSPECTIVE").

### 2. Server Implementation
*   Update `SceneToolHandler` to pass these parameters via RPC.
*   Update `server.py` (MCP Adapter) to expose these parameters to the LLM.

### 3. Blender Addon Implementation
*   **Shading Control:**
    *   Locate the 3D View area.
    *   Temporarily override `space_data.shading.type`.
*   **Camera Control & Framing:**
    *   **Case A: Specific Camera (`camera_name="Camera.001"`)**
        *   If the object exists, use it as the active camera for the render.
        *   Ignore `focus_target` (to avoid modifying the user's existing camera transform).
    *   **Case B: Dynamic View (`camera_name="USER_PERSPECTIVE"` or `None`)**
        *   Create a temporary camera.
        *   **Focus Logic:**
            *   If `focus_target` is provided and exists: Select ONLY that object and frame the camera to selection ("View Selected").
            *   If `focus_target` is None: Select ALL objects and frame the camera to bounds ("View All").
        *   Use this temporary camera for the render.
*   **State Restoration:**
    *   Ensure that after the render, the scene's active camera, selection state, and the viewport's shading mode are restored to their previous state. The tool must be side-effect free regarding the view and selection.

## ✅ Checklist
- [ ] Update `server/domain/tools/scene.py` (Interface)
- [ ] Update `server/application/tool_handlers/scene_handler.py`
- [ ] Update `server/adapters/mcp/server.py`
- [ ] Update `blender_addon/application/handlers/scene.py`
- [ ] Verify state restoration (shading/camera/selection)

## 📝 Tool Interface Examples

### Example 1: View Whole Scene in Wireframe
```json
{
  "tool": "scene_get_viewport",
  "args": {
    "width": 1024,
    "height": 768,
    "shading": "WIREFRAME",
    "camera_name": "USER_PERSPECTIVE"
  }
}
```

### Example 2: Focus on Specific Object
```json
{
  "tool": "scene_get_viewport",
  "args": {
    "shading": "SOLID",
    "focus_target": "Cube.001"
  }
}
```