# TASK-070: Mesh Topology Introspection Extensions

**Priority:** 🔴 High  
**Category:** Mesh Introspection  
**Estimated Effort:** Medium  
**Dependencies:** TASK-014-13 (Scene Inspect Mesh Topology), TASK-044 (Extraction Analysis Tools)  
**Status:** ⏳ TODO

---

## 🎯 Objective

Expose full mesh connectivity (edges, faces, UV loops) so workflows can reconstruct models 1:1 without external exports. Current tools provide only vertex positions or high-level stats; this task adds precise topology dumps.

**Primary Use Cases**
- 1:1 procedural reconstruction of existing Blender models
- Debugging and validation of mesh integrity
- Accurate bevel/crease/sharp replication
- UV-preserving re-authoring

---

## 🔧 Sub-Tasks

### TASK-070-1: mesh_get_edge_data

**Status:** ⏳ TODO

Read-only edge topology dump with essential flags and weights.

```python
@mcp.tool()
def mesh_get_edge_data(
    ctx: Context,
    object_name: str,
    selected_only: bool = False
) -> str:
    """
    [EDIT MODE][READ-ONLY][SAFE] Returns edge connectivity + attributes.
    """
```

**Return JSON (example):**
```json
{
  "object_name": "Body",
  "edge_count": 1024,
  "edges": [
    {
      "index": 0,
      "verts": [12, 45],
      "is_boundary": false,
      "is_manifold": true,
      "is_seam": false,
      "is_sharp": true,
      "crease": 0.5,
      "bevel_weight": 1.0,
      "selected": false
    }
  ]
}
```

**Blender API Notes:**
```python
import bmesh
obj = bpy.data.objects.get(object_name)
bm = bmesh.new()
bm.from_mesh(obj.data)
bm.edges.ensure_lookup_table()
bm.verts.ensure_lookup_table()
```

**Implementation Checklist:**
| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/domain/tools/mesh.py` | `def get_edge_data(...)` contract |
| Application | `server/application/tool_handlers/mesh_handler.py` | RPC wrapper + validation |
| Adapter | `server/adapters/mcp/areas/mesh.py` | `@mcp.tool()` exposure |
| Addon | `blender_addon/application/handlers/mesh.py` | BMesh edge dump |
| Metadata | `server/router/infrastructure/tools_metadata/mesh/mesh_get_edge_data.json` | Tool metadata |
| Tests | `tests/unit/tools/mesh/test_get_edge_data.py` | Edge flags + counts |

---

### TASK-070-2: mesh_get_face_data

**Status:** ⏳ TODO

Read-only face topology dump (vertex indices + normals + material assignment).

```python
@mcp.tool()
def mesh_get_face_data(
    ctx: Context,
    object_name: str,
    selected_only: bool = False
) -> str:
    """
    [EDIT MODE][READ-ONLY][SAFE] Returns face connectivity + attributes.
    """
```

**Return JSON (example):**
```json
{
  "object_name": "Body",
  "face_count": 512,
  "faces": [
    {
      "index": 0,
      "verts": [1, 2, 3, 4],
      "normal": [0.0, 0.0, 1.0],
      "center": [0.0, 0.0, 0.2],
      "area": 0.0012,
      "material_index": 0,
      "selected": false
    }
  ]
}
```

**Implementation Checklist:**
| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/domain/tools/mesh.py` | `def get_face_data(...)` contract |
| Application | `server/application/tool_handlers/mesh_handler.py` | RPC wrapper + validation |
| Adapter | `server/adapters/mcp/areas/mesh.py` | `@mcp.tool()` exposure |
| Addon | `blender_addon/application/handlers/mesh.py` | BMesh face dump |
| Metadata | `server/router/infrastructure/tools_metadata/mesh/mesh_get_face_data.json` | Tool metadata |
| Tests | `tests/unit/tools/mesh/test_get_face_data.py` | Face indices + materials |

---

### TASK-070-3: mesh_get_uv_data

**Status:** ⏳ TODO

Read-only UV loop dump for precise UV reconstruction.

```python
@mcp.tool()
def mesh_get_uv_data(
    ctx: Context,
    object_name: str,
    uv_layer: str | None = None,
    selected_only: bool = False
) -> str:
    """
    [EDIT MODE][READ-ONLY][SAFE] Returns UVs per face loop.
    """
```

**Return JSON (example):**
```json
{
  "object_name": "Body",
  "uv_layer": "UVMap",
  "faces": [
    {
      "face_index": 0,
      "verts": [1, 2, 3, 4],
      "uvs": [[0.1, 0.2], [0.4, 0.2], [0.4, 0.6], [0.1, 0.6]]
    }
  ]
}
```

**Implementation Checklist:**
| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/domain/tools/mesh.py` | `def get_uv_data(...)` contract |
| Application | `server/application/tool_handlers/mesh_handler.py` | RPC wrapper + validation |
| Adapter | `server/adapters/mcp/areas/mesh.py` | `@mcp.tool()` exposure |
| Addon | `blender_addon/application/handlers/mesh.py` | UV layer loop dump |
| Metadata | `server/router/infrastructure/tools_metadata/mesh/mesh_get_uv_data.json` | Tool metadata |
| Tests | `tests/unit/tools/mesh/test_get_uv_data.py` | UV layer selection + counts |

---

## ✅ Success Criteria
- Full edge + face + UV connectivity can be reconstructed from MCP output.
- No external file exports required to replicate the mesh.
- Works on large meshes (performance validated on 100k+ tris).

---

## 📚 References
- `_docs/TOOLS_ARCHITECTURE_DEEP_DIVE.md`
- `_docs/_ROUTER/WORKFLOWS/creating-workflows-tutorial.md`
