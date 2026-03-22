# TASK-098-02-01-02: Async Import MCP Entrypoints

**Parent:** [TASK-098-02-01](./TASK-098-02-01_Core_Import_Task_Mode_Adoption.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-098-02](./TASK-098-02_Import_Task_Mode_Adoption.md)

---

## Objective

Expose import tools as async task-capable MCP entrypoints on task-enabled surfaces.

---

## Repository Touchpoints

- `server/adapters/mcp/areas/system.py`
- `server/application/tool_handlers/system_handler.py`
- `server/adapters/mcp/tasks/task_bridge.py`

---

## Planned Work

- convert import MCP wrappers to `async def`
- attach explicit `TaskConfig(mode="optional")`
- reuse the shared background bridge and keep synchronous fallback behavior

### MCP Adapter Detail

- replace or extend the current generic `register_existing_tools(...)` path in `system.py` so import tools can carry explicit task config
- preserve current `route_tool_call(...)` behavior for foreground execution
- keep current parameter names and result strings stable on the non-task path

---

## Acceptance Criteria

- import entrypoints are task-capable on task-enabled surfaces
- no parallel bridge or import-specific task protocol is introduced
