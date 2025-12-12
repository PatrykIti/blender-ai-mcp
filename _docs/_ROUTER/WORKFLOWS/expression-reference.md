# Expression Reference

Complete reference for dynamic expressions in YAML workflows.

---

## Expression Types

| Syntax | Handler | Example |
|--------|---------|---------|
| `$CALCULATE(...)` | ExpressionEvaluator | `$CALCULATE(width * 0.5)` |
| `$AUTO_*` | ProportionResolver | `$AUTO_BEVEL` |
| `$variable` | Variable substitution | `$depth`, `$leg_angle` |
| `condition: "..."` | ConditionEvaluator | `current_mode != 'EDIT'` |

> **Note:** `$variable` can reference both context values (dimensions) and parametric variables from `defaults`/`modifiers` (TASK-052).

---

## $CALCULATE Expressions

Safe mathematical expression evaluator.

### Arithmetic Operators

| Operator | Example | Result |
|----------|---------|--------|
| `+` | `2 + 3` | `5` |
| `-` | `10 - 3` | `7` |
| `*` | `4 * 3` | `12` |
| `/` | `10 / 2` | `5` |
| `**` | `2 ** 3` | `8` |
| `%` | `10 % 3` | `1` |
| `//` | `10 // 3` | `3` |
| `-x` | `-5` | `-5` |

### Math Functions

| Function | Example | Result |
|----------|---------|--------|
| `abs(x)` | `abs(-5)` | `5` |
| `min(a, b, ...)` | `min(3, 1, 4)` | `1` |
| `max(a, b, ...)` | `max(3, 1, 4)` | `4` |
| `round(x)` | `round(3.7)` | `4` |
| `floor(x)` | `floor(3.7)` | `3` |
| `ceil(x)` | `ceil(3.2)` | `4` |
| `sqrt(x)` | `sqrt(9)` | `3` |

### Context Variables

| Variable | Source | Description |
|----------|--------|-------------|
| `width` | dimensions[0] | Object width (X) |
| `height` | dimensions[1] | Object height (Y) |
| `depth` | dimensions[2] | Object depth (Z) |
| `min_dim` | min(w, h, d) | Smallest dimension |
| `max_dim` | max(w, h, d) | Largest dimension |

### Examples

```yaml
# 5% of smallest dimension
"$CALCULATE(min_dim * 0.05)"

# Average of width and height
"$CALCULATE((width + height) / 2)"

# Square root of depth
"$CALCULATE(sqrt(depth))"

# Rounded to nearest 0.1
"$CALCULATE(round(width * 10) / 10)"

# Nested functions
"$CALCULATE(min(abs(-5), max(2, 3)))"
```

---

## $AUTO_* Parameters

Dimension-relative smart defaults.

### Bevel Parameters

| Parameter | Formula | Description |
|-----------|---------|-------------|
| `$AUTO_BEVEL` | `min(dims) * 0.05` | Standard bevel (5%) |
| `$AUTO_BEVEL_SMALL` | `min(dims) * 0.02` | Subtle bevel (2%) |
| `$AUTO_BEVEL_LARGE` | `min(dims) * 0.10` | Prominent bevel (10%) |

### Inset Parameters

| Parameter | Formula | Description |
|-----------|---------|-------------|
| `$AUTO_INSET` | `min(x, y) * 0.03` | Standard inset (3%) |
| `$AUTO_INSET_THICK` | `min(x, y) * 0.05` | Thick inset (5%) |

### Extrude Parameters

| Parameter | Formula | Description |
|-----------|---------|-------------|
| `$AUTO_EXTRUDE` | `z * 0.10` | Outward (10% of Z) |
| `$AUTO_EXTRUDE_SMALL` | `z * 0.05` | Small (5% of Z) |
| `$AUTO_EXTRUDE_DEEP` | `z * 0.20` | Deep (20% of Z) |
| `$AUTO_EXTRUDE_NEG` | `-z * 0.10` | Inward (-10% of Z) |

### Scale Parameters

| Parameter | Formula | Description |
|-----------|---------|-------------|
| `$AUTO_SCALE_SMALL` | `[x*0.8, y*0.8, z*0.8]` | Shrink to 80% |
| `$AUTO_SCALE_TINY` | `[x*0.5, y*0.5, z*0.5]` | Shrink to 50% |

### Other Parameters

| Parameter | Formula | Description |
|-----------|---------|-------------|
| `$AUTO_OFFSET` | `min(dims) * 0.02` | Small offset (2%) |
| `$AUTO_THICKNESS` | `z * 0.05` | Shell thickness (5% Z) |
| `$AUTO_SCREEN_DEPTH` | `z * 0.50` | Screen depth (50% Z) |
| `$AUTO_SCREEN_DEPTH_NEG` | `-z * 0.50` | Inward screen (-50% Z) |
| `$AUTO_LOOP_POS` | `0.8` | Loop cut position |

### Usage in Lists

```yaml
params:
  move:
    - 0
    - 0
    - "$AUTO_EXTRUDE_NEG"  # Works in lists

  scale: "$AUTO_SCALE_SMALL"  # Returns [x, y, z]
```

---

## Condition Expressions

Boolean expressions for step conditions.

### Comparison Operators

