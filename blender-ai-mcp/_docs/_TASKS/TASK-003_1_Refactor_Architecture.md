---
type: task
id: TASK-003_1_Refactor_Architecture
title: Server Architecture Refactor (Clean Architecture)
status: done
priority: high
assignee: unassigned
depends_on: TASK-003
---

# 🎯 Objective
Rebuild existing `server/` code to strictly adhere to **Clean Architecture** principles defined in `GEMINI.md`.
Current code in `main.py` mixes layers (Adapters, Application, Domain) in one file, which is unacceptable.

# 📋 Current State Analysis
- **Domain**: Empty `server/domain/tools/`. No interfaces.
- **Application**: Missing layer. Business logic is in `main.py`.
- **Adapters**:
  - `server/adapters/rpc/client.py`: OK, output adapter.
  - `server/main.py`: Acts as input adapter (MCP) but contains application logic.

# 🛠 Refactoring Plan

## 1. Domain Layer (`server/domain/`)
Pure layer, no framework dependencies.
- **Create `server/domain/tools/scene.py`**:
  - Define abstract interface `ISceneTool(ABC)`.
  - Methods: `list_objects`, `delete_object`, `clean_scene`.

## 2. Application Layer (`server/application/`)
Use-cases layer. Implements domain interfaces using injected dependencies.
- **Create `server/application/tool_handlers/scene_handler.py`**:
  - Class `SceneToolHandler` implementing `ISceneTool`.
  - Constructor takes RPC client interface (define `IRpcClient` in domain to invert dependency!).

## 3. Domain Layer (Update)
- **Add `server/domain/interfaces/rpc.py`**:
  - Interface `IRpcClient`.

## 4. Adapters Layer (Refactor)
- **Update `server/adapters/rpc/client.py`**:
  - `RpcClient` must implement `IRpcClient`.
- **Refactor `server/main.py`**:
  - Remove business logic from `@mcp.tool`.
  - In `main`:
    1. Create `RpcClient`.
    2. Create `SceneToolHandler` (injecting RPC client).
    3. In `@mcp.tool` functions call only `SceneToolHandler` methods.

# ✅ Target Structure

```
server/
  domain/
    interfaces/
      rpc.py          # class IRpcClient(ABC)
    tools/
      scene.py        # class ISceneTool(ABC)
  application/
    tool_handlers/
      scene_handler.py # class SceneToolHandler(ISceneTool)
  adapters/
    rpc/
      client.py       # class RpcClient(IRpcClient)
  main.py             # Entry point & DI
```

# ✅ Acceptance Criteria
1. No direct `RpcClient` calls in MCP functions.
2. All tools defined as interfaces in `domain`.
3. Logic is in `application`.
4. Tests pass.
