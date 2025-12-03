# YAML Workflow Guide

Complete guide to creating custom YAML workflows for the Router Supervisor.

---

## Overview

YAML workflows allow you to define sequences of Blender operations that execute automatically when triggered. Workflows support:

- **Conditional steps** - Skip steps based on scene state
- **Dynamic parameters** - Calculate values from object dimensions
- **Smart defaults** - Auto-sized operations with `$AUTO_*` params
- **Keyword triggering** - Automatic activation from user prompts

---

## File Structure

Place custom workflows in:
```
server/router/application/workflows/custom/
```

Supported formats: `.yaml`, `.yml`, `.json`

---

## Basic Structure

```yaml
# my_workflow.yaml
name: my_workflow                     # Required: unique identifier
description: Description of workflow  # Required: what it does
category: furniture                   # Optional: grouping
author: Your Name                     # Optional: creator
version: "1.0"                        # Optional: version string

trigger_pattern: box_pattern          # Optional: geometry pattern to match
trigger_keywords:                     # Optional: keywords to trigger
  - table
  - desk
  - surface

steps:                                # Required: list of tool calls
  - tool: modeling_create_primitive
    params:
      type: CUBE
    description: Create base cube
```

---

## Step Definition

Each step has:

```yaml
- tool: mesh_bevel           # Required: tool name
  params:                    # Required: tool parameters
    width: 0.05
    segments: 3
  description: Bevel edges   # Optional: human-readable description
  condition: "..."           # Optional: when to execute (see below)
```

---

## Conditional Steps

Use the `condition` field to skip steps based on scene state.

### Syntax

```yaml
condition: "current_mode != 'EDIT'"  # Only if not in EDIT mode
condition: "has_selection"           # Only if something is selected
condition: "not has_selection"       # Only if nothing is selected
condition: "object_count > 0"        # Only if objects exist
condition: "selected_verts >= 4"     # Only if enough vertices
```

### Operators

| Operator | Example | Description |
|----------|---------|-------------|
| `==` | `mode == 'EDIT'` | Equal |
| `!=` | `mode != 'EDIT'` | Not equal |
| `>` | `count > 0` | Greater than |
| `<` | `count < 10` | Less than |
| `>=` | `count >= 5` | Greater or equal |
| `<=` | `count <= 5` | Less or equal |
| `not` | `not has_selection` | Negation |
| `and` | `mode == 'EDIT' and has_selection` | Both true |
| `or` | `mode == 'OBJECT' or count > 0` | Either true |

### Available Variables

| Variable | Type | Description |
|----------|------|-------------|
| `current_mode` | str | Current Blender mode |
| `has_selection` | bool | Whether geometry is selected |
| `object_count` | int | Number of objects |
| `selected_verts` | int | Selected vertex count |
| `selected_edges` | int | Selected edge count |
| `selected_faces` | int | Selected face count |
| `active_object` | str | Active object name |

### Context Simulation

The router simulates context changes during expansion:
- After `system_set_mode mode=EDIT` → `current_mode = 'EDIT'`
- After `mesh_select action=all` → `has_selection = True`
- After `mesh_select action=none` → `has_selection = False`

This prevents redundant steps:
```yaml
steps:
  - tool: system_set_mode
    params: { mode: EDIT }
    condition: "current_mode != 'EDIT'"  # Runs

  - tool: system_set_mode
    params: { mode: EDIT }
    condition: "current_mode != 'EDIT'"  # SKIPPED (simulation says now in EDIT)
```

---

## Dynamic Parameters

### $CALCULATE Expressions

Use `$CALCULATE(...)` for mathematical expressions:

```yaml
params:
  width: "$CALCULATE(min_dim * 0.05)"     # 5% of smallest dimension
  thickness: "$CALCULATE(width / 2)"      # Half of width
  segments: "$CALCULATE(3 + 2)"           # Simple math = 5
```

**Available Math Functions:**
- `min()`, `max()`, `abs()`
- `round()`, `floor()`, `ceil()`
- `sqrt()`

**Available Variables:**
- `width`, `height`, `depth` - Object dimensions
- `min_dim`, `max_dim` - Min/max of dimensions

### $AUTO_* Parameters

Smart defaults that adapt to object size:

```yaml
params:
  width: "$AUTO_BEVEL"      # 5% of smallest dimension
  thickness: "$AUTO_INSET"  # 3% of XY smallest
  move: [0, 0, "$AUTO_EXTRUDE_NEG"]  # -10% of depth
```

**Available $AUTO_* Parameters:**

