# TASK-020-2: Mesh Select Mega Tool (Simple)

**Status:** ✅ Done
**Priority:** 🔴 High
**Phase:** LLM Context Optimization
**Created:** 2025-11-28

---

## 🎯 Goal

Create a unified tool `mesh_select` for simple selection operations (without additional parameters).

---

## 📋 Replaces (unregister @mcp.tool())

| Original Tool | Action |
|---------------|--------|
| `mesh_select_all` | `"all"` / `"none"` |
| `mesh_select_linked` | `"linked"` |
| `mesh_select_more` | `"more"` |
| `mesh_select_less` | `"less"` |
| `mesh_select_boundary` | `"boundary"` |

**DOES NOT replace (separate tools):**
- `mesh_get_vertex_data` - READ-ONLY tool returning data
- `mesh_select_by_index`, `mesh_select_loop`, `mesh_select_ring`, `mesh_select_by_location` → TASK-020-4

**Savings:** 5 tools → 1 tool (-4 definitions for LLM)

---

## 🔧 Signature

```python
from typing import Literal
from fastmcp import Context
from server.adapters.mcp.instance import mcp

@mcp.tool()
def mesh_select(
    ctx: Context,
    action: Literal["all", "none", "linked", "more", "less", "boundary"],
    boundary_mode: Literal["EDGE", "VERT"] = "EDGE"
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][SAFE] Simple selection operations for mesh geometry.

    Actions:
    - "all": Selects all geometry. No params required.
    - "none": Deselects all geometry. No params required.
    - "linked": Selects all geometry connected to current selection.
    - "more": Grows selection by 1 step.
    - "less": Shrinks selection by 1 step.
    - "boundary": Selects boundary edges/vertices. Optional: boundary_mode (EDGE/VERT).

    Workflow: BEFORE → mesh_extrude, mesh_delete, mesh_boolean | START → new selection workflow

    Examples:
        mesh_select(action="all")
        mesh_select(action="none")
        mesh_select(action="linked")
        mesh_select(action="boundary", boundary_mode="EDGE")
    """
```

---

## 📁 Files to modify

| File | Changes |
|------|--------|
| `server/adapters/mcp/areas/mesh.py` | Add `mesh_select`. Remove `@mcp.tool()` from 5 functions (keep the functions themselves). |

---

## 🧪 Tests

- **Keep:** Existing tests for the original functions (test internal logic)
- **Add:** `tests/test_mesh_select_mega.py` - tests for the unified tool

---

## ✅ Deliverables

- [ ] Implementation of `mesh_select` routing to the original functions
- [ ] Removal of `@mcp.tool()` from the 5 replaced functions
- [ ] Tests for `mesh_select`
- [ ] Documentation update

---

## 📊 Estimation

- **New lines of code:** ~40 (routing + docstring)
- **Modifications:** ~5 (removal of decorators)
- **Tests:** ~25 lines
