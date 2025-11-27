# Scene Tools Architecture

Scene tools are used for managing objects, their selection, and preview.
According to the adopted convention (just like in Modeling Tools), **each operation is a separate tool**.

---

# 1. scene_list_objects ✅ Done
Lists objects in the scene.

Example:
```json
{
  "tool": "scene_list_objects",
  "args": {}
}
```

---

# 2. scene_delete_object ✅ Done
Deletes a specific object.

Example:
```json
{
  "tool": "scene_delete_object",
  "args": {
    "name": "Cube.001"
  }
}
```

---

# 3. scene_clean_scene ✅ Done
Cleans the scene (by default keeps lights and cameras).

Example:
```json
{
  "tool": "scene_clean_scene",
  "args": {
    "keep_lights_and_cameras": true
  }
}
```

---

# 4. scene_duplicate_object ✅ Done
Duplicates an object and optionally moves it.

Example:
```json
{
  "tool": "scene_duplicate_object",
  "args": {
    "name": "Cube",
    "translation": [2.0, 0.0, 0.0]
  }
}
```

---

# 5. scene_set_active_object ✅ Done
Sets an object as active (important for modifiers).

Example:
```json
{
  "tool": "scene_set_active_object",
  "args": {
    "name": "Cube"
  }
}
```

---

# 6. scene_get_viewport ✅ Done
Gets a scene preview (viewport render) with selectable output mode.

Args:
- width: int
- height: int
- shading: str (SOLID, WIREFRAME, MATERIAL, RENDERED)
- camera_name: str (optional)
- focus_target: str (optional - object to frame)
- output_mode: str ("IMAGE" default – FastMCP Image resource, or "BASE64", "FILE", "MARKDOWN")

Example:
```json
{
  "tool": "scene_get_viewport",
  "args": {
    "width": 1024,
    "height": 768,
    "shading": "WIREFRAME",
    "camera_name": "USER_PERSPECTIVE",
    "focus_target": "Cube"
  }
}
```

---

# 7. scene_create_light ✅ Done
Creates a light source.

Args:
- type: str (POINT, SUN, SPOT, AREA)
- energy: float (Watts)
- color: [r, g, b]
- location: [x, y, z]

Example:
```json
{
  "tool": "scene_create_light",
  "args": {
    "type": "POINT",
    "energy": 1000.0,
    "color": [1.0, 0.5, 0.0],
    "location": [0.0, 0.0, 5.0]
  }
}
```

---

# 8. scene_create_camera ✅ Done
Creates a camera object.

Args:
- location: [x, y, z]
- rotation: [rx, ry, rz] (radians)
- lens: float (focal length mm)

Example:
```json
{
  "tool": "scene_create_camera",
  "args": {
    "location": [0.0, -10.0, 5.0],
    "rotation": [1.1, 0.0, 0.0],
    "lens": 85.0
  }
}
```

---

# 9. scene_create_empty ✅ Done
Creates an Empty object (helper/parent).

Args:
- type: str (PLAIN_AXES, CUBE, SPHERE, etc.)
- size: float
- location: [x, y, z]

Example:
```json
{
  "tool": "scene_create_empty",
  "args": {
    "type": "CUBE",
    "size": 2.0,
    "location": [0.0, 0.0, 0.0]
  }
}
```

---

# 10. scene_get_mode ✅ Done
Reports the current Blender mode, active object, and selection count so AI agents can branch logic safely.

Example:
```json
{
  "tool": "scene_get_mode",
  "args": {}
}
```

---

# Rules
1. **Prefix `scene_`**: All tools must start with this prefix.
2. **Atomicity**: One tool = one action. Do not group actions into one tool with an `action` parameter.