| Parameter | Calculation | Use Case |
|-----------|-------------|----------|
| `$AUTO_BEVEL` | 5% of min dim | Standard bevel |
| `$AUTO_BEVEL_SMALL` | 2% of min dim | Subtle bevel |
| `$AUTO_BEVEL_LARGE` | 10% of min dim | Prominent bevel |
| `$AUTO_INSET` | 3% of XY min | Standard inset |
| `$AUTO_INSET_THICK` | 5% of XY min | Thick inset |
| `$AUTO_EXTRUDE` | 10% of Z | Outward extrude |
| `$AUTO_EXTRUDE_NEG` | -10% of Z | Inward extrude |
| `$AUTO_EXTRUDE_DEEP` | 20% of Z | Deep extrude |
| `$AUTO_SCALE_SMALL` | 80% each dim | Shrink to 80% |
| `$AUTO_SCREEN_DEPTH` | 50% of Z | Phone screen depth |
| `$AUTO_SCREEN_DEPTH_NEG` | -50% of Z | Inward screen |

### Simple Variables

Reference context values directly:

```yaml
params:
  mode: "$mode"        # Current mode
  depth: "$depth"      # Object depth
```

---

## Complete Example

```yaml
# phone_workflow.yaml
name: phone_workflow
description: Create a smartphone model with screen
category: electronics
author: BlenderAI
version: "2.0"

trigger_keywords:
  - phone
  - smartphone
  - mobile
  - iphone
  - android

steps:
  # 1. Create base cube
  - tool: modeling_create_primitive
    params:
      type: CUBE
    description: Create phone body

  # 2. Switch to EDIT mode (if needed)
  - tool: system_set_mode
    params:
      mode: EDIT
    description: Enter edit mode
    condition: "current_mode != 'EDIT'"

  # 3. Select all geometry (if nothing selected)
  - tool: mesh_select
    params:
      action: all
    description: Select all
    condition: "not has_selection"

  # 4. Bevel edges with auto size
  - tool: mesh_bevel
    params:
      width: "$AUTO_BEVEL"
      segments: 3
    description: Round corners

  # 5. Select top face for screen
  - tool: mesh_select_targeted
    params:
      mode: FACE
      indices: [5]
    description: Select top face

  # 6. Inset for screen bezel
  - tool: mesh_inset
    params:
      thickness: "$AUTO_INSET"
    description: Create screen bezel

  # 7. Extrude screen inward
  - tool: mesh_extrude_region
    params:
      move:
        - 0
        - 0
        - "$AUTO_SCREEN_DEPTH_NEG"
    description: Create screen depth
```

---

## Triggering Workflows

### By Keywords

Workflows trigger when user prompts contain trigger keywords:

```
User: "Create a phone"
→ Matches "phone" keyword → phone_workflow executes
```

### By Pattern

Workflows can match geometry patterns:

```yaml
trigger_pattern: box_pattern  # Matches box-like objects
```

### Manual Trigger

LLM can explicitly request a workflow:

```python
router.process_llm_tool_call("workflow_trigger", {"name": "phone_workflow"})
```

---

## Best Practices

### 1. Use Conditions for Robustness

```yaml
# Good: Only switch mode if needed
- tool: system_set_mode
  params: { mode: EDIT }
  condition: "current_mode != 'EDIT'"

# Bad: Always switches, may error if already in EDIT
- tool: system_set_mode
  params: { mode: EDIT }
```

### 2. Use $AUTO_* for Scale Independence

```yaml
# Good: Works for any object size
params:
  width: "$AUTO_BEVEL"

# Bad: Only works for ~1m objects
params:
  width: 0.05
```

### 3. Provide Descriptive Names

```yaml
name: phone_with_screen_cutout  # Descriptive
name: wf1                       # Unclear
```

### 4. Include Trigger Keywords

```yaml
trigger_keywords:
  - phone
  - smartphone
  - mobile
  - cell phone
  - iphone
  - android phone
```

### 5. Add Descriptions to Steps

```yaml
- tool: mesh_bevel
  params: { width: "$AUTO_BEVEL", segments: 3 }
  description: Round edges for phone body  # Helps debugging
```

---

## Troubleshooting

### Workflow Not Triggering

1. Check trigger keywords match user prompt
2. Verify workflow loaded: check logs for "Loaded custom workflows"
3. Ensure YAML syntax is valid

### Conditions Always Skip

1. Check context variables are spelled correctly
2. Verify context is passed to `expand_workflow()`
3. Test condition in isolation

### $AUTO_* Not Resolving

1. Ensure dimensions are in context
2. Check for typos in $AUTO_* name
3. Verify object has valid dimensions

### $CALCULATE Errors

1. Check variable names match context
2. Verify math expression syntax
3. Avoid division by zero
