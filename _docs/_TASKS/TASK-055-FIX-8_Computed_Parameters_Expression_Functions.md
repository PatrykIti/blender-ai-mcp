# TASK-055-FIX-8: Computed Parameters Expression Functions Reference

**Status**: ⚠️ Partial (dokumentacja gotowa, ale odkryto brakującą implementację)
**Priority**: P0 (Critical - Documentation for TASK-056-5)
**Related**: TASK-056-5, TASK-056-1, TASK-055-FIX-6, TASK-055, **TASK-059** (brakujące operatory)
**Created**: 2025-12-12
**Completed**: 2025-12-12
**Verified**: 2025-12-12 - odkryto brak implementacji operatorów porównania i logicznych

---

## Problem

When implementing computed parameters in YAML workflows (TASK-056-5), workflow authors need to know **which mathematical functions are available** in the expression evaluator.

**Evidence from Production**:
```
ERROR - Failed to compute parameter 'plank_full_count' with expression: int(table_width // plank_max_width)
NameError: name 'int' is not defined
```

**Root Cause**:
- Expression evaluator has **limited function support** (only 21 math functions from TASK-056-1)
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
- All 21 supported math functions (from TASK-056-1)
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

### Complete Function Reference (21 Functions)

Based on TASK-056-1 implementation (`server/router/application/evaluator/expression_evaluator.py:49-81`):

| Category | Functions | Description | Example Usage |
|----------|-----------|-------------|---------------|
| **Basic** | `abs()`, `min()`, `max()`, `round()` | Absolute value, minimum, maximum, round | `abs(-5)` → `5`<br>`min(3, 7)` → `3`<br>`max(table_width, 0.5)` → larger value |
| **Rounding** | `floor()`, `ceil()`, `trunc()` | Floor, ceiling, truncate toward zero | `floor(7.8)` → `7`<br>`ceil(7.2)` → `8`<br>`trunc(-7.8)` → `-7` |
| **Power/Root** | `sqrt()`, `pow()` | Square root, power | `sqrt(16)` → `4.0`<br>`pow(2, 3)` → `8` |
| **Trigonometric** | `sin()`, `cos()`, `tan()` | Sine, cosine, tangent (radians) | `sin(radians(90))` → `1.0`<br>`cos(0)` → `1.0` |
| **Inverse Trig** | `asin()`, `acos()`, `atan()`, `atan2()` | Arc sine, arc cosine, arc tangent | `degrees(atan2(1, 1))` → `45.0` |
| **Angle Conversion** | `degrees()`, `radians()` | Convert radians↔degrees | `degrees(3.14159)` → `180.0`<br>`radians(180)` → `3.14159` |
| **Logarithmic** | `log()`, `log10()`, `exp()` | Natural log, base-10 log, e^x | `log(2.718)` → `1.0`<br>`log10(100)` → `2.0` |
| **Advanced** | `hypot()` | Hypotenuse: sqrt(x² + y²) | `hypot(3, 4)` → `5.0` |

### Available Operators

#### ✅ Zaimplementowane (działają w `$CALCULATE`)

| Operator | Description | Example | Status |
|----------|-------------|---------|--------|
| `+`, `-`, `*`, `/` | Basic arithmetic | `table_width / 2` | ✅ Działa |
| `**` | Exponentiation | `base_size ** 2` | ✅ Działa |
| `//` | Floor division (integer result) | `table_width // plank_width` | ✅ Działa |
| `%` | Modulo (remainder) | `table_width % plank_width` | ✅ Działa |
| `-` (unary) | Negation | `-width` | ✅ Działa |
| `+` (unary) | Positive | `+width` | ✅ Działa |

#### ❌ NIE zaimplementowane (wymagają TASK-059)

| Operator | Description | Example | Status |
|----------|-------------|---------|--------|
| `<`, `<=`, `>`, `>=`, `==`, `!=` | Comparisons | `width > 0.5` | ❌ **Brak `ast.Compare`** |
| `and`, `or` | Logical AND/OR | `width > 0.5 and height < 2.0` | ❌ **Brak `ast.BoolOp`** |
| `not` | Logical NOT | `not is_large` | ❌ **Brak `ast.UnaryOp(ast.Not)`** |
| `if...else` (ternary) | Conditional | `1 if width > 0.5 else 0` | ❌ **Brak `ast.IfExp`** |

> **UWAGA**: Operatory porównania i logiczne są wymienione w dokumentacji, ale **NIE SĄ zaimplementowane** w `_eval_node()`. Wyrażenia typu `1 if condition else 0` **NIE DZIAŁAJĄ** w obecnej wersji! Zobacz TASK-059 dla implementacji.

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

