# Clean Architecture w MCP Server

Projekt serwera MCP jest zorganizowany według zasad Czystej Architektury, aby odseparować logikę biznesową (narzędzia modelowania) od frameworków (MCP, Sockets).

## Warstwy

### 1. Domain (`server/domain`)
Jądro systemu. Nie zależy od żadnych zewnętrznych bibliotek (poza standardowymi typami).
- **Models**: Struktury danych (Pydantic) używane w systemie (np. `RpcRequest`).
- **Tools (Interfaces)**: Abstrakcyjne definicje narzędzi.

### 2. Application (`server/application`)
Logika aplikacji.
- **Tool Handlers**: Konkretne implementacje logiki, które "wiedzą", co zrobić z żądaniem (np. "Stwórz sześcian" -> "Przygotuj JSON RPC" -> "Wyślij").
- Nie zależy od HTTP/MCP, tylko od Domeny i Adapterów.

### 3. Adapters (`server/adapters`)
Adaptery do świata zewnętrznego.
- **RPC Client**: Implementacja klienta socketowego do Blendera.
- **MCP**: Konfiguracja serwera FastMCP.

### 4. Infrastructure (`server/infrastructure`)
Szczegóły techniczne.
- Konfiguracja (env vars).
- Logging.
