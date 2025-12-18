# TASK-020-5: Scene Inspect Mega Tool

**Status:** ✅ Done
**Priority:** 🔴 High
**Phase:** LLM Context Optimization
**Created:** 2025-11-28

---

## 🎯 Goal

Create a unified tool `scene_inspect` for deep inspection of objects and the scene (used occasionally for analysis).

---

## 📋 Replaces (unregister @mcp.tool())

| Original Tool | Action |
|---------------|--------|
| `scene_inspect_object` | `"object"` |
| `scene_inspect_mesh_topology` | `"topology"` |
| `scene_inspect_modifiers` | `"modifiers"` |
| `scene_inspect_material_slots` | `"materials"` |

**Savings:** 4 tools → 1 tool (-3 definitions for LLM)

---

## 🔧 Signature

```python
from typing import Literal, Optional
from fastmcp import Context
from server.adapters.mcp.instance import mcp

@mcp.tool()
def scene_inspect(
    ctx: Context,
    action: Literal["object", "topology", "modifiers", "materials"],
    object_name: Optional[str] = None,
    detailed: bool = False,
    include_disabled: bool = True,
    material_filter: Optional[str] = None,
    include_empty_slots: bool = True
) -> str:
    """
    [SCENE][READ-ONLY][SAFE] Detailed inspection queries for objects and scene.

    Actions and required parameters:
    - "object": Requires object_name. Returns transform, collections, materials, modifiers, mesh stats.
    - "topology": Requires object_name. Returns vertex/edge/face/tri/quad/ngon counts. Optional: detailed=True for non-manifold checks.
    - "modifiers": Optional object_name (None scans all). Returns modifier stacks. Optional: include_disabled=False.
    - "materials": No params required. Returns material slot audit. Optional: material_filter, include_empty_slots.

    Workflow: READ-ONLY | USE → detailed analysis before export or debugging

    Examples:
        scene_inspect(action="object", object_name="Cube")
        scene_inspect(action="topology", object_name="Cube", detailed=True)
        scene_inspect(action="modifiers", object_name="Cube")
        scene_inspect(action="modifiers")  # scans all objects
        scene_inspect(action="materials", material_filter="Wood")
    """
```

---

## 📁 Files to modify

| File | Changes |
|------|--------|
| `server/adapters/mcp/areas/scene.py` | Add `scene_inspect`. Remove `@mcp.tool()` from 4 functions (keep the functions themselves). |

---

## 🧪 Tests

- **Keep:** Existing tests for the original functions (testing internal logic)
- **Add:** `tests/test_scene_inspect_mega.py` - tests for the unified tool

---

## ✅ Deliverables

- [ ] Implementation of `scene_inspect` with routing to the original functions
- [ ] Removal of `@mcp.tool()` from the 4 replaced functions
- [ ] Tests for `scene_inspect`
- [ ] Documentation update

---

## 📊 Estimation

- **New lines of code:** ~45 (routing + docstring)
- **Modifications:** ~4 (removal of decorators)
- **Tests:** ~30 lines
