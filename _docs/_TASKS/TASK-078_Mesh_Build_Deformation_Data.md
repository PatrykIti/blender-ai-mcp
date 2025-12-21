# TASK-078: Mesh Build Deformation Data (Normals, Weights, Shape Keys)

**Priority:** 🔴 High  
**Category:** Mesh Reconstruction  
**Estimated Effort:** Medium  
**Dependencies:** TASK-076, TASK-077  
**Status:** ⬜ To Do

---

## 🎯 Objective

Extend `mesh_build` to restore deformation-related data: custom normals, vertex groups/weights, and shape keys.

These are required for exact shading and deformation fidelity.

---

## 📝 Documentation Updates

| File | What to Update |
|------|----------------|
| `_docs/_TASKS/TASK-078_Mesh_Build_Deformation_Data.md` | Track status and sub-tasks |
| `_docs/_TASKS/README.md` | Add to task list + stats |
| `_docs/_MCP_SERVER/README.md` | Add `mesh_build` actions |
| `_docs/AVAILABLE_TOOLS_SUMMARY.md` | Update `mesh_build` actions |
| `_docs/TOOLS/MEGA_TOOLS_ARCHITECTURE.md` | Extend `mesh_build` actions |
| `_docs/TOOLS/MESH_TOOLS_ARCHITECTURE.md` | Add deformation data section |
| `README.md` | Update tools tables |

---

## 🔧 Design

Extend `mesh_build` with the following actions:

### Actions

- `set_custom_normals`
  - Input mirrors `mesh_inspect(action="normals")` output.
  - Params: `object_name`, `loops` (list of `{loop_index, normal}`), `smooth_by_angle`, `smooth_by_angle_angle`.
  - Use Blender 5.0+ API: `mesh.normals_split_custom_set` / `mesh.corner_normals`.
  - Apply Smooth by Angle via `SMOOTH_BY_ANGLE` modifier (5.0+ replacement for Auto Smooth).

- `set_vertex_groups`
  - Create groups + assign weights in bulk.
  - Params: `object_name`, `groups` list of `{name, weights:[{vert, weight}]}`.
  - Supports chunking per group.

- `set_shape_keys`
  - Create shape keys and apply deltas.
  - Params: `object_name`, `basis_name`, `shape_keys` list of `{name, value, deltas}`.
  - `deltas` mirrors `mesh_inspect(action="shape_keys", include_deltas=True)`.

### Rules

- Must preserve order and naming of groups and shape keys.
- For normals, fallback to vertex normals if custom normals are not supported.
- For shape keys, ensure consistent basis mesh length.
- Blender 5.0+ only.

---

## 🧩 Implementation Checklist

| Layer | File | What to Add |
|------|------|-------------|
| Domain | `server/domain/tools/mesh.py` | Extend `mesh_build` actions |
| Application | `server/application/tool_handlers/mesh_handler.py` | RPC args for new actions |
| Adapter | `server/adapters/mcp/areas/mesh.py` | Route new actions |
| Addon | `blender_addon/application/handlers/mesh.py` | Implement normals/weights/shape keys setters |
| Addon Init | `blender_addon/__init__.py` | Register RPC routes |
| Dispatcher | `server/adapters/mcp/dispatcher.py` | Tool map entry updates |
| Router Metadata | `server/router/infrastructure/tools_metadata/mesh/mesh_build.json` | Add action schemas |
| Tests | `tests/unit/tools/mesh/test_mesh_build_deform.py` | Unit tests for each action |

---

## ✅ Success Criteria

- Custom normals, weights, and shape keys are restored with no data loss.
- Round-trip `mesh_inspect` -> `mesh_build` produces equivalent results.
