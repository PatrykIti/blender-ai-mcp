---
type: task
id: TASK-002
title: Communication Bridge Implementation (RPC)
status: done
priority: high
assignee: unassigned
depends_on: TASK-001
---

# 🎯 Objective
Build two-way communication between MCP Server and Blender Addon in Blender 5.0.0 using Sockets and JSON-RPC protocol.

# 📋 Scope of Work

1. **Protocol Specification**
   - Define JSON message format (Request/Response) in `server/domain/models/rpc.py`.
   - Handle `request_id`, `cmd`, `args`, `status`, `error`.

2. **Blender Addon: Socket Server**
   - Implement server listening on `localhost:8765` in `blender_addon/rpc_server.py`.
   - **Important:** Server must run in a separate thread (`threading`), but Blender API calls (`bpy`) must be delegated to the main thread using `bpy.app.timers` (thread-safety).
   - Check compatibility with Python API in Blender 5.0.

3. **MCP Server: Socket Client**
   - Implement client in `server/adapters/rpc/client.py`.
   - Handle timeouts and connection errors (reconnect).

4. **"Ping-Pong" Test**
   - Simple test: MCP sends "ping", Blender responds "pong" with Blender version.

# ✅ Acceptance Criteria
- MCP Server can connect to running Blender.
- JSON message sent from MCP is received in Addon.
- Addon can send back JSON response.
- Solution does not block Blender interface (UI does not freeze).
