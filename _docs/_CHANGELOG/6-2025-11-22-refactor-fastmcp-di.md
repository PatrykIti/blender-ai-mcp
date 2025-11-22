# 6. Refaktoryzacja FastMCP DI

**Data:** 2025-11-22  
**Wersja:** 0.1.5  
**Zadania:** TASK-003_3_Refactor_FastMCP_Dependency_Injection

## 🚀 Główne Zmiany

### Infrastructure Layer (`server/infrastructure/`)
- Zastąpiono `container.py` (Global State) przez `di.py` (Providers).
- Zaimplementowano funkcje fabryczne (`get_rpc_client`, `get_scene_handler`) zgodne ze wzorcem Singleton (cache modułu).

### Adapters Layer (`server/adapters/mcp/`)
- Usunięto globalny import kontenera w `server.py`.
- Narzędzia MCP teraz explicite pobierają swoje zależności (handlery) używając providerów z `di.py`.
- Dodano obsługę wstrzykiwania `Context` (z `fastmcp`) do narzędzi, co umożliwia strukturalne logowanie (`ctx.info`, `ctx.error`).

Ta zmiana eliminuje "magiczną" globalną zmienną kontenera w warstwie adapterów i przygotowuje grunt pod bardziej zaawansowane DI w przyszłości (np. `Depends` w FastMCP).
