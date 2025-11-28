# TASK-020-5: Scene Inspect Mega Tool

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Phase:** LLM Context Optimization
**Created:** 2025-11-28

---

## 🎯 Cel

Utworzyć zunifikowany tool `scene_inspect` dla głębokiej inspekcji obiektów i sceny (używany okazjonalnie do analizy).

---

## 📋 Zastępuje (unregister @mcp.tool())

| Oryginalny Tool | Action |
|-----------------|--------|
| `scene_inspect_object` | `"object"` |
| `scene_inspect_mesh_topology` | `"topology"` |
| `scene_inspect_modifiers` | `"modifiers"` |
| `scene_inspect_material_slots` | `"materials"` |

**Oszczędność:** 4 tools → 1 tool (-3 definitions dla LLM)

---

## 🔧 Sygnatura

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

## 📁 Pliki do modyfikacji

| Plik | Zmiany |
|------|--------|
| `server/adapters/mcp/areas/scene.py` | Dodaj `scene_inspect`. Usuń `@mcp.tool()` z 4 funkcji (zachowaj same funkcje). |

---

## 🧪 Testy

- **Zachowaj:** Istniejące testy dla oryginalnych funkcji (testują logikę wewnętrzną)
- **Dodaj:** `tests/test_scene_inspect_mega.py` - testy dla unified tool

---

## ✅ Deliverables

- [ ] Implementacja `scene_inspect` z routing do oryginalnych funkcji
- [ ] Usunięcie `@mcp.tool()` z 4 zastąpionych funkcji
- [ ] Testy dla `scene_inspect`
- [ ] Aktualizacja dokumentacji

---

## 📊 Estymacja

- **Nowe linie kodu:** ~45 (routing + docstring)
- **Modyfikacje:** ~4 (usunięcie dekoratorów)
- **Testy:** ~30 linii
