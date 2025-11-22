# 🧠 MCP Server Documentation

## 📌 Przegląd
MCP Server to "mózg" systemu, który pośredniczy między modelem AI (np. Claude) a Blenderem. Jest to aplikacja Pythonowa wykorzystująca standard Model Context Protocol (MCP).

## 🏗 Struktura
Kod źródłowy znajduje się w katalogu `server/`.

### Warstwy (Clean Architecture)
- **Domain (`server/domain/`)**:
  - `models/rpc.py`: Definicje Pydantic dla protokołu komunikacyjnego.
  - `tools/`: Interfejsy narzędzi (Abstract Base Classes).
- **Application (`server/application/`)**:
  - `tool_handlers/`: Konkretne implementacje logiki narzędzi.
- **Adapters (`server/adapters/`)**:
  - `rpc/client.py`: Klient TCP Socket do komunikacji z Blenderem.
  - `mcp/`: Konfiguracja FastMCP i rejestracja narzędzi.
- **Infrastructure (`server/infrastructure/`)**:
  - Konfiguracja, logowanie, zmienne środowiskowe.

## 🚀 Uruchomienie (Development)
Wymaga zainstalowanego `poetry`.

```bash
poetry install
poetry run python server/main.py  # (Gdy zostanie utworzony main.py)
```

## 🔌 Klient RPC
Plik `server/adapters/rpc/client.py` zawiera klasę `RpcClient`.
- Obsługuje automatyczne wznawianie połączenia (reconnect).
- Serializuje obiekty Pydantic do JSON.
- Obsługuje timeouty.

## 🛠 Dostępne Narzędzia (Tools)
*(Lista będzie uzupełniana w miarę realizacji TASK-003 i TASK-004)*
