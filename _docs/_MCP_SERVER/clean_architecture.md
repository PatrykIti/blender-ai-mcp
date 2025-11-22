# Clean Architecture w MCP Server

Projekt serwera MCP jest zorganizowany według zasad Czystej Architektury, aby odseparować logikę biznesową (narzędzia modelowania) od frameworków (MCP, Sockets).

## Warstwy (Layers)

### 1. Domain (`server/domain`)
**Jądro systemu.** Nie zależy od żadnych zewnętrznych bibliotek (poza standardowymi typami i Pydantic dla modeli). Definiuje **CO** system może robić, ale nie **JAK**.

- **Interfaces (`interfaces/`)**: Kontrakty dla zewnętrznych serwisów (np. `IRpcClient`).
- **Tools (`tools/`)**: Abstrakcyjne definicje narzędzi (np. `ISceneTool`).
- **Models (`models/`)**: Struktury danych (DTO), np. `RpcRequest`.

### 2. Application (`server/application`)
**Logika aplikacji (Use Cases).** Implementuje interfejsy z warstwy domeny. Zależy wyłącznie od Domeny.

- **Tool Handlers (`tool_handlers/`)**: Konkretne klasy (np. `SceneToolHandler`), które wiedzą jak użyć `IRpcClient` do realizacji zadania zdefiniowanego w `ISceneTool`.

### 3. Adapters (`server/adapters`)
**Adaptery do świata zewnętrznego.** Konwertują dane z formatów zewnętrznych na wewnętrzne i odwrotnie.

- **RPC (`rpc/`)**: Implementacja klienta socketowego (`RpcClient`), która spełnia interfejs `IRpcClient`.
- **MCP (`mcp/`)**: Warstwa wejściowa (Driver Adapter).
  - `server.py`: Definiuje narzędzia `@mcp.tool`. Pobiera handlery z warstwy Infrastructure i przekazuje do nich sterowanie. Wykorzystuje `fastmcp.Context` do logowania.

### 4. Infrastructure (`server/infrastructure`)
**Szczegóły techniczne i konfiguracja.**
- `di.py`: **Dependency Injection Providers**. Funkcje fabryczne (`get_scene_handler`), które tworzą graf zależności.
- Konfiguracja (zmienne środowiskowe).
- Logging.

## Przepływ Sterowania (Control Flow)
1. `main.py` -> woła `adapters.mcp.server.run()`.
2. `adapters.mcp.server` (Tool Function) -> woła `infrastructure.di.get_scene_handler()`.
3. `infrastructure.di` -> tworzy (lub zwraca istniejący) `RpcClient` i wstrzykuje go do nowego `SceneToolHandler`.
4. `adapters.mcp.server` -> woła `SceneToolHandler.list_objects()`.
5. `SceneToolHandler` -> woła `IRpcClient.send_request()`.
6. `RpcClient` -> wysyła JSON przez socket.