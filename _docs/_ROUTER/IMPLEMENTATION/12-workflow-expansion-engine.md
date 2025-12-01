# 12. Workflow Expansion Engine

## Overview

The Workflow Expansion Engine (`WorkflowExpansionEngine`) transforms single tool calls into multi-step workflows based on detected patterns.

## File Location

```
server/router/application/engines/workflow_expansion_engine.py
```

## Core Functionality

### Predefined Workflows

The engine includes several predefined workflows:

```python
PREDEFINED_WORKFLOWS = {
    "phone_workflow": {
        "description": "Complete phone/tablet modeling workflow",
        "trigger_pattern": "phone_like",
        "trigger_keywords": ["phone", "smartphone", "tablet", "mobile"],
        "steps": [
            {"tool": "modeling_create_primitive", "params": {"type": "CUBE"}},
            {"tool": "modeling_transform_object", "params": {"scale": [0.4, 0.8, 0.05]}},
            # ... 10 steps total
        ],
    },
    "tower_workflow": { ... },
    "screen_cutout_workflow": { ... },
    "bevel_all_edges_workflow": { ... },
}
```

### Workflow Expansion

When a pattern suggests a workflow, the engine expands it:

```python
result = engine.expand(
    tool_name="modeling_create_primitive",
    params={"type": "CUBE"},
    context=scene_context,
    pattern=detected_pattern,  # Has suggested_workflow="phone_workflow"
)
# Returns list of 10 CorrectedToolCall objects
```

## API

### expand()

Main expansion method:

```python
def expand(
    self,
    tool_name: str,
    params: Dict[str, Any],
    context: SceneContext,
    pattern: Optional[DetectedPattern] = None,
) -> Optional[List[CorrectedToolCall]]:
```

### Workflow Management

- `get_workflow(workflow_name)` - Get workflow steps
- `register_workflow(name, steps, trigger_pattern, trigger_keywords)` - Add custom workflow
- `get_available_workflows()` - List all workflows
- `expand_workflow(workflow_name, params)` - Expand specific workflow
- `get_workflow_for_pattern(pattern)` - Find workflow for pattern
- `get_workflow_for_keywords(keywords)` - Find workflow for keywords

## Parameter Inheritance

Workflow steps can inherit parameters using `$` syntax:

```python
{"tool": "mesh_bevel", "params": {"width": "$width", "segments": "$segments"}}
```

This inherits `width` and `segments` from the original tool call parameters.

## Configuration

Controlled via `RouterConfig`:

```python
RouterConfig(
    enable_workflow_expansion=True,  # Enable workflow expansion
)
```

## Test Coverage

- `tests/unit/router/application/test_workflow_expansion_engine.py`
- 40 tests covering workflow expansion
