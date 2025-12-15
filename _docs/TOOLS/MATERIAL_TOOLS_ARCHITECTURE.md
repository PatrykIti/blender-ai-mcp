# Material Tools Architecture

Material tools manage Blender materials and their assignments.
**Each operation is a separate tool** to ensure clarity.

---

# 1. material_list ✅ Done
Lists all materials with shader parameters and assignment counts.

Args:
- include_unassigned: bool (default True) - includes materials not assigned to objects

Returns: List of materials with name, use_nodes, base_color, roughness, metallic, alpha, assigned_object_count

Example:
```json
{
  "tool": "material_list",
  "args": {
    "include_unassigned": true
  }
}
```

---

# 2. material_list_by_object ✅ Done
Lists material slots for a given object.

Args:
- object_name: str
- include_indices: bool (default False) - attempts face-level assignment info

Returns: Dict with object_name, slot_count, slots (slot_index, slot_name, material_name, uses_nodes)

Example:
```json
{
  "tool": "material_list_by_object",
  "args": {
    "object_name": "Cube",
    "include_indices": false
  }
}
```

---

---

# 3. material_create ✅ Done

Creates a new PBR material with Principled BSDF shader.

Args:
- name: str (required) - Material name
- base_color: List[float] or string "[r,g,b,a]" (optional) - RGBA color [0-1], default [0.8, 0.8, 0.8, 1.0]
- metallic: float (optional) - Metallic value 0-1, default 0.0
- roughness: float (optional) - Roughness value 0-1, default 0.5
- emission_color: List[float] or string "[r,g,b]" (optional) - Emission RGB [0-1]
- emission_strength: float (optional) - Emission strength, default 0.0
- alpha: float (optional) - Alpha/opacity 0-1, default 1.0

Returns: Success message with created material name

Example:
```json
{
  "tool": "material_create",
  "args": {
    "name": "RedMetal",
    "base_color": [1.0, 0.0, 0.0, 1.0],
    "metallic": 0.9,
    "roughness": 0.2
  }
}
```

---

# 4. material_assign ✅ Done

Assigns material to object or selected faces.

Args:
- material_name: str (required) - Name of existing material
- object_name: str (optional) - Target object, default: active object
- slot_index: int (optional) - Material slot index, default: auto
- assign_to_selection: bool (optional) - If True and in Edit Mode, assign to selected faces

Returns: Success message with assignment details

Example (Object Mode):
```json
{
  "tool": "material_assign",
  "args": {
    "material_name": "RedMetal",
    "object_name": "Cube"
  }
}
```

Example (Edit Mode - face assignment):
```json
{
  "tool": "material_assign",
  "args": {
    "material_name": "BluePlastic",
    "assign_to_selection": true
  }
}
```

---

# 5. material_set_params ✅ Done

Modifies parameters of existing material. Only provided parameters are changed.

Args:
- material_name: str (required) - Name of material to modify
- base_color: List[float] (optional) - New RGBA color [0-1]
- metallic: float (optional) - New metallic value 0-1
- roughness: float (optional) - New roughness value 0-1
- emission_color: List[float] (optional) - New emission RGB [0-1]
- emission_strength: float (optional) - New emission strength
- alpha: float (optional) - New alpha/opacity 0-1

Returns: Success message with list of modified parameters

Example:
```json
{
  "tool": "material_set_params",
  "args": {
    "material_name": "RedMetal",
    "roughness": 0.8,
    "metallic": 0.5
  }
}
```

---

# 6. material_set_texture ✅ Done

Binds image texture to material input. Automatically creates Image Texture node and connects to Principled BSDF.

Args:
- material_name: str (required) - Target material name
- texture_path: str (required) - Path to image file
- input_name: str (optional) - BSDF input, default "Base Color"
  - Valid: "Base Color", "Roughness", "Normal", "Metallic", "Emission Color", "Alpha"
- color_space: str (optional) - Color space, default "sRGB"
  - Use "sRGB" for color maps
  - Use "Non-Color" for data maps (roughness, metallic, normal)

Returns: Success message with connection details

Example (Base Color):
```json
{
  "tool": "material_set_texture",
  "args": {
    "material_name": "WoodMaterial",
    "texture_path": "/textures/wood_diffuse.png",
    "input_name": "Base Color"
  }
}
```

Example (Normal Map):
```json
{
  "tool": "material_set_texture",
  "args": {
    "material_name": "WoodMaterial",
    "texture_path": "/textures/wood_normal.png",
    "input_name": "Normal",
    "color_space": "Non-Color"
  }
}
```

**Note:** Normal maps automatically get a Normal Map node inserted between texture and BSDF.

---

# Rules
1. **Prefix `material_`**: All tools must start with this prefix.
2. **Principled BSDF**: All materials use Principled BSDF shader by default.
3. **Shader Inspection**: Extracts Principled BSDF parameters when available.
4. **Transparency**: Alpha < 1.0 automatically sets blend mode to BLEND.
5. **Normal Maps**: Automatically create Normal Map node for proper conversion.
