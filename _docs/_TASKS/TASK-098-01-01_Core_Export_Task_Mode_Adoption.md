# TASK-098-01-01: Core Export Task Mode Adoption

**Parent:** [TASK-098-01](./TASK-098-01_Export_Task_Mode_Adoption.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-098-01](./TASK-098-01_Export_Task_Mode_Adoption.md)

---

## Objective

Implement the core code changes required to run export tools through the existing background task model.

---

## Repository Touchpoints

- `server/adapters/mcp/areas/system.py`
- `server/application/tool_handlers/system_handler.py`
- `blender_addon/application/handlers/system.py`
- `blender_addon/__init__.py`

---

## Planned Work

- convert export MCP entrypoints to explicit async task-capable adapters
- attach export handlers to addon-side background job registration
- preserve the foreground fallback path for compatibility surfaces

### Current Code Reality

- MCP registration currently uses the generic `register_existing_tools(...)` path in `system.py`
- server handlers are thin and sync-only today and only call foreground `rpc.send_request(...)`
- addon export handlers are synchronous one-shot operations with no progress/cancel hooks

The core export slice therefore has to touch all three seams, not only the MCP wrapper.

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-098-01-01-01](./TASK-098-01-01-01_Addon_Export_Job_Adoption.md) | Addon Export Job Adoption | Addon/background job slice |
| [TASK-098-01-01-02](./TASK-098-01-01-02_Async_Export_MCP_Entrypoints.md) | Async Export MCP Entrypoints | MCP adapter / handler slice |

---

## Acceptance Criteria

- exports use the shared RPC launch/poll/cancel/collect model
- exports are exposed as async task-capable MCP entrypoints