| Operator | Example | True When |
|----------|---------|-----------|
| `==` | `mode == 'EDIT'` | Equal |
| `!=` | `mode != 'EDIT'` | Not equal |
| `>` | `count > 0` | Greater |
| `<` | `count < 10` | Less |
| `>=` | `count >= 5` | Greater or equal |
| `<=` | `count <= 5` | Less or equal |

### Logical Operators

| Operator | Example | True When |
|----------|---------|-----------|
| `not` | `not has_selection` | Negates result |
| `and` | `A and B` | Both true |
| `or` | `A or B` | Either true |

### Available Variables

| Variable | Type | Example Values |
|----------|------|----------------|
| `current_mode` | str | `'OBJECT'`, `'EDIT'`, `'SCULPT'` |
| `has_selection` | bool | `True`, `False` |
| `object_count` | int | `0`, `5`, `10` |
| `selected_verts` | int | `0`, `8`, `100` |
| `selected_edges` | int | `0`, `12`, `50` |
| `selected_faces` | int | `0`, `6`, `24` |
| `active_object` | str | `'Cube'`, `'Sphere'` |

### String Literals

Use single or double quotes:
```yaml
condition: "current_mode == 'EDIT'"
condition: 'current_mode == "EDIT"'
```

### Boolean Literals

```yaml
condition: "true"   # Always execute
condition: "false"  # Never execute (for debugging)
```

### Complex Conditions

```yaml
# Edit mode AND has selection
condition: "current_mode == 'EDIT' and has_selection"

# Object mode OR no selection
condition: "current_mode == 'OBJECT' or not has_selection"

# At least 4 vertices selected
condition: "selected_verts >= 4"

# Not the active object named 'Camera'
condition: "active_object != 'Camera'"
```

---

## Simple $variable References

Direct context value lookup or parametric variable substitution (TASK-052).

### Usage

```yaml
params:
  depth: "$depth"        # Direct dimension
  current: "$mode"       # Current mode string
  angle: "$leg_angle"    # Parametric variable (from defaults/modifiers)
```

### Behavior

- If variable exists in context: returns its value
- If variable defined in `defaults`: returns default value
- If variable overridden by `modifiers`: returns modifier value
- If variable missing: returns original string (`$depth`)

### Parametric Variables (TASK-052)

When a workflow has `defaults` and `modifiers` sections, `$variable` references are resolved:

```yaml
defaults:
  leg_angle: 0.32

modifiers:
  "straight legs":
    leg_angle: 0

steps:
  - tool: modeling_transform_object
    params:
      rotation: [0, "$leg_angle", 0]  # Resolved from defaults or modifiers
```

**Resolution order:**
1. `defaults` - Base values
2. `modifiers` - Keyword-based overrides from user prompt
3. `params` - Explicit parameters (highest priority)

### Difference from $CALCULATE

| Syntax | Purpose | Example |
|--------|---------|---------|
| `$variable` | Direct lookup | `"$leg_angle"` → `0.32` |
| `$CALCULATE(...)` | Math expression | `"$CALCULATE(width * 0.5)"` → computed value |

Use `$variable` for simple substitution, `$CALCULATE` when you need math operations.

---

## Resolution Order

When expanding workflows, parameters are resolved in this order:

1. **$CALCULATE(...)** - ExpressionEvaluator
2. **$AUTO_*** - ProportionResolver
3. **$variable** - Context lookup
4. **Literal** - Pass through unchanged

---

## Error Handling

### $CALCULATE Errors

| Situation | Behavior |
|-----------|----------|
| Invalid syntax | Returns original string |
| Unknown variable | Returns `None` |
| Division by zero | Returns `None` |
| Blocked operation | Returns `None` |

### $AUTO_* Errors

| Situation | Behavior |
|-----------|----------|
| No dimensions | Returns original string |
| Unknown param | Returns original string |

### Condition Errors

| Situation | Behavior |
|-----------|----------|
| Unknown variable | Fail-open (returns `True`) |
| Parse error | Fail-open (returns `True`) |
| Empty condition | Returns `True` (execute step) |

---

## Security

### $CALCULATE Safety

The evaluator uses AST parsing (not `eval()`):

**Blocked:**
- `__import__('os')` - No imports
- `eval('code')` - No eval
- `exec('code')` - No exec
- `'str'.upper()` - No attribute access
- `list[0]` - No subscript access
- `open('file')` - No arbitrary functions

**Allowed:**
- Arithmetic operators
- Whitelisted math functions only
- Context variable references

---

## Examples by Use Case

### Proportional Bevel

```yaml
params:
  offset: "$CALCULATE(min_dim * 0.05)"
  # or simpler:
  offset: "$AUTO_BEVEL"
```

### Screen Cutout

```yaml
- tool: mesh_inset
  params:
    thickness: "$AUTO_INSET"

- tool: mesh_extrude_region
  params:
    move: [0, 0, "$AUTO_SCREEN_DEPTH_NEG"]
```

### Conditional Mode Switch

```yaml
- tool: system_set_mode
  params:
    mode: EDIT
  condition: "current_mode != 'EDIT'"
```

### Scale Transform

```yaml
- tool: modeling_transform_object
  params:
    scale: "$AUTO_SCALE_SMALL"  # Returns [0.8*w, 0.8*h, 0.8*d]
```

### Complex Calculation

```yaml
params:
  offset: "$CALCULATE(max(min_dim * 0.05, 0.01))"  # At least 0.01
```
