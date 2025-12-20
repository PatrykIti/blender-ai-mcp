# TASK-074: Mesh Inspect Mega Tool

**Priority:** 🟡 Medium  
**Category:** Mega Tools  
**Estimated Effort:** Small  
**Dependencies:** TASK-070, TASK-071  
**Status:** ✅ Done

---

## 🎯 Objective

Provide a single `mesh_inspect` mega tool that wraps mesh introspection actions to reduce LLM context usage.

---

## 📝 Documentation Updates

| File | What to Update |
|------|----------------|
| `_docs/_TASKS/TASK-074_Mesh_Inspect_Mega_Tool.md` | Mark sub-tasks ✅ Done, update status |
| `_docs/_TASKS/README.md` | Update task list + stats |
| `_docs/_CHANGELOG/{NN}-{date}-mesh-inspect-mega-tool.md` | Create changelog entry |
| `_docs/_CHANGELOG/README.md` | Add changelog index entry |
| `_docs/_MCP_SERVER/README.md` | Add `mesh_inspect` to mega tools table; remove/annotate single-action `mesh_get_*` entries if they become internal-only; note router can still call internal actions via handler + metadata |
| `_docs/AVAILABLE_TOOLS_SUMMARY.md` | Add `mesh_inspect` to Implemented table; move/annotate `mesh_get_*` tools that become internal-only under mega tool mapping |
| `_docs/TOOLS/MEGA_TOOLS_ARCHITECTURE.md` | Document `mesh_inspect` actions + summary; add explicit note that mega tool actions are internal-only (no `@mcp.tool`) and router calls handlers via metadata |
| `_docs/TOOLS/MESH_TOOLS_ARCHITECTURE.md` | If `mesh_get_*` wrappers are removed, mark them as internal actions used by `mesh_inspect` (no `@mcp.tool`) |
| `_docs/TOOLS/SCENE_TOOLS_ARCHITECTURE.md` | Mark `scene_get_constraints` as internal-only (use `scene_inspect(action="constraints")`) |
| `_docs/TOOLS/MODELING_TOOLS_ARCHITECTURE.md` | Mark `modeling_get_modifier_data` as internal-only (use `scene_inspect(action="modifier_data")`) |
| `README.md` | Update mega tools table + summary sources; remove/annotate `mesh_get_*` if they are internal-only; add note about handler+metadata execution path |

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
- `summary` → lightweight overview (counts + flags only)

**Rules:**
- Standalone tools remain required for workflow execution and router compatibility,
  but they should be internal functions (no `@mcp.tool`) when covered by a mega tool.
- For TASK-070 to TASK-073: any new single-action tools that are part of a mega tool
  must not be registered as `@mcp.tool` (internal only).
- Every function in `server/adapters/mcp/areas/` has a handler counterpart, and the
  router calls handlers directly using per-tool JSON metadata, even if there is no
  `@mcp.tool` registration.
- Remove redundant `@mcp.tool` wrappers for actions already included in a mega tool;
  keep only internal functions. Example: keep `_scene_inspect_mesh_topology` and the
  handler call, but drop any `scene_inspect_mesh_topology` MCP wrapper.
- Mega tool is read-only and delegates to the underlying tool outputs.
- Action names are short aliases of `mesh_get_*` for LLM context efficiency.
- `summary` must avoid large payloads (no per-vertex/face arrays).
- Implement action handlers as internal functions only (no `@mcp.tool`) for actions covered by the mega tool.

**Summary JSON (example):**
```json
{
  "object_name": "Body",
  "vertex_count": 1234,
  "edge_count": 2456,
  "face_count": 1200,
  "has_uvs": true,
  "has_shape_keys": true,
  "has_custom_normals": false,
  "vertex_groups": ["Spine", "Arm_L", "Arm_R"],
  "modifiers": ["Bevel", "Subdivision"]
}
```

**Summary Sources (recommended):**
- `scene_inspect(action="topology")` → vertex/edge/face counts
- `uv_list_maps` → `has_uvs`
- `mesh_get_shape_keys` → `has_shape_keys` (names only, no deltas)
- `mesh_get_loop_normals` or mesh data flags → `has_custom_normals`
- `mesh_list_groups` → `vertex_groups`
- `modeling_list_modifiers` → `modifiers`

---

## ✅ Success Criteria
- A single tool can fetch any mesh introspection payload
- Reduces prompt/tool overhead in workflow extraction
- `summary` returns a fast overview (counts + presence flags)
