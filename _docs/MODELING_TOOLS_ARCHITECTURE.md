# Modeling Tools Architecture

Modeling tools manage geometry creation, modification, and object-level manipulation.
**Each operation is a separate tool** to ensure clarity and avoid context mixing (except for strictly parametric operations like adding modifiers).

---

# 1. modeling_create_primitive ✅ Done
Creates basic 3D shapes.

Types: `Cube`, `Sphere`, `Cylinder`, `Plane`, `Cone`, `Monkey`, `Torus`.

Example:
```json
{
  "tool": "modeling_create_primitive",
  "args": {
    "primitive_type": "Cube",
    "size": 2.0,
    "location": [0.0, 0.0, 0.0],
    "rotation": [0.0, 0.0, 0.0]
  }
}
```

---

# 2. modeling_transform_object ✅ Done
Moves, rotates, or scales an existing object.

Example:
```json
{
  "tool": "modeling_transform_object",
  "args": {
    "name": "Cube",
    "location": [1.0, 2.0, 3.0],
    "rotation": [0.0, 1.57, 0.0],
    "scale": [1.0, 1.0, 2.0]
  }
}
```

---

# 3. modeling_add_modifier ✅ Done
Adds a non-destructive modifier to an object.

Example:
```json
{
  "tool": "modeling_add_modifier",
  "args": {
    "name": "Cube",
    "modifier_type": "BEVEL",
    "properties": {
      "width": 0.05,
      "segments": 3
    }
  }
}
```

---

# 4. modeling_apply_modifier ✅ Done
Permanently applies a modifier to the mesh geometry.

Example:
```json
{
  "tool": "modeling_apply_modifier",
  "args": {
    "name": "Cube",
    "modifier_name": "Bevel"
  }
}
```

---

# 5. modeling_list_modifiers ✅ Done
Lists all modifiers currently on an object.

Example:
```json
{
  "tool": "modeling_list_modifiers",
  "args": {
    "name": "Cube"
  }
}
```

---

# 6. modeling_convert_to_mesh ✅ Done
Converts objects (Curve, Text, Surface) into a Mesh.

Example:
```json
{
  "tool": "modeling_convert_to_mesh",
  "args": {
    "name": "BezierCurve"
  }
}
```

---

# 7. modeling_join_objects ✅ Done
Joins multiple mesh objects into a single one.

Example:
```json
{
  "tool": "modeling_join_objects",
  "args": {
    "object_names": ["Body", "Arm.L", "Arm.R"]
  }
}
```

---

# 8. modeling_separate_object ✅ Done
Separates a mesh object into multiple objects.

Types: `LOOSE` (loose parts), `SELECTED` (selected faces), `MATERIAL`.

Example:
```json
{
  "tool": "modeling_separate_object",
  "args": {
    "name": "Chair",
    "type": "LOOSE"
  }
}
```

---

# 9. modeling_set_origin ✅ Done
Sets the object's origin point.

Types: `GEOMETRY`, `ORIGIN_CURSOR`, `ORIGIN_CENTER_OF_MASS`.

Example:
```json
{
  "tool": "modeling_set_origin",
  "args": {
    "name": "Cube",
    "type": "GEOMETRY"
  }
}
```

---

# Rules
1. **Prefix `modeling_`**: All tools must start with this prefix.
2. **Object Mode**: These tools primarily operate in Object Mode or manage container-level data.
3. **Mesh Operations**: Edit Mode operations (like extrude, loop cut) will be handled by `mesh_` tools (Phase 2).
