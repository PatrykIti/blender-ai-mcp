# 7. Refaktoryzacja Architektury Addona

**Data:** 2025-11-22  
**Wersja:** 0.1.6  
**Zadania:** TASK-003_4_Refactor_Addon_Architecture

## 🚀 Główne Zmiany

### Blender Addon Architecture
Przebudowano strukturę katalogów addona, aby pasowała do Clean Architecture:

- **Application (`blender_addon/application/handlers/`)**
  - `scene.py`: Zawiera klasę `SceneHandler` (Application Logic). Przejęła ona kod z dawnego `api/`.

- **Infrastructure (`blender_addon/infrastructure/`)**
  - `rpc_server.py`: Przeniesiono tutaj kod serwera socketowego (był w głównym katalogu).

- **Entry Point (`blender_addon/__init__.py`)**
  - Teraz działa jako Composition Root. Tworzy instancję `SceneHandler`, inicjalizuje `rpc_server` i rejestruje handlery.

### Struktura Plików
- Usunięto katalog `blender_addon/api/`.
- Testy zaktualizowano do nowych ścieżek.

Zmiana ta ujednolica architekturę między Serwerem (Client) a Addonem (Server). Oba komponenty są teraz warstwowe i testowalne.
