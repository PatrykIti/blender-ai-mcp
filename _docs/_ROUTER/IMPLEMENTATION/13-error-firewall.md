# 13. Error Firewall

## Overview

The Error Firewall (`ErrorFirewall`) validates tool calls and blocks or fixes invalid operations before execution.

## File Location

```
server/router/application/engines/error_firewall.py
```

## Core Functionality

### Firewall Actions

The firewall can take different actions based on rule violations:

- **ALLOW** - Let the tool call proceed
- **BLOCK** - Prevent execution entirely
- **MODIFY** - Change parameters to valid values
- **AUTO_FIX** - Add pre-steps to fix the issue

### Default Rules

```python
# Mode violation rules
"mesh_in_object_mode" → auto_fix (switch to EDIT)
"modeling_in_edit_mode" → auto_fix (switch to OBJECT)
"sculpt_in_wrong_mode" → auto_fix (switch to SCULPT)

# Selection rules
"extrude_no_selection" → auto_fix (select all)
"bevel_no_selection" → auto_fix (select all)

# Parameter rules
"bevel_too_large" → modify (clamp width)
"subdivide_too_many" → modify (limit cuts to 6)

# Object existence rules
"delete_no_object" → block
```

## API

### validate()

Main validation method:

```python
def validate(
    self,
    tool_call: CorrectedToolCall,
    context: SceneContext,
) -> FirewallResult:
```

Returns `FirewallResult` containing:
- `action: FirewallAction` (ALLOW, BLOCK, MODIFY, AUTO_FIX)
- `allowed: bool`
- `message: str`
- `violations: List[FirewallViolation]`
- `modified_call: Optional[Dict]`
- `pre_steps: List[Dict]`

### Rule Management

- `register_rule(rule_name, tool_pattern, condition, action, fix_description)` - Add rule
- `enable_rule(rule_name)` - Enable a rule
- `disable_rule(rule_name)` - Disable a rule
- `get_firewall_rules()` - List all rules with status

### Other Methods

- `validate_sequence(calls, context)` - Validate multiple calls
- `can_auto_fix(tool_call, context)` - Check if auto-fix is possible

## Condition Syntax

Rules use a simple condition syntax:

```python
"mode == 'OBJECT'"          # Mode check
"mode != 'SCULPT'"          # Mode not equal
"no_selection"              # No geometry selected
"no_objects"                # Scene is empty
"param:width > dimension_ratio:0.5"  # Parameter bounds
"param:number_cuts > 6"     # Parameter threshold
```

## Configuration

Controlled via `RouterConfig`:

```python
RouterConfig(
    block_invalid_operations=True,    # Enable blocking
    auto_fix_mode_violations=True,    # Enable auto-fix for mode issues
)
```

## Test Coverage

- `tests/unit/router/application/test_error_firewall.py`
- 44 tests covering validation logic
