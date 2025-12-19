# TASK-073: Rig, Curve, and Lattice Introspection

**Priority:** 🔴 High  
**Category:** Rig/Geometry Introspection  
**Estimated Effort:** Medium  
**Dependencies:** TASK-021 (Curves), TASK-033 (Lattice), TASK-037 (Armature)  
**Status:** ⏳ TODO

---

## 🎯 Objective

Expose full data for curves, lattices, and armatures so they can be reconstructed precisely in YAML workflows.

---

## 🔧 Sub-Tasks

### TASK-073-1: curve_get_data

**Status:** ⏳ TODO

```python
@mcp.tool()
def curve_get_data(
    ctx: Context,
    object_name: str
) -> str:
    """
    [OBJECT MODE][READ-ONLY][SAFE] Returns curve splines, points, and settings.
    """
```

**Return JSON (example):**
```json
{
  "object_name": "BezierCurve",
  "splines": [
    {"type": "BEZIER", "points": [[0,0,0], [1,0,0]], "handles": [...]}
  ],
  "bevel_depth": 0.0,
  "extrude": 0.0
}
```

**Implementation Checklist:**
| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/domain/tools/curve.py` | `def get_data(...)` |
| Application | `server/application/tool_handlers/curve_handler.py` | RPC wrapper + validation |
| Adapter | `server/adapters/mcp/areas/curve.py` | `@mcp.tool()` exposure |
| Addon | `blender_addon/application/handlers/curve.py` | Curve spline dump |
| Metadata | `server/router/infrastructure/tools_metadata/curve/curve_get_data.json` | Tool metadata |
| Tests | `tests/unit/tools/curve/test_get_data.py` | Spline + handle data |

---

### TASK-073-2: lattice_get_points

**Status:** ⏳ TODO

```python
@mcp.tool()
def lattice_get_points(
    ctx: Context,
    object_name: str
) -> str:
    """
    [OBJECT MODE][READ-ONLY][SAFE] Returns lattice point positions and resolution.
    """
```

**Return JSON (example):**
```json
{
  "object_name": "Lattice",
  "points_u": 2,
  "points_v": 2,
  "points_w": 4,
  "points": [[0,0,0], [1,0,0], ...]
}
```

**Implementation Checklist:**
| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/domain/tools/lattice.py` | `def get_points(...)` |
| Application | `server/application/tool_handlers/lattice_handler.py` | RPC wrapper + validation |
| Adapter | `server/adapters/mcp/areas/lattice.py` | `@mcp.tool()` exposure |
| Addon | `blender_addon/application/handlers/lattice.py` | Lattice point dump |
| Metadata | `server/router/infrastructure/tools_metadata/lattice/lattice_get_points.json` | Tool metadata |
| Tests | `tests/unit/tools/lattice/test_get_points.py` | Resolution + points |

---

### TASK-073-3: armature_get_data

**Status:** ⏳ TODO

```python
@mcp.tool()
def armature_get_data(
    ctx: Context,
    object_name: str,
    include_pose: bool = False
) -> str:
    """
    [OBJECT MODE][READ-ONLY][SAFE] Returns armature bones and hierarchy.
    """
```

**Return JSON (example):**
```json
{
  "object_name": "Armature",
  "bones": [
    {"name": "Spine", "head": [0,0,0], "tail": [0,0,1], "parent": null}
  ],
  "pose": []
}
```

**Implementation Checklist:**
| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/domain/tools/armature.py` | `def get_data(...)` |
| Application | `server/application/tool_handlers/armature_handler.py` | RPC wrapper + validation |
| Adapter | `server/adapters/mcp/areas/armature.py` | `@mcp.tool()` exposure |
| Addon | `blender_addon/application/handlers/armature.py` | Bone hierarchy dump |
| Metadata | `server/router/infrastructure/tools_metadata/armature/armature_get_data.json` | Tool metadata |
| Tests | `tests/unit/tools/armature/test_get_data.py` | Bone list + parents |

---

## ✅ Success Criteria
- Curve, lattice, and armature structures can be reconstructed without exports
