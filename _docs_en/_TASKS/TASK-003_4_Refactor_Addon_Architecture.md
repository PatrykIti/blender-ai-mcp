---
type: task
id: TASK-003_4_Refactor_Addon_Architecture
title: Addon Architecture Refactor (Clean Architecture)
status: done
priority: high
assignee: unassigned
depends_on: TASK-003_3_Refactor_FastMCP_Dependency_Injection
---

# 🎯 Objective
Adapt `blender_addon/` code to **Clean Architecture** principles, similar to `server/`.
Current code mixes network infrastructure (`rpc_server.py`) with registration logic (`__init__.py`) and business logic (`api/`).

# 📋 Current State Analysis
- `blender_addon/rpc_server.py`: Infrastructure (Sockets).
- `blender_addon/api/`: Logic (not layered).
- `blender_addon/__init__.py`: Registration.

# 🛠 Refactoring Plan

## 1. Directory Structure
```
blender_addon/
  application/     # Use Cases
    handlers/      # e.g. scene.py
  infrastructure/  # RPC Server
  __init__.py      # Entry Point
```

## 2. Refactor `api/` -> `application/handlers/`
- Move logic from `api/scene.py` to `application/handlers/scene.py`.
- Convert functions to classes (e.g. `SceneHandler`).

## 3. Refactor `rpc_server.py` -> `infrastructure/rpc_server.py`
- Move file.

## 4. Entry Point (`__init__.py`)
- Clean up `__init__.py`. Should only:
  1. Initialize infrastructure (`RpcServer`).
  2. Register Handlers.
  3. Start server.

# ✅ Acceptance Criteria
1. Addon code divided into layers (Infrastructure, Application).
2. `api/` directory removed.
3. `rpc_server.py` in `infrastructure/`.
4. Unit tests pass.
