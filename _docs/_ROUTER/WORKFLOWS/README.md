# Router Workflows Documentation

Predefined workflow definitions for common modeling patterns.

---

## Index

| Workflow | Pattern | Steps | Task |
|----------|---------|-------|------|
| [phone-workflow.md](./phone-workflow.md) | `phone_like` | 12 | TASK-039-19 |
| [tower-workflow.md](./tower-workflow.md) | `tower_like` | 7 | TASK-039-20 |
| [screen-cutout-workflow.md](./screen-cutout-workflow.md) | Sub-workflow | 4 | TASK-039-21 |
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
2. Scale to phone proportions
3. Bevel all edges
4. Inset top face (screen area)
5. Extrude screen inward
6. Apply material

---

### Tower Workflow (`tower_workflow`)

Creates a pillar/column with tapered top.

**Trigger:**
- Pattern: `tower_like`
- Keywords: "tower", "pillar", "column", "obelisk"

**Steps:**
1. Create cube
2. Scale to tall proportions
3. Subdivide horizontally
4. Select top loop
5. Scale down (taper)

---

### Screen Cutout Workflow (`screen_cutout_workflow`)

Sub-workflow for creating display/screen insets.

**Trigger:**
- Used within phone_workflow
- Can be triggered by `mesh_extrude` on `phone_like` pattern

**Steps:**
1. Select top face
2. Inset face
3. Extrude inward
4. Bevel edges

---

## Custom Workflows

Users can define custom workflows via YAML files in `server/router/workflows/custom/`.

See [custom-workflows.md](./custom-workflows.md) for format and examples.

---

## Workflow Definition Format

```yaml
name: "workflow_name"
description: "What this workflow does"

trigger:
  pattern: "phone_like"  # Optional: geometry pattern
  keywords:              # Optional: intent keywords
    - "phone"
    - "smartphone"
  tool_override:         # Optional: replace specific tool
    tool: "mesh_extrude"
    condition: "pattern == phone_like"

steps:
  - tool: "modeling_create_primitive"
    params:
      type: "CUBE"

  - tool: "modeling_transform"
    params:
      scale: [0.4, 0.8, 0.05]

  - tool: "mesh_bevel"
    params:
      width: "$bevel_width"  # $ = parameter from config or input
      segments: 3
```

---

## See Also

- [ROUTER_HIGH_LEVEL_OVERVIEW.md](../ROUTER_HIGH_LEVEL_OVERVIEW.md)
- [ROUTER_ARCHITECTURE.md](../ROUTER_ARCHITECTURE.md)
- [TASK-039: Router Supervisor Implementation](../../_TASKS/TASK-039_Router_Supervisor_Implementation.md)
