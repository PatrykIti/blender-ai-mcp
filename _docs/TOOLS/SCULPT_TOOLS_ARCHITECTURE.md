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
| `sculpt_brush_clay` | Clay brush setup | Adds material (muscle, fat) |
| `sculpt_brush_inflate` | Inflate brush setup | Pushes outward (swelling, tumors) |
| `sculpt_brush_blob` | Blob brush setup | Creates organic bulges |
| `sculpt_brush_snake_hook` | Snake hook setup | Pulls tendrils (vessels, nerves) |
| `sculpt_brush_draw` | Draw brush setup | General sculpting |
| `sculpt_brush_pinch` | Pinch brush setup | Sharp creases (wrinkles, folds) |

> **Note:** Brush tools configure the brush and context but don't execute strokes programmatically. For whole-mesh operations, use `sculpt_auto`.

### Dynamic Topology Tools (TASK-038)

| Tool | Operation | Reliability |
|------|-----------|-------------|
| `sculpt_enable_dyntopo` | Enables dynamic topology | ✅ High |
| `sculpt_disable_dyntopo` | Disables dynamic topology | ✅ High |
| `sculpt_dyntopo_flood_fill` | Applies detail to entire mesh | ✅ High |

> **Warning:** Dynamic Topology (Dyntopo) destroys UV maps and vertex groups. Use for concept/base mesh only.

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

### sculpt_brush_clay

**[SCULPT MODE][DESTRUCTIVE]**

Clay brush for adding material. Ideal for muscle mass, fat deposits.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `object_name` | Optional[str] | None | Target object |
| `radius` | float | 50.0 | Brush radius (pixels) |
| `strength` | float | 0.5 | Brush strength (0-1) |

---

### sculpt_brush_inflate

**[SCULPT MODE][DESTRUCTIVE]**

Inflate brush for pushing geometry outward. Ideal for swelling, tumors.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `object_name` | Optional[str] | None | Target object |
| `radius` | float | 50.0 | Brush radius (pixels) |
| `strength` | float | 0.5 | Brush strength (0-1) |

---

### sculpt_brush_blob

**[SCULPT MODE][DESTRUCTIVE]**

Blob brush for creating rounded organic bulges.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `object_name` | Optional[str] | None | Target object |
| `radius` | float | 50.0 | Brush radius (pixels) |
| `strength` | float | 0.5 | Brush strength (0-1) |

---

### sculpt_brush_snake_hook

**[SCULPT MODE][DESTRUCTIVE]**

Snake hook brush for pulling tendrils. Ideal for blood vessels, nerves, tentacles.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `object_name` | Optional[str] | None | Target object |
| `radius` | float | 50.0 | Brush radius (pixels) |
| `strength` | float | 0.5 | Brush strength (0-1) |

---

### sculpt_brush_draw

**[SCULPT MODE][DESTRUCTIVE]**

Basic draw brush for general sculpting operations.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `object_name` | Optional[str] | None | Target object |
| `radius` | float | 50.0 | Brush radius (pixels) |
| `strength` | float | 0.5 | Brush strength (0-1) |

---

### sculpt_brush_pinch

**[SCULPT MODE][DESTRUCTIVE]**

Pinch brush for creating sharp creases. Ideal for wrinkles, folds, skin details.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `object_name` | Optional[str] | None | Target object |
| `radius` | float | 50.0 | Brush radius (pixels) |
| `strength` | float | 0.5 | Brush strength (0-1) |

---

### sculpt_enable_dyntopo

**[SCULPT MODE][DESTRUCTIVE]**

Enables Dynamic Topology for adaptive sculpting. Destroys UVs and vertex groups.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `object_name` | Optional[str] | None | Target object |
| `detail_mode` | Literal["RELATIVE", "CONSTANT", "BRUSH", "MANUAL"] | "RELATIVE" | Detail calculation mode |
| `detail_size` | float | 12.0 | Detail size (px for RELATIVE, units for others) |
| `use_smooth_shading` | bool | True | Use smooth shading |

**Detail Modes:**
- `RELATIVE` - Detail size in screen pixels (good for consistent detail at any zoom)
- `CONSTANT` - Fixed detail size in scene units
- `BRUSH` - Detail follows brush size
- `MANUAL` - Manual control via flood fill

---

### sculpt_disable_dyntopo

**[SCULPT MODE][SAFE]**

Disables Dynamic Topology.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `object_name` | Optional[str] | None | Target object |

---

### sculpt_dyntopo_flood_fill

**[SCULPT MODE][DESTRUCTIVE]**

Applies current detail level to entire mesh. Useful for uniform detail.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `object_name` | Optional[str] | None | Target object |

---

## Architecture

### Layer Structure

```
┌─────────────────────────────────────────────────────────────┐
│ 1. DOMAIN LAYER                                             │
│    server/domain/tools/sculpt.py                            │
│    - ISculptTool interface                                  │
│    - auto_sculpt, all brush methods, dyntopo methods        │
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
| `sculpt.brush_clay` | `SculptHandler.brush_clay()` |
| `sculpt.brush_inflate` | `SculptHandler.brush_inflate()` |
| `sculpt.brush_blob` | `SculptHandler.brush_blob()` |
| `sculpt.brush_snake_hook` | `SculptHandler.brush_snake_hook()` |
| `sculpt.brush_draw` | `SculptHandler.brush_draw()` |
| `sculpt.brush_pinch` | `SculptHandler.brush_pinch()` |
| `sculpt.enable_dyntopo` | `SculptHandler.enable_dyntopo()` |
| `sculpt.disable_dyntopo` | `SculptHandler.disable_dyntopo()` |
| `sculpt.dyntopo_flood_fill` | `SculptHandler.dyntopo_flood_fill()` |

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
