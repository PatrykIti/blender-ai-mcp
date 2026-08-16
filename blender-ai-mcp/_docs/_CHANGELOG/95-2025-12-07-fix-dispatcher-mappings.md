# 95 - Fix ToolDispatcher Mappings

**Date:** 2025-12-07
**Task:** [TASK-049](../_TASKS/TASK-049_Fix_ToolDispatcher_Mappings.md)
**Type:** Bug Fix

---

## Summary

Fixed multiple missing and incorrect tool mappings in `ToolDispatcher` that were causing "tool not found" errors when the Router tried to dispatch tool calls.

---

## Changes

### Added Mappings (12 total)

**Export/Import Tools (7):**
- `export_glb` → `export_glb`
- `export_fbx` → `export_fbx`
- `export_obj` → `export_obj`
- `import_obj` → `import_obj`
- `import_fbx` → `import_fbx`
- `import_glb` → `import_glb`
- `import_image_as_plane` → `import_image_as_plane`

**Metaball/Skin Tools (5):**
- `metaball_create` → `metaball_create`
- `metaball_add_element` → `metaball_add_element`
- `metaball_to_mesh` → `metaball_to_mesh`
- `skin_create_skeleton` → `skin_create_skeleton`
- `skin_set_radius` → `skin_set_radius`

### Fixed Mappings (3)

| Tool | Old (Wrong) | New (Correct) |
|------|-------------|---------------|
| `mesh_boolean` | `boolean_operation` | `boolean` |
| `mesh_smooth` | `smooth` | `smooth_vertices` |
| `mesh_flatten` | `flatten` | `flatten_vertices` |

### Removed Invalid Mappings (4)

Removed non-existent individual collection action methods:
- `collection_create` → ~~`create`~~
- `collection_delete` → ~~`delete`~~
- `collection_rename` → ~~`rename`~~
- `collection_move_object` → ~~`move_object`~~

Added proper mapping:
- `collection_manage` → `manage_collection`

---

## Files Modified

| File | Changes |
|------|---------|
| `server/adapters/mcp/dispatcher.py` | +12 mappings, 3 fixes, -4 invalid |

---

## Impact

- Router can now dispatch all 154 registered tools correctly
- Export/import functionality works via Router
- Metaball/skin organic modeling tools work via Router
- Mesh boolean, smooth, and flatten operations work correctly
