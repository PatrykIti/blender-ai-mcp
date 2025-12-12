# 11. Tool Override Engine

## Overview

The Tool Override Engine (`ToolOverrideEngine`) determines when a tool should be replaced with a better alternative based on detected geometry patterns.

## File Location

```
server/router/application/engines/tool_override_engine.py
```

## Core Functionality

### Pattern-Based Overrides

The engine checks if a tool call matches any override rules and suggests replacement tools:

```python
# Phone pattern: extrude → inset + extrude (screen cutout)
{
    "trigger_tool": "mesh_extrude_region",
    "trigger_pattern": "phone_like",
    "replacement_tools": [
        {"tool_name": "mesh_inset", "params": {"thickness": 0.03}},
        {"tool_name": "mesh_extrude_region", "params": {"move": [0.0, 0.0, -0.02]}},
    ],
}
```

### Default Override Rules

1. **extrude_for_screen** - When extruding on phone-like pattern, adds inset first
2. **subdivide_tower** - When subdividing tower-like pattern, adds top scaling for taper

## API

### check_override()

Main method to check for overrides:

```python
def check_override(
    self,
    tool_name: str,
    params: Dict[str, Any],
    context: SceneContext,
    pattern: Optional[DetectedPattern] = None,
) -> OverrideDecision:
```

Returns an `OverrideDecision` containing:
- `should_override: bool`
- `replacement_tools: List[ReplacementTool]`
- `reasons: List[OverrideReason]`

### Rule Management

- `register_rule(rule_name, trigger_tool, trigger_pattern, replacement_tools)` - Add new rule
- `remove_rule(rule_name)` - Remove existing rule
- `get_override_rules()` - List all rules

## Configuration

Controlled via `RouterConfig`:

```python
RouterConfig(
    enable_overrides=True,  # Enable override system
)
```

## Parameter Inheritance

Replacement tools can inherit parameters from the original call:

```python
{
    "tool_name": "mesh_extrude_region",
    "inherit_params": ["move"],  # Inherit move from original
}
```

## Test Coverage

- `tests/unit/router/application/test_tool_override_engine.py`
- 30 tests covering override logic
