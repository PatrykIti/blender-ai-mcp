# TASK-055-FIX-8: Computed Parameters Expression Functions Reference

**Status**: ✅ Done
**Priority**: P0 (Critical - Documentation for TASK-056-5)
**Related**: TASK-056-5, TASK-056-1, TASK-055-FIX-6, TASK-055
**Created**: 2025-12-12
**Completed**: 2025-12-12

---

## Problem

When implementing computed parameters in YAML workflows (TASK-056-5), workflow authors need to know **which mathematical functions are available** in the expression evaluator.

**Evidence from Production**:
```
ERROR - Failed to compute parameter 'plank_full_count' with expression: int(table_width // plank_max_width)
NameError: name 'int' is not defined
```

**Root Cause**:
- Expression evaluator has **limited function support** (only 13 math functions from TASK-056-1)
- Common Python functions like `int()`, `str()`, `len()` are **NOT available**
- No comprehensive documentation exists for workflow authors

**Real-World Impact**:
- `simple_table.yaml` fractional plank system failed due to `int()` usage
- Workflow authors must guess which functions are supported
- Trial-and-error approach wastes development time

---

## Requirements

### 1. Document Available Expression Functions

Create authoritative reference listing:
- All 13 supported math functions (from TASK-056-1)
- Function categories (basic, rounding, trigonometric, etc.)
- Usage examples for each function
- Common pitfalls and NOT supported functions

### 2. Provide Workflow-Specific Examples

Show real-world computed parameter use cases:
- Integer division for plank counting
- Modulo for remainder calculation
- Boolean-to-int conversion for conditional logic
- Min/max for constraint enforcement

### 3. Clear Error Messages

Document common errors:
- `NameError: name 'int' is not defined` → Use `floor()` instead
- Boolean expressions → Convert to `1 if condition else 0`
- String operations → NOT supported (no `str()`, `format()`, etc.)

---

## Available Expression Functions

### Complete Function Reference (13 Functions)

Based on TASK-056-1 implementation (`server/router/infrastructure/expression_evaluator.py:60-72`):

| Category | Functions | Description | Example Usage |
|----------|-----------|-------------|---------------|
| **Basic** | `abs()`, `min()`, `max()` | Absolute value, minimum, maximum | `abs(-5)` → `5`<br>`min(3, 7)` → `3`<br>`max(table_width, 0.5)` → larger value |
| **Rounding** | `round()`, `floor()`, `ceil()`, `trunc()` | Round to integer, floor, ceiling, truncate | `floor(7.8)` → `7`<br>`ceil(7.2)` → `8`<br>`round(7.5)` → `8` |
| **Power/Root** | `sqrt()`, `pow()`, `**` | Square root, power, exponentiation | `sqrt(16)` → `4.0`<br>`pow(2, 3)` → `8`<br>`2 ** 3` → `8` |
| **Trigonometric** | `sin()`, `cos()`, `tan()` | Sine, cosine, tangent (radians) | `sin(radians(90))` → `1.0`<br>`cos(0)` → `1.0` |
| **Inverse Trig** | `asin()`, `acos()`, `atan()`, `atan2()` | Arc sine, arc cosine, arc tangent | `degrees(atan2(1, 1))` → `45.0` |
| **Angle Conversion** | `degrees()`, `radians()` | Convert radians↔degrees | `degrees(3.14159)` → `180.0`<br>`radians(180)` → `3.14159` |
| **Logarithmic** | `log()`, `log10()`, `exp()` | Natural log, base-10 log, e^x | `log(2.718)` → `1.0`<br>`log10(100)` → `2.0` |
| **Advanced** | `hypot()` | Hypotenuse: sqrt(x² + y²) | `hypot(3, 4)` → `5.0` |

### Available Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `+`, `-`, `*`, `/` | Basic arithmetic | `table_width / 2` |
| `**` | Exponentiation | `base_size ** 2` |
| `//` | Floor division (integer result) | `table_width // plank_width` |
| `%` | Modulo (remainder) | `table_width % plank_width` |
| `<`, `<=`, `>`, `>=`, `==`, `!=` | Comparisons (return bool) | `width > 0.5` |
| `and`, `or`, `not` | Logical operators | `width > 0.5 and height < 2.0` |