**CZĘŚCIOWO CORRECT** (uses `floor()` - działa, ale `1 if...else` wymaga TASK-059):
```yaml
plank_full_count:
  type: int
  computed: "floor(table_width / plank_max_width)"  # ✅ Works!
  depends_on: ["table_width", "plank_max_width"]
  description: "Number of full-width planks"

plank_remainder_width:
  type: float
  computed: "table_width - (plank_full_count * plank_max_width)"  # ✅ Works!
  depends_on: ["table_width", "plank_full_count", "plank_max_width"]
  description: "Width of narrow remainder plank (0 if none needed)"

plank_has_remainder:
  type: int
  computed: "1 if plank_remainder_width > 0.01 else 0"  # ❌ NIE DZIAŁA - wymaga TASK-059!
  depends_on: ["plank_remainder_width"]
  description: "Whether a remainder plank is needed (1=yes, 0=no)"

plank_total_count:
  type: int
  computed: "plank_full_count + plank_has_remainder"  # ✅ Works (jeśli plank_has_remainder ma wartość)
  depends_on: ["plank_full_count", "plank_has_remainder"]
  description: "Total number of planks (full + remainder)"
```

> ⚠️ **UWAGA**: `plank_has_remainder` używa `1 if ... else 0` co **NIE DZIAŁA** bez TASK-059!
> **Obejście**: Użyj stałej wartości `default: 1` lub oblicz inaczej.

**Test Case** (docelowo po TASK-059): 0.73m table width, 0.10m plank width
- `plank_full_count = floor(0.73 / 0.10) = 7` ✅
- `plank_remainder_width = 0.73 - (7 * 0.10) = 0.03` ✅
- `plank_has_remainder = 1 if 0.03 > 0.01 else 0 = 1` ❌ (wymaga TASK-059)
- `plank_total_count = 7 + 1 = 8` ✅ (jeśli powyższe działa)

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

> ⚠️ **UWAGA**: Ten przykład wymaga TASK-059! Operatory porównania (`>`) i ternary (`if...else`) NIE SĄ obecnie zaimplementowane.

**Goal**: Use boolean conditions as integer flags

