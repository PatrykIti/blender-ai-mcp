---
type: task
id: TASK-003_2_Refactor_Main_DI
title: Main and DI Refactor (Separation of Concerns)
status: done
priority: high
assignee: unassigned
depends_on: TASK-003_1_Refactor_Architecture
---

# 🎯 Objective
Further refactor server to remove configuration logic and adapters from `server/main.py`.
Extract Dependency Injection container and MCP tool definitions to appropriate layers.

# 📋 Analysis
Currently `server/main.py` does three things:
1. Creates object instances (`RpcClient`, `SceneToolHandler`).
2. Defines MCP input adapters (`@mcp.tool`).
3. Starts the server.

# 🛠 Work Plan

1. **Infrastructure Layer (`server/infrastructure/`)**
   - Create `server/infrastructure/container.py`: `Container` class (or simple function) that creates and wires dependencies.

2. **Adapters Layer (`server/adapters/mcp/`)**
   - Create `server/adapters/mcp/server.py`:
     - Move `FastMCP` instance here.
     - Define `@mcp.tool` functions here.
     - Functions use handlers provided by DI container.

3. **Entry Point (`server/main.py`)**
   - Clean up file.
   - Should only import `server` from adapters and call `run()`.

# ✅ Target Structure

```
server/
  infrastructure/
    container.py       # DI Container
  adapters/
    mcp/
      server.py        # FastMCP tools definition
  main.py              # Entry point
```

# ✅ Acceptance Criteria
- `main.py` has minimal code.
- No object construction logic in `main.py`.
- MCP tools defined in `adapters/mcp/`.
- Application works as before.
