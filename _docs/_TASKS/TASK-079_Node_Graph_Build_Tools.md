# TASK-079: Node Graph Build Tools (Material + Geometry Nodes)

**Priority:** 🔴 High  
**Category:** Material/Geometry Reconstruction  
**Estimated Effort:** Large  
**Dependencies:** TASK-023, TASK-072  
**Status:** ⬜ To Do

---

## 🎯 Objective

Add a `node_graph` mega tool to reconstruct node trees from `material_inspect_nodes` and `scene_inspect(action="modifier_data", include_node_tree=True)` outputs.

This enables 1:1 rebuild of shader and geometry node graphs.

---

## 📝 Documentation Updates

| File | What to Update |
|------|----------------|
| `_docs/_TASKS/TASK-079_Node_Graph_Build_Tools.md` | Track status and sub-tasks |
| `_docs/_TASKS/README.md` | Add to task list + stats |
| `_docs/_MCP_SERVER/README.md` | Add `node_graph` tool |
| `_docs/AVAILABLE_TOOLS_SUMMARY.md` | Add `node_graph` |
| `_docs/TOOLS/MEGA_TOOLS_ARCHITECTURE.md` | Document `node_graph` actions |
| `_docs/TOOLS/MATERIAL_TOOLS_ARCHITECTURE.md` | Reference `node_graph` for shader rebuild |
| `_docs/TOOLS/MODELING_TOOLS_ARCHITECTURE.md` | Reference `node_graph` for GN rebuild |
| `README.md` | Update tools tables |

---

## 🔧 Design

```python
@mcp.tool()
def node_graph(
    ctx: Context,
    action: Literal[
        "create_graph",
        "add_nodes",
        "set_node_props",
        "link_nodes",
        "clear_graph",
        "bind_material",
        "bind_geometry_nodes"
    ],
    graph_type: Literal["SHADER", "GEOMETRY", "WORLD"],
    graph_name: str,
    nodes: Optional[List[dict]] = None,
    links: Optional[List[dict]] = None,
    object_name: Optional[str] = None,
    material_name: Optional[str] = None,
    modifier_name: Optional[str] = None,
) -> str:
    """
    [NODES][WRITE][DESTRUCTIVE] Mega tool for node graph reconstruction.
    """
```

### Actions

- `create_graph`: Create empty node tree (shader/world/geometry).
- `add_nodes`: Bulk create nodes (type, name, location, properties).
- `set_node_props`: Patch node properties (socket defaults, enums, booleans).
- `link_nodes`: Create links using node names + socket identifiers.
- `clear_graph`: Remove existing nodes and links.
- `bind_material`: Assign shader graph to material.
- `bind_geometry_nodes`: Assign geometry graph to GN modifier.

### Rules

- Node names must be stable identifiers to allow linking.
- Socket names/identifiers must match `material_inspect_nodes` output.
- Geometry Nodes graphs are stored on modifiers; binding requires object+modifier.
- World graphs are stored on `bpy.data.worlds`.
- Mega tool uses internal action functions (TASK-074 pattern).

---

## 🧩 Implementation Checklist

| Layer | File | What to Add |
|------|------|-------------|
| Domain | `server/domain/tools/material.py` + `server/domain/tools/modeling.py` | Add node graph methods or a shared interface |
| Application | `server/application/tool_handlers/*` | RPC wrappers |
| Adapter | `server/adapters/mcp/areas/material.py` or new `nodes.py` | `node_graph` mega tool |
| Addon | `blender_addon/application/handlers/material.py` + `handlers/modeling.py` | Node graph creation + binding |
| Addon Init | `blender_addon/__init__.py` | Register RPC routes |
| Dispatcher | `server/adapters/mcp/dispatcher.py` | Tool map entry |
| Router Metadata | `server/router/infrastructure/tools_metadata/nodes/node_graph.json` | Tool metadata |
| Tests | `tests/unit/tools/nodes/test_node_graph.py` | Unit tests for graph creation and linking |

---

## ✅ Success Criteria

- Shader graphs can be reconstructed from `material_inspect_nodes`.
- Geometry Nodes graphs can be reconstructed and bound to modifiers.
- Links and node properties are preserved for round-trip fidelity.
