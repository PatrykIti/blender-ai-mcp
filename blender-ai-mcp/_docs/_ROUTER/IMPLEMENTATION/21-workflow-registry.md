# 21. Workflow Registry

> **Task:** TASK-039-20 (+ subsequent workflow pipeline tasks) | **Status:** ✅ Active/Current  
> **Layer:** Application (`server/router/application/workflows/`)

---

## Overview

`WorkflowRegistry` is the central access point for workflows:

- stores workflow definitions (YAML/JSON via `WorkflowLoader`, or programmatic registration),
- provides lookup (pattern / keywords),
- expands a workflow into `CorrectedToolCall[]` using a **single canonical pipeline**.

This pipeline is used for both:

- normal expansion, and
- adaptation (TASK-051) via `steps_override` (TASK-058), so adaptation does not bypass computed params / loops / conditions.

---

## File Location

`server/router/application/workflows/registry.py`

---

## Interface

```python
class WorkflowRegistry:
    def register_workflow(self, workflow: BaseWorkflow) -> None: ...
    def register_definition(self, definition: WorkflowDefinition) -> None: ...

    def get_definition(self, name: str) -> Optional[WorkflowDefinition]: ...
    def get_all_workflows(self) -> List[str]: ...

    def find_by_pattern(self, pattern_name: str) -> Optional[str]: ...
    def find_by_keywords(self, text: str) -> Optional[str]: ...

    def expand_workflow(
        self,
        workflow_name: str,
        params: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        user_prompt: Optional[str] = None,
        steps_override: Optional[List[WorkflowStep]] = None,  # TASK-058/TASK-051
    ) -> List[CorrectedToolCall]: ...
```

---

## Expansion Pipeline (Custom YAML Workflows)

For custom workflow definitions, the registry applies the pipeline below:

1. **Build variables** (defaults + prompt modifiers) (TASK-052)
2. **Merge explicit params** (explicit overrides variables)
3. **Resolve computed parameters** (`parameters.*.computed`) (TASK-056-5)
4. **Loop expansion + `{var}` interpolation** (TASK-058)
5. **Resolve step params** (`$CALCULATE(...)`, `$AUTO_*`, `$variable`)
6. **Evaluate `condition` + simulate step effects** (TASK-041-11/12)
7. **Return `CorrectedToolCall[]`**

### `steps_override` (TASK-058/TASK-051)

`steps_override` changes only the step source:

- `definition.steps` → normal execution
- `steps_override` → adaptation execution

Everything else in the pipeline stays identical (computed params, loops, conditions, etc.).

This is the key fix that prevents adaptation from bypassing critical workflow logic.

---

## Key Components Used by Registry

- `ExpressionEvaluator` – `$CALCULATE(...)` + computed params resolution
- `ProportionResolver` – `$AUTO_*` parameters
- `ConditionEvaluator` – `condition` evaluation + context simulation
- `LoopExpander` – loops + `{var}` interpolation (TASK-058)

---

## Tests

- `tests/unit/router/application/workflows/test_registry.py`
- `tests/unit/router/application/test_supervisor_router.py` (adaptation path integration)

---

## See Also

- `22-custom-workflow-loader.md`
- `32-workflow-adapter.md`
- `37-loop-expander.md`
