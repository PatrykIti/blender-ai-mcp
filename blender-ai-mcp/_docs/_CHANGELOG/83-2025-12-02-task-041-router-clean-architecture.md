# Changelog 83: Router Clean Architecture & YAML Integration (Phase -1, P0)

**Date:** 2025-12-02
**Task:** [TASK-041](../_TASKS/TASK-041_Router_YAML_Workflow_Integration.md)
**Type:** Feature / Refactoring

---

## Summary

Implemented Phase -1 (Intent Source) and P0 (Connect YAML) of TASK-041. Added Clean Architecture pattern to router tools, following the same structure as other tool handlers.

---

## Changes

### 1. Router MCP Tools (TASK-041-0)

Created new MCP tools for router control:

| Tool | Purpose |
|------|---------|
| `router_set_goal` | Set modeling goal before starting work |
| `router_get_status` | Get router status and statistics |
| `router_clear_goal` | Clear current goal when done |

**File:** `server/adapters/mcp/areas/router.py`

### 2. WorkflowTriggerer Component (TASK-041-0b)

Created `WorkflowTriggerer` with heuristic-based workflow detection:

- Flat scale detection -> `phone_workflow`
- Tall scale detection -> `tower_workflow`
- Keyword-based goal matching

**File:** `server/router/application/triggerer/workflow_triggerer.py`

### 3. YAML Workflow Integration (TASK-041-1, TASK-041-2, TASK-041-3)

Connected WorkflowLoader with WorkflowRegistry and WorkflowExpansionEngine:

- `WorkflowRegistry.load_custom_workflows()` loads YAML from `workflows/custom/`
- `WorkflowExpansionEngine` now uses `WorkflowRegistry` instead of hardcoded dict
- Removed `PREDEFINED_WORKFLOWS` constant
- Lazy loading via `ensure_custom_loaded()`

### 4. Clean Architecture for Router Tools

Applied Clean Architecture pattern to router tools:

| Layer | File | Purpose |
|-------|------|---------|
| Domain | `server/domain/tools/router.py` | `IRouterTool` interface |
| Application | `server/application/tool_handlers/router_handler.py` | `RouterToolHandler` implementation |
| Infrastructure | `server/infrastructure/di.py` | `get_router_handler()` provider |
| Adapter | `server/adapters/mcp/areas/router.py` | MCP tool definitions |

---

## Files Created

| File | Purpose |
|------|---------|
| `server/domain/tools/router.py` | IRouterTool interface |
| `server/application/tool_handlers/router_handler.py` | RouterToolHandler |
| `server/adapters/mcp/areas/router.py` | MCP router tools |
| `server/router/application/triggerer/__init__.py` | Module init |
| `server/router/application/triggerer/workflow_triggerer.py` | Workflow triggerer |

## Files Modified

| File | Change |
|------|--------|
| `server/infrastructure/di.py` | Added `get_router_handler()` provider |
| `server/router/application/router.py` | Added goal tracking methods |
| `server/router/application/workflows/registry.py` | Added `load_custom_workflows()` |
| `server/router/application/engines/workflow_expansion_engine.py` | Use registry instead of hardcoded dict |
| `server/router/application/engines/__init__.py` | Removed PREDEFINED_WORKFLOWS export |
| `server/router/infrastructure/logger.py` | Added `log_info()` method |

---

## Interface: IRouterTool

```python
class IRouterTool(ABC):
    @abstractmethod
    def set_goal(self, goal: str) -> str: ...

    @abstractmethod
    def get_status(self) -> str: ...

    @abstractmethod
    def clear_goal(self) -> str: ...

    @abstractmethod
    def get_goal(self) -> Optional[str]: ...

    @abstractmethod
    def get_pending_workflow(self) -> Optional[str]: ...

    @abstractmethod
    def is_enabled(self) -> bool: ...
```

---

## Tests

All 561 router tests pass after refactoring.

---

## Next Steps

- TASK-041-4 to TASK-041-6: Integrate WorkflowTriggerer into SupervisorRouter
- TASK-041-7 to TASK-041-9: Expression Evaluator for `$CALCULATE(...)`
- TASK-041-10 to TASK-041-12: Condition Evaluator for step conditions
