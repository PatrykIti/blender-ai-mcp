# TASK-020-2: Mesh Select Mega Tool (Simple)

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Phase:** LLM Context Optimization
**Created:** 2025-11-28

---

## 🎯 Cel

Utworzyć zunifikowany tool `mesh_select` dla prostych operacji selekcji (bez dodatkowych parametrów).

---

## 📋 Zastępuje (unregister @mcp.tool())

| Oryginalny Tool | Action |
|-----------------|--------|
| `mesh_select_all` | `"all"` / `"none"` |
| `mesh_select_linked` | `"linked"` |
| `mesh_select_more` | `"more"` |
| `mesh_select_less` | `"less"` |
| `mesh_select_boundary` | `"boundary"` |

**NIE zastępuje (osobne narzędzia):**
- `mesh_get_vertex_data` - READ-ONLY tool zwracający dane
- `mesh_select_by_index`, `mesh_select_loop`, `mesh_select_ring`, `mesh_select_by_location` → TASK-020-4

**Oszczędność:** 5 tools → 1 tool (-4 definitions dla LLM)

---

## 🔧 Sygnatura

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

## 📁 Pliki do modyfikacji

| Plik | Zmiany |
|------|--------|
| `server/adapters/mcp/areas/mesh.py` | Dodaj `mesh_select`. Usuń `@mcp.tool()` z 5 funkcji (zachowaj same funkcje). |

---

## 🧪 Testy

- **Zachowaj:** Istniejące testy dla oryginalnych funkcji (testują logikę wewnętrzną)
- **Dodaj:** `tests/test_mesh_select_mega.py` - testy dla unified tool

---

## ✅ Deliverables

- [ ] Implementacja `mesh_select` z routing do oryginalnych funkcji
- [ ] Usunięcie `@mcp.tool()` z 5 zastąpionych funkcji
- [ ] Testy dla `mesh_select`
- [ ] Aktualizacja dokumentacji

---

## 📊 Estymacja

- **Nowe linie kodu:** ~40 (routing + docstring)
- **Modyfikacje:** ~5 (usunięcie dekoratorów)
- **Testy:** ~25 linii
