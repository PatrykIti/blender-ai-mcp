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

# 11. scene_list_selection ✅ Done
Lists current selection information. In Object Mode it returns the selected object names/count. In Edit Mode it includes selected vertex/edge/face counts.

Example:
```json
{
  "tool": "scene_list_selection",
  "args": {}
}
```

---

# 12. scene_inspect_object ✅ Done
Provides a structured report for a specific object (transform, collections, materials, modifiers, mesh stats, custom properties).

Example:
```json
{
  "tool": "scene_inspect_object",
  "args": {
    "name": "Cube"
  }
}
```

---

# 13. scene_snapshot_state ✅ Done
Captures a lightweight JSON snapshot of the scene state (object transforms, hierarchy, modifiers, selection) for client-side storage and later diffing.

Args:
- include_mesh_stats: bool (default False) - includes vertex/edge/face counts for meshes
- include_materials: bool (default False) - includes material names assigned to objects

Returns: Dict with `hash` (SHA256 for change detection) and `snapshot` (JSON payload)

Example:
```json
{
  "tool": "scene_snapshot_state",
  "args": {
    "include_mesh_stats": true,
    "include_materials": false
  }
}
```

---

# 14. scene_compare_snapshot ✅ Done
Compares two scene snapshots and returns a structured diff summary (added/removed/modified objects).

Args:
- baseline_snapshot: str (JSON string from scene_snapshot_state)
- target_snapshot: str (JSON string from scene_snapshot_state)
- ignore_minor_transforms: float (default 0.0) - threshold for ignoring small transform changes

Note: This tool runs entirely on the MCP server side without requiring RPC to Blender.

Example:
```json
{
  "tool": "scene_compare_snapshot",
  "args": {
    "baseline_snapshot": "{...}",
    "target_snapshot": "{...}",
    "ignore_minor_transforms": 0.001
  }
}
```

---

# 15. scene_inspect_material_slots ✅ Done
Audits material slot assignments across the entire scene, providing a comprehensive view of how materials are distributed across all objects.

Args:
- material_filter: str (optional) - filter results by material name
- include_empty_slots: bool (default True) - include slots with no material assigned

Returns structured data including:
- total_slots: total number of material slots
- assigned_slots: number of slots with materials
- empty_slots: number of empty slots
- warnings: list of issues (empty slots, missing materials)
- slots: detailed slot data for each object

Example:
```json
{
  "tool": "scene_inspect_material_slots",
  "args": {
    "material_filter": null,
    "include_empty_slots": true
  }
}
```

---

# Rules
1. **Prefix `scene_`**: All tools must start with this prefix.
2. **Atomicity**: One tool = one action. Do not group actions into one tool with an `action` parameter.
