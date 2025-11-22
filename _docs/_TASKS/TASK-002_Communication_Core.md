---
type: task
id: TASK-002
title: Implementacja Mostu Komunikacyjnego (RPC)
status: todo
priority: high
assignee: unassigned
depends_on: TASK-001
---

# 🎯 Cel
Zbudowanie dwukierunkowej komunikacji między MCP Serverem a Addonem w Blenderze 5.0.0 przy użyciu gniazd (Sockets) i protokołu JSON-RPC.

# 📋 Zakres prac

1. **Specyfikacja Protokołu**
   - Zdefiniować format wiadomości JSON (Request/Response) w `server/domain/models/rpc.py`.
   - Obsługa `request_id`, `cmd`, `args`, `status`, `error`.

2. **Blender Addon: Socket Server**
   - Implementacja serwera nasłuchującego na `localhost:8765` w `blender_addon/rpc_server.py`.
   - **Ważne:** Serwer musi działać w osobnym wątku (`threading`), ale wywołania API Blendera (`bpy`) muszą być delegowane do głównego wątku przy użyciu `bpy.app.timers` (thread-safety).
   - Sprawdzenie kompatybilności z Python API w Blender 5.0.

3. **MCP Server: Socket Client**
   - Implementacja klienta w `server/adapters/rpc/client.py`.
   - Obsługa timeoutów i błędów połączenia (reconnect).

4. **Test "Ping-Pong"**
   - Prosty test: MCP wysyła "ping", Blender odpowiada "pong" z wersją Blendera.

# ✅ Kryteria Akceptacji
- MCP Server potrafi połączyć się z działającym Blenderem.
- Wiadomość JSON wysłana z MCP jest odbierana w Addonie.
- Addon potrafi odesłać odpowiedź JSON.
- Rozwiązanie nie blokuje interfejsu Blendera (nie zawiesza UI).
