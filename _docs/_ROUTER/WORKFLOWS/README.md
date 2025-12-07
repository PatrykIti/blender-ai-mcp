# Router Workflows Documentation

Predefined workflow definitions for common modeling patterns.

---

## Quick Start

**Chcesz stworzyć własny workflow?** → [creating-workflows-tutorial.md](./creating-workflows-tutorial.md)

---

## Index

### Dokumentacja

| Dokument | Opis |
|----------|------|
| [creating-workflows-tutorial.md](./creating-workflows-tutorial.md) | **Tutorial: Tworzenie workflow od podstaw** |
| [yaml-workflow-guide.md](./yaml-workflow-guide.md) | Kompletny przewodnik po składni YAML |
| [expression-reference.md](./expression-reference.md) | Referencja wyrażeń ($CALCULATE, $AUTO_*, warunki) |

### Wbudowane Workflow

| Workflow | Pattern | Steps | Task |
|----------|---------|-------|------|
| [phone-workflow.md](./phone-workflow.md) | `phone_like` | 10 | TASK-039-19 |
| [tower-workflow.md](./tower-workflow.md) | `tower_like` | 5-8 | TASK-039-20 |
| [screen-cutout-workflow.md](./screen-cutout-workflow.md) | Sub-workflow | 3-4 | TASK-039-21 |
| [custom-workflows.md](./custom-workflows.md) | User-defined | - | TASK-039-22 |

---

## What is a Workflow?

A **workflow** is a predefined sequence of tool calls that accomplish a common modeling task. Instead of the LLM figuring out each step, the Router can detect patterns and automatically expand a simple intent into a complete workflow.

**Example:**

```
User intent: "create a phone"

Without workflow:
  LLM must generate 10+ tool calls manually (error-prone)

With workflow:
  Router detects "phone" intent → executes phone_workflow automatically
```

---

## Workflow Triggers

Workflows can be triggered by:

1. **Pattern Detection** - Router detects geometry pattern (e.g., `phone_like`)
2. **Intent Matching** - User prompt matches workflow keywords
3. **Override Rule** - LLM tool call triggers workflow expansion

---

## Built-in Workflows

### Phone Workflow (`phone_workflow`)

Creates a smartphone/tablet shape with screen cutout.

**Trigger:**
- Pattern: `phone_like`
- Keywords: "phone", "smartphone", "tablet", "device"

**Steps:**
1. Create cube
2. Scale to phone proportions (0.4 × 0.8 × 0.05)
3. Enter Edit mode
4. Select all
5. Bevel all edges
6. Deselect all
7. Select top face (screen area)
8. Inset top face
9. Extrude screen inward
10. Return to Object mode

---

### Tower Workflow (`tower_workflow`)

Creates a pillar/column with tapered top.

**Trigger:**
- Pattern: `tower_like`
- Keywords: "tower", "pillar", "column", "obelisk"

**Steps:**
1. Create cube
2. Scale to tall proportions
3. Enter Edit mode
4. Subdivide horizontally
5. Deselect all
6. Select top vertices
7. Scale down (taper effect)
8. Return to Object mode

---

### Screen Cutout Workflow (`screen_cutout_workflow`)

Sub-workflow for creating display/screen insets.

**Trigger:**
- Used within phone_workflow
- Can be triggered by keywords: "screen", "display", "cutout"

**Steps:**
1. Select top face
2. Inset face
3. Extrude inward
4. Bevel edges (optional)

---

## Creating Custom Workflows

You can create your own workflows **without writing Python code** - just create a YAML or JSON file!

### Step 1: Create a File

Create a file in: `server/router/application/workflows/custom/`

Supported formats:
- `.yaml` or `.yml` - YAML format (recommended)
- `.json` - JSON format

### Step 2: Define Your Workflow

**YAML Example (`my_table.yaml`):**

```yaml
# Required fields
name: "table_workflow"
description: "Creates a simple table with four legs"

# Optional metadata
category: "furniture"
author: "your_name"
version: "1.0.0"

# Trigger configuration (optional)
trigger_pattern: "table_like"          # Pattern from GeometryPatternDetector
trigger_keywords:                      # Keywords to match in prompts
  - "table"
  - "desk"
  - "surface"

# Required: list of steps
steps:
  # Step 1: Create table top
  - tool: "modeling_create_primitive"
    params:
      type: "CUBE"
    description: "Create base cube for table top"

  # Step 2: Scale table top
  - tool: "modeling_transform_object"
    params:
      scale: [1.2, 0.8, 0.05]
      location: [0, 0, 0.75]
    description: "Scale and position table top"

  # Step 3: Create first leg
  - tool: "modeling_create_primitive"
    params:
      type: "CUBE"
    description: "Create first leg"

  # Step 4: Position first leg
  - tool: "modeling_transform_object"
    params:
      scale: [0.05, 0.05, 0.75]
      location: [0.55, 0.35, 0.375]
    description: "Scale and position first leg"

  # ... add more legs similarly
```

