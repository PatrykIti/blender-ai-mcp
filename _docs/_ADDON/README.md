# Blender Addon Documentation

Dokumentacja modułu Addona (Server Side).

## 📚 Indeks Tematyczny

- **[Architektura RPC i Wątkowość](./rpc_architecture.md)**
  - Wyjaśnienie modelu wielowątkowego.
  - Mechanizm `bpy.app.timers`.
  - Protokół JSON.

## 🛠 Struktura Plików
- `__init__.py`: Rejestracja Addona.
- `rpc_server.py`: Implementacja serwera socket.