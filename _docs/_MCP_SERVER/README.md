# MCP Server Documentation

Dokumentacja serwera MCP (Client Side).

## 📚 Indeks Tematyczny

- **[Clean Architecture](./clean_architecture.md)**
  - Opis warstw: Domain, Application, Adapters, Infrastructure.
  - Zasady separacji zależności.

## 🛠 Kluczowe Komponenty
- `RpcClient` (`server/adapters/rpc/client.py`): Odpowiada za niskopoziomową komunikację z Blenderem.
- `FastMCP` (planowane w `main.py`): Wystawia narzędzia dla modelu AI.