# Phone Workflow

## Overview

Complete workflow for creating smartphone/tablet 3D models with rounded edges and screen cutout.

**Task:** TASK-039-19

## Interface

```python
class PhoneWorkflow(BaseWorkflow):
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

Location: `server/router/application/workflows/phone_workflow.py`

### Default Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `width` | 0.4 | Phone width (X) |
| `height` | 0.8 | Phone height (Y) |
| `depth` | 0.05 | Phone thickness (Z) |
| `bevel_width` | 0.02 | Edge bevel width |
| `bevel_segments` | 3 | Bevel smoothness |
| `screen_inset` | 0.03 | Screen border width |
| `screen_depth` | 0.02 | Screen depth |

### Workflow Steps

1. Create base cube primitive
2. Scale to phone proportions
3. Enter Edit mode
4. Select all geometry
5. Bevel all edges for rounded corners
6. Deselect all
7. Select top face (screen area)
8. Inset face for screen border
9. Extrude inward for screen depth
10. Return to Object mode

### Variants

| Variant | Description |
|---------|-------------|
| `smartphone` | Realistic smartphone proportions (0.07 × 0.15) |
| `tablet` | Tablet proportions (0.18 × 0.24) |
| `laptop_screen` | Laptop display (0.35 × 0.22) |

## Usage

```python
from server.router.application.workflows import phone_workflow

# Get default steps
steps = phone_workflow.get_steps()

# Get custom steps
steps = phone_workflow.get_steps({
    "width": 0.5,
    "height": 1.0,
    "bevel_width": 0.05,
})

# Get variant parameters
tablet_params = phone_workflow.get_variant("tablet")
```

## Trigger

- **Pattern:** `phone_like`
- **Keywords:** phone, smartphone, tablet, mobile, cellphone, iphone, android, device

## Tests

- `tests/unit/router/application/workflows/test_workflows.py::TestPhoneWorkflow`

## See Also

- [Tower Workflow](./19-tower-workflow.md)
- [Screen Cutout Workflow](./20-screen-cutout-workflow.md)
- [Workflow Registry](./21-workflow-registry.md)
