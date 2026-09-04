# Tutorial: Creating a Workflow from Scratch

Complete step-by-step guide to creating your own YAML workflows.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Step 1: Planning the Workflow](#2-step-1-planning-the-workflow)
3. [Step 2: Creating the YAML File](#3-step-2-creating-the-yaml-file)
4. [Step 3: Defining Steps](#4-step-3-defining-steps)
5. [Step 4: Adding Conditions](#5-step-4-adding-conditions)
6. [Step 5: Dynamic Parameters](#6-step-5-dynamic-parameters)
6b. [Loops and String Interpolation (TASK-058)](#6b-loops-and-string-interpolation-task-058)
7. [Step 6: Optional Steps and Adaptation](#7-step-6-optional-steps-and-adaptation)
8. [Step 7: Testing](#8-step-7-testing)
9. [Complete Example](#9-complete-example)
10. [Common Errors](#10-common-errors)

---

## 1. Overview

A workflow is a sequence of Blender operations saved in a YAML/JSON file that runs automatically. Instead of manually invoking 10+ tools, the user says "create a phone" and the workflow does the rest.

What a workflow can contain:
- A sequence of steps (tool calls)
- Conditions for step execution (`condition`)
- Dynamic parameters (`$CALCULATE`, `$AUTO_*`)
- Triggers (keywords, geometry patterns)

---

## 2. Step 1: Planning the Workflow

### 2.1 Define the Goal

Before you write code, answer:
1. What should be created? - e.g., "phone with a screen"
2. What steps are needed? - list of Blender operations
3. What should be configurable? - sizes, proportions

### 2.2 Test Manually

Run the workflow manually in Blender and record:
- Which tools you used
- In what order
- What parameters you set

### 2.3 Example: Phone

```
Goal: Phone with rounded edges and an inset screen

Steps:
1. Create a cube
2. Switch to Edit mode
3. Select all
4. Bevel the edges (round corners)
5. Select the top face
6. Inset (screen frame)
7. Extrude down (screen inset)
8. Return to Object mode
```

---

## 3. Step 2: Creating the YAML File

### 3.1 Location

Create a file at:
```
server/router/application/workflows/custom/my_workflow.yaml
```

### 3.2 Basic Structure

```yaml
# my_workflow.yaml

# === METADATA (required) ===
name: my_workflow                    # Unique name (snake_case)
description: Description of what the workflow does    # What the workflow creates

# === METADATA (optional) ===
category: my_category                # Category (e.g., furniture, electronics)
author: Your Name                      # Author
version: "1.0"                        # Version

# === TRIGGERS (optional) ===
trigger_pattern: box_pattern          # Geometry pattern to detect
trigger_keywords:                     # Keywords that trigger the workflow
  - phone
  - smartphone
  - cell phone

# === STEPS (required) ===
steps:
  - tool: tool_name
    params:
      param1: value1
    description: What this step does
```

### 3.3 Naming Conventions

| Element | Convention | Example |
|---------|-----------|----------|
| name | snake_case | `phone_workflow` |
| tool | snake_case | `modeling_create_primitive` |
| params | snake_case | `number_cuts` |

---

## 4. Step 3: Defining Steps

### 4.1 Step Structure

```yaml
- tool: mesh_bevel              # Tool name (required)
  params:                       # Parameters (required)
    offset: 0.05
    segments: 3
  description: Round the edges  # Description (optional)
  condition: "has_selection"    # Condition (optional)
```

### 4.2 Finding Tool Names

Check `_docs/AVAILABLE_TOOLS_SUMMARY.md` or use:

```bash
grep -r "def " server/adapters/mcp/areas/ | grep "@mcp.tool"
```

### 4.3 Common Tools

| Category | Tool | What it does |
|-----------|-----------|---------|
| **Creation** | `modeling_create_primitive` | Creates a cube, sphere, etc. |
| **Transformation** | `modeling_transform_object` | Scales, moves, rotates |
| **Mode** | `system_set_mode` | Changes mode (OBJECT/EDIT) |
| **Selection** | `mesh_select` | Selects geometry |
| **Selection** | `mesh_select_targeted` | Selects by index |
| **Edit** | `mesh_bevel` | Bevels edges |
| **Edit** | `mesh_inset` | Insets a face |
| **Edit** | `mesh_extrude_region` | Extrudes geometry |

### 4.4 Example: First 3 Steps of the Phone

```yaml
steps:
  # Step 1: Create a cube
  - tool: modeling_create_primitive
    params:
      type: CUBE
    description: Create the base cube

  # Step 2: Switch to Edit mode
  - tool: system_set_mode
    params:
      mode: EDIT
    description: Enter edit mode

  # Step 3: Select all
  - tool: mesh_select
    params:
      action: all
    description: Select all geometry
```

---

## 5. Step 4: Adding Conditions

Conditions (`condition`) allow skipping steps when they are not needed.

### 5.1 Why Conditions?

```yaml
# WITHOUT condition - error if already in EDIT mode
- tool: system_set_mode
  params: { mode: EDIT }

# WITH condition - skip if already in EDIT
- tool: system_set_mode
  params: { mode: EDIT }
  condition: "current_mode != 'EDIT'"
```

### 5.2 Condition Syntax

```yaml
# String comparisons
condition: "current_mode == 'EDIT'"
condition: "current_mode != 'OBJECT'"
condition: "active_object == 'Cube'"

# Boolean variables
condition: "has_selection"
condition: "not has_selection"

# Numeric comparisons
condition: "object_count > 0"
condition: "selected_verts >= 4"

# Math functions in conditions - TASK-060
condition: "floor(table_width / plank_width) > 5"

# Logical operators
condition: "current_mode == 'EDIT' and has_selection"
condition: "current_mode == 'OBJECT' or not has_selection"

# Parentheses (grouping) - TASK-056-2
condition: "(leg_angle > 0.5 and has_selection) or (object_count >= 3)"
condition: "not (leg_style == 'straight' or leg_angle == 0)"
```

### 5.2a Complex Logical Expressions (TASK-056-2)

The condition system supports **parentheses** for grouping and correct **operator precedence**:

Operator precedence (from highest to lowest):
1. `()` - Parentheses (grouping)
2. `not` - Logical NOT
3. `and` - Logical AND
4. `or` - Logical OR

Examples:

```yaml
# Nested parentheses
condition: "(leg_angle > 0.5 and has_selection) or (object_count >= 3 and current_mode == 'EDIT')"

# NOT with parentheses
condition: "not (leg_style == 'straight' or (leg_angle < 0.1 and leg_angle > -0.1))"

# Precedence without parentheses (NOT > AND > OR)
condition: "width > 1.0 and length > 1.0 and height > 0.5 or is_tall"
# Evaluates as: ((width > 1.0 and length > 1.0) and height > 0.5) or is_tall

# Multiple AND/OR
condition: "A and B or C and D"
# Evaluates as: (A and B) or (C and D)

# Complex nested conditions
condition: "((A or B) and (C or D)) or (E and not F)"
```

Best practices:

```yaml
# ✅ GOOD - parentheses for readability
condition: "(leg_angle_left > 0.5) or (leg_angle_left < -0.5)"

# ⚠️ Works but less readable - relies on precedence
condition: "leg_angle_left > 0.5 or leg_angle_left < -0.5"

# ✅ GOOD - nested conditions with clear grouping
condition: "(current_mode == 'EDIT' and has_selection) or (current_mode == 'OBJECT' and object_count > 0)"
```

### 5.3 Available Variables

| Variable | Type | Example |
|---------|-----|----------|
| `current_mode` | str | `'OBJECT'`, `'EDIT'`, `'SCULPT'` |
| `has_selection` | bool | `True`, `False` |
| `object_count` | int | `0`, `5`, `10` |
| `selected_verts` | int | `0`, `8`, `100` |
| `selected_edges` | int | `0`, `12` |
| `selected_faces` | int | `0`, `6` |
| `active_object` | str | `'Cube'`, `'Sphere'` |

### 5.4 Context Simulation

The router simulates context changes while expanding the workflow:

```yaml
steps:
  # Step 1: Change mode (will execute)
  - tool: system_set_mode
    params: { mode: EDIT }
    condition: "current_mode != 'EDIT'"

  # Step 2: Select (will execute)
  - tool: mesh_select
    params: { action: all }
    condition: "not has_selection"

  # Step 3: Another mode change (SKIPPED - simulation says already EDIT)
  - tool: system_set_mode
    params: { mode: EDIT }
    condition: "current_mode != 'EDIT'"
```

---

## 6. Step 5: Dynamic Parameters

### 6.1 Problem with Static Values

```yaml
# BAD - 0.05 works for a 1m cube, but not for 10m or 1cm
params:
  offset: 0.05
```

### 6.2 Solution 1: $CALCULATE

Compute values mathematically:

```yaml
params:
  # 5% of the smallest dimension
  offset: "$CALCULATE(min_dim * 0.05)"

  # Average of width and height
  size: "$CALCULATE((width + height) / 2)"

  # Rounded
  count: "$CALCULATE(round(depth * 10))"
```

New in TASK-060: `$CALCULATE(...)` also supports comparison operators, logical operators, and ternary expressions.
Comparisons/conditions in `$CALCULATE(...)` return `1.0` (true) / `0.0` (false):

```yaml
params:
  # Numeric flag from a condition
  has_objects: "$CALCULATE(object_count > 0)"

  # Ternary expression
  bevel: "$CALCULATE(0.05 if width > 1.0 else 0.02)"

  # Logic + ternary
  detail: "$CALCULATE(2 if (object_count > 0 and has_selection) else 1)"
```

Available variables:
- `width`, `height`, `depth` - object dimensions
- `min_dim`, `max_dim` - min/max dimensions
- All parameters from `defaults` and `modifiers`

Available math functions (TASK-056-1):

| Category | Functions | Description |
|-----------|---------|------|
| **Basic** | `abs()`, `min()`, `max()` | Absolute value, minimum, maximum |
| **Rounding** | `round()`, `floor()`, `ceil()`, `trunc()` | Round, floor, ceil, truncate |
| **Power/Root** | `sqrt()`, `pow()`, `**` | Square root, power |
| **Trigonometric** | `sin()`, `cos()`, `tan()` | Sine, cosine, tangent (radians) |
| **Inverse Trig** | `asin()`, `acos()`, `atan()`, `atan2()` | Arcus sine, arcus cosine, arcus tangent |
| **Angle Conversion** | `degrees()`, `radians()` | Convert radians↔degrees |
| **Logarithmic** | `log()`, `log10()`, `exp()` | Natural log, base-10 log, e^x |
| **Advanced** | `hypot()` | Hypotenuse: sqrt(x² + y²) |

Usage examples:

```yaml
# Compute rotation angle from dimensions
rotation: ["$CALCULATE(atan2(height, width))", 0, 0]

# Logarithmic scaling
scale: "$CALCULATE(log10(100))"  # = 2.0

# Exponential decay
alpha: "$CALCULATE(exp(-distance / falloff_radius))"

# Diagonal (hypotenuse)
diagonal: "$CALCULATE(hypot(width, height))"

# Degrees to radians
angle_rad: "$CALCULATE(radians(45))"  # = 0.785...

# Tangent for slope
slope: "$CALCULATE(tan(leg_angle))"
```

### 6.3 Solution 2: $AUTO_*

Ready-made predefined values:

```yaml
params:
  # Automatic bevel (5% of min dimension)
  offset: "$AUTO_BEVEL"

  # Automatic inset (3% of min XY)
  thickness: "$AUTO_INSET"

  # Automatic extrude (10% depth down)
  move: [0, 0, "$AUTO_EXTRUDE_NEG"]
```

Full list of $AUTO_*:

| Parameter | Formula | Description |
|----------|------|------|
| `$AUTO_BEVEL` | `min * 5%` | Standard bevel |
| `$AUTO_BEVEL_SMALL` | `min * 2%` | Small bevel |
| `$AUTO_BEVEL_LARGE` | `min * 10%` | Large bevel |
| `$AUTO_INSET` | `XY_min * 3%` | Standard inset |
| `$AUTO_INSET_THICK` | `XY_min * 5%` | Thick inset |
| `$AUTO_EXTRUDE` | `Z * 10%` | Extrude up |
| `$AUTO_EXTRUDE_NEG` | `Z * -10%` | Extrude down |
| `$AUTO_EXTRUDE_DEEP` | `Z * 20%` | Deep extrude |
| `$AUTO_SCREEN_DEPTH` | `Z * 50%` | Screen depth |
| `$AUTO_SCREEN_DEPTH_NEG` | `Z * -50%` | Screen inset |
| `$AUTO_SCALE_SMALL` | `[80%, 80%, 80%]` | Scale down to 80% |

### 6.4 Solution 3: Simple Variables

Reference values from the context:

```yaml
params:
  mode: "$mode"        # Current mode
  move: [0, 0, "$depth"]  # Using object dimensions
```

### 6.5 Resolution Order

0. `{var}` - string interpolation (TASK-058; only inside strings)
1. `$CALCULATE(...)` - evaluate math expressions first
2. `$AUTO_*` - then predefined values
3. `$variable` - finally simple variables

---

## 6b. Loops and String Interpolation (TASK-058)

When a workflow has many repetitive elements (e.g., countertop planks, windows in a facade, buttons on a phone), manually copying steps becomes unreadable. The solution is **loops** + **string interpolation**.

### 6b.1 Interpolation `{var}`

In strings you can use placeholders `{var}` (e.g., `{i}`, `{row}`, `{col}`) that will be substituted before `$CALCULATE(...)` evaluations and before `condition` evaluation:

```yaml
params:
  name: "TablePlank_{i}"
condition: "{i} <= plank_count"
description: "Create plank {i} of {plank_count}"
```

Escaping: `{{` and `}}` represent literal `{` and `}`.

### 6b.2 Loop on a Step

The simplest loop (inclusive range):
```yaml
loop:
  variable: i
  range: "1..plank_count"
```

Nested loops (grid):
```yaml
loop:
  variables: [row, col]
  ranges: ["0..(rows - 1)", "0..(cols - 1)"]
```

### 6b.3 Step Order: `loop.group` (interleaving)

If you want steps executed "per iteration" (e.g., `create_i → transform_i`), set the same `loop.group` on successive steps:

```yaml
- tool: modeling_create_primitive
  params: { primitive_type: CUBE, name: "TablePlank_{i}" }
  loop: { group: planks, variable: i, range: "1..plank_count" }

- tool: modeling_transform_object
  params:
    name: "TablePlank_{i}"
    location: ["$CALCULATE(-table_width/2 + plank_actual_width * ({i} - 0.5))", 0, 0]
  loop: { group: planks, variable: i, range: "1..plank_count" }
```

Tip: for shorter YAML use anchors and `<<` merge (PyYAML `safe_load` supports this).

## 7. Step 6: Optional Steps and Adaptation

> English deep dive: For a precise explanation of how adaptation (TASK-051) and `condition` interact (two filters),
> plus the full expansion order (computed params → loops/interpolation → `$CALCULATE/$AUTO_/$variable` → `condition`),
> see: [workflow-execution-pipeline.md](./workflow-execution-pipeline.md).

### 7.1 Problem: Overly Detailed Workflow

Imagine a `picnic_table` workflow with 49 steps that creates a picnic table with benches and an A-frame. When a user says "simple table with 4 legs", running the full workflow is excessive.

### 7.2 Solution: Confidence-Based Adaptation (TASK-051)

The router automatically adapts the workflow based on matching confidence:

| Confidence | Strategy | Behavior |
|------------|-----------|------------|
| **HIGH** (≥0.90) | `FULL` | Execute ALL steps |
| **MEDIUM** (≥0.75) | `FILTERED` | Core + matching optional steps |
| **LOW** (≥0.60) | `CORE_ONLY` | Only CORE steps |
| **NONE** (<0.60) | `CORE_ONLY` | Only CORE (fallback) |

### 7.3 How the Intent Classifier Works

**WorkflowIntentClassifier** computes confidence based on:

1. **Semantic Similarity (LaBSE embeddings)** - compares the user prompt to:
   - `sample_prompts` from the workflow YAML
   - `description` of the workflow
   - `trigger_keywords`

2. **Thresholds for confidence levels:**
   ```python
   HIGH_THRESHOLD = 0.90   # Very high confidence
   MEDIUM_THRESHOLD = 0.75  # Moderate confidence
   LOW_THRESHOLD = 0.60     # Minimum required confidence
   ```

3. **Classification examples:**
   ```
   "create a picnic table"           → 0.95 (HIGH)   - direct match
   "make outdoor table with benches" → 0.82 (MEDIUM) - semantically similar
   "rectangular table with 4 legs"   → 0.65 (LOW)    - partial match
   "build a shelf"                   → 0.35 (NONE)   - no match
   ```

### 7.4 Marking Steps as Optional

Use `optional: true` and `tags` to mark steps that can be skipped:

```yaml
steps:
  # Core step - always executed
  - tool: modeling_create_primitive
    params:
      primitive_type: CUBE
      name: "TableTop"
    description: Create the tabletop
    # optional: false  # Default, no need to specify

  # Optional step - may be skipped at low confidence
  - tool: modeling_create_primitive
    params:
      primitive_type: CUBE
      name: "BenchLeft"
    description: Create the left bench
    optional: true
    tags: ["bench", "seating", "side"]
```

### 7.5 How Tags Work at MEDIUM Confidence

**WorkflowAdapter** filters optional steps based on tags:

```python
# Filtering algorithm (pseudocode):
for step in optional_steps:
    # 1. Tag matching (fast, keyword-based)
    if any(tag.lower() in user_prompt.lower() for tag in step.tags):
        include_step(step)
        continue

    # 2. Semantic similarity fallback (for steps without tags)
    if step.description and similarity(prompt, description) >= 0.6:
        include_step(step)
```

Filtering examples:

```yaml
# Prompt: "table with benches"
# Step tags: ["bench", "seating"]
# Result: Step INCLUDED (tag "bench" matches "benches")

# Prompt: "simple table with 4 legs"
# Step tags: ["bench", "seating"]
# Result: Step SKIPPED (no tag matches)

# Prompt: "table with A-frame legs"
# Step tags: ["a-frame", "structural"]
# Result: Step INCLUDED (tag "a-frame" matches)
```

### 7.6 Tag Best Practices

```yaml
# GOOD - specific, searchable tags
tags: ["bench", "seating", "side", "left"]
tags: ["a-frame", "structural", "cross-support"]
tags: ["handle", "grip", "ergonomic"]
tags: ["decoration", "detail", "ornament"]

# BAD - too generic
tags: ["extra", "optional"]  # Non-specific
tags: ["part"]               # Everything is a "part"
```

Recommended tag categories:

| Category | Example tags | Use |
|-----------|------------------|--------------|
| **Components** | `bench`, `leg`, `shelf`, `drawer` | Main parts |
| **Structure** | `a-frame`, `cross-support`, `diagonal`, `brace` | Structural elements |
| **Position** | `left`, `right`, `front`, `back`, `top`, `bottom` | Location |
| **Function** | `seating`, `storage`, `decoration` | Purpose |
| **Style** | `ornate`, `minimal`, `modern`, `rustic` | Aesthetics |

### 7.7 Groups of Optional Steps

For complex workflows, group related optional steps using shared tags:

```yaml
steps:
  # === CORE: Always executed ===
  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "TableTop" }
    description: Table top

  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "Leg_FL" }
    description: Front-left leg

  # ... other legs ...

  # === OPTIONAL GROUP 1: A-Frame supports ===
  # Shared tags: ["a-frame", "structural"]

  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "CrossBeam_Front" }
    description: Front crossbeam for A-frame
    optional: true
    tags: ["a-frame", "cross-support", "structural"]

  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "CrossBeam_Back" }
    description: Back crossbeam for A-frame
    optional: true
    tags: ["a-frame", "cross-support", "structural"]

  # === OPTIONAL GROUP 2: Benches ===
  # Shared tags: ["bench", "seating"]

  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "BenchLeft" }
    description: Left bench
    optional: true
    tags: ["bench", "seating", "left"]

  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "BenchRight" }
    description: Right bench
    optional: true
    tags: ["bench", "seating", "right"]
```

### 7.8 Finalization with Adaptation

Finalization steps (join, rename, material) must handle different variants:

```yaml
steps:
  # ... steps that create geometry ...

  # === FINALIZE: Minimal variant (CORE) ===
  - tool: modeling_join_objects
    params:
      object_names:
        - "TableTop"
        - "Leg_FL"
        - "Leg_FR"
        - "Leg_BL"
        - "Leg_BR"
    description: Join 5 basic table parts

  - tool: scene_rename_object
    params:
      old_name: "Leg_BR"
      new_name: "Table"
    description: Rename object to "Table"

  # === FINALIZE: A-frame variant (add when we have a-frame) ===
  - tool: modeling_join_objects
    params:
      object_names:
        - "Table"
        - "CrossBeam_Front"
        - "CrossBeam_Back"
    description: Attach A-frame elements to the table
    optional: true
    tags: ["a-frame", "structural"]

  # === FINALIZE: Benches variant (add when we have benches) ===
  - tool: modeling_join_objects
    params:
      object_names:
        - "Table"
        - "BenchLeft"
        - "BenchRight"
    description: Attach benches to the table
    optional: true
    tags: ["bench", "seating"]

  - tool: scene_rename_object
    params:
      old_name: "BenchRight"
      new_name: "Picnic_Table"
    description: Rename the full picnic table
    optional: true
    tags: ["bench", "seating"]
```

### 7.9 Example: Picnic Table with Full Adaptation

```yaml
# picnic_table.yaml (simplified)
name: picnic_table_workflow
description: Picnic table with optional benches and A-frame

sample_prompts:
  - "create a picnic table"
  - "make outdoor table with benches"
  - "build a park table"

steps:
  # === CORE STEPS (always executed) ===
  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "TableTop" }
    description: Table top

  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "Leg_FL" }
    description: Front-left leg (may be slanted or straight)

  # ... more legs ...

  # === OPTIONAL: A-Frame elements ===
  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "CrossBeam" }
    description: Crossbeam connecting A-frame legs
    optional: true
    tags: ["a-frame", "structural", "cross-support"]

  # === OPTIONAL: Bench elements ===
  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "BenchLeft" }
    description: Left bench
    optional: true
    tags: ["bench", "seating", "left"]
```

Adaptation results:

```
"create a picnic table"       → HIGH (0.95)   → 57 steps (full workflow)
"table with A-frame legs"     → MEDIUM (0.78) → 45 steps (core + a-frame)
"table with benches"          → MEDIUM (0.80) → 48 steps (core + benches)
"simple table with 4 legs"    → LOW (0.65)    → 25 steps (core only)
```

### 7.10 Per-Step Adaptation Control (TASK-055-FIX-5)

Problem: Conflict between semantic filtering and mathematical conditions.

For MEDIUM confidence, WorkflowAdapter filters optional steps by tag matching. When a step is governed by a **mathematical condition** (`leg_angle > 0.5`), semantic filtering may skip it even though the condition is true.

Example:
- Prompt: `"stół z nogami w X"` (Polish)
- Tags: `["x-shaped", "crossed-legs"]` (English)
- Semantic matching: ❌ FAIL (Polish prompt doesn't match English tags)
- Parameters: `leg_angle_left=1.0` (X-shaped)
- Condition: `leg_angle_left > 0.5` → **TRUE**
- Result WITHOUT fix: Step skipped by semantic filtering ❌
- Result WITH fix: Step executed (condition=True) ✅

Solution: `disable_adaptation` flag

```yaml
steps:
  # Conditional step - controlled by mathematical condition
  - tool: mesh_transform_selected
    params:
      translate: ["$CALCULATE(0.342 * sin(leg_angle_left))", 0, "$CALCULATE(0.342 * cos(leg_angle_left))"]
    description: "Stretch leg top for X-shaped configuration"
    condition: "leg_angle_left > 0.5 or leg_angle_left < -0.5"
    optional: true                # Documents: optional feature
    disable_adaptation: true      # CRITICAL: Skip semantic filtering, use condition
    tags: ["x-shaped", "crossed-legs", "leg-stretch"]
```

Flag semantics:

| Flag | Meaning | Purpose |
|-------|-----------|-----|
| `optional: true` | Step is an optional feature | Documentation/readability |
| `disable_adaptation: true` | Skip semantic filtering | Treat as core step |
| `condition` | Mathematical expression | Control execution at runtime |

When to use `disable_adaptation: true`:

✅ Use when:
- The step is controlled by a mathematical condition (`leg_angle > 0.5`)
- The workflow is multilingual (tag matching fails)
- You want precise control via condition, not semantic matching

❌ Don't use when:
- The step is tag-based (benches, decorations) → use semantic filtering
- The step is core → simply remove `optional: true`

Adaptation flow with `disable_adaptation`:

```
MEDIUM confidence:
1. Ensemble matcher sets requires_adaptation=True
2. WorkflowAdapter separates:
   - Core: not optional OR disable_adaptation=True → ALWAYS included
   - Optional: optional=True AND disable_adaptation=False → Semantic filtering
3. All steps with disable_adaptation=True passed to registry
4. ConditionEvaluator evaluates conditions at runtime
5. Only steps with condition=True execute
```

Benefits:
1. ✅ Mathematical precision (condition) > semantic approximation (tags)
2. ✅ Multilingual support (no dependency on tag matching)
3. ✅ Clear intent in YAML
4. ✅ `optional` semantics preserved for documentation

### 7.11 Custom Semantic Parameters (TASK-055-FIX-6 Phase 2)

Problem: How to add custom semantic filters specific to a workflow without modifying the Router code?

Solution: Semantic parameters - custom boolean fields in YAML that automatically act as filters.

#### 7.11.1 What Are Semantic Parameters?

Semantic parameters are any boolean fields added to a workflow step that:
1. Are not explicitly documented in `WorkflowStep` (like `disable_adaptation`, `optional`)
2. Are automatically detected by `WorkflowLoader`
3. Are mapped to keywords by `WorkflowAdapter`
4. Are compared against the user prompt

Example:

```yaml
steps:
  # Basic table structure (always)
  - tool: modeling_create_primitive
    params: { primitive_type: CUBE }
    description: "Create the tabletop"

  # Bench (semantic parameter)
  - tool: modeling_create_primitive
    params: { primitive_type: CUBE }
    description: "Create a bench"
    optional: true
    add_bench: true  # SEMANTIC PARAMETER - detects "bench"/"ławka" in the prompt
    tags: ["bench", "seating"]
```

#### 7.11.2 How It Works

1. **WorkflowLoader** detects `add_bench` as an unknown field
2. It adds it as a dynamic attribute to `WorkflowStep` (via `setattr()`)
3. **WorkflowAdapter** extracts semantic parameters:
   - `add_bench` → keyword: `"bench"`
4. It checks whether `"bench"` appears in the user prompt
5. If YES → include the step; if NO → skip the step

Name conversion:

| Parameter name | Extracted word | Matching |
|-----------------|-------------------|-------------|
| `add_bench` | `"bench"` | bench, ławka, банка |
| `include_stretchers` | `"stretchers"` | stretchers, rozpórki |
| `decorative` | `"decorative"` | decorative, ozdobny |
| `add_handles` | `"handles"` | handles, uchwyty |

The system strips prefixes `add_`, `include_` and replaces `_` with spaces.

#### 7.11.3 Positive vs Negative Matching

Positive (`true`) - Enable the step if the keyword **appears** in the prompt:

```yaml
- tool: modeling_create_primitive
  params: { primitive_type: CUBE }
  description: "Create a bench"
  optional: true
  add_bench: true  # Enable ONLY when "bench" in prompt
  tags: ["bench"]
```

Negative (`false`) - Enable the step if the keyword **does NOT appear** in the prompt:

```yaml
- tool: modeling_create_primitive
  params: { primitive_type: CUBE }
  description: "Simple table without decoration"
  optional: true
  decorative: false  # Enable ONLY when "decorative" NOT in prompt
```

Why `true`/`false`? Mutually exclusive variants

The boolean value indicates the direction of matching, allowing mutually exclusive variants in one workflow:

```yaml
steps:
  # Core: always executed
  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "TableTop" }
    description: "Create the tabletop"

  # Variant A: With bench (when user wants)
  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "Bench" }
    description: "Create a bench"
    optional: true
    add_bench: true  # Enable when "bench" IS in prompt

  # Variant B: Extra support (when NO bench)
  - tool: modeling_create_primitive
    params: { primitive_type: CYLINDER, name: "ExtraSupport" }
    description: "Add extra support (because there is no bench for stability)"
    optional: true
    add_bench: false  # Enable when "bench" is NOT in prompt
```

Results:

| User prompt | `add_bench: true` (Bench) | `add_bench: false` (Extra support) |
|--------------------|---------------------------|------------------------------------------|
| `"table"` | ❌ Skipped | ✅ Included (no bench → needs support) |
| `"table with bench"` | ✅ Included | ❌ Skipped (bench present → no extra support) |

More examples:

```yaml
# Decorative vs Simple
- tool: mesh_bevel
  params: { offset: 0.1 }
  description: "Large bevels (decorative)"
  optional: true
  decorative: true  # Enable when "decorative"/"ozdobny" in prompt

- tool: mesh_bevel
  params: { offset: 0.01 }
  description: "Small bevels (minimalist)"
  optional: true
  decorative: false  # Enable when "decorative" NOT in prompt

# With Handles vs Without
- tool: modeling_create_primitive
  params: { primitive_type: CYLINDER, name: "Handle" }
  description: "Create a handle"
  optional: true
  add_handles: true  # Enable when "handles"/"uchwyty" in prompt

- tool: mesh_bevel
  params: { offset: 0.05 }
  description: "Bevel edges (instead of handles)"
  optional: true
  add_handles: false  # Enable when "handles" NOT in prompt
```

Key understanding:

Without `true`/`false` the system wouldn't know whether to:
- Enable the step when the word **appears** (positive match)
- Enable the step when the word **does NOT appear** (negative match)

With `true`/`false`:
- `true` = "User wants this feature" → enable when the word is in the prompt
- `false` = "User does NOT want this feature" → enable when the word is ABSENT in the prompt

This enables **mutually exclusive variants** (either bench or support, but not both) within one workflow.

#### 7.11.4 Usage Examples

Example 1: Picnic Table with Bench

```yaml
name: picnic_table_workflow
description: Picnic table with optional bench

defaults:
  leg_angle: 0.32

steps:
  # === CORE (always) ===
  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "TableTop" }
    description: "Table top"

  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "Leg_FL" }
    description: "Table leg"

  # === OPTIONAL: Bench (semantic parameter) ===
  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "BenchSeat" }
    description: "Bench seat"
    optional: true
    add_bench: true  # Semantic filter
    tags: ["bench", "seating"]

  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "BenchLeg" }
    description: "Bench leg"
    optional: true
    add_bench: true  # Semantic filter
    tags: ["bench"]

  # === OPTIONAL: Stretchers (semantic parameter) ===
  - tool: modeling_create_primitive
    params: { primitive_type: CYLINDER, name: "Stretcher" }
    description: "Stretcher between legs"
    optional: true
    include_stretchers: true  # Semantic filter
    tags: ["stretchers", "support", "structural"]
```

Matching results:

| User prompt | Bench enabled? | Stretchers enabled? |
|--------------------|-----------------|--------------------|
| `"picnic table"` | ❌ No | ❌ No |
| `"picnic table with bench"` | ✅ Yes (`"ławką"`) | ❌ No |
| `"picnic table with bench"` | ✅ Yes (`"bench"`) | ❌ No |
| `"table with stretchers"` | ❌ No | ✅ Yes (`"stretchers"`) |
| `"table with bench and stretchers"` | ✅ Yes | ✅ Yes |

#### 7.11.5 Filtering Strategy (3 Levels)

WorkflowAdapter uses a multi-level strategy for MEDIUM confidence:

```
1. Tag matching (fast)
   → Check if any tag appears in the prompt

2. Semantic parameters (Phase 2)
   → Check custom boolean fields

3. Semantic similarity (slow, fallback)
   → LaBSE embeddings on description
```

Example:

```yaml
- tool: modeling_create_primitive
  params: { primitive_type: CUBE }
  description: "Create a bench for seating"
  optional: true
  add_bench: true
  tags: ["bench", "seating"]
```

Prompt: `"stół z ławką"`

1. ✅ **Tag matching**: `"ławką"` does not match `"bench"` → SKIP
2. ✅ **Semantic parameter**: `add_bench` → `"bench"` → maps `"ławką"` (LaBSE) → MATCH!
3. ❌ **Semantic similarity**: NOT checked (match already found)

#### 7.11.6 Best Practices

✅ GOOD - Combine semantic parameters with tags:

```yaml
- tool: modeling_create_primitive
  params: { primitive_type: CUBE }
  description: "Create a bench"
  optional: true
  add_bench: true        # Semantic parameter (multilingual)
  tags: ["bench"]        # Fallback tag matching
```

❌ BAD - Only semantic parameter, no tags:

```yaml
- tool: modeling_create_primitive
  params: { primitive_type: CUBE }
  description: "Create a bench"
  optional: true
  add_bench: true        # What if I change the parameter name?
  # No tags - less reliable
```

✅ GOOD - Descriptive parameter names:

```yaml
add_bench: true           # Clear: looks for "bench"
include_handles: true     # Clear: looks for "handles"
decorative: true          # Clear: looks for "decorative"
```

❌ BAD - Ambiguous names:

```yaml
feature_1: true           # Ambiguous: what word is it looking for?
enable_extra: true        # Ambiguous: what's "extra"?
has_option: true          # Ambiguous: which option?
```

#### 7.11.7 When to Use Semantic Parameters

| Feature | Use for | Example |
|---------|------|----------|
| **Explicit fields** | Documented behavior with logic in code | `disable_adaptation`, `optional`, `condition` |
| **Semantic parameters** | Workflow-specific filters | `add_bench`, `include_stretchers`, `decorative` |
| **Tags** | Quick keyword matching | `tags: ["bench", "seating"]` |

Use semantic parameters when:
✅ You want a workflow-specific filter without changing Router code
✅ You need multilingual matching (LaBSE)
✅ The parameter name naturally maps to a concept (e.g., `add_bench` → `"bench"`)

Use tags when:
✅ You need a list of synonyms
✅ You want fast matching (no LaBSE)
✅ You have many word variants (e.g., `["bench", "seat", "seating"]`)

#### 7.11.8 System Flexibility

Automatic loading (TASK-055-FIX-6 Phase 1):
- All `WorkflowStep` fields are loaded automatically from YAML
- New fields added to `WorkflowStep` → automatically supported
- No manual loader ↔ dataclass sync required

Dynamic attributes (TASK-055-FIX-6 Phase 2):
- Unknown YAML fields → dynamic attributes (`setattr()`)
- Automatically detected by `WorkflowAdapter`
- No need to modify the `WorkflowStep` class

---

## 7b. Interactive Parameter Resolution (TASK-055)

### 7b.1 Overview

The parameter system supports **interactive questioning** the user for values when the prompt mentions a parameter but does not provide an explicit value.

Example:
```
Prompt: "table with legs at 45 degrees"

The system recognizes:
  - Workflow: picnic_table_workflow ✅
  - Parameter "leg_angle" mentioned but value unknown

Reaction:
  → Mark the parameter as "unresolved"
  → LLM asks the user: "What angle for the legs? (range: -90° to +90°, default: 18°)"
```

### 7b.2 Three Levels of Resolution

The system uses **three levels** to resolve parameters:

| Priority | Source | Description |
|-----------|--------|------|
| 1. YAML modifiers | Highest | Semantic match to `modifiers` in the workflow |
| 2. Learned mappings | Medium | Remembered mappings from past interactions |
| 3. LLM interaction | Lowest | Ask the user when parameter is mentioned but unknown |

### 7b.3 Parameter Definition in YAML

```yaml
# In the workflow.yaml file

# Default values
defaults:
  leg_angle_left: 0.32
  leg_angle_right: -0.32

# Predefined modifiers (priority 1)
modifiers:
  "straight legs":
    leg_angle_left: 0
    leg_angle_right: 0
    negative_signals: ["X", "crossed", "angled", "diagonal", "skośne", "skrzyżowane"]  # TASK-055-FIX-2
  "angled legs":
    leg_angle_left: 0.32
    leg_angle_right: -0.32

# Parameter schemas for interactive resolution (priority 3)
parameters:
  leg_angle_left:
    type: float                     # Type: float, int, string, bool
    range: [-1.57, 1.57]           # Value range (optional)
    default: 0.32                   # Default value
    description: "Rotation angle for left table legs"
    semantic_hints:                 # English keywords - LaBSE handles other languages
      - angle      # Auto-matches: kąt (PL), Winkel (DE), ángulo (ES)
      - legs       # Auto-matches: nogi (PL), Beinen (DE), pieds (FR)
      - crossed    # Auto-matches: skrzyżowane (PL), croisé (FR)
    group: leg_angles              # Parameter group (optional)
```

### 7b.4 How semantic_hints Work

`semantic_hints` are used to detect whether the prompt **mentions** a parameter.

Three detection mechanisms:

1. **LaBSE similarity (whole prompt)** - compares the entire prompt to the hint
   ```
   "table with legs at 45 degrees" ↔ "angle" = 0.42
   ```

2. **Literal matching** - whether the hint literally appears in the prompt
   ```
   "table with angle" contains "angle" → relevance = 0.8
   ```

3. **Semantic word matching (TASK-055)** - whether ANY word in the prompt is semantically similar to the hint
   ```
   "Tisch mit Beinen" → "Beinen" ↔ "legs" = 0.757 → relevance = 0.75
   ```

### 7b.5 Automatic Multilingual Support

ONLY English hints are required!

Thanks to **semantic word matching** with LaBSE, the system automatically recognizes words from other languages:

| Language | Word in prompt | Match to hint (EN) | Similarity |
|-------|----------------|--------------------------|------------|
| Polish | "kątem" | "angle" | 0.879 |
| German | "Beinen" | "legs" | 0.757 |
| French | "pieds" | "legs" | 0.939 |
| Spanish | "ángulo" | "angle" | 0.959 |
| Italian | "angolo" | "angle" | 0.935 |

You do not need to add hints for every language - LaBSE automatically maps concepts cross-language.

### 7b.6 Thresholds

| Parameter | Value | Meaning |
|----------|---------|-----------|
| `relevance_threshold` | 0.4 | Min. similarity to consider a parameter "mentioned" |
| `memory_threshold` | 0.85 | Min. similarity to use a remembered mapping |
| Literal match boost | 0.8 | Relevance when hint literally appears in prompt |
| Semantic word threshold | 0.65 | Min. similarity for single-word matches |
| Semantic word boost | 0.75 | Relevance when a word semantically matches |

### 7b.7 Example: Table with Legs at Angle X

Workflow YAML:
```yaml
defaults:
  leg_angle_left: 0.32

modifiers:
  "straight legs":
    leg_angle_left: 0
    leg_angle_right: 0
    negative_signals: ["X", "crossed", "angled", "diagonal", "skośne", "skrzyżowane"]  # TASK-055-FIX-2

parameters:
  leg_angle_left:
    type: float
    range: [-1.57, 1.57]
    default: 0.32
    description: "Rotation angle for left table legs"
    semantic_hints:
      - angle      # LaBSE matches: kątem (PL)=0.879, ángulo (ES)=0.959, angolo (IT)=0.935
      - legs       # LaBSE matches: Beinen (DE)=0.757, pieds (FR)=0.939, nogi (PL)=0.967
      - crossed    # LaBSE matches: skrzyżowane (PL)=0.855, croisés (FR)=0.887
```

Scenarios:

| Prompt | Resolution | Result |
|--------|-------------|-------|
| "create a picnic table" | defaults | leg_angle=0.32 |
| "table with straight legs" | modifier match | leg_angle=0 |
| "stół z prostymi nogami" | modifier match (LaBSE) | leg_angle=0 |
| "table with legs at 45°" | **UNRESOLVED** → ask | LLM asks the user |
| "Tisch mit Beinen im Winkel" | **UNRESOLVED** → ask | LLM asks the user |

### 7b.8 Best Practices for semantic_hints

```yaml
# GOOD - English only, specific
semantic_hints:
  - angle      # LaBSE will match: kąt, Winkel, ángulo, angolo
  - legs       # LaBSE will match: nogi, Beinen, pieds, piernas
  - crossed    # LaBSE will match: skrzyżowane, gekreuzt, croisé

# BAD - too general
semantic_hints:
  - table      # Too general, always matches
  - create     # Not relevant to a parameter
```

Tips:
1. Use 2-4 specific English hints per parameter
2. LaBSE automatically matches other languages (do not add translations)
3. Avoid overly general words
4. Hints should relate to the **parameter**, not the workflow

---

## 8. Step 7: Testing

### 7.1 YAML Syntax Validation

```bash
# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('server/router/application/workflows/custom/my_workflow.yaml'))"
```

### 7.2 Load Test

```python
from server.router.application.workflows.registry import WorkflowRegistry

registry = WorkflowRegistry()
registry.load_custom_workflows()

# Check if workflow loaded
print(registry.get_all_workflows())

# Get the definition
definition = registry.get_definition("my_workflow")
print(definition)
```

### 7.3 Expansion Test

```python
# Expand the workflow with context
calls = registry.expand_workflow(
    "my_workflow",
    context={
        "dimensions": [2.0, 4.0, 0.5],
        "mode": "OBJECT",
        "has_selection": False,
    }
)

# Inspect the result
for call in calls:
    print(f"{call.tool_name}: {call.params}")
```

### 7.4 Trigger Test

```python
# Test keyword matching
workflow = registry.find_by_keywords("create a phone")
print(f"Found: {workflow}")
```

---

## 9. Complete Example

### 8.1 Workflow: Phone with Screen

```yaml
# server/router/application/workflows/custom/phone_complete.yaml

name: phone_complete
description: Phone with rounded corners and an inset screen
category: electronics
author: BlenderAI
version: "2.0"

trigger_keywords:
  - phone
  - smartphone
  - cell phone
  - iphone
  - android

steps:
  # === PHASE 1: Create base geometry ===

  - tool: modeling_create_primitive
    params:
      type: CUBE
    description: Create the base cube for the phone

  # === PHASE 2: Switch to Edit mode ===

  - tool: system_set_mode
    params:
      mode: EDIT
    description: Enter edit mode
    condition: "current_mode != 'EDIT'"

  # === PHASE 3: Selection and editing ===

  - tool: mesh_select
    params:
      action: all
    description: Select all geometry
    condition: "not has_selection"

  - tool: mesh_bevel
    params:
      offset: "$AUTO_BEVEL"
      segments: 3
    description: Bevel all edges

  # === PHASE 4: Create the screen ===

  - tool: mesh_select
    params:
      action: none
    description: Deselect everything

  - tool: mesh_select_targeted
    params:
      mode: FACE
      indices: [5]
    description: Select the top face (screen)

  - tool: mesh_inset
    params:
      thickness: "$AUTO_INSET"
    description: Create the screen frame

  - tool: mesh_extrude_region
    params:
      move:
        - 0
        - 0
        - "$AUTO_SCREEN_DEPTH_NEG"
    description: Inset the screen

  # === PHASE 5: Finalization ===

  - tool: system_set_mode
    params:
      mode: OBJECT
    description: Return to Object mode
    condition: "current_mode != 'OBJECT'"
```

### 8.2 Workflow Test

```python
from server.router.application.workflows.registry import WorkflowRegistry

registry = WorkflowRegistry()
registry.load_custom_workflows()

# Expand with phone dimensions (7cm x 15cm x 8mm)
calls = registry.expand_workflow(
    "phone_complete",
    context={
        "dimensions": [0.07, 0.15, 0.008],
        "mode": "OBJECT",
        "has_selection": False,
    }
)

print(f"Workflow expanded to {len(calls)} steps:")
for i, call in enumerate(calls, 1):
    print(f"  {i}. {call.tool_name}")
    for k, v in call.params.items():
        print(f"      {k}: {v}")
```

Expected result:
```
Workflow expanded to 9 steps:
  1. modeling_create_primitive
      type: CUBE
  2. system_set_mode
      mode: EDIT
  3. mesh_select
      action: all
4. mesh_bevel
      offset: 0.0004  # 5% of 8mm
      segments: 3
  5. mesh_select
      action: none
  6. mesh_select_targeted
      mode: FACE
      indices: [5]
  7. mesh_inset
      thickness: 0.0021  # 3% of 7cm
  8. mesh_extrude_region
      move: [0, 0, -0.004]  # 50% of 8mm down
  9. system_set_mode
      mode: OBJECT
```

---

## 10. Common Errors

### 9.1 YAML Syntax Errors

```yaml
# BAD - missing space after colon
params:
  offset:0.05

# GOOD
params:
  offset: 0.05
```

```yaml
# BAD - incorrect indentation
steps:
- tool: mesh_bevel
params:
  offset: 0.05

# GOOD
steps:
  - tool: mesh_bevel
    params:
      offset: 0.05
```

### 9.2 Condition Errors

```yaml
# BAD - missing quotes in string
condition: current_mode != EDIT

# GOOD
condition: "current_mode != 'EDIT'"
```

```yaml
# BAD - typo in variable name
condition: "curent_mode != 'EDIT'"

# GOOD
condition: "current_mode != 'EDIT'"
```

### 9.3 $CALCULATE Errors

```yaml
# BAD - missing closing parenthesis
offset: "$CALCULATE(min_dim * 0.05"

# GOOD
offset: "$CALCULATE(min_dim * 0.05)"
```

```yaml
# BAD - non-existent variable
offset: "$CALCULATE(szerokość * 0.05)"

# GOOD (use English names)
offset: "$CALCULATE(width * 0.05)"
```

### 9.4 Logical Errors

```yaml
# BAD - extrude without selection
- tool: mesh_extrude_region
  params:
    move: [0, 0, 1]

# GOOD - select first
- tool: mesh_select
  params:
    action: all
  condition: "not has_selection"

- tool: mesh_extrude_region
  params:
    move: [0, 0, 1]
```

---

## 11. Advanced Workflow Features (TASK-056)

### 11.1 Enum Validation for Parameters (TASK-056-3)

Restrict parameter values to discrete options:

```yaml
parameters:
  table_style:
    type: string
    enum: ["modern", "rustic", "industrial", "traditional"]
    default: "modern"
    description: Construction style of the table
    semantic_hints: ["style", "design", "styl"]

  detail_level:
    type: string
    enum: ["low", "medium", "high", "ultra"]
    default: "medium"
    description: Mesh detail level (affects polygon count)

  leg_count:
    type: int
    enum: [3, 4, 6, 8]
    default: 4
    description: Number of table legs
```

Benefits:
- Type safety: Invalid values are rejected automatically
- Self-documenting: Clear options for users
- LLM support: LLM sees valid options in the schema

Validation:
- Enum check happens **before** range validation
- Default value must be in the enum list
- Works with any type (string, int, float, bool)
- For `type: string` the router normalizes input (trim + case-insensitive), e.g., `"Sides"` → `"sides"`
- When a parameter is `unresolved`, `router_set_goal` returns the `enum` list in the response (so LLM/caller can choose a valid value)

### 11.2 Computed Parameters (TASK-056-5)

Define parameters computed from other parameters:

```yaml
parameters:
  table_width:
    type: float
    default: 1.2
    description: Table width in meters

  plank_max_width:
    type: float
    default: 0.10
    description: Maximum width of a single plank

  # Computed: Number of planks needed
  plank_count:
    type: int
    computed: "ceil(table_width / plank_max_width)"
    depends_on: ["table_width", "plank_max_width"]
    description: Number of planks needed to cover the table width

  # Computed: Actual plank width (adjusted to fit exactly)
  plank_actual_width:
    type: float
    computed: "table_width / plank_count"
    depends_on: ["table_width", "plank_count"]
    description: Actual width of each plank (adjusted to fit exactly)

  # Computed: Aspect ratio
  aspect_ratio:
    type: float
    computed: "width / height"
    depends_on: ["width", "height"]
    description: Width-to-height ratio

  # Computed: Diagonal distance
  diagonal:
    type: float
    computed: "hypot(width, height)"
    depends_on: ["width", "height"]
    description: Diagonal distance of the tabletop
```

How it works:
1. The router resolves computed parameters in **dependency order** (topological sort)
2. Each computed parameter evaluates its `computed` expression
3. The result becomes available to dependent parameters
4. Cyclic dependencies are detected and rejected

Note (interactive resolution + learned mappings):
- Parameters with `computed: "..."` are treated as internal results and **are not** asked as `unresolved`.
- Computed params are ignored by learned mappings (so you don't "learn" computed values and avoid drift).
- If you really want to override a computed value (advanced), pass it explicitly via `resolved_params` or YAML `modifiers`.

Usage in steps:

```yaml
steps:
  # Use a computed parameter like any other
  - tool: modeling_create_primitive
    params:
      primitive_type: CUBE
      scale: ["$plank_actual_width", 1, 0.1]
    description: "Create a plank with exact width"

  # Conditional step based on a computed value
  - tool: modeling_create_primitive
    params:
      primitive_type: CUBE
    description: "Add extra support for wide tables"
    condition: "plank_count >= 12"
```

Benefits:
- Automatic calculations: No need to repeat formulas in steps
- Dependency tracking: Parameters resolve in correct order
- Dynamic adaptation: Computed values adjust to input dimensions

### 11.3 Step Dependencies and Execution Control (TASK-056-4)

Control step execution order and error handling:

```yaml
steps:
  - id: "create_base"
    tool: modeling_create_primitive
    params:
      primitive_type: CUBE
      name: "Base"
    description: Create the table base
    timeout: 5.0                # Max execution time (seconds)
    max_retries: 2              # Retry attempts on error
    retry_delay: 1.0            # Delay between retries (seconds)

  - id: "scale_base"
    tool: modeling_transform_object
    depends_on: ["create_base"]  # Wait for create_base to finish
    params:
      name: "Base"
      scale: [1, 2, 0.1]
    description: Scale the base to correct proportions
    on_failure: "abort"         # "skip", "abort", "continue"
    priority: 10                # Higher priority = execute earlier

  - id: "add_legs"
    tool: modeling_create_primitive
    depends_on: ["scale_base"]  # Wait for scale_base
    params:
      primitive_type: CUBE
      name: "Leg_1"
    max_retries: 1
    retry_delay: 0.5
```

Fields:

| Field | Type | Description |
|------|-----|------|
| `id` | string | Unique step identifier |
| `depends_on` | list[string] | IDs of steps this step depends on |
| `timeout` | float | Max execution time (seconds) |
| `max_retries` | int | Number of retry attempts on error |
| `retry_delay` | float | Delay between retries |
| `on_failure` | string | "skip", "abort", "continue" |
| `priority` | int | Higher = execute earlier |

Features:
- **Dependency resolution**: Steps execute in the correct order (topological sorting)
- **Cycle detection**: Rejects invalid cyclic dependency graphs
- **Timeout enforcement**: Kills long-running steps
- **Retry mechanism**: Automatically retries failed steps
- **Priority scheduling**: Control execution order for independent steps

Usage examples:

```yaml
# Ensure creation before transformation
- id: "create"
  tool: modeling_create_primitive
  params: {primitive_type: CUBE}

- id: "transform"
  depends_on: ["create"]
  tool: modeling_transform_object
  params: {scale: [1, 2, 1]}

# Retry on failure (e.g., network import)
- tool: import_fbx
  params: {filepath: "https://example.com/model.fbx"}
  max_retries: 3
  retry_delay: 2.0
  timeout: 30.0
  on_failure: "skip"
```

---

## Summary

1. Plan - test manually, write down steps
2. Create the file - in `workflows/custom/name.yaml`
3. Add metadata - name, description, trigger_keywords
4. Define steps - tool, params, description
5. Add conditions - `condition` for robustness (use parentheses when needed)
6. Use dynamic parameters - `$AUTO_*` or `$CALCULATE`
7. Consider advanced features - enum, computed params, dependencies (TASK-056)
8. Test - check loading and expansion

New in TASK-056:
- Extended math functions (tan, atan2, log, exp, hypot, etc.)
- Parentheses in conditions with correct operator precedence
- Enum validation for parameters
- Computed parameters with automatic dependency resolution
- Execution control (timeout, retry, dependencies)

New in TASK-060:
- Math functions in `condition` (e.g., `floor()`, `sqrt()`)
- Comparison/logical operators and ternary in `$CALCULATE(...)`

See also:
- [yaml-workflow-guide.md](./yaml-workflow-guide.md) - Full syntax documentation
- [expression-reference.md](./expression-reference.md) - Expression reference
