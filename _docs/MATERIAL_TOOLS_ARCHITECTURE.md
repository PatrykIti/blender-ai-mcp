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

# Rules
1. **Prefix `material_`**: All tools must start with this prefix.
2. **Read-Only**: Material tools primarily query material state.
3. **Shader Inspection**: Extracts Principled BSDF parameters when available.