---

## NOT Supported Functions

### Common Python Functions That DO NOT Work

| Function | Error | Use Instead |
|----------|-------|-------------|
| `int()` | `NameError: name 'int' is not defined` | `floor()` for positive numbers<br>`trunc()` for rounding toward zero |
| `str()` | `NameError: name 'str' is not defined` | NOT AVAILABLE - no string operations |
| `len()` | `NameError: name 'len' is not defined` | NOT AVAILABLE - no list/string operations |
| `bool()` | `NameError: name 'bool' is not defined` | Use `1 if condition else 0` |
| `range()` | `NameError: name 'range' is not defined` | NOT AVAILABLE - no iteration |
| `sum()` | `NameError: name 'sum' is not defined` | Use explicit addition: `a + b + c` |

---

## Real-World Workflow Examples

### Example 1: Fractional Plank System (simple_table.yaml)

**Goal**: Calculate how many full-width planks fit, plus remainder width

**WRONG** (uses `int()` - not available):
```yaml
plank_full_count:
  type: int
  computed: "int(table_width / plank_max_width)"  # ❌ NameError!
  depends_on: ["table_width", "plank_max_width"]
```

**CORRECT** (uses `floor()`):
```yaml
plank_full_count:
  type: int
  computed: "floor(table_width / plank_max_width)"  # ✅ Works!
  depends_on: ["table_width", "plank_max_width"]
  description: "Number of full-width planks"

plank_remainder_width:
  type: float
  computed: "table_width - (plank_full_count * plank_max_width)"
  depends_on: ["table_width", "plank_full_count", "plank_max_width"]
  description: "Width of narrow remainder plank (0 if none needed)"

plank_has_remainder:
  type: int
  computed: "1 if plank_remainder_width > 0.01 else 0"  # Boolean → int
  depends_on: ["plank_remainder_width"]
  description: "Whether a remainder plank is needed (1=yes, 0=no)"

plank_total_count:
  type: int
  computed: "plank_full_count + plank_has_remainder"
  depends_on: ["plank_full_count", "plank_has_remainder"]
  description: "Total number of planks (full + remainder)"
```

**Test Case**: 0.73m table width, 0.10m plank width
- `plank_full_count = floor(0.73 / 0.10) = 7`
- `plank_remainder_width = 0.73 - (7 * 0.10) = 0.03`
- `plank_has_remainder = 1 if 0.03 > 0.01 else 0 = 1`
- `plank_total_count = 7 + 1 = 8`

### Example 2: Angled Leg Constraints

**Goal**: Ensure leg angles stay within safe range

```yaml
leg_angle_clamped:
  type: float
  computed: "max(-1.57, min(1.57, leg_angle_raw))"  # Clamp to ±90°
  depends_on: ["leg_angle_raw"]
  description: "Leg angle clamped to safe range (±π/2 radians)"

leg_angle_degrees:
  type: float
  computed: "degrees(leg_angle_clamped)"
  depends_on: ["leg_angle_clamped"]
  description: "Leg angle in degrees for human readability"
```

### Example 3: Aspect Ratio Calculation

**Goal**: Calculate screen aspect ratio and diagonal

```yaml
aspect_ratio:
  type: float
  computed: "screen_width / screen_height"
  depends_on: ["screen_width", "screen_height"]
  description: "Screen aspect ratio (e.g., 1.778 for 16:9)"

diagonal_size:
  type: float
  computed: "hypot(screen_width, screen_height)"
  depends_on: ["screen_width", "screen_height"]
  description: "Screen diagonal in meters (Pythagorean theorem)"
```

### Example 4: Boolean to Int Conversion

**Goal**: Use boolean conditions as integer flags

