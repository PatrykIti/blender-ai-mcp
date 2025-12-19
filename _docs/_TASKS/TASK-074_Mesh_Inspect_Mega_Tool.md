# TASK-074: Mesh Inspect Mega Tool

**Priority:** 🟡 Medium  
**Category:** Mega Tools  
**Estimated Effort:** Small  
**Dependencies:** TASK-070, TASK-071  
**Status:** ⏳ TODO

---

## 🎯 Objective

Provide a single `mesh_inspect` mega tool that wraps mesh introspection actions to reduce LLM context usage.

---

## 🔧 Design

```python
@mcp.tool()
def mesh_inspect(ctx: Context, action: str, **kwargs) -> str:
    """
    [MESH][READ-ONLY][SAFE] Mega tool for mesh introspection.
    """
```

**Actions (proposed):**
- `vertices` → `mesh_get_vertex_data`
- `edges` → `mesh_get_edge_data`
- `faces` → `mesh_get_face_data`
- `uvs` → `mesh_get_uv_data`
- `normals` → `mesh_get_loop_normals`
- `attributes` → `mesh_get_attributes`
- `shape_keys` → `mesh_get_shape_keys`
- `group_weights` → `mesh_get_vertex_group_weights`

---

## ✅ Success Criteria
- A single tool can fetch any mesh introspection payload
- Reduces prompt/tool overhead in workflow extraction
