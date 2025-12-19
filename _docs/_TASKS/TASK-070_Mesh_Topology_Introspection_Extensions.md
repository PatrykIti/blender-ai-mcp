# TASK-070: Mesh Topology Introspection Extensions

**Priority:** 🔴 High  
**Category:** Mesh Introspection  
**Estimated Effort:** Medium  
**Dependencies:** TASK-014-13 (Scene Inspect Mesh Topology), TASK-044 (Extraction Analysis Tools)  
**Status:** ✅ Done

---

## 🎯 Objective

Expose full mesh connectivity (edges, faces, UV loops) so workflows can reconstruct models 1:1 without external exports. Current tools provide only vertex positions or high-level stats; this task adds precise topology dumps.

**Primary Use Cases**
- 1:1 procedural reconstruction of existing Blender models
- Debugging and validation of mesh integrity
- Accurate bevel/crease/sharp replication
- UV-preserving re-authoring

---

## 📝 Documentation Updates

| File | What to Update |
|------|----------------|
| `_docs/_TASKS/TASK-070_Mesh_Topology_Introspection_Extensions.md` | Mark sub-tasks ✅ Done, update status |
| `_docs/_TASKS/README.md` | Update task list + stats |
| `_docs/_CHANGELOG/{NN}-{date}-mesh-topology-introspection.md` | Create changelog entry |
| `_docs/_CHANGELOG/README.md` | Add changelog index entry |
| `_docs/_ADDON/README.md` | Add mesh RPC commands (`mesh.get_edge_data`, `mesh.get_face_data`, `mesh.get_uv_data`) |
| `_docs/_MCP_SERVER/README.md` | Add MCP wrappers (if exposed) |
| `_docs/AVAILABLE_TOOLS_SUMMARY.md` | Add tools to Implemented table |
| `_docs/TOOLS/MESH_TOOLS_ARCHITECTURE.md` | Document new mesh introspection tools |
| `README.md` | Update tools tables |

---

## ✅ Naming Conventions (Introspection Tools)

- `get_*` = raw data payload (exact topology/attributes)
- `list_*` = names or lightweight summaries only
- `inspect_*` = aggregated stats (human-readable)
- `analyze_*` = heuristics/interpretation (not raw data)
- Parameters: `object_name`, `selected_only`, `uv_layer`, `group_name`, `attribute_name`

---

## 🧱 Implementation Pattern

- Action handlers are internal functions (no `@mcp.tool`) called via addon RPC.
- Add a thin MCP wrapper only if a standalone tool is required for workflow/router compatibility.

---

## 🔧 Sub-Tasks

### TASK-070-1: mesh_get_edge_data

**Status:** ✅ Done

Read-only edge topology dump with essential flags and weights.

```python
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
| Adapter | `server/adapters/mcp/areas/mesh.py` | Internal action + optional `@mcp.tool` wrapper |
| Addon | `blender_addon/application/handlers/mesh.py` | BMesh edge dump |
| Metadata | `server/router/infrastructure/tools_metadata/mesh/mesh_get_edge_data.json` | Tool metadata |
| Tests | `tests/unit/tools/mesh/test_mesh_topology_introspection.py` | Edge flags + counts |

---

### TASK-070-2: mesh_get_face_data

**Status:** ✅ Done

Read-only face topology dump (vertex indices + normals + material assignment).

```python
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
| Adapter | `server/adapters/mcp/areas/mesh.py` | Internal action + optional `@mcp.tool` wrapper |
| Addon | `blender_addon/application/handlers/mesh.py` | BMesh face dump |
| Metadata | `server/router/infrastructure/tools_metadata/mesh/mesh_get_face_data.json` | Tool metadata |
| Tests | `tests/unit/tools/mesh/test_mesh_topology_introspection.py` | Face indices + materials |

---

### TASK-070-3: mesh_get_uv_data

**Status:** ✅ Done

Read-only UV loop dump for precise UV reconstruction.

```python
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
| Adapter | `server/adapters/mcp/areas/mesh.py` | Internal action + optional `@mcp.tool` wrapper |
| Addon | `blender_addon/application/handlers/mesh.py` | UV layer loop dump |
| Metadata | `server/router/infrastructure/tools_metadata/mesh/mesh_get_uv_data.json` | Tool metadata |
| Tests | `tests/unit/tools/mesh/test_mesh_topology_introspection.py` | UV layer selection + counts |

---

## ✅ Success Criteria
- Full edge + face + UV connectivity can be reconstructed from MCP output.
- No external file exports required to replicate the mesh.
- Works on large meshes (performance validated on 100k+ tris).

---

## 📚 References
- `_docs/TOOLS_ARCHITECTURE_DEEP_DIVE.md`
- `_docs/_ROUTER/WORKFLOWS/creating-workflows-tutorial.md`
