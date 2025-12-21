# TASK-076: Mesh Build Mega Tool (Core Topology)

**Priority:** 🔴 High  
**Category:** Mega Tools / Mesh Reconstruction  
**Estimated Effort:** Medium  
**Dependencies:** TASK-074  
**Status:** ⬜ To Do

---

## 🎯 Objective

Add a `mesh_build` mega tool that can reconstruct mesh topology (vertices, edges, faces) from `mesh_inspect` output with chunked uploads.

This is the write-side counterpart to `mesh_inspect` and is required for 1:1 reconstruction of geometry.

---

## 📝 Documentation Updates

| File | What to Update |
|------|----------------|
| `_docs/_TASKS/TASK-076_Mesh_Build_Mega_Tool.md` | Track status and sub-tasks |
| `_docs/_TASKS/README.md` | Add to task list + stats |
| `_docs/_MCP_SERVER/README.md` | Add `mesh_build` to tools list |
| `_docs/AVAILABLE_TOOLS_SUMMARY.md` | Add `mesh_build` |
| `_docs/TOOLS/MEGA_TOOLS_ARCHITECTURE.md` | Document `mesh_build` actions |
| `_docs/TOOLS/MESH_TOOLS_ARCHITECTURE.md` | Add `mesh_build` section |
| `README.md` | Update tools tables |

---

## 🔧 Design

```python
@mcp.tool()
def mesh_build(
    ctx: Context,
    action: Literal["create", "set_geometry", "finalize", "clear"],
    object_name: str,
    vertices: Optional[List[List[float]]] = None,
    edges: Optional[List[List[int]]] = None,
    faces: Optional[List[List[int]]] = None,
    indices_are_relative: bool = True,
    vertex_offset: int = 0,
    clear_existing: bool = False,
    location: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
    scale: Optional[List[float]] = None,
    use_smooth_shading: bool = True,
    validate: bool = True,
    merge_by_distance: Optional[float] = None,
) -> str:
    """
    [MESH][WRITE][DESTRUCTIVE] Mega tool for mesh reconstruction.
    """
```

### Actions

- `create` -> Create an empty mesh object (optionally clear existing).  
- `set_geometry` -> Append or replace vertices/edges/faces in chunks.  
- `finalize` -> Recalculate normals, apply smoothing, optional validation/merge.  
- `clear` -> Remove all geometry data from the mesh (prepare rebuild).

### Rules

- Mega tool follows the internal-action pattern from TASK-074.
- `set_geometry` supports chunked uploads using `vertex_offset` and `indices_are_relative`.
- Input format should match `mesh_inspect` output (faces use vertex indices).
- No implicit reindexing; caller controls offsets.
- Must work in Blender 5.0+.

### Example

```json
{
  "tool": "mesh_build",
  "args": {
    "action": "set_geometry",
    "object_name": "Body",
    "vertices": [[0,0,0],[1,0,0],[1,1,0],[0,1,0]],
    "faces": [[0,1,2,3]],
    "indices_are_relative": true,
    "vertex_offset": 0
  }
}
```

---

## 🧩 Implementation Checklist

| Layer | File | What to Add |
|------|------|-------------|
| Domain | `server/domain/tools/mesh.py` | `mesh_build(...)` abstract method |
| Application | `server/application/tool_handlers/mesh_handler.py` | RPC wrapper |
| Adapter | `server/adapters/mcp/areas/mesh.py` | `mesh_build` mega tool + internal actions |
| Addon | `blender_addon/application/handlers/mesh.py` | Build handlers for create/set_geometry/finalize |
| Addon Init | `blender_addon/__init__.py` | Register RPC routes |
| Dispatcher | `server/adapters/mcp/dispatcher.py` | Tool map entry |
| Router Metadata | `server/router/infrastructure/tools_metadata/mesh/mesh_build.json` | Tool metadata |
| Tests | `tests/unit/tools/mesh/test_mesh_build.py` | Unit tests for routing + chunking |

---

## ✅ Success Criteria

- Can reconstruct topology from `mesh_inspect` data in multiple chunks.
- Works reliably in Blender 5.0+ with large meshes.
- Clear separation between geometry creation and finalization steps.
