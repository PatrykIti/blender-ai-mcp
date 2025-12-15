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

# 10. metaball_create ✅ Done (TASK-038)
Creates a metaball object for organic blob shapes. Metaballs automatically merge when close together.

**Tag:** `[OBJECT MODE][NON-DESTRUCTIVE]`

Args:
- name: str (name for the metaball object)
- location: [x, y, z] (world position)
- element_type: str ("BALL", "CAPSULE", "PLANE", "ELLIPSOID", "CUBE") - default "BALL"
- radius: float (element radius, default 1.0)
- resolution: float (viewport resolution, default 0.2)
- threshold: float (merge threshold, default 0.6)

Example:
```json
{
  "tool": "metaball_create",
  "args": {
    "name": "OrganicBlob",
    "location": [0.0, 0.0, 0.0],
    "element_type": "BALL",
    "radius": 1.0
  }
}
```

Use Case:
- Organic shapes (organs, tumors, cells)
- Blob-based modeling
- Quick organic prototypes

---

# 11. metaball_add_element ✅ Done (TASK-038)
Adds an element to an existing metaball for organic merging effects.

**Tag:** `[OBJECT MODE][NON-DESTRUCTIVE]`

Args:
- metaball_name: str (target metaball object)
- element_type: str ("BALL", "CAPSULE", "PLANE", "ELLIPSOID", "CUBE") - default "BALL"
- location: [x, y, z] (local position relative to metaball)
- radius: float (element radius, default 1.0)
- stiffness: float (merge stiffness 0-10, default 2.0)

Example:
```json
{
  "tool": "metaball_add_element",
  "args": {
    "metaball_name": "OrganicBlob",
    "element_type": "BALL",
    "location": [1.5, 0.0, 0.0],
    "radius": 0.8
  }
}
```

Use Case:
- Building complex organic forms
- Adding chambers to organs
- Creating multi-lobe structures

---

# 12. metaball_to_mesh ✅ Done (TASK-038)
Converts a metaball to mesh geometry for further editing.

**Tag:** `[OBJECT MODE][DESTRUCTIVE]`

Args:
- metaball_name: str (target metaball object)
- apply_resolution: bool (apply current resolution before conversion) - default true

Example:
```json
{
  "tool": "metaball_to_mesh",
  "args": {
    "metaball_name": "OrganicBlob",
    "apply_resolution": true
  }
}
```

Use Case:
- Finalizing metaball shapes
- Preparing for sculpting
- Converting to editable geometry

---

# 13. skin_create_skeleton ✅ Done (TASK-038)
Creates a skeleton mesh with Skin modifier for tubular/organic structures.

**Tag:** `[OBJECT MODE][NON-DESTRUCTIVE]`

Args:
- name: str (name for skeleton object)
- vertices: List[[x, y, z]] (vertex positions)
- edges: List[[v1, v2]] (edge connections by vertex index)
- location: [x, y, z] (world position, optional)

Example:
```json
{
  "tool": "skin_create_skeleton",
  "args": {
    "name": "BloodVessel",
    "vertices": [[0, 0, 0], [0, 0, 1], [0.3, 0, 1.5], [-0.3, 0, 1.5]],
    "edges": [[0, 1], [1, 2], [1, 3]]
  }
}
```

Use Case:
- Blood vessels, arteries, veins
- Nerve networks
- Tentacles, roots, branches
- Organic tube structures

---

# 14. skin_set_radius ✅ Done (TASK-038)
Sets skin radius at vertices for varying thickness along skeleton.

**Tag:** `[EDIT MODE][SELECTION-BASED][NON-DESTRUCTIVE]`

Args:
- object_name: str (target skeleton object)
- vertex_index: int or List[int] (vertex indices to modify)
- radius_x: float (radius in X direction)
- radius_y: float (radius in Y direction, optional - defaults to radius_x)

Example:
```json
{
  "tool": "skin_set_radius",
  "args": {
    "object_name": "BloodVessel",
    "vertex_index": 0,
    "radius_x": 0.15,
    "radius_y": 0.15
  }
}
```

Use Case:
- Tapering blood vessels
- Varying thickness for nerves
- Creating natural organic flow

---

# Rules
1. **Prefix `modeling_`**: All tools must start with this prefix (except metaball/skin tools which use their domain prefix).
2. **Object Mode**: These tools primarily operate in Object Mode or manage container-level data.
3. **Mesh Operations**: Edit Mode operations (like extrude, loop cut) will be handled by `mesh_` tools (Phase 2).
