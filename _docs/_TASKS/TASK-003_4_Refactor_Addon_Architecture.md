---
type: task
id: TASK-003_4_Refactor_Addon_Architecture
title: Refaktoryzacja Architektury Addona (Clean Architecture)
status: done
priority: high
assignee: unassigned
depends_on: TASK-003_3_Refactor_FastMCP_Dependency_Injection
---

# 🎯 Cel
Dostosowanie kodu `blender_addon/` do zasad **Clean Architecture**, analogicznie jak w `server/`.
Obecny kod miesza infrastrukturę sieciową (`rpc_server.py`) z logiką rejestracji (`__init__.py`) i logiką biznesową (bezpośrednio w `api/`).

# 📋 Analiza Stanu Obecnego
- `blender_addon/rpc_server.py`: Łączy logikę socketów z zarządzaniem wątkami i kolejkami `bpy`. To jest "Infrastructure".
- `blender_addon/api/`: Zawiera logikę, ale nie jest ona zorganizowana w warstwy (Domain/Application). To są po prostu funkcje.
- `blender_addon/__init__.py`: Rejestracja addona i "brzydkie" importy warunkowe.

# 🛠 Plan Przebudowy (Refactoring Plan)

## 1. Struktura Katalogów
Utworzyć nową strukturę wewnątrz `blender_addon/`:
```
blender_addon/
  domain/          # Interfejsy (jeśli potrzebne w Pythonie Blendera, tutaj raczej zbędne, wystarczy Application)
  application/     # Use Cases (logika biznesowa)
    handlers/      # np. scene.py
  infrastructure/  # RPC Server, Bpy Context Wrapper
  presentation/    # Rejestracja operatorów (jeśli będą) lub Handlery RPC
  __init__.py      # Entry Point
```

## 2. Refaktoryzacja `api/` -> `application/handlers/`
- Przenieść logikę z `api/scene.py` do `application/handlers/scene.py`.
- Zamienić wolne funkcje na klasy (np. `SceneHandler`), aby łatwiej zarządzać zależnościami (nawet jeśli `bpy` jest globalne, warto to opakować).

## 3. Refaktoryzacja `rpc_server.py` -> `infrastructure/rpc_server.py`
- Przenieść plik.
- Oddzielić logikę socketów od logiki dyspozytora (`command_registry`).
- Dyspozytor powinien być wstrzykiwany lub konfigurowany osobno.

## 4. Entry Point (`__init__.py`)
- Oczyścić `__init__.py`. Powinien tylko:
  1. Inicjalizować infrastrukturę (`RpcServer`).
  2. Rejestrować Handlery z warstwy Application w serwerze RPC.
  3. Startować serwer.

# ✅ Kryteria Akceptacji
1. Kod addona podzielony na warstwy (Infrastructure, Application).
2. `api/` znika (zastąpione przez `application/`).
3. `rpc_server.py` jest w `infrastructure/`.
4. Testy jednostkowe addona (mocki) nadal działają po aktualizacji ścieżek importów.
