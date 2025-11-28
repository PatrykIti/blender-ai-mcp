# TASK-020-2: Mesh Select Mega Tool

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Phase:** LLM Context Optimization
**Created:** 2025-11-28

---

## 🎯 Cel

Utworzyć zunifikowany tool `mesh_select` który zastąpi 9 osobnych narzędzi selection, oszczędzając kontekst LLM.

---

## 📋 Zastępuje (unregister @mcp.tool())

| Oryginalny Tool | Action |
|-----------------|--------|
| `mesh_select_all` | `"all"` / `"none"` |
| `mesh_select_by_index` | `"by_index"` |
| `mesh_select_loop` | `"loop"` |
| `mesh_select_ring` | `"ring"` |
| `mesh_select_linked` | `"linked"` |
| `mesh_select_more` | `"more"` |
| `mesh_select_less` | `"less"` |
| `mesh_select_by_location` | `"by_location"` |
| `mesh_select_boundary` | `"boundary"` |

**NIE zastępuje (zostaje osobno):**
- `mesh_get_vertex_data` - READ-ONLY tool zwracający dane, nie pasuje do selection

**Oszczędność:** 9 tools → 1 tool (-8 definitions dla LLM)

---

## 🔧 Sygnatura

```python
from typing import List, Literal, Optional
from fastmcp import Context
from server.adapters.mcp.instance import mcp

@mcp.tool()
def mesh_select(
    ctx: Context,
    action: Literal["all", "none", "by_index", "loop", "ring", "linked", "more", "less", "by_location", "boundary"],
    indices: Optional[List[int]] = None,
    element_type: Literal["VERT", "EDGE", "FACE"] = "VERT",
    selection_mode: Literal["SET", "ADD", "SUBTRACT"] = "SET",
    edge_index: Optional[int] = None,
    axis: Optional[Literal["X", "Y", "Z"]] = None,
    min_coord: Optional[float] = None,
    max_coord: Optional[float] = None,
    boundary_mode: Literal["EDGE", "VERT"] = "EDGE"
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][SAFE] Unified selection tool for mesh geometry.

    Actions and required parameters:
    - "all": Selects all geometry. No params required.
    - "none": Deselects all geometry. No params required.
    - "by_index": Requires indices (list of ints), element_type (VERT/EDGE/FACE). Optional: selection_mode (SET/ADD/SUBTRACT).
    - "loop": Requires edge_index (int). Selects edge loop starting from that edge.
    - "ring": Requires edge_index (int). Selects edge ring starting from that edge.
    - "linked": No params required. Selects all geometry connected to current selection.
    - "more": No params required. Grows selection by 1 step.
    - "less": No params required. Shrinks selection by 1 step.
    - "by_location": Requires axis (X/Y/Z), min_coord, max_coord. Optional: element_type. Selects geometry within coordinate range.
    - "boundary": Optional boundary_mode (EDGE/VERT). Selects boundary edges or vertices (1 adjacent face).

    Workflow: BEFORE → mesh_get_vertex_data (for indices) | AFTER → mesh_extrude, mesh_delete, mesh_boolean

    Examples:
        mesh_select(action="all")
        mesh_select(action="none")
        mesh_select(action="by_index", indices=[0, 1, 2], element_type="VERT")
        mesh_select(action="loop", edge_index=4)
        mesh_select(action="by_location", axis="Z", min_coord=0.5, max_coord=2.0)
        mesh_select(action="boundary", boundary_mode="EDGE")
    """
```

---

## 📁 Pliki do modyfikacji

| Plik | Zmiany |
|------|--------|
| `server/adapters/mcp/areas/mesh.py` | Dodaj `mesh_select`. Usuń `@mcp.tool()` z 9 funkcji (zachowaj same funkcje). |

---

## 🧪 Testy

- **Zachowaj:** Istniejące testy dla oryginalnych funkcji (testują logikę wewnętrzną)
- **Dodaj:** `tests/test_mesh_select_mega.py` - testy dla unified tool

---

## ✅ Deliverables

- [ ] Implementacja `mesh_select` z routing do oryginalnych funkcji
- [ ] Usunięcie `@mcp.tool()` z 9 zastąpionych funkcji
- [ ] Testy dla `mesh_select`
- [ ] Aktualizacja dokumentacji

---

## 📊 Estymacja

- **Nowe linie kodu:** ~80 (routing + docstring)
- **Modyfikacje:** ~9 (usunięcie dekoratorów)
- **Testy:** ~50 linii
