# TASK-083-05: Context, Session, and Execution Bridge

**Parent:** [TASK-083](./TASK-083_FastMCP_3x_Platform_Migration.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-03](./TASK-083-03_Server_Factory_and_Composition_Root.md)

---

## Objective

Normalize how adapter tools use `Context`, session state, and execution metadata so the repo is ready for visibility, elicitation, prompts, and background tasks.

## Current State

The baseline bridge primitives are implemented: session helpers, execution context, execution report, and sync-compatible context utilities all exist and are covered by tests.

This task is now closed. The downstream interaction tasks that originally blocked broader validation are complete, and the bridge now has real elicitation, task-mode, and diagnostics coverage.

---

## Repository Touchpoints

- `server/adapters/mcp/context_utils.py`
- `server/adapters/mcp/router_helper.py`
- `server/router/adapters/mcp_integration.py`
- `server/router/application/router.py`
- `server/application/tool_handlers/router_handler.py`
- `tests/unit/router/adapters/test_mcp_integration.py`

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

## Pseudocode

```python
async def get_session_phase(ctx: Context) -> str:
    return await ctx.get_state("phase") or "bootstrap"


async def set_session_phase(ctx: Context, phase: str) -> None:
    await ctx.set_state("phase", phase)


def build_execution_report(tool_name, params, router_result, raw_result):
    return {
        "tool_name": tool_name,
        "params": params,
        "router": router_result,
        "result": raw_result,
    }
```

### Migration Rule

Do not convert the entire repo to async in one step.
Convert the interaction-heavy entry points first:

- router entry tools
- workflow catalog entry tools
- prompt and task-capable entry tools

Legacy sync wrappers may remain temporarily for compatibility.

---

## Tests

- session state helpers
- structured execution report generation
- backward-compatibility coverage for sync wrappers

---

## Atomic Work Items

1. Add session helpers around `ctx.get_state()` / `ctx.set_state()`.
2. Add execution context and report objects that adapters can reuse.
3. Convert the highest-value interaction entry points to async-aware context usage.
4. Preserve sync compatibility for the flat legacy surface.

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-083-05-01](./TASK-083-05-01_Core_Context_Session_Execution_Bridge.md) | Core Context, Session, and Execution Bridge | Core implementation layer |
| [TASK-083-05-02](./TASK-083-05-02_Tests_Context_Session_Execution_Bridge.md) | Tests and Docs Context, Session, and Execution Bridge | Tests, docs, and QA |

---

## Acceptance Criteria

- adapter tools have a consistent session and execution bridge
- later platform features do not need to introduce ad hoc `ctx.*` helper patterns
