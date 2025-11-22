# 2. Implementacja Scene Tools (MVP)

**Data:** 2025-11-22  
**Wersja:** 0.1.1  
**Zadania:** TASK-003

## 🚀 Główne Zmiany

### MCP Server (Client Side)
- Zainicjalizowano główny plik serwera: `server/main.py`.
- Skonfigurowano instancję `FastMCP`.
- Zaimplementowano pierwsze narzędzia dostępne dla AI:
  - `list_objects()`: Zwraca listę obiektów na scenie (nazwa, typ, lokalizacja).
  - `delete_object(name)`: Usuwa obiekt o podanej nazwie.
  - `clean_scene()`: Czyści scenę z obiektów geometrycznych (Mesh, Curve, etc.), pozostawiając kamery i światła.

### Blender Addon (Server Side)
- Dodano moduł `blender_addon/api/scene.py` z implementacją logiki na poziomie `bpy`.
- Zarejestrowano nowe handlery RPC w `blender_addon/__init__.py`.
- Dodano zabezpieczenia przed usuwaniem nieistniejących obiektów (rzuca `ValueError` -> zwraca JSON error).

### Testing
- Dodano `tests/test_scene_tools.py`: Testy jednostkowe z pełnym mockowaniem `bpy.data` i `bpy.context`. Weryfikują logikę bez konieczności uruchamiania Blendera.
