# TASK-098-02-01: Core Import Task Mode Adoption

**Parent:** [TASK-098-02](./TASK-098-02_Import_Task_Mode_Adoption.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-098-02](./TASK-098-02_Import_Task_Mode_Adoption.md)

---

## Objective

Implement the core code changes required to run import tools through the shared background task model.

---

## Repository Touchpoints

- `server/adapters/mcp/areas/system.py`
- `server/application/tool_handlers/system_handler.py`
- `blender_addon/application/handlers/system.py`
- `blender_addon/__init__.py`

---

## Planned Work

- convert import MCP entrypoints to explicit async task-capable adapters
- attach import handlers to addon-side background job registration
- preserve the foreground fallback path for compatibility surfaces

### Current Code Reality

- MCP registration is currently generic and sync-only
- server handlers are thin and sync-only today
- addon import handlers already expose a natural staged flow:
  - validate file path
  - capture pre-import object set
  - run Blender importer
  - compute imported object delta

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-098-02-01-01](./TASK-098-02-01-01_Addon_Import_Job_Adoption.md) | Addon Import Job Adoption | Addon/background job slice |
| [TASK-098-02-01-02](./TASK-098-02-01-02_Async_Import_MCP_Entrypoints.md) | Async Import MCP Entrypoints | MCP adapter / handler slice |

---

## Acceptance Criteria

- imports use the shared RPC launch/poll/cancel/collect model
- imports are exposed as async task-capable MCP entrypoints
