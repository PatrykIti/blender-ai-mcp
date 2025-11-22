# 📜 Changelog

Wszystkie istotne zmiany w projekcie będą dokumentowane w tym pliku.

## [Unreleased]

### Planowane
- Implementacja `Scene Tools` (TASK-003).
- Implementacja `Modeling Tools` (TASK-004).

## [0.1.0] - 2025-11-22
### Dodane
- **Core**: Zainicjalizowano projekt przy użyciu `poetry`.
- **Core**: Utworzono strukturę katalogów Clean Architecture.
- **Addon**: Zaimplementowano wielowątkowy serwer RPC (`blender_addon/rpc_server.py`) z bezpieczną integracją z pętlą wydarzeń Blendera (`bpy.app.timers`).
- **Server**: Zaimplementowano klienta RPC (`server/adapters/rpc/client.py`) z obsługą błędów i Pydantic.
- **Docs**: Utworzono dokumentację techniczną w `_docs/` oraz system zadań Kanban.
- **Tests**: Dodano test integracyjny `tests/test_rpc_connection.py` (Ping-Pong).

### Zmienione
- Zaktualizowano `README.md` o instrukcje instalacji oparte o Poetry.
