# TASK-010: Scene Construction Tools (Lights, Cameras, Empties)

## 🎯 Objective
Implement tools for creating non-geometric scene elements essential for rendering and organization: **Lights**, **Cameras**, and **Empties**. These tools belong to the `scene_` domain as they relate to scene composition.

## 📋 Requirements

### 1. Interface & Schema (Domain)
*   Update `ISceneTool` interface with new methods:
    *   `create_light(type: str, energy: float, color: List[float], location: List[float], name: Optional[str]) -> str`
    *   `create_camera(name: str, location: List[float], rotation: List[float], lens: float, clip_start: Optional[float], clip_end: Optional[float]) -> str`
    *   `create_empty(type: str, size: float, location: List[float], name: Optional[str]) -> str`

### 2. Blender Addon Implementation
*   **Lights (`create_light`):**
    *   Use `bpy.data.lights.new()` and `bpy.data.objects.new()`.
    *   Set properties: Type (POINT, SUN, SPOT, AREA), Energy (Watts), Color (RGB).
    *   Link to scene collection.
*   **Cameras (`create_camera`):**
    *   Use `bpy.data.cameras.new()` and `bpy.data.objects.new()`.
    *   Set properties: Lens (focal length), Clip Start/End.
    *   Set transform (Location, Rotation Euler).
*   **Empties (`create_empty`):**
    *   Use `bpy.data.objects.new(name, None)`.
    *   Set `empty_display_type` (PLAIN_AXES, SPHERE, CUBE) and `empty_display_size`.

### 3. Server Implementation
*   Update `SceneToolHandler` to delegate these calls via RPC.
*   Update `server/adapters/mcp/server.py` to expose:
    *   `scene_create_light`
    *   `scene_create_camera`
    *   `scene_create_empty`

## ✅ Checklist
- [x] Update `server/domain/tools/scene.py`
- [x] Update `blender_addon/application/handlers/scene.py`
- [x] Update `server/application/tool_handlers/scene_handler.py`
- [x] Update `server/adapters/mcp/server.py`
- [x] Add tests in `tests/test_scene_construction.py`

## 📝 Tool Interface Examples

### Create Light
```json
{
  "tool": "scene_create_light",
  "args": {
    "type": "POINT",
    "energy": 1000.0,
    "color": [1.0, 0.9, 0.8],
    "location": [5.0, 5.0, 5.0]
  }
}
```

### Create Camera
```json
{
  "tool": "scene_create_camera",
  "args": {
    "name": "ShotCam",
    "location": [0, -10, 2],
    "rotation": [1.57, 0, 0],
    "lens": 85.0
  }
}
```
