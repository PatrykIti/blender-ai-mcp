---
type: task
id: TASK-003_1_Refactor_Architecture
title: Refaktoryzacja Architektury Servera (Clean Architecture)
status: done
priority: high
assignee: unassigned
depends_on: TASK-003
---

# 🎯 Cel
Przebudowa istniejącego kodu `server/` w celu ścisłego dostosowania do zasad **Clean Architecture** zdefiniowanych w `GEMINI.md`.
Obecny kod w `main.py` miesza warstwy (Adaptery, Aplikacja, Domena) w jednym pliku, co jest niedopuszczalne.

# 📋 Analiza Stanu Obecnego
- **Domain**: Puste `server/domain/tools/`. Brak interfejsów.
- **Application**: Brak warstwy. Logika biznesowa ("co zrobić z wynikiem RPC") siedzi w `main.py`.
- **Adapters**:
  - `server/adapters/rpc/client.py`: OK, to jest adapter wyjściowy.
  - `server/main.py`: Pełni rolę adaptera wejściowego (MCP), ale zawiera też logikę aplikacji.

# 🛠 Plan Przebudowy (Refactoring Plan)

## 1. Domain Layer (`server/domain/`)
Warstwa czysta, bez zależności od frameworków.
- **Utworzyć `server/domain/tools/scene.py`**:
  - Zdefiniować interfejs abstrakcyjny `ISceneTool` (dziedziczący po `ABC`).
  - Metody: `list_objects`, `delete_object`, `clean_scene`.
  - Używać modeli Pydantic z `server/domain/models` jeśli potrzebne, lub typów prostych.

## 2. Application Layer (`server/application/`)
Warstwa use-cases. Implementuje interfejsy domenowe, używając wstrzykniętych zależności.
- **Utworzyć `server/application/tool_handlers/scene_handler.py`**:
  - Klasa `SceneToolHandler` implementująca `ISceneTool`.
  - Konstruktor powinien przyjmować interfejs klienta RPC (należy zdefiniować `IRpcClient` w domenie, aby odwrócić zależność!).
  - Implementacja metod: wywołanie `rpc_client.send(...)` i wstępne przetworzenie odpowiedzi (np. rzucenie wyjątkiem domenowym w razie błędu).

## 3. Domain Layer (Update)
- **Dodać `server/domain/interfaces/rpc.py`**:
  - Interfejs `IRpcClient` z metodą `send_request`. To pozwoli uniezależnić warstwę aplikacji od konkretnej implementacji socketów.

## 4. Adapters Layer (Refactor)
- **Zaktualizować `server/adapters/rpc/client.py`**:
  - Klasa `RpcClient` musi implementować `IRpcClient`.
- **Przebudować `server/main.py` (lub przenieść do `server/adapters/mcp/server.py`)**:
  - Usunąć logikę biznesową z dekoratorów `@mcp.tool`.
  - W `main` (Composition Root):
    1. Utworzyć instancję `RpcClient`.
    2. Utworzyć instancję `SceneToolHandler` (wstrzykując klienta RPC).
    3. W funkcjach `@mcp.tool` wywoływać tylko metody `SceneToolHandler`.
    4. Obsługiwać błędy domenowe i zamieniać je na komunikaty dla AI.

# ✅ Struktura Docelowa

```
server/
  domain/
    interfaces/
      rpc.py          # class IRpcClient(ABC)
    tools/
      scene.py        # class ISceneTool(ABC)
    models/
      rpc.py          # RpcRequest, RpcResponse
  
  application/
    tool_handlers/
      scene_handler.py # class SceneToolHandler(ISceneTool)
  
  adapters/
    rpc/
      client.py       # class RpcClient(IRpcClient)
    mcp/
      registry.py     # Rejestracja tooli w FastMCP (delegacja do handlerów)
  
  main.py             # Entry point & Dependency Injection
```

# ✅ Kryteria Akceptacji
1. Brak bezpośrednich wywołań `RpcClient` w funkcjach MCP.
2. Wszystkie narzędzia zdefiniowane są jako interfejsy w `domain`.
3. Logika jest w `application`.
4. Kod działa identycznie jak przed refaktoryzacją (Testy przechodzą).
