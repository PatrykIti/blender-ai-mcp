# 48. Sculpt Tools (TASK-027)

**Date:** 2025-11-29
**Version:** 1.21.0
**Task:** [TASK-027](../_TASKS/TASK-027_Sculpting_Tools.md)

---

## Summary

Implemented sculpting tools for organic shape manipulation in Blender's Sculpt Mode. These tools enable AI-driven organic modeling workflows.

**Key Insight:** For AI workflows, mesh filters (`sculpt.mesh_filter`) are more reliable and predictable than programmatic brush strokes. The `sculpt_auto` tool uses this approach for consistent results.

---

## New Tools

### sculpt_auto
**[SCULPT MODE][DESTRUCTIVE]**

High-level sculpt operation using Blender's mesh filters. Most reliable for AI workflows.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `operation` | Literal["smooth", "inflate", "flatten", "sharpen"] | "smooth" | Filter type |
| `object_name` | Optional[str] | None | Target object |
| `strength` | float | 0.5 | Operation strength (0-1) |
| `iterations` | int | 1 | Number of passes |
| `use_symmetry` | bool | True | Enable symmetry |
| `symmetry_axis` | Literal["X", "Y", "Z"] | "X" | Symmetry axis |

### sculpt_brush_smooth
**[SCULPT MODE][DESTRUCTIVE]**

Sets up smooth brush at specified location.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `object_name` | Optional[str] | None | Target object |
| `location` | Optional[List[float]] | None | World position [x, y, z] |
| `radius` | float | 0.1 | Brush radius |
| `strength` | float | 0.5 | Brush strength (0-1) |

### sculpt_brush_grab
**[SCULPT MODE][DESTRUCTIVE]**

Sets up grab brush for moving geometry.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `object_name` | Optional[str] | None | Target object |
| `from_location` | Optional[List[float]] | None | Start position |
| `to_location` | Optional[List[float]] | None | End position |
| `radius` | float | 0.1 | Brush radius |
| `strength` | float | 0.5 | Brush strength (0-1) |

### sculpt_brush_crease
**[SCULPT MODE][DESTRUCTIVE]**

Sets up crease brush for creating sharp lines.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `object_name` | Optional[str] | None | Target object |
| `location` | Optional[List[float]] | None | World position [x, y, z] |
| `radius` | float | 0.1 | Brush radius |
| `strength` | float | 0.5 | Brush strength (0-1) |
| `pinch` | float | 0.5 | Pinch amount (0-1) |

---

## Files Changed

### Server (MCP)
- `server/domain/tools/sculpt.py` - ISculptTool interface (NEW)
- `server/application/tool_handlers/sculpt_handler.py` - SculptToolHandler (NEW)
- `server/adapters/mcp/areas/sculpt.py` - MCP adapter with @mcp.tool() (NEW)
- `server/adapters/mcp/areas/__init__.py` - Added sculpt import
- `server/infrastructure/di.py` - Added get_sculpt_handler()

### Blender Addon
- `blender_addon/application/handlers/sculpt.py` - SculptHandler (NEW)
- `blender_addon/__init__.py` - Registered RPC handlers

### Tests
- `tests/unit/tools/sculpt/__init__.py` (NEW)
- `tests/unit/tools/sculpt/test_sculpt_tools.py` - 25 unit tests (NEW)
- `tests/e2e/tools/sculpt/__init__.py` (NEW)
- `tests/e2e/tools/sculpt/test_sculpt_tools.py` - E2E tests (NEW)

### Documentation
- `_docs/SCULPT_TOOLS_ARCHITECTURE.md` (NEW)
- `_docs/AVAILABLE_TOOLS_SUMMARY.md` - Added sculpt tools section
- `_docs/_MCP_SERVER/README.md` - Added sculpt tools
- `_docs/_ADDON/README.md` - Added sculpt handlers
- `_docs/_TASKS/TASK-027_Sculpting_Tools.md` - Marked as done

---

## RPC Commands

| RPC Command | Handler Method |
|-------------|----------------|
| `sculpt.auto` | `SculptHandler.auto_sculpt()` |
| `sculpt.brush_smooth` | `SculptHandler.brush_smooth()` |
| `sculpt.brush_grab` | `SculptHandler.brush_grab()` |
| `sculpt.brush_crease` | `SculptHandler.brush_crease()` |

---

## Recommended Workflow

For AI-driven sculpting:

```
# 1. Create base mesh
modeling_create_primitive(type="UV_SPHERE")

# 2. Add geometry for sculpting
mesh_remesh_voxel(voxel_size=0.05)

# 3. Use sculpt_auto for organic shaping
sculpt_auto(operation="smooth", iterations=2, strength=0.3)
sculpt_auto(operation="inflate", strength=0.2)
```

---

## Test Results

```
25 passed in 0.08s
```