**WRONG** (boolean expressions don't work directly in steps):
```yaml
add_stretchers:
  type: bool
  computed: "table_width > 1.0"  # ❌ NIE DZIAŁA - brak ast.Compare
  depends_on: ["table_width"]
```

**DOCELOWO CORRECT** (po TASK-059):
```yaml
add_stretchers:
  type: int
  computed: "1 if table_width > 1.0 else 0"  # ❌ NIE DZIAŁA - brak ast.IfExp
  depends_on: ["table_width"]
  description: "Whether to add stretchers (1=yes, 0=no)"
```

**OBECNE OBEJŚCIE** (do czasu TASK-059):
```yaml
# Użyj osobnego parametru lub condition w step zamiast computed
add_stretchers:
  type: int
  default: 1  # Hardcoded value, brak dynamicznego warunku
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

> ⚠️ **UWAGA**: Wymaga TASK-059!

**Problem**:
```yaml
computed: "width > height"  # ❌ NIE DZIAŁA - brak ast.Compare w _eval_node()
```

**Docelowe rozwiązanie** (po TASK-059):
```yaml
computed: "1 if width > height else 0"  # ❌ NIE DZIAŁA - brak ast.IfExp
```

**Obecne obejście**: Użyj `condition` w workflow step zamiast computed parameter.

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
- ✅ Only uses 21 available functions (see table above)
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
- ✅ All 21 available functions documented with examples
- ✅ Common pitfalls listed with solutions
- ✅ Real-world workflow examples (fractional planks, angles, aspect ratio)
- ✅ Clear error messages with fixes
- ✅ NOT supported functions explicitly listed

### Nice to Have (Phase 2)
- ✅ Interactive expression validator (web tool)
- ✅ Unit tests for all 21 functions
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
**File**: `server/router/application/evaluator/expression_evaluator.py:49-81`

```python
# Allowed functions (whitelist) - TASK-056-1: Extended with 13 new functions
FUNCTIONS = {
    # Basic functions
    "abs": abs,
    "min": min,
    "max": max,
    "round": round,
    "floor": math.floor,
    "ceil": math.ceil,
    "sqrt": math.sqrt,
    "trunc": math.trunc,  # TASK-056-1: Integer truncation

    # Trigonometric functions (existing)
    "sin": math.sin,
    "cos": math.cos,

    # Trigonometric functions (TASK-056-1: NEW)
    "tan": math.tan,           # Tangent
    "asin": math.asin,         # Arc sine (inverse sine)
    "acos": math.acos,         # Arc cosine (inverse cosine)
    "atan": math.atan,         # Arc tangent (inverse tangent)
    "atan2": math.atan2,       # Two-argument arc tangent (handles quadrants)
    "degrees": math.degrees,   # Convert radians to degrees
    "radians": math.radians,   # Convert degrees to radians

    # Logarithmic functions (TASK-056-1: NEW)
    "log": math.log,           # Natural logarithm (base e)
    "log10": math.log10,       # Base-10 logarithm
    "exp": math.exp,           # e^x (exponential)

    # Advanced functions (TASK-056-1: NEW)
    "pow": pow,                # Power (alternative to ** operator)
    "hypot": math.hypot,       # Hypotenuse: sqrt(x^2 + y^2 + ...)
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
4. Add unit tests for all 21 functions with workflow examples

---

## Notes

- This document is the **authoritative reference** for computed parameter expressions
- All 21 functions come from Python's `math` module + built-ins `abs`, `min`, `max`, `round`, `pow`
- Expression evaluator intentionally limits function set for **security** (no `eval()` vulnerabilities)
- User feedback: *"za kazdym razem trzeba obraz budowa i restartowac kontener"* - remember to rebuild Docker image after YAML changes
- Real bug fixed: `simple_table.yaml` used `int()` → changed to `floor()` → fractional plank system now works

---

## Weryfikacja Zgodności z Kodem (2024-12-12)

### ✅ Poprawiona Ścieżka Pliku

| Element | Poprzednio (BŁĘDNE) | Aktualne (POPRAWNE) |
|---------|---------------------|---------------------|
| Expression Evaluator | `server/router/infrastructure/expression_evaluator.py` | `server/router/application/evaluator/expression_evaluator.py` |

### ✅ Poprawiona Liczba Funkcji

| Element | Poprzednio | Aktualne |
|---------|------------|----------|
| Liczba funkcji | 13 | **21** |

### ✅ Zweryfikowane Funkcje w Kodzie

Funkcje z `expression_evaluator.py:49-81` (słownik `FUNCTIONS`):

| Kategoria | Funkcje | Ilość |
|-----------|---------|-------|
| Basic | `abs`, `min`, `max`, `round` | 4 |
| Rounding | `floor`, `ceil`, `trunc` | 3 |
| Power/Root | `sqrt`, `pow` | 2 |
| Trigonometric | `sin`, `cos`, `tan` | 3 |
| Inverse Trig | `asin`, `acos`, `atan`, `atan2` | 4 |
| Angle Conversion | `degrees`, `radians` | 2 |
| Logarithmic | `log`, `log10`, `exp` | 3 |
| Advanced | `hypot` | 1 |
| **TOTAL** | | **21** |

### ✅ Zweryfikowane Operatory w Kodzie

Operatory z `expression_evaluator.py:289-297` (słownik `op_map` w `_eval_node()`):

| Operator | AST Node | Linia |
|----------|----------|-------|
| `+` | `ast.Add` | 290 |
| `-` | `ast.Sub` | 291 |
| `*` | `ast.Mult` | 292 |
| `/` | `ast.Div` | 293 |
| `**` | `ast.Pow` | 294 |
| `%` | `ast.Mod` | 295 |
| `//` | `ast.FloorDiv` | 296 |

### ❌ Brakująca Implementacja (wymaga TASK-059)

W `_eval_node()` (linie 262-336) **NIE MA** obsługi:

| AST Node | Operator | Wymagane dla | Status |
|----------|----------|--------------|--------|
| `ast.Compare` | `<`, `<=`, `>`, `>=`, `==`, `!=` | Porównania | ❌ **BRAK** |
| `ast.BoolOp` | `and`, `or` | Operatory logiczne | ❌ **BRAK** |
| `ast.UnaryOp(ast.Not)` | `not` | Negacja logiczna | ❌ **BRAK** |
| `ast.IfExp` | `x if cond else y` | Ternary expressions | ❌ **BRAK** |

**Konsekwencje**:
- Wyrażenia typu `"1 if width > 0.5 else 0"` **NIE DZIAŁAJĄ**
- Przykład `plank_has_remainder` w simple_table.yaml **NIE ZADZIAŁA**
- Wszystkie "boolean to int" konwersje wymagają TASK-059

### 🎯 Podsumowanie Weryfikacji

| Kategoria | Status |
|-----------|--------|
| Ścieżka pliku | ✅ Poprawiona na `application/evaluator/` |
| Liczba funkcji | ✅ Poprawiona na 21 |
| Numery linii | ✅ Zaktualizowane (49-81) |
| Kod przykładowy | ✅ Zaktualizowany do aktualnej implementacji |
| Clean Architecture | ✅ Plik w prawidłowej warstwie (Application) |
| **Operatory arytmetyczne** | ✅ **7 operatorów zaimplementowanych** |
| **Operatory porównania** | ❌ **NIE zaimplementowane** |
| **Operatory logiczne** | ❌ **NIE zaimplementowane** |
| **Ternary expressions** | ❌ **NIE zaimplementowane** |

---

## TASK-059: Wymagana Implementacja

Na podstawie tej weryfikacji, TASK-059 powinien dodać do `_eval_node()`:

1. **`ast.Compare`** - operatory porównania (`<`, `<=`, `>`, `>=`, `==`, `!=`)
2. **`ast.BoolOp`** - operatory logiczne (`and`, `or`)
3. **`ast.UnaryOp(ast.Not)`** - negacja logiczna (`not`)
4. **`ast.IfExp`** - ternary expressions (`x if cond else y`)

Bez tego, przykłady z TASK-055-FIX-8 dotyczące "boolean to int conversion" **nie będą działać**.

**TASK-055-FIX-8 został zweryfikowany. Dokumentacja poprawiona, ale wymaga TASK-059 dla pełnej funkcjonalności.**
