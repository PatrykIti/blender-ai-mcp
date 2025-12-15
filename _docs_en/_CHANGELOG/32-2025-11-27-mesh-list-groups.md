# Changelog #32 - Mesh List Groups (TASK-014-12)

**Date:** 2025-11-27
**Version:** 1.9.11
**Phase:** Phase 7 - Introspection & Listing APIs
**Task:** TASK-014-12

---

## 📋 Summary

Implemented `mesh_list_groups` tool to list vertex groups and face maps/attributes on a mesh object. This allows AI to verify rigging setup, modifier targets, and geometry organization.

---

## ✨ Features Added

### Domain Layer
- **`server/domain/tools/mesh.py`**
  - Added `list_groups(object_name, group_type)` to `IMeshTool`.

### Application Layer
- **`server/application/tool_handlers/mesh_handler.py`**
  - Implemented `list_groups` delegating to RPC.

### Blender Addon Handler
- **`blender_addon/application/handlers/mesh.py`**
  - Implemented `list_groups` logic.
  - Supports `VERTEX` groups (returns index, member_count, lock_weight).
  - Supports `FACE` groups (checks `face_maps` or fallback to `attributes` for Blender 3.0+).
  - Validates object type.

### MCP Adapter
- **`server/adapters/mcp/server.py`**
  - Exposed `mesh_list_groups` tool.
  - Formats output with group details and counts.

### Registration
- **`blender_addon/__init__.py`**
  - Registered `mesh.list_groups` RPC endpoint.

---

## 📊 Return Data Structure

```json
{
  "object_name": "Cube",
  "group_type": "VERTEX",
  "group_count": 2,
  "groups": [
    {
      "name": "Group",
      "index": 0,
      "member_count": 8,
      "lock_weight": false
    }
  ]
}
```

---

## 🧪 Testing

### Test File
- **`tests/test_mesh_list_groups.py`**
  - Verified vertex group listing with member counts.
  - Verified face map/attribute fallback.
  - Validated error handling for missing objects or wrong types.

---

## 📚 Documentation Updates

- Updated `_docs/AVAILABLE_TOOLS_SUMMARY.md`.
- Updated `_docs/MESH_TOOLS_ARCHITECTURE.md`.
- Updated `_docs/_TASKS/TASK-014-12_Mesh_List_Groups.md`.

---

**Status:** ✅ Complete
**Next:** TASK-014-13 (Scene Inspect Mesh Topology)
