---
type: task
id: TASK-004_Modeling_Tools
title: Narzędzia Modelowania (Mesh Ops) - Clean Architecture
status: todo
priority: medium
assignee: unassigned
depends_on: TASK-003_4_Refactor_Addon_Architecture
---

# 🎯 Cel
Implementacja kluczowych narzędzi do edycji geometrii (tworzenie prymitywów, modyfikatory), które pozwolą AI tworzyć proste modele 3D.
Zadanie musi być wykonane zgodnie z zasadami **Clean Architecture** wdrożonymi w poprzednich krokach.

# 📋 Zakres prac (Domain & Application)

## 1. Domain Layer (`server/domain/`)
- **Utworzyć `server/domain/tools/modeling.py`**:
  - Interfejs `IModelingTool(ABC)`.
  - Metody:
    - `create_primitive(type: str, size: float, location: List[float], rotation: List[float])`
    - `transform_object(name: str, location: List[float], rotation: List[float], scale: List[float])`
    - `add_modifier(name: str, type: str, properties: Dict[str, Any])`
    - `apply_modifier(name: str, modifier_name: str)`

## 2. Application Layer (`server/application/`)
- **Utworzyć `server/application/tool_handlers/modeling_handler.py`**:
  - Klasa `ModelingToolHandler(IModelingTool)`.
  - Wstrzykiwanie `IRpcClient`.
  - Implementacja metod wołających RPC (np. `modeling.create_primitive`).

# 📋 Zakres prac (Infrastructure & Adapters)

## 3. Infrastructure (`server/infrastructure/di.py`)
- Zaktualizować `di.py`: Dodać `get_modeling_handler()`.

## 4. Adapters (`server/adapters/mcp/server.py`)
- Dodać nowe toole MCP (`@mcp.tool`):
  - `create_primitive`
  - `transform_object`
  - `add_modifier`
- Toole powinny pobierać handler przez `get_modeling_handler()`.

# 📋 Zakres prac (Blender Addon)

## 5. Addon Application (`blender_addon/application/handlers/modeling.py`)
- Klasa `ModelingHandler`.
- Metody:
  - `create_primitive`: Obsługa `bpy.ops.mesh.primitive_..._add`.
  - `transform_object`: Ustawianie `obj.location`, `obj.rotation_euler`, `obj.scale`.
  - `add_modifier`: `obj.modifiers.new(...)`.

## 6. Addon Infrastructure (`blender_addon/__init__.py`)
- Zarejestrować `ModelingHandler` i jego metody w `rpc_server`.

# ✅ Kryteria Akceptacji
- AI może stworzyć: Cube, Sphere, Cylinder, Plane.
- AI może przesunąć/obrócić/zeskalować obiekt.
- AI może dodać modyfikator (np. Bevel, Subdivision Surface).
- Wszystkie operacje przechodzą przez warstwy Clean Architecture.