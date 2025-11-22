# 1. Inicjalizacja Projektu i Core RPC

**Data:** 2025-11-22  
**Wersja:** 0.1.0  
**Zadania:** TASK-001, TASK-002

## 🚀 Główne Zmiany

### Core & Struktura
- Zainicjalizowano projekt przy użyciu **Poetry**.
- Utworzono strukturę katalogów zgodną z **Clean Architecture** (`domain`, `application`, `adapters`, `infrastructure`).
- Skonfigurowano `.gitignore` i środowisko developerskie.

### Blender Addon (Server Side)
- Zaimplementowano **Serwer RPC** (`blender_addon/rpc_server.py`) działający na gniazdach TCP (domyślnie port 8765).
- Zastosowano model wielowątkowy (`threading`) dla obsługi sieci.
- Zabezpieczono wywołania API Blendera (`bpy`) przy użyciu `bpy.app.timers`, co gwarantuje bezpieczeństwo wątków (Thread Safety).
- Dodano obsługę trybu "Mock" (uruchamianie poza Blenderem).

### MCP Server (Client Side)
- Zaimplementowano **Klienta RPC** (`server/adapters/rpc/client.py`).
- Zdefiniowano modele komunikacyjne **Pydantic** (`RpcRequest`, `RpcResponse`).
- Dodano mechanizmy automatycznego wznawiania połączenia (reconnect) i obsługi timeoutów.

### Testing
- Utworzono test integracyjny `tests/test_rpc_connection.py` weryfikujący komunikację "Ping-Pong".
