# TASK-081: Scene Render + World Settings (Inspect & Apply)

**Priority:** 🟡 Medium  
**Category:** Scene Reconstruction  
**Estimated Effort:** Medium  
**Dependencies:** TASK-020-5  
**Status:** ⬜ To Do

---

## 🎯 Objective

Expose render, world, and color-management settings so scene appearance can be reconstructed 1:1.

This extends `scene_inspect` and adds a write-side `scene_configure` mega tool.

---

## 📝 Documentation Updates

| File | What to Update |
|------|----------------|
| `_docs/_TASKS/TASK-081_Scene_Render_World_Settings.md` | Track status and sub-tasks |
| `_docs/_TASKS/README.md` | Add to task list + stats |
| `_docs/_MCP_SERVER/README.md` | Add `scene_inspect` actions + `scene_configure` tool |
| `_docs/AVAILABLE_TOOLS_SUMMARY.md` | Update tools list |
| `_docs/TOOLS/MEGA_TOOLS_ARCHITECTURE.md` | Extend `scene_inspect`; add `scene_configure` |
| `_docs/TOOLS/SCENE_TOOLS_ARCHITECTURE.md` | Add render/world sections |
| `README.md` | Update tools tables |

---

## 🔧 Design

### Extend `scene_inspect`

Add read-only actions:
- `render`: engine, samples, film, output, device, resolution.
- `color_management`: view transform, look, exposure, gamma, sequencer.
- `world`: world name, background strength, use_nodes, node graph reference.

### New `scene_configure` mega tool

```python
@mcp.tool()
def scene_configure(
    ctx: Context,
    action: Literal["render", "color_management", "world"],
    settings: dict,
) -> str:
    """
    [SCENE][NON-DESTRUCTIVE] Apply scene-level configuration.
    """
```

### Rules

- `scene_configure(action="world")` should accept a world name and optionally delegate to `node_graph` when `use_nodes=True`.
- Settings must be applied deterministically and be reversible by re-running with prior data.
- Must be compatible with Blender 5.0+.

---

## 🧩 Implementation Checklist

| Layer | File | What to Add |
|------|------|-------------|
| Domain | `server/domain/tools/scene.py` | Add new inspect/config methods |
| Application | `server/application/tool_handlers/scene_handler.py` | RPC wrappers |
| Adapter | `server/adapters/mcp/areas/scene.py` | Extend `scene_inspect`, add `scene_configure` |
| Addon | `blender_addon/application/handlers/scene.py` | Read/write render/world settings |
| Addon Init | `blender_addon/__init__.py` | Register RPC routes |
| Dispatcher | `server/adapters/mcp/dispatcher.py` | Tool map updates |
| Router Metadata | `server/router/infrastructure/tools_metadata/scene/scene_configure.json` | Tool metadata |
| Tests | `tests/unit/tools/scene/test_scene_configure.py` | Unit tests for settings |

---

## ✅ Success Criteria

- Scene render and world settings can be exported and applied 1:1.
- World node graphs can be reattached via `node_graph`.
