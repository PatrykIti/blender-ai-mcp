# TASK-020-1: Scene Context Mega Tool

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Phase:** LLM Context Optimization
**Created:** 2025-11-28

---

## 🎯 Cel

Utworzyć lekki tool `scene_context` dla szybkich zapytań o stan sceny (używany przed prawie każdą operacją).

---

## 📋 Zastępuje (unregister @mcp.tool())

| Oryginalny Tool | Action |
|-----------------|--------|
| `scene_get_mode` | `"mode"` |
| `scene_list_selection` | `"selection"` |

**NIE zastępuje (osobne narzędzia):**
- `scene_inspect_object`, `scene_inspect_mesh_topology`, `scene_inspect_modifiers`, `scene_inspect_material_slots` → TASK-020-5

**Oszczędność:** 2 tools → 1 tool (-1 definition dla LLM)

---

## 🔧 Sygnatura

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

## 📁 Pliki do modyfikacji

| Plik | Zmiany |
|------|--------|
| `server/adapters/mcp/areas/scene.py` | Dodaj `scene_context`. Usuń `@mcp.tool()` z 2 funkcji (zachowaj same funkcje). |

---

## 🧪 Testy

- **Zachowaj:** Istniejące testy dla oryginalnych funkcji (testują logikę wewnętrzną)
- **Dodaj:** `tests/test_scene_context_mega.py` - testy dla unified tool

---

## ✅ Deliverables

- [ ] Implementacja `scene_context` z routing do oryginalnych funkcji
- [ ] Usunięcie `@mcp.tool()` z 2 zastąpionych funkcji
- [ ] Testy dla `scene_context`
- [ ] Aktualizacja dokumentacji

---

## 📊 Estymacja

- **Nowe linie kodu:** ~25 (routing + docstring)
- **Modyfikacje:** ~2 (usunięcie dekoratorów)
- **Testy:** ~15 linii