**JSON Example (`my_chair.json`):**

```json
{
  "name": "chair_workflow",
  "description": "Creates a simple chair with back support",
  "category": "furniture",
  "trigger_keywords": ["chair", "seat", "stool"],
  "steps": [
    {
      "tool": "modeling_create_primitive",
      "params": {"type": "CUBE"},
      "description": "Create seat base"
    },
    {
      "tool": "modeling_transform_object",
      "params": {
        "scale": [0.45, 0.45, 0.05],
        "location": [0, 0, 0.45]
      }
    }
  ]
}
```

### Step 3: Add Conditional Steps (TASK-041)

Use `condition` to skip steps when not needed:

```yaml
steps:
  # Only switch mode if not already in EDIT
  - tool: "system_set_mode"
    params:
      mode: "EDIT"
    condition: "current_mode != 'EDIT'"

  # Only select if nothing selected
  - tool: "mesh_select"
    params:
      action: "all"
    condition: "not has_selection"
```

**Available conditions:**
- `current_mode == 'EDIT'` / `!= 'OBJECT'`
- `has_selection` / `not has_selection`
- `object_count > 0`
- `selected_verts >= 4`
- `A and B` / `A or B`

### Step 4: Use Dynamic Parameters (TASK-041)

#### $CALCULATE - Mathematical Expressions

```yaml
params:
  # 5% of smallest dimension
  width: "$CALCULATE(min_dim * 0.05)"

  # Average of width and height
  size: "$CALCULATE((width + height) / 2)"
```

#### $AUTO_* - Smart Defaults

```yaml
params:
  # Auto-sized bevel (5% of min dim)
  width: "$AUTO_BEVEL"

  # Auto-sized inset (3% of XY min)
  thickness: "$AUTO_INSET"

  # Screen depth (50% of Z inward)
  move: [0, 0, "$AUTO_SCREEN_DEPTH_NEG"]
```

**Available $AUTO_* params:**
| Param | Formula |
|-------|---------|
| `$AUTO_BEVEL` | 5% of min dim |
| `$AUTO_BEVEL_SMALL` | 2% of min dim |
| `$AUTO_INSET` | 3% of XY min |
| `$AUTO_EXTRUDE` | 10% of Z |
| `$AUTO_EXTRUDE_NEG` | -10% of Z |
| `$AUTO_SCREEN_DEPTH_NEG` | -50% of Z |
| `$AUTO_SCALE_SMALL` | 80% scale |

#### Simple Variables

```yaml
params:
  width: "$width"        # From context
  depth: "$depth"
```

---

## Example Workflows Included

The following example workflows are included in `server/router/application/workflows/custom/`:

| File | Description |
|------|-------------|
| `example_table.yaml` | Table with 4 legs (YAML format) |
| `example_chair.json` | Chair with back support (JSON format) |

Use these as templates for your own workflows!

---

## Workflow Schema Reference

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Unique identifier (use snake_case) |
| `steps` | array | List of tool call steps |

### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `description` | string | `""` | Human-readable description |
| `category` | string | `"custom"` | Workflow category |
| `author` | string | `"user"` | Author name |
| `version` | string | `"1.0.0"` | Version string |
| `trigger_pattern` | string | `null` | Geometry pattern to trigger |
| `trigger_keywords` | array | `[]` | Keywords to match |

### Step Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tool` | string | Yes | Tool name to call |
| `params` | object | Yes | Parameters for the tool |
| `description` | string | No | Step description |
| `condition` | string | No | Condition expression |
| `optional` | bool | No | If true, step can be skipped by WorkflowAdapter (TASK-051) |
| `tags` | array | No | Tags for MEDIUM confidence filtering (TASK-051) |

### Parametric Variables (TASK-052)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `defaults` | object | `{}` | Default variable values (e.g., `leg_angle: 0.32`) |
| `modifiers` | object | `{}` | Keyword → variable override mappings |

---

