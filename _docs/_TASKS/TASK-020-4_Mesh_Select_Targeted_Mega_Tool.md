# TASK-020-4: Mesh Select Targeted Mega Tool

**Status:** ✅ Done
**Priority:** 🔴 High
**Phase:** LLM Context Optimization
**Created:** 2025-11-28

---

## 🎯 Goal

Create a unified tool `mesh_select_targeted` for precise selection operations (requiring additional parameters).

---

## 📋 Replaces (unregister @mcp.tool())

| Original Tool | Action |
|---------------|--------|
| `mesh_select_by_index` | `"by_index"` |
| `mesh_select_loop` | `"loop"` |
| `mesh_select_ring` | `"ring"` |
| `mesh_select_by_location` | `"by_location"` |

**Savings:** 4 tools → 1 tool (-3 definitions for LLM)

---

## 🔧 Signature

```python
from typing import List, Literal, Optional
from fastmcp import Context
from server.adapters.mcp.instance import mcp

@mcp.tool()
def mesh_select_targeted(
    ctx: Context,
    action: Literal["by_index", "loop", "ring", "by_location"],
    # by_index params:
    indices: Optional[List[int]] = None,
    element_type: Literal["VERT", "EDGE", "FACE"] = "VERT",
    selection_mode: Literal["SET", "ADD", "SUBTRACT"] = "SET",
    # loop/ring params:
    edge_index: Optional[int] = None,
    # by_location params:
    axis: Optional[Literal["X", "Y", "Z"]] = None,
    min_coord: Optional[float] = None,
    max_coord: Optional[float] = None
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][SAFE] Targeted selection operations for mesh geometry.

    Actions and required parameters:
    - "by_index": Requires indices (list of ints). Optional: element_type (VERT/EDGE/FACE), selection_mode (SET/ADD/SUBTRACT).
    - "loop": Requires edge_index (int). Selects edge loop starting from that edge.
    - "ring": Requires edge_index (int). Selects edge ring starting from that edge.
    - "by_location": Requires axis (X/Y/Z), min_coord, max_coord. Optional: element_type. Selects geometry within coordinate range.

    Workflow: BEFORE → mesh_get_vertex_data (for indices) | AFTER → mesh_extrude, mesh_delete, mesh_boolean

    Examples:
        mesh_select_targeted(action="by_index", indices=[0, 1, 2], element_type="VERT")
        mesh_select_targeted(action="by_index", indices=[0, 1], element_type="FACE", selection_mode="ADD")
        mesh_select_targeted(action="loop", edge_index=4)
        mesh_select_targeted(action="ring", edge_index=3)
        mesh_select_targeted(action="by_location", axis="Z", min_coord=0.5, max_coord=2.0)
        mesh_select_targeted(action="by_location", axis="X", min_coord=-1.0, max_coord=0.0, element_type="FACE")
    """
```

---

## 📁 Files to modify

| File | Changes |
|------|---------|
| `server/adapters/mcp/areas/mesh.py` | Add `mesh_select_targeted`. Remove `@mcp.tool()` from the 4 functions (keep the functions themselves). |

---

## 🧪 Tests

- **Keep:** Existing tests for the original functions (testing internal logic)
- **Add:** `tests/test_mesh_select_targeted_mega.py` - tests for the unified tool

---

## ✅ Deliverables

- [ ] Implement `mesh_select_targeted` with routing to the original functions
- [ ] Remove `@mcp.tool()` from the 4 replaced functions
- [ ] Tests for `mesh_select_targeted`
- [ ] Update documentation

---

## 📊 Estimate

- **New lines of code:** ~50 (routing + docstring)
- **Modifications:** ~4 (removal of decorators)
- **Tests:** ~35 lines
