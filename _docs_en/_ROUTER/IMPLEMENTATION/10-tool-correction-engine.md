# 10. Tool Correction Engine

## Overview

The Tool Correction Engine (`ToolCorrectionEngine`) is responsible for correcting tool calls by:
- Fixing mode violations (automatically switching to correct mode)
- Adding missing selection operations
- Clamping parameters to valid ranges

## File Location

```
server/router/application/engines/tool_correction_engine.py
```

## Core Functionality

### Mode Correction

The engine automatically adds mode switch commands when a tool is called in the wrong mode:

```python
MODE_REQUIREMENTS = {
    "mesh_": "EDIT",
    "modeling_": "OBJECT",
    "sculpt_": "SCULPT",
    "scene_": "OBJECT",
    "system_": "ANY",
    # ... more prefixes
}
```

### Selection Auto-Fix

Tools that require geometry selection automatically get a `mesh_select(action="all")` prepended:

```python
SELECTION_REQUIRED_TOOLS = [
    "mesh_extrude_region",
    "mesh_bevel",
    "mesh_inset",
    "mesh_delete_selected",
    # ... more tools
]
```

### Parameter Clamping

Parameters are clamped to valid ranges to prevent errors:

```python
PARAM_LIMITS = {
    "mesh_bevel": {
        "offset": (0.001, 10.0),
        "segments": (1, 10),
    },
    "mesh_subdivide": {
        "number_cuts": (1, 6),
    },
    # ... more tools
}
```

## API

### correct()

Main method that corrects a tool call:

```python
def correct(
    self,
    tool_name: str,
    params: Dict[str, Any],
    context: SceneContext,
) -> Tuple[CorrectedToolCall, List[CorrectedToolCall]]:
```

Returns:
- `CorrectedToolCall` - The corrected main tool call
- `List[CorrectedToolCall]` - Pre-steps (mode switch, selection)

### Helper Methods

- `get_required_mode(tool_name)` - Get required mode for a tool
- `requires_selection(tool_name)` - Check if tool needs selection
- `clamp_parameters(tool_name, params, context)` - Clamp params to valid ranges
- `get_mode_switch_call(target_mode)` - Create mode switch call
- `get_selection_call(selection_type)` - Create selection call

## Configuration

Controlled via `RouterConfig`:

```python
RouterConfig(
    auto_mode_switch=True,    # Enable mode auto-switching
    auto_selection=True,      # Enable selection auto-fix
    clamp_parameters=True,    # Enable parameter clamping
    bevel_max_ratio=0.5,      # Max bevel offset relative to dimension
)
```

## Test Coverage

- `tests/unit/router/application/test_tool_correction_engine.py`
- 44 tests covering all functionality
