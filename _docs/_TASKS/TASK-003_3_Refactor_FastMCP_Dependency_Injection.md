---
type: task
id: TASK-003_3_Refactor_FastMCP_Dependency_Injection
title: Implementacja DI w FastMCP (Depends)
status: done
priority: high
assignee: unassigned
depends_on: TASK-003_2_Refactor_Main_DI
---

# 🎯 Cel
Zastąpienie globalnego importu kontenera w `server/adapters/mcp/server.py` natywnym mechanizmem Dependency Injection oferowanym przez biblioteki MCP/FastMCP (wzorzec `Depends`).
Ma to na celu całkowite wyeliminowanie "Global State" (globalnej zmiennej `_container` i `container = get_container()`) z warstwy adapterów, co uczyni kod bardziej testowalnym i zgodnym z idiomatami FastMCP/FastAPI.

# 📋 Analiza Obecnego Stanu
- **Problem:** W `server/adapters/mcp/server.py` mamy linię `from server.infrastructure.container import get_container` oraz `container = get_container()`. To jest wzorzec "Service Locator" w najprostszej postaci (Global Variable).
- **Cel:** Funkcje `@mcp.tool` powinny przyjmować zależności jako argumenty, np. `list_objects(handler: SceneToolHandler = Depends(get_scene_handler))`.

# 🛠 Plan Prac

## 1. Infrastructure Layer (`server/infrastructure/di.py`)
- Przemianować `container.py` na `di.py` (opcjonalnie, dla klarowności).
- Zdefiniować funkcje-fabryki ("Providers"), które będą używane przez system DI:
  - `get_rpc_client() -> IRpcClient`
  - `get_scene_handler(rpc: IRpcClient = Depends(get_rpc_client)) -> ISceneTool`
- Usunąć globalną instancję `_container` (lub zostawić tylko jako cache dla Singletonów).

## 2. Adapters Layer (`server/adapters/mcp/server.py`)
- Usunąć `container = get_container()`.
- Zaktualizować sygnatury funkcji `@mcp.tool`:
  - Zamiast odwoływać się do `container.scene_handler`, dodać parametr: `handler: ISceneTool` (wstrzyknięty przez kontekst/zależność).
- **Weryfikacja techniczna:** Sprawdzić, czy zainstalowana wersja `fastmcp` wspiera `Depends`. Jeśli nie wprost, użyć `Context` do przekazywania stanu aplikacji (Context Injection).
  - *Fallback Plan:* Jeśli `fastmcp` nie ma `Depends` (bo to nowość w `mcp` SDK), użyjemy `Context` i zainicjalizujemy go w `lifespan`.

## 3. Entry Point (`server/main.py`)
- Upewnić się, że `mcp.run()` poprawnie inicjalizuje kontekst aplikacji (jeśli wymagane przez framework).

# ✅ Kryteria Akceptacji
1. Brak globalnej zmiennej `container` w `server/adapters/mcp/server.py`.
2. Narzędzia MCP otrzymują `SceneToolHandler` poprzez wstrzykiwanie (argument funkcji).
3. Kod jest zgodny z dokumentacją/praktykami FastMCP.
4. Testy nadal przechodzą.