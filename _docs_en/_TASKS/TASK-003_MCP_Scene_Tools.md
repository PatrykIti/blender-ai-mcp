---
type: task
id: TASK-003_MCP_Scene_Tools
title: MVP MCP Server and Scene Tools
status: done
priority: medium
assignee: unassigned
depends_on: TASK-002
---

# 🎯 Objective
Launch MCP Server and implement the first group of tools (Scene Tools) allowing object management.

# 📋 Scope of Work

1. **FastMCP Initialization**
   - Create server instance in `server/main.py`.

2. **Handler Implementation (Scene)**
   - `scene.list_objects()`: Return list of objects.
   - `scene.delete_object(name)`: Delete object.
   - `scene.clean_scene()`: Delete everything.

3. **MCP Registration**
   - Tag functions with `@mcp.tool`.
   - Connect handlers to RPC client.

4. **Error Handling**
   - Return readable JSON errors.

# ✅ Acceptance Criteria
- Can connect MCP Server to client (Claude Desktop / CLI).
- `scene.list_objects` returns valid JSON.
- AI can clear the scene.
