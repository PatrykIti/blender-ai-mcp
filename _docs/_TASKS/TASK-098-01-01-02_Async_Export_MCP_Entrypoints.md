# TASK-098-01-01-02: Async Export MCP Entrypoints

**Parent:** [TASK-098-01-01](./TASK-098-01-01_Core_Export_Task_Mode_Adoption.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-098-01](./TASK-098-01_Export_Task_Mode_Adoption.md)

---

## Objective

Expose export tools as async task-capable MCP entrypoints on task-enabled surfaces.

---

## Repository Touchpoints

- `server/adapters/mcp/areas/system.py`
- `server/application/tool_handlers/system_handler.py`
- `server/adapters/mcp/tasks/task_bridge.py`

---

## Planned Work

- convert export MCP wrappers to `async def`
- attach explicit `TaskConfig(mode="optional")`
- reuse the shared background bridge and keep synchronous fallback behavior

### MCP Adapter Detail

- replace or extend the current generic `register_existing_tools(...)` path in `system.py` so export tools can carry explicit task config
- preserve current `route_tool_call(...)` behavior for foreground execution
- use the TASK-088 bridge only for task-mode execution, not for all calls

---

## Acceptance Criteria

- export entrypoints are task-capable on task-enabled surfaces
- no parallel bridge or export-specific task protocol is introduced
