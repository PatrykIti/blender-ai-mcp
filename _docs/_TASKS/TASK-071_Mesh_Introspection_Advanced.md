# TASK-071: Mesh Introspection Advanced

**Priority:** 🔴 High  
**Category:** Mesh Introspection  
**Estimated Effort:** Medium  
**Dependencies:** TASK-070 (Mesh Topology Introspection Extensions)  
**Status:** ⏳ TODO

---

## 🎯 Objective

Add deeper mesh inspection tools beyond topology so workflows can preserve shading, attributes, weights, and shape keys for 1:1 reconstruction.

**Primary Use Cases**
- Preserve split/custom normals for accurate shading
- Reconstruct vertex group weights for rigged assets
- Restore custom attributes (vertex colors, data layers)
- Rebuild shape keys with correct deltas

---

## 🔧 Sub-Tasks

### TASK-071-1: mesh_get_loop_normals

**Status:** ⏳ TODO

```python
@mcp.tool()
def mesh_get_loop_normals(
    ctx: Context,
    object_name: str,
    selected_only: bool = False
) -> str:
    """
    [EDIT MODE][READ-ONLY][SAFE] Returns per-loop normals (split/custom).
    """
```

**Return JSON (example):**
```json
{
  "object_name": "Body",
  "loop_count": 2048,
  "loops": [
    {"loop_index": 0, "vert": 12, "normal": [0.0, 0.0, 1.0]}
  ],
  "auto_smooth": true,
  "custom_normals": true
}
```

**Implementation Checklist:**
| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/domain/tools/mesh.py` | `def get_loop_normals(...)` contract |
| Application | `server/application/tool_handlers/mesh_handler.py` | RPC wrapper + validation |
| Adapter | `server/adapters/mcp/areas/mesh.py` | `@mcp.tool()` exposure |
| Addon | `blender_addon/application/handlers/mesh.py` | Loop normal dump (mesh loops) |
| Metadata | `server/router/infrastructure/tools_metadata/mesh/mesh_get_loop_normals.json` | Tool metadata |
| Tests | `tests/unit/tools/mesh/test_get_loop_normals.py` | Custom/split normals |

---

### TASK-071-2: mesh_get_vertex_group_weights

**Status:** ⏳ TODO

```python
@mcp.tool()
def mesh_get_vertex_group_weights(
    ctx: Context,
    object_name: str,
    group_name: str | None = None,
    selected_only: bool = False
) -> str:
    """
    [EDIT MODE][READ-ONLY][SAFE] Returns vertex group weights.
    """
```

**Return JSON (example):**
```json
{
  "object_name": "Body",
  "group_name": "Spine",
  "weights": [
    {"vert": 0, "weight": 1.0},
    {"vert": 5, "weight": 0.42}
  ]
}
```

**Implementation Checklist:**
| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/domain/tools/mesh.py` | `def get_vertex_group_weights(...)` |
| Application | `server/application/tool_handlers/mesh_handler.py` | RPC wrapper + validation |
| Adapter | `server/adapters/mcp/areas/mesh.py` | `@mcp.tool()` exposure |
| Addon | `blender_addon/application/handlers/mesh.py` | Vertex group weight dump |
| Metadata | `server/router/infrastructure/tools_metadata/mesh/mesh_get_vertex_group_weights.json` | Tool metadata |
| Tests | `tests/unit/tools/mesh/test_get_vertex_group_weights.py` | Group lookup + counts |

---

### TASK-071-3: mesh_get_attributes

**Status:** ⏳ TODO

```python
@mcp.tool()
def mesh_get_attributes(
    ctx: Context,
    object_name: str,
    attribute_name: str | None = None,
    selected_only: bool = False
) -> str:
    """
    [EDIT MODE][READ-ONLY][SAFE] Returns mesh attributes (e.g., vertex colors).
    """
```

**Return JSON (example):**
```json
{
  "object_name": "Body",
  "attributes": [
    {"name": "Col", "type": "FLOAT_COLOR", "domain": "POINT"}
  ]
}
```

**Implementation Checklist:**
| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/domain/tools/mesh.py` | `def get_attributes(...)` |
| Application | `server/application/tool_handlers/mesh_handler.py` | RPC wrapper + validation |
| Adapter | `server/adapters/mcp/areas/mesh.py` | `@mcp.tool()` exposure |
| Addon | `blender_addon/application/handlers/mesh.py` | Attribute dump (mesh.attributes) |
| Metadata | `server/router/infrastructure/tools_metadata/mesh/mesh_get_attributes.json` | Tool metadata |
| Tests | `tests/unit/tools/mesh/test_get_attributes.py` | Attribute list + data |

---

### TASK-071-4: mesh_get_shape_keys

**Status:** ⏳ TODO

```python
@mcp.tool()
def mesh_get_shape_keys(
    ctx: Context,
    object_name: str
) -> str:
    """
    [OBJECT MODE][READ-ONLY][SAFE] Returns shape key data.
    """
```

**Return JSON (example):**
```json
{
  "object_name": "Body",
  "shape_keys": [
    {"name": "Basis", "value": 0.0},
    {"name": "Smile", "value": 0.2}
  ]
}
```

**Implementation Checklist:**
| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/domain/tools/mesh.py` | `def get_shape_keys(...)` |
| Application | `server/application/tool_handlers/mesh_handler.py` | RPC wrapper + validation |
| Adapter | `server/adapters/mcp/areas/mesh.py` | `@mcp.tool()` exposure |
| Addon | `blender_addon/application/handlers/mesh.py` | Shape key list + values |
| Metadata | `server/router/infrastructure/tools_metadata/mesh/mesh_get_shape_keys.json` | Tool metadata |
| Tests | `tests/unit/tools/mesh/test_get_shape_keys.py` | Shape key listing |

---

## ✅ Success Criteria
- Can reconstruct shading and weights without exports
- Attribute data is preserved across reconstruction
