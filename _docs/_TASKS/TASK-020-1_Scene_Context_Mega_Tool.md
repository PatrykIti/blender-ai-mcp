# TASK-020-1: Scene Context Mega Tool

**Status:** ✅ Done
**Priority:** 🔴 High
**Phase:** LLM Context Optimization
**Created:** 2025-11-28

---

## 🎯 Goal

Create a lightweight tool `scene_context` for quick queries about the scene state (used before almost every operation).

---

## 📋 Replaces (unregister @mcp.tool())

| Original Tool | Action |
|---------------|--------|
| `scene_get_mode` | `"mode"` |
| `scene_list_selection` | `"selection"` |

**NOT replaced (separate tools):**
- `scene_inspect_object`, `scene_inspect_mesh_topology`, `scene_inspect_modifiers`, `scene_inspect_material_slots` → TASK-020-5

**Savings:** 2 tools → 1 tool (-1 definition for LLM)

---

## 🔧 Signature

```python
from typing import Literal
from fastmcp import Context
from server.adapters.mcp.instance import mcp

@mcp.tool()
def scene_context(
    ctx: Context,
    action: Literal["mode", "selection"]
) -> str:
    """
    [SCENE][READ-ONLY][SAFE] Quick context queries for scene state.

    Actions:
    - "mode": Returns current Blender mode, active object, selection count.
    - "selection": Returns selected objects list + edit mode vertex/edge/face counts.

    Workflow: READ-ONLY | FIRST STEP → check context before any operation

    Examples:
        scene_context(action="mode")
        scene_context(action="selection")
    """
```

---

## 📁 Files to modify

| File | Changes |
|------|---------|
| `server/adapters/mcp/areas/scene.py` | Add `scene_context`. Remove `@mcp.tool()` from 2 functions (keep the functions themselves). |

---

## 🧪 Tests

- **Keep:** Existing tests for the original functions (test internal logic)
- **Add:** `tests/test_scene_context_mega.py` - tests for the unified tool

---

## ✅ Deliverables

- [ ] Implementation of `scene_context` with routing to the original functions
- [ ] Removal of `@mcp.tool()` from the 2 replaced functions
- [ ] Tests for `scene_context`
- [ ] Documentation update

---

## 📊 Estimation

- **New lines of code:** ~25 (routing + docstring)
- **Modifications:** ~2 (removal of decorators)
- **Tests:** ~15 lines
