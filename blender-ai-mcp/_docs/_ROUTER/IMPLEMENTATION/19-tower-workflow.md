# Tower Workflow

## Overview

Workflow for creating tower, pillar, and column-like structures with optional taper effect.

**Task:** TASK-039-20

## Interface

```python
class TowerWorkflow(BaseWorkflow):
    @property
    def name(self) -> str: ...
    @property
    def description(self) -> str: ...
    @property
    def trigger_pattern(self) -> Optional[str]: ...
    @property
    def trigger_keywords(self) -> List[str]: ...
    def get_steps(self, params: Optional[Dict] = None) -> List[WorkflowStep]: ...
    def get_variant(self, variant_name: str) -> Optional[Dict]: ...
```

## Implementation

Location: `server/router/application/workflows/tower_workflow.py`

### Default Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `base_size` | 0.3 | Base X/Y size |
| `height` | 2.0 | Tower height (Z) |
| `subdivisions` | 3 | Number of loop cuts |
| `taper_factor` | 0.7 | Top scale factor |
| `add_taper` | True | Whether to add taper effect |

### Workflow Steps

1. Create base cube primitive
2. Scale to tower proportions
3. Enter Edit mode
4. Subdivide for segments
5. (Optional) Deselect all
6. (Optional) Select top geometry
7. (Optional) Scale down for taper effect
8. Return to Object mode

### Variants

| Variant | Description |
|---------|-------------|
| `obelisk` | Tall with sharp taper (factor 0.4) |
| `pillar` | Classical pillar (slight taper 0.9) |
| `chimney` | Tall, no taper |
| `spire` | Very pointed (factor 0.1) |

## Usage

```python
from server.router.application.workflows import tower_workflow

# Get default steps with taper
steps = tower_workflow.get_steps()

# Get steps without taper
steps = tower_workflow.get_steps({"add_taper": False})

# Get obelisk variant
obelisk_params = tower_workflow.get_variant("obelisk")
```

## Trigger

- **Pattern:** `tower_like`
- **Keywords:** tower, pillar, column, obelisk, spire, minaret, chimney, post

## Tests

- `tests/unit/router/application/workflows/test_workflows.py::TestTowerWorkflow`

## See Also

- [Phone Workflow](./18-phone-workflow.md)
- [Screen Cutout Workflow](./20-screen-cutout-workflow.md)
