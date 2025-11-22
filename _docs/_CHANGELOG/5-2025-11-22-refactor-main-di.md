# 5. Refaktoryzacja Main i DI

**Data:** 2025-11-22  
**Wersja:** 0.1.4  
**Zadania:** TASK-003_2_Refactor_Main_DI

## 🚀 Główne Zmiany

### Infrastructure (Dependency Injection)
- Dodano `server/infrastructure/container.py`: Kontener DI, który buduje graf zależności (tworzy `RpcClient` i wstrzykuje go do `SceneToolHandler`).

### Adapters (MCP)
- Przeniesiono definicje narzędzi MCP do `server/adapters/mcp/server.py`. Narzędzia korzystają teraz z instancji handlerów dostarczanych przez kontener DI.

### Entry Point
- Plik `server/main.py` został maksymalnie uproszczony. Służy teraz tylko do uruchomienia serwera zdefiniowanego w adapterach.

Ta zmiana kończy proces dostosowywania kodu do **Clean Architecture**. Architektura jest teraz w pełni modularna i gotowa na dodawanie nowych narzędzi (TASK-004).
