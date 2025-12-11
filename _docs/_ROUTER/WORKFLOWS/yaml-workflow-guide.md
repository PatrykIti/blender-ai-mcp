# YAML Workflow Guide

Complete guide to creating custom YAML workflows for the Router Supervisor.

---

## Overview

YAML workflows allow you to define sequences of Blender operations that execute automatically when triggered. Workflows support:

- **Conditional steps** - Skip steps based on scene state with parentheses support (TASK-056-2)
- **Dynamic parameters** - Calculate values with 13+ math functions (TASK-056-1)
- **Smart defaults** - Auto-sized operations with `$AUTO_*` params
- **Keyword triggering** - Automatic activation from user prompts
- **Semantic matching** - LaBSE-powered multilingual prompt matching (TASK-046)
- **Parametric variables** - `$variable` syntax with `defaults` and `modifiers` (TASK-052)
- **Enum validation** - Restrict parameters to discrete choices (TASK-056-3)
- **Computed parameters** - Auto-calculate derived values (TASK-056-5)
- **Step dependencies** - Control execution order with timeout/retry (TASK-056-4)

> **New in TASK-056:** Advanced math functions (tan, atan2, log, exp, hypot), complex boolean expressions with parentheses, enum constraints, computed parameters, and step dependency management. See [Advanced Workflow Features](#advanced-workflow-features-task-056) for details.

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

sample_prompts:                       # Optional: LaBSE semantic matching (TASK-046)
  - "create a table"
  - "make a desk"
  - "zrób stół"                       # Polish - LaBSE supports 109 languages

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
  optional: false            # Optional: can be skipped for low-confidence matches (default: false)
  disable_adaptation: false  # Optional: skip semantic filtering (default: false)
  tags: []                   # Optional: semantic tags for filtering (default: empty)
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
| `()` | `(A and B) or C` | Grouping (parentheses) |

### Complex Boolean Expressions (TASK-056-2)

Conditions support **parentheses** for grouping and proper **operator precedence**:

**Operator Precedence** (highest to lowest):
1. `()` - Parentheses (grouping)
2. `not` - Logical NOT
3. `and` - Logical AND
4. `or` - Logical OR

**Examples:**

```yaml
# Nested parentheses
condition: "(leg_angle > 0.5 and has_selection) or (object_count >= 3 and current_mode == 'EDIT')"

# NOT with parentheses
condition: "not (leg_style == 'straight' or (leg_angle < 0.1 and leg_angle > -0.1))"

# Precedence without parentheses (NOT > AND > OR)
condition: "width > 1.0 and length > 1.0 and height > 0.5 or is_tall"
# Evaluates as: ((width > 1.0 and length > 1.0) and height > 0.5) or is_tall

# Multiple AND/OR operations
condition: "A and B or C and D"
# Evaluates as: (A and B) or (C and D)

# Complex nested conditions
condition: "((A or B) and (C or D)) or (E and not F)"
```

**Best Practices:**

```yaml
# ✅ Good: Use parentheses for clarity
condition: "(leg_angle_left > 0.5) or (leg_angle_left < -0.5)"

# ⚠️ Works but less clear: Relies on precedence
condition: "leg_angle_left > 0.5 or leg_angle_left < -0.5"

# ✅ Good: Nested conditions with clear grouping
condition: "(mode == 'EDIT' and has_selection) or (mode == 'OBJECT' and object_count > 0)"
```

### Available Variables

**Scene Context Variables:**

| Variable | Type | Description |
|----------|------|-------------|
| `current_mode` | str | Current Blender mode |
| `has_selection` | bool | Whether geometry is selected |
| `object_count` | int | Number of objects |
| `selected_verts` | int | Selected vertex count |
| `selected_edges` | int | Selected edge count |
| `selected_faces` | int | Selected face count |
| `active_object` | str | Active object name |

**Workflow Parameters (NEW):**

All workflow parameters from `defaults` and `modifiers` are also available in conditions:

```yaml
defaults:
  leg_angle_left: 0.32
  leg_angle_right: -0.32

steps:
  - tool: mesh_transform_selected
    params:
      translate: ["$CALCULATE(0.342 * sin(leg_angle_left))", 0, "$CALCULATE(0.342 * cos(leg_angle_left))"]
    # Access workflow parameters directly in conditions (no $ prefix)
    condition: "leg_angle_left > 0.5 or leg_angle_left < -0.5"
```

**Important:** Use bare variable names in conditions (`leg_angle_left`), not parameter syntax (`$leg_angle_left`).

### Conditional Steps with `disable_adaptation`

**Problem**: For MEDIUM/LOW confidence, WorkflowAdapter filters optional steps semantically using tags/similarity. This conflicts with mathematical conditions.

**Solution**: Use `disable_adaptation: true` to skip semantic filtering for condition-based steps:

```yaml
defaults:
  leg_angle_left: 0.32
  leg_angle_right: -0.32

steps:
  # Conditional leg stretching - controlled by mathematical condition
  - tool: mesh_transform_selected
    params:
      translate: ["$CALCULATE(0.342 * sin(leg_angle_left))", 0, "$CALCULATE(0.342 * cos(leg_angle_left))"]
    description: "Stretch leg top for X-shaped configuration"
    condition: "leg_angle_left > 0.5 or leg_angle_left < -0.5"
    optional: true                # Documents this is an optional feature
    disable_adaptation: true      # CRITICAL: Skip semantic filtering, use condition only
    tags: ["x-shaped", "crossed-legs", "leg-stretch"]
```

**Field Meanings**:
- `optional: true` → Documents step is an optional feature (for readability)
- `disable_adaptation: true` → Treats step as **core** (always included), bypassing semantic filtering
- `condition` → Mathematical evaluation at runtime determines execution

**When to Use**:
- ✅ Steps controlled by mathematical conditions (`leg_angle > 0.5`)
- ✅ Multilingual workflows where tag matching is unreliable
- ❌ Tag-based optional steps (benches, decorations) → use semantic filtering

### Custom Semantic Filter Parameters (Phase 2)

> **Status:** ✅ Done (TASK-055-FIX-6 Phase 2) | Automatic parameter loading

**What Are Semantic Filters?**

You can add **custom boolean parameters** to workflow steps that act as semantic filters. Unlike explicit fields like `disable_adaptation` (which has hardcoded logic), semantic filters are automatically discovered and matched against user prompts.

**Example:**

```yaml
steps:
  # Core table structure (always included)
  - tool: modeling_create_primitive
    params:
      primitive_type: CUBE
    description: "Create table top"

  # Optional bench (semantic filter)
  - tool: modeling_create_primitive
    params:
      primitive_type: CUBE
    description: "Create bench"
    optional: true
    add_bench: true  # SEMANTIC FILTER: included only if "bench" in prompt
    tags: ["bench", "seating"]
```

**How It Works:**

1. WorkflowLoader automatically detects `add_bench` as a custom parameter
2. Sets it as a dynamic attribute on the WorkflowStep object
3. WorkflowAdapter extracts it during filtering
4. Converts parameter name to keyword: `add_bench` → `"bench"`
5. Checks if keyword appears in user prompt

**User Prompt Matching:**

| User Prompt | `add_bench: true` | Result |
|-------------|-------------------|--------|
| "stół piknikowy" | ❌ No "bench" | Step skipped |
| "stół piknikowy z ławką" | ✅ "ławką" matches | Step included |
| "picnic table with bench" | ✅ "bench" matches | Step included |

**Naming Conventions:**

The adapter strips common prefixes and converts to natural language:

| Parameter Name | Extracted Keyword | Matches |
|----------------|-------------------|---------|
| `add_bench` | "bench" | bench, ławka |
| `include_stretchers` | "stretchers" | stretchers, rozpórki |
| `decorative` | "decorative" | decorative, ozdobny |
| `add_handles` | "handles" | handles, uchwyty |

**Negative Matching:**

Set a semantic filter to `false` to include step when feature is NOT mentioned:

```yaml
- tool: modeling_create_primitive
  params:
    primitive_type: CUBE
  description: "Simple table without decorations"
  optional: true
  decorative: false  # Include only if "decorative" NOT in prompt
```

**Why `true`/`false`? Mutually Exclusive Variants**

The boolean value determines **matching direction**, enabling mutually exclusive variants in a single workflow:

```yaml
steps:
  # Core: always included
  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "TableTop" }
    description: "Create table top"

  # Variant A: WITH bench (when user wants it)
  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "Bench" }
    description: "Create bench"
    optional: true
    add_bench: true  # Include when "bench" IS in prompt

  # Variant B: EXTRA support (when NO bench)
  - tool: modeling_create_primitive
    params: { primitive_type: CYLINDER, name: "ExtraSupport" }
    description: "Add extra support (no bench to provide stability)"
    optional: true
    add_bench: false  # Include when "bench" NOT in prompt
```

**Results:**

| User Prompt | `add_bench: true` (Bench) | `add_bench: false` (Extra Support) |
|-------------|---------------------------|-------------------------------------|
| `"table"` | ❌ Skipped | ✅ Included (no bench → needs support) |
| `"table with bench"` | ✅ Included | ❌ Skipped (has bench → no extra support needed) |

**More Examples:**

```yaml
# Decorative vs Simple
- tool: mesh_bevel
  params: { width: 0.1 }
  description: "Large bevel (decorative)"
  optional: true
  decorative: true  # Include when "decorative" in prompt

- tool: mesh_bevel
  params: { width: 0.01 }
  description: "Small bevel (minimalist)"
  optional: true
  decorative: false  # Include when "decorative" NOT in prompt

# With Handles vs Without
- tool: modeling_create_primitive
  params: { primitive_type: CYLINDER, name: "Handle" }
  description: "Create handle"
  optional: true
  add_handles: true  # Include when "handles" in prompt

- tool: mesh_bevel
  params: { width: 0.05 }
  description: "Round edges (instead of handles)"
  optional: true
  add_handles: false  # Include when "handles" NOT in prompt
```

**Complete Example:**

```yaml
name: picnic_table_workflow
description: Picnic table with optional bench

defaults:
  leg_angle: 0.32

steps:
  # Core structure (always included)
  - tool: modeling_create_primitive
    params: { primitive_type: CUBE }
    description: "Create table top"

  - tool: modeling_create_primitive
    params: { primitive_type: CUBE }
    description: "Create leg"

  # Optional bench (semantic filter)
  - tool: modeling_create_primitive
    params: { primitive_type: CUBE }
    description: "Create bench seat"
    optional: true
    add_bench: true
    tags: ["bench", "seating"]

  - tool: modeling_create_primitive
    params: { primitive_type: CUBE }
    description: "Create bench leg"
    optional: true
    add_bench: true
    tags: ["bench", "seating"]

  # Optional stretchers (semantic filter)
  - tool: modeling_create_primitive
    params: { primitive_type: CYLINDER }
    description: "Add stretchers between legs"
    optional: true
    include_stretchers: true
    tags: ["stretchers", "support"]
```

**Filtering Strategy (3 Tiers):**

WorkflowAdapter uses a multi-tier fallback strategy for MEDIUM confidence:

1. **Tag Matching** (fast) - Check if any `tags` appear in prompt
2. **Semantic Filter Parameters** (Phase 2) - Check custom boolean params
3. **Semantic Similarity** (slow) - Use LaBSE embeddings as fallback

**When to Use:**

| Feature Type | Use | Example |
|--------------|-----|---------|
| **Explicit fields** | Documented behavior with code logic | `disable_adaptation`, `optional`, `condition` |
| **Semantic filters** | Workflow-specific features | `add_bench`, `include_stretchers`, `decorative` |
| **Tags** | Fast keyword matching | `tags: ["bench", "seating"]` |

**Best Practices:**

```yaml
# ✅ Good: Combine semantic filter with tags for reliability
- tool: modeling_create_primitive
  params: { primitive_type: CUBE }
  description: "Create bench"
  optional: true
  add_bench: true        # Semantic filter
  tags: ["bench"]        # Fallback tag matching

# ❌ Bad: No tags, only semantic filter (less reliable)
- tool: modeling_create_primitive
  params: { primitive_type: CUBE }
  description: "Create bench"
  optional: true
  add_bench: true        # What if parameter name changes?

# ✅ Good: Use descriptive parameter names
add_bench: true          # Clear: "bench" keyword
include_handles: true    # Clear: "handles" keyword

# ❌ Bad: Unclear parameter names
feature_1: true          # Unclear: what keyword?
enable_extra: true       # Unclear: what keyword?
```

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
  # Trigonometry for leg stretching
  translate: ["$CALCULATE(0.342 * sin(leg_angle_left))", 0, "$CALCULATE(0.342 * cos(leg_angle_left))"]
  # Advanced: logarithmic scaling
  scale_factor: "$CALCULATE(log10(object_count + 1))"
  # Advanced: angle calculation
  rotation: ["$CALCULATE(atan2(height, width))", 0, 0]
```

**Available Math Functions** (TASK-056-1):

| Category | Functions | Description |
|----------|-----------|-------------|
| **Basic** | `abs()`, `min()`, `max()` | Absolute value, minimum, maximum |
| **Rounding** | `round()`, `floor()`, `ceil()`, `trunc()` | Round to integer, floor, ceiling, truncate |
| **Power/Root** | `sqrt()`, `pow()`, `**` | Square root, power, exponentiation |
| **Trigonometric** | `sin()`, `cos()`, `tan()` | Sine, cosine, tangent (radians) |
| **Inverse Trig** | `asin()`, `acos()`, `atan()`, `atan2()` | Arc sine, arc cosine, arc tangent |
| **Angle Conversion** | `degrees()`, `radians()` | Convert radians↔degrees |
| **Logarithmic** | `log()`, `log10()`, `exp()` | Natural log, base-10 log, e^x |
| **Advanced** | `hypot()` | Hypotenuse: sqrt(x² + y²) |

**Usage Examples:**

```yaml
# Angle calculation from dimensions
rotation: ["$CALCULATE(atan2(height, width))", 0, 0]

# Logarithmic scaling
scale: "$CALCULATE(log10(100))"  # = 2.0

# Exponential decay
alpha: "$CALCULATE(exp(-distance / falloff_radius))"

# Hypotenuse for diagonal distance
diagonal: "$CALCULATE(hypot(width, height))"

# Convert degrees to radians
angle_rad: "$CALCULATE(radians(45))"  # = 0.785...

# Tangent for slope calculation
slope: "$CALCULATE(tan(leg_angle))"
```

**Available Variables:**
- `width`, `height`, `depth` - Object dimensions
- `min_dim`, `max_dim` - Min/max of dimensions
- Any workflow parameter from `defaults` or `modifiers`

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

## Parametric Variables (TASK-052)

Define variable defaults and keyword-based modifiers for dynamic parameter adaptation.

### Defaults Section

Define default values for variables used in step params:

```yaml
defaults:
  leg_angle: 0.32        # Default angle (A-frame)
  table_height: 0.75     # Standard table height
  leg_count: 4           # Number of legs
```

### Modifiers Section

Map keywords/phrases to variable overrides:

```yaml
modifiers:
  # English
  "straight legs":
    leg_angle: 0
    negative_signals: ["X", "crossed", "angled", "diagonal"]  # TASK-055-FIX-2
  "vertical legs":
    leg_angle: 0
  "angled legs":
    leg_angle: 0.32

  # Polish
  "proste nogi":
    leg_angle: 0
    negative_signals: ["X", "skrzyżowane", "skośne"]  # Polish contradictions
  "skośne nogi":
    leg_angle: 0.32

  # Combined modifiers
  "coffee table":
    table_height: 0.45
  "bar table":
    table_height: 1.1
```

**Negative Signals (TASK-055-FIX-2)**: Optional list of contradictory terms that reject the match. If any term from `negative_signals` appears in the user prompt, the modifier is rejected even if semantic similarity is high.

**Example**:
- Prompt: "table with X-shaped legs" + modifier `"straight legs"`
  - "X" is in `negative_signals` → Match rejected ❌
- Prompt: "table with straight legs" + modifier `"straight legs"`
  - No negative signals present → Match accepted ✅

### Using Variables in Steps

Reference variables with `$variable_name` syntax:

```yaml
steps:
  - tool: modeling_transform_object
    params:
      name: "Leg_FL"
      rotation: [0, "$leg_angle", 0]      # Single variable
      location: [0.5, 0.5, "$table_height"]  # Mixed with literals

  - tool: modeling_transform_object
    params:
      scale: ["$leg_width", "$leg_width", "$leg_height"]  # Multiple variables
```

### Variable Resolution Order

Variables are resolved in this order (later overrides earlier):

1. **defaults** - Workflow-defined defaults
2. **modifiers** - Keyword matches from user prompt
3. **params** - Explicit parameters passed to expand_workflow()

---

## Advanced Workflow Features (TASK-056)

### Enum Parameter Validation (TASK-056-3)

Restrict parameter values to a discrete set of choices:

```yaml
parameters:
  table_style:
    type: string
    enum: ["modern", "rustic", "industrial", "traditional"]
    default: "modern"
    description: Style of table construction
    semantic_hints: ["style", "design"]

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

**Benefits:**
- Type safety: Invalid values rejected automatically
- Self-documenting: Clear choices for users
- LLM guidance: LLM sees valid options in schema

**Validation:**
- Enum check happens **before** range validation
- Default value must be in enum list
- Works with any type (string, int, float, bool)

### Computed Parameters (TASK-056-5)

Define parameters that are automatically calculated from other parameters:

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
    description: Number of planks needed to span table width

  # Computed: Actual plank width (adjusted to fit exactly)
  plank_actual_width:
    type: float
    computed: "table_width / plank_count"
    depends_on: ["table_width", "plank_count"]
    description: Actual width of each plank (adjusted to fit)

  # Computed: Aspect ratio
  aspect_ratio:
    type: float
    computed: "width / height"
    depends_on: ["width", "height"]
    description: Width to height ratio

  # Computed: Diagonal distance
  diagonal:
    type: float
    computed: "hypot(width, height)"
    depends_on: ["width", "height"]
    description: Diagonal distance across table top
```

**How It Works:**
1. Router resolves computed parameters in **dependency order** (topological sort)
2. Each computed parameter evaluates its `computed` expression
3. Result becomes available for dependent parameters
4. Circular dependencies are detected and rejected

**Usage in Steps:**

```yaml
steps:
  # Use computed parameter like any other
  - tool: modeling_create_primitive
    params:
      primitive_type: CUBE
      scale: ["$plank_actual_width", 1, 0.1]
    description: "Create plank with exact width"

  # Conditional step based on computed value
  - tool: modeling_create_primitive
    params:
      primitive_type: CUBE
    description: "Add extra support for wide tables"
    condition: "plank_count >= 12"
```

**Benefits:**
- Automatic calculations: No need to repeat formulas in steps
- Dependency tracking: Parameters resolve in correct order
- Dynamic adaptation: Computed values adjust to input dimensions

### Step Dependencies and Execution Control (TASK-056-4)

Control step execution order and error handling:

```yaml
steps:
  - id: "create_base"
    tool: modeling_create_primitive
    params:
      primitive_type: CUBE
      name: "Base"
    description: Create table base
    timeout: 5.0                # Max execution time (seconds)
    max_retries: 2              # Retry attempts on failure
    retry_delay: 1.0            # Delay between retries (seconds)

  - id: "scale_base"
    tool: modeling_transform_object
    depends_on: ["create_base"]  # Wait for create_base to complete
    params:
      name: "Base"
      scale: [1, 2, 0.1]
    description: Scale base to correct proportions
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

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique step identifier |
| `depends_on` | list[string] | Step IDs this depends on |
| `timeout` | float | Max execution time (seconds) |
| `max_retries` | int | Retry attempts on failure |
| `retry_delay` | float | Delay between retries |
| `on_failure` | string | "skip", "abort", "continue" |
| `priority` | int | Higher = execute earlier |

**Features:**
- **Dependency resolution**: Steps execute in correct order (topological sort)
- **Circular dependency detection**: Rejects invalid dependency graphs
- **Timeout enforcement**: Kills long-running steps
- **Retry mechanism**: Automatically retries failed steps
- **Priority ordering**: Control execution order for independent steps

**Use Cases:**

```yaml
# Ensure creation before transformation
- id: "create"
  tool: modeling_create_primitive
  params: {primitive_type: CUBE}

- id: "transform"
  depends_on: ["create"]
  tool: modeling_transform_object
  params: {scale: [1, 2, 1]}

# Retry on failure (e.g., import from network)
- tool: import_fbx
  params: {filepath: "https://example.com/model.fbx"}
  max_retries: 3
  retry_delay: 2.0
  timeout: 30.0
  on_failure: "skip"
```

---

### Complete Example

```yaml
name: configurable_table_workflow
description: Table with configurable leg angle

defaults:
  leg_angle_left: 0.32
  leg_angle_right: -0.32
  table_height: 0.75

modifiers:
  "straight legs":
    leg_angle_left: 0
    leg_angle_right: 0
  "proste nogi":
    leg_angle_left: 0
    leg_angle_right: 0
  "coffee table":
    table_height: 0.45

steps:
  - tool: modeling_create_primitive
    params:
      primitive_type: CUBE
      name: "TableTop"

  - tool: modeling_transform_object
    params:
      name: "TableTop"
      location: [0, 0, "$table_height"]

  - tool: modeling_transform_object
    params:
      name: "Leg_FL"
      rotation: [0, "$leg_angle_left", 0]

  - tool: modeling_transform_object
    params:
      name: "Leg_FR"
      rotation: [0, "$leg_angle_right", 0]

  # Optional step: only execute for X-shaped legs with high angles
  - tool: mesh_transform_selected
    params:
      translate: ["$CALCULATE(0.342 * sin(leg_angle_left))", 0, "$CALCULATE(0.342 * cos(leg_angle_left))"]
    description: "Stretch leg top for X-shaped configuration"
    condition: "leg_angle_left > 0.5 or leg_angle_left < -0.5"
```

### Behavior Examples

| User Prompt | Variables Applied |
|-------------|-------------------|
| "create a table" | defaults only: leg_angle_left=0.32 |
| "table with straight legs" | modifier: leg_angle_left=0 |
| "straight legs coffee table" | both modifiers: leg_angle=0, height=0.45 |
| "stół z proste nogi" | Polish modifier: leg_angle=0 |

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

## Sample Prompts (Semantic Matching)

> **Status:** ✅ Done (TASK-046) | Requires LaBSE model (~1.8GB)

`sample_prompts` enable **semantic matching** using LaBSE embeddings. Unlike keyword matching (exact "phone" → phone_workflow), semantic matching understands meaning:

```
User: "design a mobile device"
→ No exact keyword match
→ LaBSE finds similarity to "create a phone" (0.85)
→ phone_workflow triggers
```

### Why Use Sample Prompts?

| Feature | `trigger_keywords` | `sample_prompts` |
|---------|-------------------|------------------|
| Matching | Exact substring | Semantic similarity |
| Multilingual | Manual per language | Automatic (109 languages) |
| Variations | Must list all | Understands synonyms |
| Speed | Instant | ~10ms (embeddings) |

### Syntax

```yaml
sample_prompts:
  # English variations
  - "create a phone"
  - "make a smartphone"
  - "model a mobile device"
  - "build a cellphone"

  # Polish (LaBSE understands meaning)
  - "zrób telefon"
  - "stwórz smartfon"

  # German
  - "erstelle ein Handy"

  # Spanish
  - "crear un teléfono móvil"
```

### How It Works

1. **Embedding**: Each `sample_prompt` is converted to a 768-dim vector by LaBSE
2. **User Prompt**: User's text is also embedded
3. **Similarity**: Cosine similarity finds closest workflow
4. **Threshold**: Match if similarity > 0.5 (configurable)

### Matching Hierarchy

Router tries matching in this order:

```
1. Exact keyword match (fastest)     → confidence = 1.0
2. Semantic similarity (sample_prompts) → confidence = score
3. Generalization (combine similar workflows) → confidence = score * 0.8
```

### Best Practices for Sample Prompts

```yaml
# Good: Diverse, natural language
sample_prompts:
  - "create a phone"
  - "model a smartphone with screen"
  - "I want to make a mobile device"
  - "design an iPhone-like object"

# Bad: Too similar, keyword-like
sample_prompts:
  - "phone"
  - "smartphone"
  - "mobile"
```

### Multilingual Support

LaBSE supports 109 languages. Add prompts in any language:

```yaml
sample_prompts:
  # No need to translate all - LaBSE understands cross-lingual
  - "create a chair"      # English
  - "zrób krzesło"        # Polish
  - "créer une chaise"    # French
  - "Stuhl erstellen"     # German
  - "создать стул"        # Russian
  - "椅子を作る"           # Japanese
```

### Complete Example with Sample Prompts

```yaml
name: chair_workflow
description: Create a simple chair with legs and seat
category: furniture
author: BlenderAI
version: "1.0"

trigger_keywords:
  - chair
  - seat
  - stool

sample_prompts:
  # English
  - "create a chair"
  - "make a wooden chair"
  - "model a seat with legs"
  - "build a simple stool"
  - "design an office chair"

  # Polish
  - "zrób krzesło"
  - "stwórz fotel"
  - "zaprojektuj taboret"

  # German
  - "erstelle einen Stuhl"
  - "baue einen Hocker"

steps:
  - tool: modeling_create_primitive
    params:
      type: CUBE
    description: Create seat base
  # ... more steps
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
