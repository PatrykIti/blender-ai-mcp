# TASK-077: Mesh Build Surface Data (UVs, Materials, Attributes)

**Priority:** 🔴 High  
**Category:** Mesh Reconstruction  
**Estimated Effort:** Medium  
**Dependencies:** TASK-076  
**Status:** ⬜ To Do

---

## 🎯 Objective

Extend `mesh_build` to restore surface-level data required for 1:1 appearance: UVs, per-face material indices, and custom attributes (vertex colors, generic layers).

---

## 📝 Documentation Updates

| File | What to Update |
|------|----------------|
| `_docs/_TASKS/TASK-077_Mesh_Build_Surface_Data.md` | Track status and sub-tasks |
| `_docs/_TASKS/README.md` | Add to task list + stats |
| `_docs/_MCP_SERVER/README.md` | Add `mesh_build` actions |
| `_docs/AVAILABLE_TOOLS_SUMMARY.md` | Update `mesh_build` actions |
| `_docs/TOOLS/MEGA_TOOLS_ARCHITECTURE.md` | Extend `mesh_build` actions |
| `_docs/TOOLS/MESH_TOOLS_ARCHITECTURE.md` | Add surface data section |
| `README.md` | Update tools tables |

---

## 🔧 Design

Extend `mesh_build` with the following actions:

### Actions

- `set_uvs`
  - Input mirrors `mesh_inspect(action="uvs")` output.
  - Params: `object_name`, `uv_layer`, `create_if_missing`, `faces`.
  - `faces`: list of `{face_index, uvs: [[u,v], ...]}`.
  - Supports chunking by face index ranges.

- `set_material_indices`
  - Assign `material_index` per face.
  - Params: `object_name`, `indices`, `slot_map` (optional remap).
  - `indices`: list of `{face_index, material_index}`.

- `set_attributes`
  - Generic attribute setter for POINT/EDGE/FACE/CORNER domains.
  - Params: `object_name`, `attribute_name`, `data_type`, `domain`, `values`.
  - `values`: list of `{index, value}` matching `mesh_inspect(action="attributes")`.

### Rules

- Keep action functions internal; exposed via `mesh_build` mega tool.
- Attribute data must preserve `data_type` and `domain`.
- UVs are per-loop; face indices must map to polygon loops.
- Chunking required for large datasets (limit payload size).
- Blender 5.0+ API only.

---

## 🧩 Implementation Checklist

| Layer | File | What to Add |
|------|------|-------------|
| Domain | `server/domain/tools/mesh.py` | Extend `mesh_build` params/actions |
| Application | `server/application/tool_handlers/mesh_handler.py` | RPC args for new actions |
| Adapter | `server/adapters/mcp/areas/mesh.py` | Route `set_uvs` / `set_material_indices` / `set_attributes` |
| Addon | `blender_addon/application/handlers/mesh.py` | Implement setters in Blender |
| Addon Init | `blender_addon/__init__.py` | Register RPC routes |
| Dispatcher | `server/adapters/mcp/dispatcher.py` | Tool map entry updates |
| Router Metadata | `server/router/infrastructure/tools_metadata/mesh/mesh_build.json` | Add action schemas |
| Tests | `tests/unit/tools/mesh/test_mesh_build_surface.py` | Unit tests for each action |

---

## ✅ Success Criteria

- UVs, material indices, and attributes can be restored from `mesh_inspect` output.
- Chunked upload works without data loss.
- Output matches original `mesh_inspect` for round-trip reconstruction.
