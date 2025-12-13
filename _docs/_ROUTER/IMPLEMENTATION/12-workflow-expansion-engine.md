# 12. Workflow Expansion Engine

> **Task:** TASK-039-13 (+ YAML workflow integration) | **Status:** ✅ Current  
> **Layer:** Application (`server/router/application/engines/`)

---

## Overview

`WorkflowExpansionEngine` is an application-level facade that exposes workflow expansion via the domain `IExpansionEngine` interface.

In the current architecture, workflows are sourced from `WorkflowRegistry` (YAML/JSON or programmatic definitions), and the registry is responsible for the full expansion pipeline:

- computed params
- loops + `{var}` interpolation
- `$CALCULATE(...)` / `$AUTO_*` / `$variable`
- `condition` evaluation + context simulation

So the expansion engine primarily delegates to the registry and provides convenience helpers.

---

## File Location

`server/router/application/engines/workflow_expansion_engine.py`

---

## Responsibilities

1. **Expose registry workflows via `IExpansionEngine`**
   - `get_workflow()`, `get_available_workflows()`, `register_workflow()`
2. **Expand a named workflow into tool calls**
   - delegates to `WorkflowRegistry.expand_workflow(...)`
3. **Legacy/simple parameter inheritance**
   - resolves `$param` strings in expanded calls using the original tool call params (kept for compatibility)

---

## API

```python
class WorkflowExpansionEngine(IExpansionEngine):
    def get_workflow(self, workflow_name: str) -> Optional[List[Dict[str, Any]]]: ...
    def register_workflow(self, name: str, steps: List[Dict[str, Any]], ...) -> None: ...
    def get_available_workflows(self) -> List[str]: ...

    def expand_workflow(
        self,
        workflow_name: str,
        params: Dict[str, Any],
        user_prompt: Optional[str] = None,
    ) -> List[CorrectedToolCall]: ...
```

Notes:

- `user_prompt` is passed through to the registry so prompt modifiers can be applied (TASK-052).
- Scene context (`dimensions`, `mode`, etc.) is handled where the router calls into the registry directly.

---

## Configuration

`RouterConfig.enable_workflow_expansion` controls whether workflows should be expanded by the router.

---

## Tests

- `tests/unit/router/application/test_workflow_expansion_engine.py`

---

## See Also

- `21-workflow-registry.md` (canonical workflow expansion pipeline)
- `22-custom-workflow-loader.md` (YAML/JSON loading)
