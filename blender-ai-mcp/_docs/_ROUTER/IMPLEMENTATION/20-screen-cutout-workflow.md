# Screen Cutout Workflow

## Overview

Sub-workflow for creating screen or display cutouts on surfaces. Often used as a component within larger workflows.

**Task:** TASK-039-21

## Interface

```python
class ScreenCutoutWorkflow(BaseWorkflow):
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

Location: `server/router/application/workflows/screen_cutout_workflow.py`

### Default Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `face_location` | [0, 0, 1] | Location to select face (top) |
| `inset_thickness` | 0.05 | Border thickness |
| `extrude_depth` | 0.02 | Screen depth |
| `bevel_width` | 0.005 | Edge bevel width |
| `bevel_segments` | 2 | Bevel segments |
| `add_bevel` | True | Whether to add bevel |

### Workflow Steps

1. Select target face by location
2. Inset face for border
3. Extrude inward for screen depth
4. (Optional) Bevel screen edges

### Variants

| Variant | Description |
|---------|-------------|
| `phone_screen` | Phone screen cutout |
| `button` | Small button cutout |
| `display_panel` | Large display panel |
| `deep_recess` | Deep recess without bevel |

## Usage

```python
from server.router.application.workflows import screen_cutout_workflow

# Get default steps
steps = screen_cutout_workflow.get_steps()

# Without bevel
steps = screen_cutout_workflow.get_steps({"add_bevel": False})

# Button variant
button_params = screen_cutout_workflow.get_variant("button")
```

## Trigger

- **Pattern:** `phone_like`
- **Keywords:** screen, display, cutout, inset, button, panel, lcd, monitor

## Tests

- `tests/unit/router/application/workflows/test_workflows.py::TestScreenCutoutWorkflow`

## See Also

- [Phone Workflow](./18-phone-workflow.md) (uses this as sub-workflow)
- [Tower Workflow](./19-tower-workflow.md)
