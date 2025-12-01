# Custom Workflow Loader

## Overview

Loads workflow definitions from YAML/JSON files, enabling user-defined workflows without code changes.

**Task:** TASK-039-22

## Interface

```python
class WorkflowLoader:
    def __init__(self, workflows_dir: Optional[Path] = None): ...
    def load_all(self) -> Dict[str, WorkflowDefinition]: ...
    def load_file(self, file_path: Path) -> WorkflowDefinition: ...
    def get_workflow(self, name: str) -> Optional[WorkflowDefinition]: ...
    def reload(self) -> Dict[str, WorkflowDefinition]: ...
    def validate_workflow_data(self, data: Dict) -> List[str]: ...
    def create_workflow_template(self) -> Dict: ...
    def save_workflow(self, workflow: Union[WorkflowDefinition, Dict], filename: str, format: str = "yaml") -> Path: ...
```

## Implementation

Location: `server/router/infrastructure/workflow_loader.py`

### Supported Formats

- YAML (.yaml, .yml)
- JSON (.json)

### Workflow File Schema

```yaml
# Required fields
name: "my_workflow"                    # Unique identifier
steps:                                 # List of tool calls
  - tool: "modeling_create_primitive"
    params:
      type: "CUBE"
    description: "Create base cube"    # Optional

# Optional fields
description: "Human-readable description"
category: "custom"                     # Workflow category
author: "your_name"
version: "1.0.0"
trigger_pattern: "pattern_name"        # Pattern to trigger
trigger_keywords:                      # Keywords to trigger
  - "keyword1"
  - "keyword2"
```

### Parameter Inheritance

Use `$param_name` syntax to inherit parameters from the original tool call:

```yaml
steps:
  - tool: "mesh_bevel"
    params:
      width: "$width"      # Inherited from original call
      segments: "$segments"
```

### Workflows Directory

Default location: `server/router/application/workflows/custom/`

## Usage

```python
from server.router.infrastructure.workflow_loader import get_workflow_loader

loader = get_workflow_loader()

# Load all workflows
workflows = loader.load_all()

# Get specific workflow
workflow = loader.get_workflow("my_workflow")

# Reload after file changes
loader.reload()

# Create a template
template = loader.create_workflow_template()

# Save a workflow
loader.save_workflow(my_data, "new_workflow", format="yaml")
```

## Example Workflows

### Table (YAML)

```yaml
name: "table_workflow"
description: "Creates a simple table with four legs"
category: "furniture"
trigger_keywords:
  - "table"
  - "desk"
steps:
  - tool: "modeling_create_primitive"
    params: {type: "CUBE"}
  - tool: "modeling_transform_object"
    params:
      scale: [1.2, 0.8, 0.05]
      location: [0, 0, 0.75]
  # ... leg creation steps
```

### Chair (JSON)

```json
{
  "name": "chair_workflow",
  "description": "Creates a simple chair",
  "category": "furniture",
  "trigger_keywords": ["chair", "seat"],
  "steps": [
    {"tool": "modeling_create_primitive", "params": {"type": "CUBE"}},
    {"tool": "modeling_transform_object", "params": {"scale": [0.45, 0.45, 0.05]}}
  ]
}
```

## Validation

```python
errors = loader.validate_workflow_data(data)
if errors:
    for error in errors:
        print(f"Validation error: {error}")
```

## Tests

- `tests/unit/router/infrastructure/test_workflow_loader.py`

## See Also

- [Workflow Registry](./21-workflow-registry.md)
- [Phone Workflow](./18-phone-workflow.md)
