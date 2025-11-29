# Sculpt Tools Architecture

This document describes the architecture and implementation details for Sculpt Mode tools in blender-ai-mcp.

## Overview

Sculpt tools enable organic shape manipulation through Blender's Sculpt Mode. They are categorized as **lower priority** since they require Sculpt Mode and are more advanced workflows.

**Key Insight:** For AI workflows, mesh filters (`sculpt.mesh_filter`) are more reliable and predictable than programmatic brush strokes. The `sculpt_auto` tool uses this approach for consistent results.

---

## Tool Categories

### High-Level Operations (Recommended for AI)

| Tool | Operation | Reliability |
|------|-----------|-------------|
| `sculpt_auto` | Whole-mesh filters (smooth, inflate, flatten, sharpen) | ✅ High |

### Brush Setup Tools (Lower Reliability)

| Tool | Operation | Note |
|------|-----------|------|
| `sculpt_brush_smooth` | Smooth brush setup | Sets up brush only |
| `sculpt_brush_grab` | Grab brush setup | Sets up brush only |
| `sculpt_brush_crease` | Crease brush setup | Sets up brush only |

> **Note:** Brush tools configure the brush and context but don't execute strokes programmatically. For whole-mesh operations, use `sculpt_auto`.

---

## Tool Specifications

### sculpt_auto

**[SCULPT MODE][DESTRUCTIVE]**

High-level sculpt operation using Blender's mesh filters. Most reliable for AI workflows.

```
Workflow: BEFORE → scene_set_mode(mode='SCULPT') | AFTER → mesh_remesh_voxel
```

**Operations:**
- `smooth` - Smooths entire surface, removes noise
- `inflate` - Expands mesh outward along normals
- `flatten` - Creates planar areas, reduces irregularities
- `sharpen` - Enhances surface detail and edges

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `operation` | Literal["smooth", "inflate", "flatten", "sharpen"] | "smooth" | Filter type |
| `object_name` | Optional[str] | None | Target object (default: active) |
| `strength` | float | 0.5 | Operation strength (0-1) |
| `iterations` | int | 1 | Number of passes |
| `use_symmetry` | bool | True | Enable symmetry |
| `symmetry_axis` | Literal["X", "Y", "Z"] | "X" | Symmetry axis |

**Examples:**
```
sculpt_auto(operation="smooth", iterations=3)
sculpt_auto(operation="inflate", strength=0.3, use_symmetry=False)
```

---

### sculpt_brush_smooth

**[SCULPT MODE][DESTRUCTIVE]**

Sets up the smooth brush. For whole-mesh smoothing, prefer `sculpt_auto(operation="smooth")`.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `object_name` | Optional[str] | None | Target object |
| `location` | Optional[List[float]] | None | World position [x, y, z] |
| `radius` | float | 0.1 | Brush radius (Blender units) |
| `strength` | float | 0.5 | Brush strength (0-1) |

---

### sculpt_brush_grab

**[SCULPT MODE][DESTRUCTIVE]**

Sets up the grab brush for moving geometry.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `object_name` | Optional[str] | None | Target object |
| `from_location` | Optional[List[float]] | None | Start position [x, y, z] |
| `to_location` | Optional[List[float]] | None | End position [x, y, z] |
| `radius` | float | 0.1 | Brush radius |
| `strength` | float | 0.5 | Brush strength (0-1) |

---

### sculpt_brush_crease

**[SCULPT MODE][DESTRUCTIVE]**

Sets up the crease brush for creating sharp lines.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `object_name` | Optional[str] | None | Target object |
| `location` | Optional[List[float]] | None | World position [x, y, z] |
| `radius` | float | 0.1 | Brush radius |
| `strength` | float | 0.5 | Brush strength (0-1) |
| `pinch` | float | 0.5 | Pinch amount (0-1) |

---

## Architecture

### Layer Structure

```
┌─────────────────────────────────────────────────────────────┐
│ 1. DOMAIN LAYER                                             │
│    server/domain/tools/sculpt.py                            │
│    - ISculptTool interface                                  │
│    - auto_sculpt, brush_smooth, brush_grab, brush_crease    │
├─────────────────────────────────────────────────────────────┤
│ 2. APPLICATION LAYER                                        │
│    server/application/tool_handlers/sculpt_handler.py       │
│    - SculptToolHandler implements ISculptTool               │
│    - Sends RPC requests to Blender                          │
├─────────────────────────────────────────────────────────────┤
│ 3. ADAPTER LAYER                                            │
│    server/adapters/mcp/areas/sculpt.py                      │
│    - @mcp.tool() decorated functions                        │
│    - sculpt_auto, sculpt_brush_smooth, etc.                 │
├─────────────────────────────────────────────────────────────┤
│ 4. BLENDER ADDON                                            │
│    blender_addon/application/handlers/sculpt.py             │
│    - SculptHandler class                                    │
│    - bpy.ops.sculpt.* and bpy.ops.wm.tool_set_by_id calls   │
└─────────────────────────────────────────────────────────────┘
```

### RPC Commands

| RPC Command | Handler Method |
|-------------|----------------|
| `sculpt.auto` | `SculptHandler.auto_sculpt()` |
| `sculpt.brush_smooth` | `SculptHandler.brush_smooth()` |
| `sculpt.brush_grab` | `SculptHandler.brush_grab()` |
| `sculpt.brush_crease` | `SculptHandler.brush_crease()` |

---

## Implementation Notes

### Mode Handling

All sculpt tools automatically:
1. Verify target is a mesh object
2. Switch to Sculpt Mode if needed
3. Configure symmetry settings

### Mesh Filters vs Brush Strokes

**Mesh Filters (used by `sculpt_auto`):**
- Apply uniformly to entire mesh
- Predictable, reproducible results
- No need for screen coordinates
- Ideal for AI workflows

**Brush Strokes (brush setup tools):**
- Require screen-space coordinates
- Need manual interaction
- Results depend on brush path
- Less suitable for programmatic use

### Recommended Workflow

For AI-driven sculpting:

1. Create base mesh with primitives
2. Add geometry with `mesh_remesh_voxel`
3. Use `sculpt_auto` for organic shaping
4. Apply multiple iterations with varying strength

```
# Example workflow for organic shape
modeling_create_primitive(type="UV_SPHERE")
mesh_remesh_voxel(voxel_size=0.05)
sculpt_auto(operation="smooth", iterations=2, strength=0.3)
sculpt_auto(operation="inflate", strength=0.2)
```

---

## Alternatives for Organic Shaping

When sculpt tools are too complex, consider:

| Task | Alternative Tool |
|------|------------------|
| Smoothing | `mesh_smooth(iterations=5, factor=0.5)` |
| Inflate/Deflate | `mesh_shrink_fatten(value=0.1)` |
| Noise/Organic | `mesh_randomize(amount=0.05)` |
| Sharp edges | `mesh_bevel(offset=0.01, segments=2)` |

These mesh tools work in Edit Mode and are more predictable for AI workflows.

---

## Testing

### Unit Tests

Location: `tests/unit/tools/sculpt/test_sculpt_tools.py`

Tests cover:
- Filter operations (smooth, inflate, flatten, sharpen)
- Symmetry configuration
- Value clamping (strength, pinch)
- Error handling (invalid object, non-mesh)
- Mode switching

### E2E Tests

Location: `tests/e2e/tools/sculpt/test_sculpt_tools.py`

Requires running Blender with addon enabled.
