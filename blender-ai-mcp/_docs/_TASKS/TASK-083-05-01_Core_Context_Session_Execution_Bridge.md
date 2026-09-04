# TASK-083-05-01: Core Context, Session, and Execution Bridge

**Parent:** [TASK-083-05](./TASK-083-05_Context_Session_and_Execution_Bridge.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-03](./TASK-083-03_Server_Factory_and_Composition_Root.md)

---

## Objective

Implement the core code changes for **Context, Session, and Execution Bridge**.

---

## Repository Touchpoints

- `server/adapters/mcp/context_utils.py`
- `server/adapters/mcp/router_helper.py`
- `server/router/adapters/mcp_integration.py`
- `server/router/application/router.py`
- `server/application/tool_handlers/router_handler.py`

---

## Planned Work

### Existing Files To Update

- `server/adapters/mcp/context_utils.py`
  - add helpers for session read/write, progress, and elicitation handoff
  - stop treating `ctx.info()` bridging as the only shared context utility
- `server/adapters/mcp/router_helper.py`
  - separate execution reporting from plain text concatenation
- `server/router/adapters/mcp_integration.py`
  - align executor wrapping with the new execution contract

### New Files To Create

- `server/adapters/mcp/session_state.py`
- `server/adapters/mcp/execution_context.py`
- `server/adapters/mcp/execution_report.py`
- `tests/unit/adapters/mcp/test_context_bridge.py`
---

## Acceptance Criteria

- adapter tools have a consistent session and execution bridge
- later platform features do not need to introduce ad hoc `ctx.*` helper patterns
---

## Atomic Work Items

1. Add session helpers around `ctx.get_state()` / `ctx.set_state()`.
2. Add execution context and report objects that adapters can reuse.
3. Convert the highest-value interaction entry points to async-aware context usage.
4. Preserve sync compatibility for the flat legacy surface.
