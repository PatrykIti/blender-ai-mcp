---
type: task
id: TASK-003_3_Refactor_FastMCP_Dependency_Injection
title: FastMCP DI Implementation (Depends)
status: done
priority: high
assignee: unassigned
depends_on: TASK-003_2_Refactor_Main_DI
---

# 🎯 Objective
Replace global container import in `server/adapters/mcp/server.py` with Dependency Injection mechanism offered by MCP/FastMCP libraries (or Context Injection).
Goal: Eliminate "Global State" (`container = get_container()`) from adapters layer.

# 📋 Current State Analysis
- **Problem:** `server/adapters/mcp/server.py` imports global container. This is "Service Locator" pattern.
- **Goal:** MCP tools should receive dependencies.

# 🛠 Work Plan

## 1. Infrastructure Layer (`server/infrastructure/di.py`)
- Rename `container.py` to `di.py`.
- Define Factory Functions ("Providers"):
  - `get_rpc_client() -> IRpcClient`
  - `get_scene_handler() -> ISceneTool`

## 2. Adapters Layer (`server/adapters/mcp/server.py`)
- Remove `container = get_container()`.
- Update `@mcp.tool` signatures to retrieve handler via `get_scene_handler()`.
- Add `Context` injection for logging.

## 3. Entry Point (`server/main.py`)
- Ensure `mcp.run()` works correctly.

# ✅ Acceptance Criteria
1. No global `container` variable in `server/adapters/mcp/server.py`.
2. MCP Tools retrieve `SceneToolHandler` via providers.
3. Code follows FastMCP best practices.
4. Tests pass.
