# 98 - Parametric Workflow Variables (TASK-052)

**Date:** 2025-12-07

---

## Summary

Added parametric variable substitution to YAML workflows. Workflows can now define `defaults` and `modifiers` sections that allow automatic parameter adaptation based on user prompts.

---

## Changes

### New Features

1. **`defaults` Section in Workflows**
   - Define default variable values in workflow YAML
   - Variables are referenced with `$variable` syntax in step params
   - Example: `leg_angle: 0.32` → `rotation: [0, "$leg_angle", 0]`

2. **`modifiers` Section in Workflows**
   - Map keywords/phrases to variable overrides
   - Supports multiple languages (English, Polish, etc.)
   - Later matches override earlier ones

3. **Variable Substitution Functions**
   - `extract_modifiers(prompt, workflow_modifiers)` - Extract overrides from user prompt
   - `substitute_variables(params, variables)` - Replace `$variable` with values
   - `_substitute_list(lst, variables)` - Handle variables in lists

---

## Files Modified

| File | Changes |
|------|---------|
| `server/router/application/workflows/base.py` | Added `defaults` and `modifiers` fields to `WorkflowDefinition` |
| `server/router/infrastructure/workflow_loader.py` | Parse `defaults` and `modifiers` from YAML |
| `server/router/application/engines/workflow_expansion_engine.py` | Added `extract_modifiers()`, `substitute_variables()`, `_substitute_list()` |
| `server/router/application/workflows/registry.py` | Pass `user_prompt` to `expand_workflow()` for modifier extraction |
| `server/router/application/workflows/custom/picnic_table.yaml` | Added `defaults` + `modifiers` + `$variable` syntax |

---

## New Tests

| File | Tests |
|------|-------|
| `tests/unit/router/application/test_variable_substitution.py` | 37 tests for parametric variable system |

### Test Classes
- `TestExtractModifiers` - 9 tests for keyword extraction
- `TestSubstituteVariables` - 12 tests for variable substitution
- `TestSubstituteList` - 3 tests for list handling
- `TestWorkflowDefinitionWithModifiers` - 6 tests for definition with defaults/modifiers
- `TestRegistryModifierIntegration` - 4 tests for registry integration
- `TestPicnicTableWorkflow` - 3 tests for picnic table workflow

---

## Usage Example

### Workflow Definition

```yaml
name: picnic_table_workflow
description: Picnic table with configurable legs

defaults:
  leg_angle_left: 0.32      # A-frame angle (default)
  leg_angle_right: -0.32

modifiers:
  "straight legs":          # English
    leg_angle_left: 0
    leg_angle_right: 0
  "straight legs":          # Polish
    leg_angle_left: 0
    leg_angle_right: 0

steps:
  - tool: modeling_transform_object
    params:
      name: "Leg_FL"
      rotation: [0, "$leg_angle_left", 0]  # Variable reference
```

### Behavior

```
User: "create a table"
→ defaults applied
→ rotation: [0, 0.32, 0]  (A-frame legs)

User: "table with straight legs"
→ modifier "straight legs" matches
→ rotation: [0, 0, 0]  (vertical legs)

User: "table with straight legs"
→ modifier "straight legs" matches
→ rotation: [0, 0, 0]  (vertical legs)
```

---

## Performance

- Variable substitution: < 1ms
- No external API calls
- Pure in-memory operations

---

## Related

- **TASK-051**: Confidence-Based Workflow Adaptation (dependency)
- **TASK-041**: YAML Workflow Integration (foundation)
- **TASK-046**: Semantic Generalization (LaBSE matching)
