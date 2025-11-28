# TASK-020-1: Scene Inspect Mega Tool

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Phase:** LLM Context Optimization
**Created:** 2025-11-28

---

## 🎯 Cel

Utworzyć zunifikowany tool `scene_inspect` który zastąpi 6 osobnych narzędzi inspection, oszczędzając kontekst LLM.

---

## 📋 Zastępuje (unregister @mcp.tool())

| Oryginalny Tool | Action |
|-----------------|--------|
| `scene_get_mode` | `"mode"` |
| `scene_list_selection` | `"selection"` |
| `scene_inspect_object` | `"object"` |
| `scene_inspect_mesh_topology` | `"topology"` |
| `scene_inspect_modifiers` | `"modifiers"` |
| `scene_inspect_material_slots` | `"materials"` |

**Oszczędność:** 6 tools → 1 tool (-5 definitions dla LLM)

---

## 🔧 Sygnatura

```python
from typing import Literal, Optional
from fastmcp import Context
from server.adapters.mcp.instance import mcp

@mcp.tool()
def scene_inspect(
    ctx: Context,
    action: Literal["mode", "selection", "object", "topology", "modifiers", "materials"],
    object_name: Optional[str] = None,
    detailed: bool = False,
    include_disabled: bool = True,
    material_filter: Optional[str] = None,
    include_empty_slots: bool = True
) -> str:
    """
    [SCENE][SAFE][READ-ONLY] Unified inspection tool for scene state queries.

    Actions and required parameters:
    - "mode": No params required. Returns current Blender mode, active object, selection count.
    - "selection": No params required. Returns selected objects list + edit mode vertex/edge/face counts.
    - "object": Requires object_name. Returns detailed report (transform, collections, materials, modifiers, mesh stats).
    - "topology": Requires object_name. Returns vertex/edge/face/triangle/quad/ngon counts. Optional: detailed=True for non-manifold checks.
    - "modifiers": Optional object_name (None scans all objects). Returns modifier stacks. Optional: include_disabled=False to skip disabled.
    - "materials": No params required. Returns material slot audit. Optional: material_filter, include_empty_slots.

    Workflow: READ-ONLY | FIRST STEP → understand scene state before operations

    Examples:
        scene_inspect(action="mode")
        scene_inspect(action="object", object_name="Cube")
        scene_inspect(action="topology", object_name="Cube", detailed=True)
        scene_inspect(action="modifiers", object_name="Cube")
        scene_inspect(action="materials", material_filter="Wood")
    """
```

---

## 📁 Pliki do modyfikacji

| Plik | Zmiany |
|------|--------|
| `server/adapters/mcp/areas/scene.py` | Dodaj `scene_inspect`. Usuń `@mcp.tool()` z 6 funkcji (zachowaj same funkcje). |

---

## 🧪 Testy

- **Zachowaj:** Istniejące testy dla oryginalnych funkcji (testują logikę wewnętrzną)
- **Dodaj:** `tests/test_scene_inspect_mega.py` - testy dla unified tool

---

## ✅ Deliverables

- [ ] Implementacja `scene_inspect` z routing do oryginalnych funkcji
- [ ] Usunięcie `@mcp.tool()` z 6 zastąpionych funkcji
- [ ] Testy dla `scene_inspect`
- [ ] Aktualizacja dokumentacji

---

## 📊 Estymacja

- **Nowe linie kodu:** ~50 (routing + docstring)
- **Modyfikacje:** ~6 (usunięcie dekoratorów)
- **Testy:** ~30 linii
