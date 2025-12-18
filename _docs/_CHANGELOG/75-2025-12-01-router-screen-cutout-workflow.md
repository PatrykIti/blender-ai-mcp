# Changelog 75: Router Screen Cutout Workflow

**Date:** 2025-12-01
**Type:** Feature
**Task:** TASK-039-21

## Summary

Implemented the Screen Cutout sub-workflow for creating screen or display cutouts on surfaces.

## Changes

### New/Updated Files

- `server/router/application/workflows/screen_cutout_workflow.py` - Full implementation
- `tests/unit/router/application/workflows/test_workflows.py` - Tests

### Features

1. **Workflow Steps**
   - 3-4 step sub-workflow
   - Select face → Inset → Extrude → (Optional) Bevel

2. **Customizable Parameters**
   - face_location (where to select)
   - inset_thickness, extrude_depth
   - bevel_width, bevel_segments, add_bevel

3. **Predefined Variants**
   - phone_screen (standard phone display)
   - button (small button cutout)
   - display_panel (large panel)
   - deep_recess (deep without bevel)

4. **Pattern Matching**
   - Trigger pattern: `phone_like`
   - Keywords: screen, display, cutout, button, panel, etc.

### API

```python
from server.router.application.workflows import screen_cutout_workflow

# Default with bevel
steps = screen_cutout_workflow.get_steps()

# Without bevel
steps = screen_cutout_workflow.get_steps({"add_bevel": False})

# Button variant
button_params = screen_cutout_workflow.get_variant("button")
```

## Test Coverage

- 7 unit tests for ScreenCutoutWorkflow
- All tests passing

## Related

- Part of Phase 5: Workflows & Patterns
- Used as sub-workflow in PhoneWorkflow
