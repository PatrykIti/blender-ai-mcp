# Workflow Registry

## Overview

Central registry for all available workflows, providing unified access and lookup methods.

**Task:** TASK-039-20 (Pattern Library)

## Interface

```python
class WorkflowRegistry:
    def __init__(self): ...
    def register_workflow(self, workflow: BaseWorkflow) -> None: ...
    def register_definition(self, definition: WorkflowDefinition) -> None: ...
    def get_workflow(self, name: str) -> Optional[BaseWorkflow]: ...
    def get_definition(self, name: str) -> Optional[WorkflowDefinition]: ...
    def get_all_workflows(self) -> List[str]: ...
    def find_by_pattern(self, pattern_name: str) -> Optional[str]: ...
    def find_by_keywords(self, text: str) -> Optional[str]: ...
    def expand_workflow(self, name: str, params: Optional[Dict] = None) -> List[CorrectedToolCall]: ...
    def get_workflow_info(self, name: str) -> Optional[Dict]: ...
```

## Implementation

Location: `server/router/application/workflows/registry.py`

### Features

1. **Built-in Workflow Registration**
   - Automatically registers phone, tower, and screen_cutout workflows

2. **Pattern-Based Lookup**
   - Find workflows by detected geometry pattern

3. **Keyword-Based Lookup**
   - Find workflows by natural language keywords

4. **Workflow Expansion**
   - Convert workflow to list of tool calls
   - Support parameter substitution

5. **Custom Workflow Support**
   - Register custom workflow classes
   - Register workflow definitions

## Usage

```python
from server.router.application.workflows import get_workflow_registry

registry = get_workflow_registry()

# Get all workflows
names = registry.get_all_workflows()
# ["phone_workflow", "screen_cutout_workflow", "tower_workflow"]

# Find by pattern
workflow_name = registry.find_by_pattern("phone_like")
# "phone_workflow" or "screen_cutout_workflow"

# Find by keywords
workflow_name = registry.find_by_keywords("create a tall tower")
# "tower_workflow"

# Expand to tool calls
calls = registry.expand_workflow("phone_workflow")
# [CorrectedToolCall(...), CorrectedToolCall(...), ...]

# Get workflow info
info = registry.get_workflow_info("phone_workflow")
# {"name": "phone_workflow", "type": "builtin", "step_count": 10, ...}
```

## Singleton Access

```python
from server.router.application.workflows import get_workflow_registry

# Always returns the same instance
registry = get_workflow_registry()
```

## Tests

- `tests/unit/router/application/workflows/test_registry.py`

## See Also

- [Phone Workflow](./18-phone-workflow.md)
- [Tower Workflow](./19-tower-workflow.md)
- [Custom Workflow Loader](./22-custom-workflow-loader.md)