**WRONG** (boolean expressions don't work directly in steps):
```yaml
add_stretchers:
  type: bool
  computed: "table_width > 1.0"  # ❌ Returns True/False, not 0/1
  depends_on: ["table_width"]
```

**CORRECT** (convert to int):
```yaml
add_stretchers:
  type: int
  computed: "1 if table_width > 1.0 else 0"  # ✅ Returns 0 or 1
  depends_on: ["table_width"]
  description: "Whether to add stretchers (1=yes, 0=no)"
```

---

## Common Pitfalls

### Pitfall 1: Using `int()` for Type Casting

**Problem**:
```yaml
computed: "int(value)"  # ❌ NameError: name 'int' is not defined
```

**Solution**:
```yaml
computed: "floor(value)"  # ✅ For positive numbers
computed: "trunc(value)"  # ✅ For rounding toward zero (handles negatives)
```

### Pitfall 2: Boolean Results in Numeric Context

**Problem**:
```yaml
computed: "width > height"  # ❌ Returns True/False (boolean)
```

**Solution**:
```yaml
computed: "1 if width > height else 0"  # ✅ Returns 0 or 1 (int)
```

### Pitfall 3: String Operations

**Problem**:
```yaml
computed: "str(width) + 'm'"  # ❌ NameError: name 'str' is not defined
```

**Solution**:
NOT AVAILABLE - Expression evaluator only supports numeric operations.
Use description field for string context instead.

### Pitfall 4: Division by Zero

**Problem**:
```yaml
computed: "total / count"  # ❌ ZeroDivisionError if count=0
```

**Solution**:
```yaml
computed: "total / max(count, 1)"  # ✅ Avoid division by zero
```

---

## Implementation Guide

### Step 1: Plan Your Computed Parameters

1. Identify parameter dependencies (which params depend on others)
2. Check if required functions are in the 13 available functions
3. Convert booleans to `1 if condition else 0` pattern
4. Use `floor()` instead of `int()` for integer conversion

### Step 2: Write Expressions

**Template**:
```yaml
param_name:
  type: int | float
  computed: "mathematical_expression_here"
  depends_on: ["dependency1", "dependency2"]
  description: "Human-readable description"
```

**Validation Checklist**:
- ✅ Only uses 13 available functions (see table above)
- ✅ No `int()`, `str()`, `len()`, `bool()` calls
- ✅ Boolean expressions converted to `1 if ... else 0`
- ✅ Dependencies listed in `depends_on` array
- ✅ Type matches expression result (`int` for `floor()`, `float` for `/`)

### Step 3: Test Expressions

**Manual Testing** (before workflow execution):
```python
# Python REPL test (same math module used by expression evaluator)
from math import *

table_width = 0.73
plank_max_width = 0.10

plank_full_count = floor(table_width / plank_max_width)
print(f"Full planks: {plank_full_count}")  # Expected: 7

plank_remainder_width = table_width - (plank_full_count * plank_max_width)
print(f"Remainder width: {plank_remainder_width}")  # Expected: 0.03

plank_has_remainder = 1 if plank_remainder_width > 0.01 else 0
print(f"Has remainder: {plank_has_remainder}")  # Expected: 1
```

---

## Error Handling Reference

### Common Errors and Solutions

| Error Message | Cause | Solution |
|---------------|-------|----------|
| `NameError: name 'int' is not defined` | Used `int()` function | Replace with `floor()` or `trunc()` |
| `NameError: name 'str' is not defined` | Used `str()` function | NOT AVAILABLE - remove string operations |
| `ZeroDivisionError` | Division by zero | Use `max(denominator, 1)` or conditional |
| `ValueError: math domain error` | Invalid input (e.g., `sqrt(-1)`) | Add validation: `sqrt(max(value, 0))` |
| `TypeError: unsupported operand type(s)` | Mixed types (e.g., bool + int) | Convert booleans: `1 if condition else 0` |

---

## Success Criteria

### Must Have (Phase 1)
- ✅ All 13 available functions documented with examples
- ✅ Common pitfalls listed with solutions
- ✅ Real-world workflow examples (fractional planks, angles, aspect ratio)
- ✅ Clear error messages with fixes
- ✅ NOT supported functions explicitly listed

### Nice to Have (Phase 2)
- ✅ Interactive expression validator (web tool)
- ✅ Unit tests for all 13 functions
- ✅ IDE autocomplete for workflow YAML files
- ✅ Linter to catch unsupported function usage

---

## Related Documentation

- **TASK-056-5**: Computed Parameters Implementation (uses this function reference)
- **TASK-056-1**: Expression Evaluator Implementation (defines the 13 functions)
- **TASK-055-FIX-6**: Flexible YAML Parameter Loading (template for this document)
- **yaml-workflow-guide.md**: Complete workflow authoring guide
- **creating-workflows-tutorial.md**: Step-by-step workflow creation

---

## Files to Reference

### Expression Evaluator Implementation
**File**: `server/router/infrastructure/expression_evaluator.py:60-72`

```python
def _get_safe_math_context(self) -> Dict[str, Any]:
    """Provide math functions for expressions."""
    return {
        # Basic
        "abs": abs,
        "min": min,
        "max": max,
        # Rounding
        "round": round,
        "floor": math.floor,
        "ceil": math.ceil,
        "trunc": math.trunc,
        # Power/Root
        "sqrt": math.sqrt,
        "pow": pow,
        # Trigonometric
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "asin": math.asin,
        "acos": math.acos,
        "atan": math.atan,
        "atan2": math.atan2,
        # Angle conversion
        "degrees": math.degrees,
        "radians": math.radians,
        # Logarithmic
        "log": math.log,
        "log10": math.log10,
        "exp": math.exp,
        # Advanced
        "hypot": math.hypot,
    }
```

### Workflow Example
**File**: `server/router/application/workflows/custom/simple_table.yaml:168-186`

```yaml
plank_full_count:
  type: int
  computed: "floor(table_width / plank_max_width)"
  depends_on: ["table_width", "plank_max_width"]
  description: "Number of full-width planks (realistic wood plank count)"

plank_remainder_width:
  type: float
  computed: "table_width - (plank_full_count * plank_max_width)"
  depends_on: ["table_width", "plank_full_count", "plank_max_width"]
  description: "Width of narrow remainder plank (0 if none needed)"

plank_has_remainder:
  type: int
  computed: "1 if plank_remainder_width > 0.01 else 0"
  depends_on: ["plank_remainder_width"]
  description: "Whether a remainder plank is needed (1=yes, 0=no)"

plank_total_count:
  type: int
  computed: "plank_full_count + plank_has_remainder"
  depends_on: ["plank_full_count", "plank_has_remainder"]
  description: "Total number of planks (full + remainder)"
```

---

## Quick Reference Card

### ✅ DO Use These Functions

```yaml
# Integer conversion
computed: "floor(value)"        # ✅ Positive numbers → int
computed: "trunc(value)"        # ✅ Round toward zero
computed: "ceil(value)"         # ✅ Round up

# Boolean to int
computed: "1 if condition else 0"  # ✅ Convert bool to 0/1

# Min/max constraints
computed: "max(value, 0)"       # ✅ Clamp minimum
computed: "min(value, 100)"     # ✅ Clamp maximum
computed: "max(-1.57, min(1.57, angle))"  # ✅ Clamp range

# Safe division
computed: "numerator / max(denominator, 1)"  # ✅ Avoid division by zero

# Modulo/remainder
computed: "width % plank_width"  # ✅ Get remainder
```

### ❌ DON'T Use These Functions

```yaml
computed: "int(value)"          # ❌ NameError
computed: "str(value)"          # ❌ NameError
computed: "bool(value)"         # ❌ NameError
computed: "len(list)"           # ❌ NameError
computed: "sum([a, b, c])"      # ❌ NameError
computed: "range(10)"           # ❌ NameError
```

---

## Recommendation

**For Workflow Authors**:
1. Bookmark this document as function reference
2. Test expressions in Python REPL before adding to YAML
3. Always use `floor()` instead of `int()`
4. Convert booleans to `1 if condition else 0`

**For Future Development**:
1. Consider adding `int()` wrapper in expression evaluator (wraps `floor()`)
2. Add expression validator to workflow loader (fail early with helpful errors)
3. Create IDE plugin for YAML workflow autocomplete
4. Add unit tests for all 13 functions with workflow examples

---

## Notes

- This document is the **authoritative reference** for computed parameter expressions
- All 13 functions come from Python's `math` module + built-ins `abs`, `min`, `max`, `round`, `pow`
- Expression evaluator intentionally limits function set for **security** (no `eval()` vulnerabilities)
- User feedback: *"za kazdym razem trzeba obraz budowa i restartowac kontener"* - remember to rebuild Docker image after YAML changes
- Real bug fixed: `simple_table.yaml` used `int()` → changed to `floor()` → fractional plank system now works
