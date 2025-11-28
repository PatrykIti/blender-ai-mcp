# TASK-020-3: Scene Create Mega Tool

**Status:** ⏳ To Do
**Priority:** 🟡 Medium
**Phase:** LLM Context Optimization
**Created:** 2025-11-28

---

## 🎯 Cel

Utworzyć zunifikowany tool `scene_create` który zastąpi 4 osobne narzędzia tworzenia obiektów, oszczędzając kontekst LLM.

---

## 📋 Zastępuje (unregister @mcp.tool())

| Oryginalny Tool | Action | Plik źródłowy |
|-----------------|--------|---------------|
| `scene_create_light` | `"light"` | scene.py |
| `scene_create_camera` | `"camera"` | scene.py |
| `scene_create_empty` | `"empty"` | scene.py |
| `modeling_create_primitive` | `"primitive"` | modeling.py |

**Oszczędność:** 4 tools → 1 tool (-3 definitions dla LLM)

---

## 🔧 Sygnatura

```python
from typing import List, Literal, Optional, Union
from fastmcp import Context
from server.adapters.mcp.instance import mcp

@mcp.tool()
def scene_create(
    ctx: Context,
    action: Literal["light", "camera", "empty", "primitive"],
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
    size: float = 1.0,
    # Primitive params:
    primitive_type: Literal["Cube", "Sphere", "Cylinder", "Plane", "Cone", "Monkey", "Torus"] = "Cube",
    radius: float = 1.0
) -> str:
    """
    [SCENE][SAFE] Unified creation tool for scene objects.

    Actions and required parameters:
    - "light": Creates light source. Optional: light_type (POINT/SUN/SPOT/AREA), energy, color, location, name.
    - "camera": Creates camera. Optional: location, rotation, lens, clip_start, clip_end, name.
    - "empty": Creates empty object. Optional: empty_type (PLAIN_AXES/ARROWS/CIRCLE/CUBE/SPHERE/CONE/IMAGE), size, location, name.
    - "primitive": Creates mesh primitive. Optional: primitive_type (Cube/Sphere/Cylinder/Plane/Cone/Monkey/Torus), radius, size, location, rotation, name.

    All location/rotation/color params accept either list [x,y,z] or string "[x,y,z]".

    Workflow: START → new scene object | AFTER → modeling_transform, scene_set_mode('EDIT')

    Examples:
        scene_create(action="light", light_type="SUN", energy=5.0)
        scene_create(action="camera", location=[0, -10, 5], rotation=[1.0, 0, 0])
        scene_create(action="empty", empty_type="ARROWS", location=[0, 0, 2])
        scene_create(action="primitive", primitive_type="Sphere", radius=2.0, location=[0, 0, 3])
    """
```

---

## 📁 Pliki do modyfikacji

| Plik | Zmiany |
|------|--------|
| `server/adapters/mcp/areas/scene.py` | Dodaj `scene_create`. Usuń `@mcp.tool()` z 3 funkcji. |
| `server/adapters/mcp/areas/modeling.py` | Usuń `@mcp.tool()` z `modeling_create_primitive`. |

---

## 🧪 Testy

- **Zachowaj:** Istniejące testy dla oryginalnych funkcji (testują logikę wewnętrzną)
- **Dodaj:** `tests/test_scene_create_mega.py` - testy dla unified tool

---

## ✅ Deliverables

- [ ] Implementacja `scene_create` z routing do oryginalnych funkcji
- [ ] Usunięcie `@mcp.tool()` z 4 zastąpionych funkcji (3 w scene.py, 1 w modeling.py)
- [ ] Testy dla `scene_create`
- [ ] Aktualizacja dokumentacji

---

## 📊 Estymacja

- **Nowe linie kodu:** ~60 (routing + docstring)
- **Modyfikacje:** ~4 (usunięcie dekoratorów)
- **Testy:** ~40 linii
