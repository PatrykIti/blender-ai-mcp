# TASK-020-3: Scene Create Mega Tool

**Status:** ✅ Done
**Priority:** 🟡 Medium
**Phase:** LLM Context Optimization
**Created:** 2025-11-28

---

## 🎯 Goal

Create a unified tool `scene_create` for creating scene helper objects (lights, cameras, empties).

---

## 📋 Replaces (unregister @mcp.tool())

| Original Tool | Action | File |
|---------------|--------|------|
| `scene_create_light` | `"light"` | scene.py |
| `scene_create_camera` | `"camera"` | scene.py |
| `scene_create_empty` | `"empty"` | scene.py |

**Does NOT replace (remains separate):**
- `modeling_create_primitive` - the most frequently used tool, it's worth keeping direct access

**Savings:** 3 tools → 1 tool (-2 definitions for LLM)

---

## 🔧 Signature

```python
from typing import List, Literal, Optional, Union
from fastmcp import Context
from server.adapters.mcp.instance import mcp

@mcp.tool()
def scene_create(
    ctx: Context,
    action: Literal["light", "camera", "empty"],
    location: Union[str, List[float]] = [0.0, 0.0, 0.0],
    rotation: Union[str, List[float]] = [0.0, 0.0, 0.0],
    name: Optional[str] = None,
    # Light params:
    light_type: Literal["POINT", "SUN", "SPOT", "AREA"] = "POINT",
    energy: float = 1000.0,
    color: Union[str, List[float]] = [1.0, 1.0, 1.0],
    # Camera params:
    lens: float = 50.0,
    clip_start: Optional[float] = None,
    clip_end: Optional[float] = None,
    # Empty params:
    empty_type: Literal["PLAIN_AXES", "ARROWS", "SINGLE_ARROW", "CIRCLE", "CUBE", "SPHERE", "CONE", "IMAGE"] = "PLAIN_AXES",
    size: float = 1.0
) -> str:
    """
    [SCENE][SAFE] Creates scene helper objects (lights, cameras, empties).

    Actions and parameters:
    - "light": Creates light source. Optional: light_type (POINT/SUN/SPOT/AREA), energy, color, location, name.
    - "camera": Creates camera. Optional: location, rotation, lens, clip_start, clip_end, name.
    - "empty": Creates empty object. Optional: empty_type (PLAIN_AXES/ARROWS/CIRCLE/CUBE/SPHERE/CONE/IMAGE), size, location, name.

    All location/rotation/color params accept either list [x,y,z] or string "[x,y,z]".

    For mesh primitives (Cube, Sphere, etc.) use modeling_create_primitive instead.

    Workflow: AFTER → geometry complete | BEFORE → scene_get_viewport

    Examples:
        scene_create(action="light", light_type="SUN", energy=5.0)
        scene_create(action="light", light_type="AREA", location=[0, 0, 5], color=[1.0, 0.9, 0.8])
        scene_create(action="camera", location=[0, -10, 5], rotation=[1.0, 0, 0])
        scene_create(action="empty", empty_type="ARROWS", location=[0, 0, 2])
    """
```

---

## 📁 Files to modify

| File | Changes |
|------|--------|
| `server/adapters/mcp/areas/scene.py` | Add `scene_create`. Remove `@mcp.tool()` from 3 functions (keep the functions themselves). |

---

## 🧪 Tests

- **Keep:** Existing tests for original functions (test internal logic)
- **Add:** `tests/test_scene_create_mega.py` - tests for the unified tool

---

## ✅ Deliverables

- [ ] Implementation of `scene_create` with routing to the original functions
- [ ] Removal of `@mcp.tool()` from the 3 replaced functions
- [ ] Tests for `scene_create`
- [ ] Documentation update

---

## 📊 Estimate

- **New lines of code:** ~45 (routing + docstring)
- **Modifications:** ~3 (removal of decorators)
- **Tests:** ~30 lines