## Parametric Workflow Variables (TASK-052)

Workflows can define `defaults` and `modifiers` to adapt parameters based on user prompts:

### Example

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
  "proste nogi":            # Polish
    leg_angle_left: 0
    leg_angle_right: 0

steps:
  - tool: modeling_transform_object
    params:
      name: "Leg_FL"
      rotation: [0, "$leg_angle_left", 0]  # Variable reference
```

### Behavior

| User Prompt | Result |
|-------------|--------|
| "create a table" | A-frame legs (defaults: 0.32 rad) |
| "table with straight legs" | Vertical legs (modifier: 0 rad) |
| "stół z proste nogi" | Vertical legs (Polish modifier) |

### Variable Resolution Order

1. **defaults** - Workflow-defined default values
2. **modifiers** - Overrides from user prompt keywords
3. **params** - Explicit parameters (highest priority)

### See Also

- [expression-reference.md](./expression-reference.md) - `$variable` syntax reference
- [Implementation: 33-parametric-variables.md](../IMPLEMENTATION/33-parametric-variables.md)

---

## Confidence-Based Workflow Adaptation (TASK-051)

The router adapts workflows based on match confidence level:

| Confidence | Strategy | Behavior |
|------------|----------|----------|
| **HIGH** (≥0.90) | `FULL` | Execute ALL steps |
| **MEDIUM** (≥0.75) | `FILTERED` | Core + tag-matching optional steps |
| **LOW** (≥0.60) | `CORE_ONLY` | Core steps only (skip optional) |
| **NONE** (<0.60) | `CORE_ONLY` | Core steps only (fallback) |

### Marking Steps as Optional

```yaml
steps:
  # Core step - always executed
  - tool: modeling_create_primitive
    params:
      primitive_type: CUBE
      name: "TableTop"
    optional: false  # Default

  # Optional step - can be skipped based on confidence
  - tool: modeling_create_primitive
    params:
      primitive_type: CUBE
      name: "BenchLeft"
    optional: true
    tags: ["bench", "seating", "side"]
```

### Tag Matching (MEDIUM Confidence)

When confidence is MEDIUM, optional steps are included if their tags match the user prompt:

```yaml
# User: "table with benches"
# Step tags: ["bench", "seating"]
# Result: Step included (tag "bench" matches prompt)
```

---

## Validation

Before the workflow is loaded, it's validated. Common errors:

| Error | Cause |
|-------|-------|
| `Missing required field 'name'` | No `name` field in workflow |
| `Missing required field 'steps'` | No `steps` array in workflow |
| `Workflow must have at least one step` | Empty `steps` array |
| `Step N: Missing required field 'tool'` | Step doesn't have `tool` |
| `Workflow name should not contain spaces` | Use underscores, not spaces |

---

## Using Your Workflow

After creating your workflow file, it's automatically loaded on server start:

```python
from server.router.application.workflows import get_workflow_registry

registry = get_workflow_registry()

# Find your workflow by keywords
workflow_name = registry.find_by_keywords("create a table")

# Expand to tool calls
calls = registry.expand_workflow("table_workflow")

# Expand with custom parameters
calls = registry.expand_workflow("table_workflow", {
    "width": 1.5,
    "height": 0.8
})
```

---

## Available Tools for Workflows

Common tools you can use in workflow steps:

| Category | Tools |
|----------|-------|
| **Modeling** | `modeling_create_primitive`, `modeling_transform_object`, `modeling_add_modifier`, `modeling_apply_modifier` |
| **Mesh** | `mesh_select`, `mesh_select_targeted`, `mesh_extrude_region`, `mesh_bevel`, `mesh_inset`, `mesh_subdivide` |
| **System** | `system_set_mode`, `system_export_obj`, `system_import_obj` |
| **Scene** | `scene_delete_object`, `scene_duplicate_object` |
| **Material** | `material_create`, `material_assign` |

See `_docs/AVAILABLE_TOOLS_SUMMARY.md` for the complete list.

---

## See Also

- [ROUTER_HIGH_LEVEL_OVERVIEW.md](../ROUTER_HIGH_LEVEL_OVERVIEW.md)
- [ROUTER_ARCHITECTURE.md](../ROUTER_ARCHITECTURE.md)
- [Custom Workflow Loader](../IMPLEMENTATION/22-custom-workflow-loader.md)
- [TASK-039: Router Supervisor Implementation](../../_TASKS/TASK-039_Router_Supervisor_Implementation.md)
