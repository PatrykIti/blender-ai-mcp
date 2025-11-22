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
- **MCP (`mcp/` / `main.py`)**: Warstwa wejściowa. Odbiera żądania od LLM (przez FastMCP), przekazuje je do Handlera Aplikacji i zwraca wynik jako string.

### 4. Infrastructure (`server/infrastructure`)
**Szczegóły techniczne.**
- Konfiguracja (zmienne środowiskowe).
- Logging.

## Zasada Zależności (Dependency Rule)
Zależności w kodzie źródłowym mogą wskazywać **tylko do wewnątrz**.
- `Adapters` -> `Application` -> `Domain`
- `Infrastructure` -> `Adapters`

Przykład: `SceneToolHandler` (Application) zależy od `IRpcClient` (Domain). `RpcClient` (Adapters) implementuje `IRpcClient`. Dzięki temu logika aplikacji nie zależy od socketów.