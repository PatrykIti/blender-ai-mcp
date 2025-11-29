# TASK-020-3: Scene Create Mega Tool

**Status:** ✅ Done
**Priority:** 🟡 Medium
**Phase:** LLM Context Optimization
**Created:** 2025-11-28

---

## 🎯 Cel

Utworzyć zunifikowany tool `scene_create` dla tworzenia obiektów pomocniczych sceny (światła, kamery, empty).

---

## 📋 Zastępuje (unregister @mcp.tool())

| Oryginalny Tool | Action | Plik |
|-----------------|--------|------|
| `scene_create_light` | `"light"` | scene.py |
| `scene_create_camera` | `"camera"` | scene.py |
| `scene_create_empty` | `"empty"` | scene.py |

**NIE zastępuje (zostaje osobno):**
- `modeling_create_primitive` - najczęściej używany tool, warto zachować bezpośredni dostęp

**Oszczędność:** 3 tools → 1 tool (-2 definitions dla LLM)

---

## 🔧 Sygnatura

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

## 📁 Pliki do modyfikacji

| Plik | Zmiany |
|------|--------|
| `server/adapters/mcp/areas/scene.py` | Dodaj `scene_create`. Usuń `@mcp.tool()` z 3 funkcji (zachowaj same funkcje). |

---

## 🧪 Testy

- **Zachowaj:** Istniejące testy dla oryginalnych funkcji (testują logikę wewnętrzną)
- **Dodaj:** `tests/test_scene_create_mega.py` - testy dla unified tool

---

## ✅ Deliverables

- [ ] Implementacja `scene_create` z routing do oryginalnych funkcji
- [ ] Usunięcie `@mcp.tool()` z 3 zastąpionych funkcji
- [ ] Testy dla `scene_create`
- [ ] Aktualizacja dokumentacji

---

## 📊 Estymacja

- **Nowe linie kodu:** ~45 (routing + docstring)
- **Modyfikacje:** ~3 (usunięcie dekoratorów)
- **Testy:** ~30 linii
