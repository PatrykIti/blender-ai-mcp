# TASK-014-12: Mesh List Groups Tool

**Status:** ⏳ To Do  
**Priority:** 🟡 Medium  
**Phase:** Phase 7 - Introspection & Listing APIs

## 🎯 Objective
Expose vertex/face group inspection for a mesh object so AI workflows (rig prep, modifiers) can confirm groups exist and understand membership counts.

## 🏗️ Architecture Requirements
### 1. Domain Layer (`server/domain/tools/mesh_list_groups.py`)
- Request model: `object_name: str`, `group_type: Literal["VERTEX", "FACE"] = "VERTEX"`.
- Response model: `MeshGroupSummary` (name, index, member_count, locked flag, normalized flag, notes).
- Interface `IMeshListGroupsTool.list_groups(request) -> MeshGroupsReport`.

### 2. Application Layer (`server/application/handlers/mesh_list_groups_handler.py`)
- Handler calls RPC `mesh.list_groups` and enforces object type validation before remote call if possible.

### 3. Adapter Layer
- MCP tool signature: `mesh_list_groups(object_name: str, group_type: Literal["VERTEX", "FACE"] = "VERTEX") -> str`.
- Docstring: `[MESH][SAFE][READ-ONLY] Lists vertex/face groups defined on mesh.`

### 4. Blender Addon API (`blender_addon/api/mesh_list_groups_api.py`)
- Use `obj.vertex_groups` for vertex groups; for face maps (Blender 4+ `obj.face_maps` or `obj.data.attributes`), provide fallback message if unsupported.
- Include totals plus e.g., top 5 sample vertex indices when group small (optional for context, ensure toggle?).

### 5. RPC Registration & Addon Registration
- Register `mesh.list_groups` endpoint.
- **IMPORTANT:** Register handler in `blender_addon/__init__.py`:
  ```python
  rpc_server.register_handler("mesh.list_groups", mesh_handler.list_groups)
  ```

## ✅ Deliverables
- Domain contracts.
- Handler + DI wiring.
- Adapter entry + docstring.
- Blender API implementation + RPC registration.
- Documentation updates + changelog + README.

## 🧪 Testing
- Mesh with multiple vertex groups (auto from armature) -> counts accurate.
- No groups -> "Object has no vertex groups".

## 📚 References
- `_docs/TOOLS_ARCHITECTURE_DEEP_DIVE.md` for additive tooling guidelines.
